"""
Air-Drawing HUD - Complete Project (Week 1-4)
================================================
This is the final, fully consolidated version of the project, combining
everything built across all 22 sessions (mapped to the original 30-day
roadmap through Day 30 - Final Polish):

Week 1: Webcam capture, MediaPipe hand detection, landmark extraction,
        palm-size normalization, pinch detection, buffer smoothing
Week 2: Custom neon HUD (glow effect, tuned intensity), FPS measurement,
        left/right hand labeling
Week 3: Pinch-to-draw with fading ink trail (age-based opacity)
Week 4: Peace sign -> color change, open palm -> clear canvas, two-hand
        confirm gesture with animated ring, gesture stability buffers,
        per-hand state tracking (critical bug fixes - see notes below),
        on-screen instructions, final FPS tuning

IMPORTANT - per-hand tracking:
Every piece of state that differs between hands (pinch history, active
stroke, color choice, peace-sign counter) is stored in a dictionary keyed
by handedness ("Left"/"Right"), NOT as a single shared variable. This was
a real bug found during Day 21 integration testing - using shared
variables caused strokes, colors, and pinch states to bleed between hands.

Controls:
- Pinch (thumb + index touching) = draw
- Peace sign = cycle ink color (per hand)
- Open palm = clear entire canvas
- Both hands' index fingertips touching = confirmed animation
- 'q' = quit
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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

print("Press 'q' to exit!")

# --- Pinch detection settings (Week 1) ---
PINCH_THRESHOLD = 0.4
buffer_size = 3
pinch_history_per_hand = {}      # {"Left": [...], "Right": [...]}
was_pinched_per_hand = {}        # {"Left": False, "Right": True}

# --- Drawing / fading ink settings (Week 3) ---
active_strokes = {}              # {"Left": [...], "Right": [...]}
drawing_segments = []            # each item: (point1, point2, birth_time, color_index)
segment_lifetime = 4.0           # seconds until fully faded
MAX_JUMP = 80                    # px - guards against MediaPipe handedness misreads

# --- Gesture (peace sign / open palm) settings (Week 4) ---
ink_colors = [(0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 255, 0)]  # yellow, magenta, green, cyan
color_index_per_hand = {}        # {"Left": 0, "Right": 2}
peace_sign_counter_per_hand = {}
open_palm_counter = 0
REQUIRED_FRAMES = 5

# --- Two-hand confirm gesture settings (Week 4) ---
confirm_counter = 0
confirm_animation_start = None
ANIMATION_DURATION = 2.0
CONFIRM_DISTANCE_THRESHOLD = 20

# --- FPS tracking (Week 2) ---
prev_frame_time = 0


def fingers_up(landmark_list):
    """Returns [index, middle, ring, pinky] as True/False (extended or not)."""
    fingers = []
    finger_tips = [8, 12, 16, 20]
    finger_knuckles = [6, 10, 14, 18]

    for tip_idx, knuckle_idx in zip(finger_tips, finger_knuckles):
        tip_y = landmark_list[tip_idx][1]
        knuckle_y = landmark_list[knuckle_idx][1]
        fingers.append(tip_y < knuckle_y)

    return fingers


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

    all_index_tips = []   # collected across both hands, used for the confirm gesture

    if result.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            handedness = result.multi_handedness[idx].classification[0].label

            # --- Extract landmarks (Week 1) ---
            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            # --- Custom neon HUD: glow + skeleton (Week 2) ---
            glow_layer = np.zeros_like(frame)
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                cv2.line(glow_layer, landmark_list[start_idx], landmark_list[end_idx], (0, 255, 255), 2)
            for point in landmark_list:
                cv2.circle(glow_layer, point, 4, (255, 255, 0), -1)

            glow_small = cv2.GaussianBlur(glow_layer, (5, 5), 0)
            glow_large = cv2.GaussianBlur(glow_layer, (15, 15), 0)
            combined_glow = cv2.addWeighted(glow_small, 0.8, glow_large, 0.8, 0)
            frame = cv2.addWeighted(frame, 1.0, combined_glow, 0.8, 0)

            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                cv2.line(frame, landmark_list[start_idx], landmark_list[end_idx], (0, 255, 255), 2)
            for point in landmark_list:
                cv2.circle(frame, point, 5, (255, 255, 0), -1)

            # --- Key landmarks ---
            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]
            all_index_tips.append(index_tip)

            cv2.putText(frame, handedness, (wrist[0] - 20, wrist[1] + 35),
                        cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 255), 1)

            # --- Palm size + pinch ratio (Week 1) ---
            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            x3, y3 = thumb_tip
            x4, y4 = index_tip
            pinch_distance = math.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2)
            pinch_ratio = pinch_distance / palm_size
            is_pinched_now = pinch_ratio < PINCH_THRESHOLD

            # --- Per-hand pinch smoothing buffer (Week 1, fixed Day 21) ---
            pinch_history = pinch_history_per_hand.get(handedness, [])
            pinch_history.append(is_pinched_now)
            if len(pinch_history) > buffer_size:
                pinch_history.pop(0)
            pinch_history_per_hand[handedness] = pinch_history

            if pinch_history.count(True) > buffer_size // 2:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

            was_pinched = was_pinched_per_hand.get(handedness, False)

            # --- Per-hand stroke recording with fading ink (Week 3, fixed Day 21) ---
            if pinch_status == "Pinched" and not was_pinched:
                active_strokes[handedness] = []

            if pinch_status == "Pinched":
                if handedness not in active_strokes:
                    active_strokes[handedness] = []

                midpoint_x = (x3 + x4) // 2
                midpoint_y = (y3 + y4) // 2
                new_point = (midpoint_x, midpoint_y)

                # Safety check: guard against MediaPipe briefly mislabeling
                # which hand is which when hands are close together
                if len(active_strokes[handedness]) >= 1:
                    last_point = active_strokes[handedness][-1]
                    lx, ly = last_point
                    jump_distance = math.sqrt((midpoint_x - lx) ** 2 + (midpoint_y - ly) ** 2)
                    if jump_distance > MAX_JUMP:
                        active_strokes[handedness] = []

                active_strokes[handedness].append(new_point)

                if len(active_strokes[handedness]) >= 2:
                    previous_point = active_strokes[handedness][-2]
                    birth_time = time.time()
                    this_hand_color_index = color_index_per_hand.get(handedness, 0)
                    drawing_segments.append((previous_point, new_point, birth_time, this_hand_color_index))

            was_pinched_per_hand[handedness] = (pinch_status == "Pinched")

            # --- Gesture detection: peace sign / open palm (Week 4) ---
            fingers = fingers_up(landmark_list)
            is_peace_sign = fingers == [True, True, False, False]
            is_open_palm = fingers == [True, True, True, True] and pinch_status != "Pinched"

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

            if open_palm_counter == REQUIRED_FRAMES:
                drawing_segments = []
                active_strokes = {}

            if peace_sign_counter == REQUIRED_FRAMES:
                current_color = color_index_per_hand.get(handedness, 0)
                color_index_per_hand[handedness] = (current_color + 1) % len(ink_colors)

    # --- Two-hand confirm gesture (Week 4) ---
    if len(all_index_tips) == 2:
        tip1, tip2 = all_index_tips
        x1, y1 = tip1
        x2, y2 = tip2
        distance_between_hands = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        is_confirmed_gesture = distance_between_hands < CONFIRM_DISTANCE_THRESHOLD
    else:
        is_confirmed_gesture = False

    if is_confirmed_gesture:
        confirm_counter += 1
    else:
        confirm_counter = 0

    if confirm_counter == REQUIRED_FRAMES:
        confirm_animation_start = time.time()
        confirm_animation_point = ((x1 + x2) // 2, (y1 + y2) // 2)

    # --- Render fading ink segments onto a fresh canvas each frame ---
    canvas = np.zeros_like(frame)
    current_time = time.time()
    still_alive_segments = []

    for point1, point2, birth_time, color_idx in drawing_segments:
        age = current_time - birth_time
        if age < segment_lifetime:
            opacity = 1.0 - (age / segment_lifetime)
            base_color = ink_colors[color_idx]
            color = tuple(int(c * opacity) for c in base_color)
            cv2.line(canvas, point1, point2, color, 3)
            still_alive_segments.append((point1, point2, birth_time, color_idx))

    drawing_segments = still_alive_segments
    frame = cv2.addWeighted(frame, 1.0, canvas, 1.0, 0)

    # --- Confirm animation: expanding, fading ring ---
    if confirm_animation_start is not None:
        elapsed = time.time() - confirm_animation_start
        if elapsed < ANIMATION_DURATION:
            progress = elapsed / ANIMATION_DURATION
            radius = int(20 + progress * 60)
            opacity = 1.0 - progress
            color = (0, int(255 * opacity), int(255 * opacity))
            cv2.circle(canvas, confirm_animation_point, radius, color, 3)
            frame = cv2.addWeighted(frame, 1.0, canvas, 1.0, 0)
        else:
            confirm_animation_start = None

    # --- On-screen instructions (Week 4 - final polish) ---
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

    # --- FPS counter (Week 2 - final polish) ---
    current_frame_time = time.time()
    time_taken = current_frame_time - prev_frame_time
    fps = 1 / time_taken if time_taken > 0 else 0
    prev_frame_time = current_frame_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Air-Drawing HUD - Complete", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------------------------------------------------
# CLEANUP
# ---------------------------------------------------------
cap.release()
cv2.destroyAllWindows()
