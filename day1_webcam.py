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
buffer_size= 10
prev_frame_time = 0

while True:
    success, frame = cap.read()
    if not success:
        print("Wasn't able to capture the frame")
        break
    frame = cv2.flip(frame, 1)
    h, w,_ = frame.shape
    rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        print(f"Hands Found: {len(result.multi_hand_landmarks)}")
        for hand_landmarks in result.multi_hand_landmarks:

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
                cv2.line(glow_layer, start_point, end_point, (0,255,255),4)

            for point in landmark_list:
                cv2.circle(glow_layer,point, 8 ,(255,255,0),-1)

            glow_small = cv2.GaussianBlur(glow_layer, (15,15),0)
            glow_large = cv2.GaussianBlur(glow_layer,(45,45),0)
            combined_glow = cv2.addWeighted(glow_small,0.8,glow_large,0.6,0)

            

            frame = cv2.addWeighted(frame,1.0,combined_glow,0.6,0)

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

            x1,y1 = wrist
            x2,y2 = middle_knuckle
            palm_size = math.sqrt((x2-x1)**2 + (y2-y1)**2)

            x3,y3 = thumb_tip
            x4,y4 = index_tip
            pinch_distance = math.sqrt((x4-x3)**2 + (y4-y3)**2)

            pinch_ratio = pinch_distance/palm_size

            is_pinched_now = pinch_ratio<0.4

            pinch_history.append(is_pinched_now)
            if len(pinch_history)>buffer_size:
                pinch_history.pop(0)

            if pinch_history.count(True) > buffer_size // 5:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

        
            #print(f"pinch ratio : {pinch_ratio:.2f}---->{pinch_status}")
            #print(f"raw : {is_pinched_now} | smoothed: {pinch_status} | pinch history: {pinch_history}")
            #print(f"wrist at : {wrist}")
            #print(f"middle knuckle at : {middle_knuckle}")
            #print(f"index fingertip at : {index_tip}")
            #print(f"thumb fingertip at : {thumb_tip}")
            #print(f"palm size is : {palm_size}")
          

    current_frame_time = time.time()
    time_taken = current_frame_time - prev_frame_time
    fps = 1/time_taken if time_taken>0 else 0
    prev_frame_time = current_frame_time

    cv2.putText(frame, f"FPS: {int(fps)}", (10,30), 
                cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Day11-- Taha's Webcam Feed (FPS test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()