import cv2
import mediapipe as mp
import math
import numpy as np
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

print("Press 'q' to exit!")

pinch_history = []
buffer_size= 3
prev_frame_time = 0
was_pinched= False
drawing_segments = []
segment_lifetime = 3.0
active_strokes = {} # e.g. {"Left": [...], "Right": [...]}
was_pinched_per_hand = {} # e.g. {"Left": False, "Right": True}
pinch_history_per_hand = {} # e.g. {"Left": [...], "Right": [...]}

#=======================================================================================================================================
def fingers_up(landmark_list):
    fingers = []
    finger_tips = [8,12,16,20]
    finger_knuckles = [6,10,14,18]

    for tip_idx, knuckle_idx in zip(finger_tips,finger_knuckles):
        tip_y = landmark_list[tip_idx][1]
        knuckle_y = landmark_list[knuckle_idx][1]

        if tip_y < knuckle_y:
            fingers.append(True)
        else:
            fingers.append(False)
    return fingers

ink_colors = [(0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 255, 0)]  # yellow, magenta, green, cyan
current_color_index = 0
#was_peace_sign = False
#was_open_palm = False

open_palm_counter = 0
#peace_sign_counter = 0
required_frames = 5
color_index_per_hand = {}  # e.g. {"Left": 0, "Right": 2}
peace_sign_counter_per_hand = {} # each hand's different counter is needed
#=======================================================================================================================================

confirm_counter = 0
confirm_animation_start = None
animation_duration = 2.0


while True:
    success, frame = cap.read()
    if not success:
        print("Wasn't able to capture the frame")
        break
    frame = cv2.flip(frame, 1)
    h, w,_ = frame.shape

    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    all_index_tips = []

    if result.multi_hand_landmarks:
        print(f"Hands Found: {len(result.multi_hand_landmarks)}")
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            handedness = result.multi_handedness[idx].classification[0].label

            landmark_list=[]
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px,py))

            glow_layer = np.zeros_like(frame)

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx,end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(glow_layer, start_point, end_point, (0,255,255),2)

            for point in landmark_list:
                cv2.circle(glow_layer,point, 4 ,(255,255,0),-1)

            glow_small = cv2.GaussianBlur(glow_layer, (5,5),0)
            glow_large = cv2.GaussianBlur(glow_layer,(15,15),0)
            combined_glow = cv2.addWeighted(glow_small,0.8,glow_large,0.8,0)

            

            frame = cv2.addWeighted(frame,1.0,combined_glow,0.8,0)

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx,end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(frame, start_point, end_point, (0,255,255),2)

            for point in landmark_list:
                cv2.circle(frame, point, 5,(255,255,0),-1)

            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]
            all_index_tips.append(index_tip)
            
            cv2.putText(frame, handedness, (wrist[0] - 20, wrist[1] + 35),
                            cv2.FONT_HERSHEY_COMPLEX, 0.9, (255,255,255),1)

            x1,y1 = wrist
            x2,y2 = middle_knuckle
            palm_size = math.sqrt((x2-x1)**2 + (y2-y1)**2)

            x3,y3 = thumb_tip
            x4,y4 = index_tip
            pinch_distance = math.sqrt((x4-x3)**2 + (y4-y3)**2)

            pinch_ratio = pinch_distance/palm_size

            is_pinched_now = pinch_ratio<0.4

            pinch_history = pinch_history_per_hand.get(handedness, [])
 
            pinch_history.append(is_pinched_now)
            if len(pinch_history)>buffer_size:
                pinch_history.pop(0)

            pinch_history_per_hand[handedness] = pinch_history    

            if pinch_history.count(True) > buffer_size // 2:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

            was_pinched = was_pinched_per_hand.get(handedness, False)

            if pinch_status =="Pinched" and not was_pinched:
                active_strokes[handedness] = []
            if pinch_status == "Pinched":
                if handedness not in active_strokes or len(active_strokes.get(handedness, [])) == 0:
                    active_strokes[handedness] = []

                midpoint_x = (x3 + x4)//2
                midpoint_y = (y3 + y4)//2
                new_point = (midpoint_x,midpoint_y)
                
                if len(active_strokes[handedness]) >= 1:
                    last_point = active_strokes[handedness][-1]
                    lx, ly = last_point
                    jump_distance = math.sqrt((midpoint_x - lx) ** 2 + (midpoint_y - ly) ** 2)

                    MAX_JUMP = 80   # if the new point is farther than this, it's likely a
                                                        # mislabeled hand (MediaPipe briefly swapped Left/Right)

                    if jump_distance > MAX_JUMP:
                        active_strokes[handedness] = []   # start a fresh stroke instead of
                                                                                 # connecting to the wrong hand's point

                active_strokes[handedness].append(new_point)

                if len(active_strokes[handedness]) >= 2:
                    previous_point = active_strokes[handedness][-2]
                    birth_time = time.time()
                    this_hand_color_index = color_index_per_hand.get(handedness, 0)
                    drawing_segments.append((previous_point, new_point, birth_time, this_hand_color_index))

            was_pinched_per_hand[handedness] = (pinch_status == "Pinched")
            
            fingers = fingers_up(landmark_list)
            # fingers = [index, middle, ring, pinky] as True/False
            is_peace_sign = fingers == [True,True,False,False]
            is_open_palm = fingers == [True,True,True,True] and pinch_status != "Pinched"
                
            if is_open_palm:
                open_palm_counter += 1
            else:
                open_palm_counter = 0

            peace_sign_counter = peace_sign_counter_per_hand.get(handedness, 0)

            if is_peace_sign:
                peace_sign_counter += 1
            else:
                peace_sign_counter = 0

            peace_sign_counter_per_hand[handedness] = peace_sign_counter

            if open_palm_counter == required_frames:
                drawing_segments = []
                active_strokes = {}

            if peace_sign_counter == required_frames:
                current_color = color_index_per_hand.get(handedness, 0)
                color_index_per_hand[handedness] = (current_color + 1) % len(ink_colors)
            
            #if len(drawing_strokes)>0:
               # print(f"total strokes {len(drawing_strokes)}| length of current strokes {len(drawing_strokes[-1])}")


    print(f"collected tips : {all_index_tips}")
            #print(f"pinch ratio : {pinch_ratio:.2f}---->{pinch_status}")
            #print(f"raw : {is_pinched_now} | smoothed: {pinch_status} | pinch history: {pinch_history}")
            #print(f"wrist at : {wrist}")
            #print(f"middle knuckle at : {middle_knuckle}")
            #print(f"index fingertip at : {index_tip}")
            #print(f"thumb fingertip at : {thumb_tip}")
            #print(f"palm size is : {palm_size}")

    if len(all_index_tips) == 2:
        tip1 = all_index_tips[0]
        tip2 = all_index_tips[1]
        x1,y1 = tip1
        x2,y2 = tip2
        distance_between_hands = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        print(f"distance calculated : {distance_between_hands}")
        is_confirmed_gesture = distance_between_hands<20
    else:
        is_confirmed_gesture = False

    if is_confirmed_gesture:
        confirm_counter += 1
    else:
        confirm_counter = 0

    if confirm_counter == required_frames:
        confirm_animation_start = time.time()
        confirm_animation_point = ((x1+x2)//2 , (y1+y2)//2)




    canvas = np.zeros_like(frame)
    current_time = time.time()
    still_alive_segments = []

    for point1,point2, birth_time, color_idx in drawing_segments:
        age = current_time-birth_time
        if age < segment_lifetime:
            opacity = 1.0 - (age/segment_lifetime)
            base_color = ink_colors[color_idx]
            color = tuple(int(c * opacity) for c in base_color)
            cv2.line(canvas, point1, point2, color, 3)
            still_alive_segments.append((point1, point2, birth_time, color_idx))
    drawing_segments = still_alive_segments
    frame = cv2.addWeighted(frame, 1.0, canvas,1.0,0)    

    if confirm_animation_start is not None:
        elapsed = time.time() - confirm_animation_start

        if elapsed < animation_duration:
            progress = elapsed/animation_duration
            radius = int(20 + progress*60)
            opacity = 1.0 - progress

            color = (0, int(255*opacity), int(255*opacity))
            cv2.circle(canvas,confirm_animation_point,radius,color,3)
            frame = cv2.addWeighted(frame,1.0 , canvas,1.0,0)
        else:
            confirm_animation_start = None
        


    #current_frame_time = time.time()
    #time_taken = current_frame_time - prev_frame_time
    #fps = 1/time_taken if time_taken>0 else 0
    #prev_frame_time = current_frame_time

    #cv2.putText(frame, f"FPS: {int(fps)}", (10,30), 
     #           cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

    
    instructions = [
    "Pinch (thumb+index) = Draw",
    "Peace sign = Change color",
    "Open palm = Clear canvas",
    "Two hands touch = Confirm"
    ]

    y_offset = frame.shape[0] - 100
    for i, text in enumerate(instructions):
         cv2.putText(frame, text, (10, y_offset + i * 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


    cv2.imshow("Day11-- Taha's Webcam Feed (FPS test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()