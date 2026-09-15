"""
Air-Drawing HUD - Week 3 Starter Code
========================================
This consolidates everything built in Week 1-2 (Days 1-12) into one clean file:
- Webcam capture (Day 1-2)
- MediaPipe two-hand detection (Day 3)
- Landmark coordinate extraction (Day 4)
- Palm-size normalization reference (Day 5)
- Normalized pinch detection (Day 6)
- Smoothed pinch detection with a rolling buffer (Day 7)
- Custom-drawn neon skeleton HUD (Day 8)
- Glow effect with layered blur (Day 9)
- Fine-tuned glow intensity (Day 10)
- FPS measurement (Day 11)
- Left/Right hand labeling (Day 12) - Week 2 checkpoint complete

Week 3 goal: turn pinch detection into an actual drawing feature - when
pinched, the index fingertip's movement gets drawn as a trail on screen,
persisting on a separate canvas layer merged with the live video each frame.

Note: pinch detection (Days 6-7) and palm-size normalization (Day 5) were
already built in Week 1, ahead of the original roadmap's pace - so Week 3
here focuses specifically on the DRAWING mechanics, not re-deriving pinch
detection from scratch.

Build on top of THIS file for the rest of Week 3 - don't start a new file
each day. Sections you'll be modifying this week are marked with TODO.
"""

import cv2
import mediapipe as mp
import math
import numpy as np
import time

# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")

# Rolling history for smoothed pinch detection (Day 7)
pinch_history = []
buffer_size = 5

# Pinch threshold (calibrated in Day 6 using real test data)
PINCH_THRESHOLD = 0.4

# FPS tracking (Day 11)
prev_frame_time = 0

# ---------------------------------------------------------
# TODO (Week 3): This is where your drawing canvas will live.
# It needs to persist ACROSS frames (unlike glow_layer, which is
# recreated fresh every frame) - so drawn strokes stay visible over time.
# Day 19-20 will fill this in: a list of drawn points/segments, and a
# canvas layer to render them onto each frame.
# ---------------------------------------------------------
drawing_points = []   # will hold recorded points while pinched

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
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            handedness = result.multi_handedness[idx].classification[0].label

            # --- Extract all 21 landmark pixel coordinates (Day 4) ---
            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            # --- Custom neon HUD: glow layer + skeleton (Day 8-10) ---
            glow_layer = np.zeros_like(frame)

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(glow_layer, start_point, end_point, (0, 255, 255), 4)

            for point in landmark_list:
                cv2.circle(glow_layer, point, 8, (255, 255, 0), -1)

            glow_small = cv2.GaussianBlur(glow_layer, (15, 15), 0)
            glow_large = cv2.GaussianBlur(glow_layer, (45, 45), 0)
            combined_glow = cv2.addWeighted(glow_small, 0.8, glow_large, 0.6, 0)

            frame = cv2.addWeighted(frame, 1.0, combined_glow, 0.6, 0)

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(frame, start_point, end_point, (0, 255, 255), 2)

            for point in landmark_list:
                cv2.circle(frame, point, 5, (255, 255, 0), -1)

            # --- Key landmarks (Day 4-5) ---
            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            cv2.putText(frame, handedness, (wrist[0] - 20, wrist[1] + 35),
                        cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 255), 1)

            # --- Palm size reference (Day 5) ---
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
            # TODO (Day 13-14): when pinch_status == "Pinched", record
            # the midpoint between thumb_tip and index_tip into
            # drawing_points. When not pinched, "lift the pen" so a new
            # stroke starts fresh next time (don't connect old and new
            # strokes with a stray line).
            # ---------------------------------------------------------

    # ---------------------------------------------------------
    # TODO (Day 15-16): draw drawing_points as connected line segments
    # onto a persistent canvas layer, then merge that canvas with frame
    # here, every frame - so strokes remain visible over time.
    # ---------------------------------------------------------

    # --- FPS display (Day 11) ---
    current_frame_time = time.time()
    time_taken = current_frame_time - prev_frame_time
    fps = 1 / time_taken if time_taken > 0 else 0
    prev_frame_time = current_frame_time

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Week 3 - Air Drawing", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------
cap.release()
cv2.destroyAllWindows()