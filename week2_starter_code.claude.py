"""
Air-Drawing HUD - Week 2 Starter Code
========================================
This consolidates everything built in Week 1 (Days 1-8) into one clean file:
- Webcam capture (Day 1-2)
- MediaPipe hand detection (Day 3)
- Landmark coordinate extraction (Day 4)
- Palm-size normalization reference (Day 5)
- Normalized pinch detection (Day 6)
- Smoothed pinch detection with a rolling buffer (Day 7)
- Custom-drawn skeleton HUD replacing MediaPipe's default look (Day 8)

Week 2 goal: turn this plain colored skeleton into an actual glowing neon HUD,
matching the reference video's look.

Build on top of THIS file for the rest of Week 2 - don't start a new file
each day. Sections you'll be modifying this week are marked with TODO.
"""

import cv2
import mediapipe as mp
import math

# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7
)
# Note: mp_drawing is intentionally NOT used - all drawing is done manually
# to allow full custom styling (see Day 8)

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")

# Rolling history for smoothed pinch detection (Day 7)
pinch_history = []
buffer_size = 5

# Pinch threshold (calibrated in Day 6 using real test data)
PINCH_THRESHOLD = 0.4

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

while True:
    success, frame = cap.read()
    if not success:
        print("Wasn't able to capture the frame")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # --- Extract all 21 landmark pixel coordinates (Day 4) ---
            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            # ---------------------------------------------------------
            # TODO (Week 2): Replace this plain skeleton drawing with a
            # glowing neon version. Currently just flat lines + dots (Day 8).
            # ---------------------------------------------------------
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(frame, start_point, end_point, (0, 255, 255), 2)  # yellow

            for point in landmark_list:
                cv2.circle(frame, point, 5, (255, 255, 0), -1)  # cyan
            # ---------------------------------------------------------
            # END TODO section
            # ---------------------------------------------------------

            # --- Key landmarks (Day 4-5) ---
            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            # --- Palm size reference for distance normalization (Day 5) ---
            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            # --- Normalized pinch detection (Day 6) ---
            x3, y3 = thumb_tip
            x4, y4 = index_tip
            pinch_distance = math.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2)
            pinch_ratio = pinch_distance / palm_size
            is_pinched_now = pinch_ratio < PINCH_THRESHOLD

            # --- Smoothing via rolling buffer + majority vote (Day 7) ---
            pinch_history.append(is_pinched_now)
            if len(pinch_history) > buffer_size:
                pinch_history.pop(0)

            if pinch_history.count(True) > buffer_size // 2:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

            # ---------------------------------------------------------
            # TODO (later in Week 2/3): use pinch_status + index_tip here
            # to start drawing on a separate canvas layer
            # ---------------------------------------------------------

    cv2.imshow("Week 2 - Custom HUD", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------
cap.release()
cv2.destroyAllWindows()