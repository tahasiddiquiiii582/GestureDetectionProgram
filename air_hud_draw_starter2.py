"""
Air-Drawing HUD - Starter Code
================================
This covers the Week 1 foundation from your roadmap:
- Webcam capture
- MediaPipe two-hand detection
- Extracting key landmarks (thumb tip, index tip, wrist, middle knuckle)
- A blank canvas layer merged with the live feed

Build on top of THIS file each day - don't rewrite from scratch.
Everything from Week 2 onward (custom HUD, pinch detection, fading trail,
gestures) gets added into the marked sections below as you progress.
"""

import cv2
import mediapipe as mp
import numpy as np

# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------

mp_hands = mp.solutions.hands

# max_num_hands=2 because you'll need both hands later for the
# "two hands touching index fingers = confirmed" gesture
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Landmark indices you'll need throughout this project (MediaPipe's numbering)
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_KNUCKLE = 9  # used later for palm-size normalization

cap = cv2.VideoCapture(0)

# canvas will hold your drawing (Week 3+). For now it's just blank.
canvas = None

print("Press 'q' to quit.")

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame from webcam.")
        break

    # Mirror the frame so movement feels natural (like a mirror, not inverted)
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Create the canvas once we know the frame size
    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # MediaPipe expects RGB, OpenCV gives BGR - convert before processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # This will store landmark data for each detected hand this frame
    all_hands_data = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Convert normalized (0-1) coordinates to pixel coordinates
            landmark_points = []
            for lm in hand_landmarks.landmark:
                px, py = int(lm.x * w), int(lm.y * h)
                landmark_points.append((px, py))

            all_hands_data.append(landmark_points)

            # --- TEMPORARY VISUALIZATION (Week 1 only) ---
            # This is MediaPipe's default drawing, just so you can confirm
            # detection is working. You'll REPLACE this in Week 2 with your
            # own custom glowing HUD instead of using mp_drawing.
            for point in landmark_points:
                cv2.circle(frame, point, 4, (0, 255, 0), -1)

    # ---------------------------------------------------------
    # WEEK 1 CHECKPOINT: extract and print key landmarks
    # ---------------------------------------------------------
    for idx, hand_points in enumerate(all_hands_data):
        wrist = hand_points[WRIST]
        thumb_tip = hand_points[THUMB_TIP]
        index_tip = hand_points[INDEX_TIP]
        middle_knuckle = hand_points[MIDDLE_KNUCKLE]

        # For now, just draw these key points in a different color
        # so you can visually confirm they're the right ones
        cv2.circle(frame, wrist, 8, (255, 0, 0), -1)
        cv2.circle(frame, thumb_tip, 8, (0, 0, 255), -1)
        cv2.circle(frame, index_tip, 8, (0, 255, 255), -1)
        cv2.circle(frame, middle_knuckle, 8, (255, 255, 0), -1)

    # ---------------------------------------------------------
    # WEEK 2+: Your custom HUD drawing will go here
    # (replace the temporary green dots above)
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # WEEK 3+: Pinch detection + drawing trail logic will go here
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # WEEK 4+: Gesture detection (peace sign, open palm, two-hand
    # confirm) and fading ink logic will go here
    # ---------------------------------------------------------

    # Merge the canvas (your drawing layer) onto the live frame.
    # Right now canvas is empty, but this is the exact mechanism
    # you'll use once you're actually drawing on it.
    output = cv2.addWeighted(frame, 1.0, canvas, 1.0, 0)

    cv2.imshow("Air-Drawing HUD - Starter", output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------
cap.release()
cv2.destroyAllWindows()