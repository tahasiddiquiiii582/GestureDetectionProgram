import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")

pinch_history = []
buffer_size= 10
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
            mp_drawing.draw_landmarks(frame, hand_landmarks,mp_hands.HAND_CONNECTIONS)

            landmark_list=[]
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px,py))

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

        
            print(f"pinch ratio : {pinch_ratio:.2f}---->{pinch_status}")
            print(f"raw : {is_pinched_now} | smoothed: {pinch_status} | pinch history: {pinch_history}")
            print(f"wrist at : {wrist}")
            print(f"middle knuckle at : {middle_knuckle}")
            print(f"index fingertip at : {index_tip}")
            print(f"thumb fingertip at : {thumb_tip}")
            print(f"palm size is : {palm_size}")
          
    cv2.imshow("Day6-- Taha's Webcam Feed (The hard part test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()