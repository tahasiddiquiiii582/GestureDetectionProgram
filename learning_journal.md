# Gesture Detection Program — Learning Journal
Personal record of each day's lesson, concepts learned, tasks completed, and code.
Following the 30-day roadmap (1 hour/day) to build the Air-Drawing HUD project.

---

## Day 1 — Environment Setup

### Concept learned
Before writing any real code, the development environment needs to be set up
correctly: Python itself, an editor (VS Code), and the specific libraries the
project depends on (OpenCV, MediaPipe, NumPy). Getting versions to match matters —
not all libraries support every Python version, and mismatches cause errors that
have nothing to do with the actual code being wrong.

### What was set up
- Installed Python and VS Code, plus the Python extension for VS Code
- Created the project folder `GestureDetectionProgram` and opened it as a
  workspace in VS Code
- Installed required libraries: `opencv-python`, `mediapipe`, `numpy`

### Problems hit + how they were fixed
1. **`AttributeError: module 'mediapipe' has no attribute 'solutions'`**
   Cause: the system's default Python was version 3.14, which is too new —
   MediaPipe's classic `solutions` API isn't available on very new Python
   versions in the way most tutorials expect.
   Fix: installed **Python 3.11** alongside 3.14 (both can coexist), and
   selected 3.11 as the interpreter in VS Code (`Ctrl+Shift+P` →
   "Python: Select Interpreter").

2. **Same error persisted even after switching interpreters**
   Cause: an already-open terminal doesn't refresh to a newly selected
   interpreter — a **new** terminal must be opened after switching.

3. **`pip install` kept installing into the wrong (3.14) environment**
   Cause: plain `pip`/`python` commands defaulted to 3.14 regardless of the
   VS Code interpreter setting.
   Fix: used `py -3.11 -m pip install ...` to explicitly target the 3.11
   environment.

4. **Even in 3.11, `mediapipe` still had no `solutions` attribute**
   Cause: newer MediaPipe releases (approaching and including 1.x) removed the
   legacy `solutions` API entirely in favor of a new "Tasks" API.
   Fix: pinned to a specific older version that still includes it:
   ```
   py -3.11 -m pip uninstall mediapipe -y
   py -3.11 -m pip install mediapipe==0.10.9
   ```

5. **`ImportError: DLL load failed while importing _framework_bindings`**
   Cause: a required Windows system component (Microsoft Visual C++
   Redistributable) was missing — MediaPipe's core is compiled C++ and needs
   this runtime to load.
   Fix: downloaded and installed the Redistributable from
   `https://aka.ms/vs/17/release/vc_redist.x64.exe`, then restarted the PC.

### Reference commands (for future setup on another machine)
- Run files with: `py -3.11 <filename>.py`
- Install packages with: `py -3.11 -m pip install <package>`
- Check installed version: `py -3.11 -m pip show mediapipe`

### Outcome
After all fixes, `import mediapipe as mp; print(mp.solutions.hands)` ran
without error, confirming the environment was fully working and ready for
actual project code.

---

## Day 2 — Basic Webcam Capture

### Concept learned
A video is not one continuous thing to a computer — it's a rapid sequence of still
images ("frames") shown one after another (usually ~30 per second) to create the
illusion of motion. The entire program's job, at its core, is a loop:
1. Ask the camera for the current frame
2. Do something with that image
3. Show it on screen
4. Repeat until told to stop

A frame itself is just a NumPy array of numbers — a grid of pixels, where each pixel
is 3 values (Blue, Green, Red), each ranging 0–255.

### Key building blocks
- `cv2.VideoCapture(0)` — opens a connection to the webcam (`0` = first camera found)
- `cap.read()` — returns two values: `success` (True/False) and `frame` (the image data)
- `cv2.imshow(window_title, frame)` — displays the frame in a window
- `cv2.waitKey(1)` — waits 1ms for a keypress; required for the window to refresh
- `cap.release()` + `cv2.destroyAllWindows()` — cleanup, releases the camera

### Code — base version
```python
import cv2

# Step 1: Open a connection to the webcam (0 = first camera on your PC)
cap = cv2.VideoCapture(0)

print("Press 'q' to quit.")

# Step 2: Loop forever, grabbing one frame at a time
while True:
    success, frame = cap.read()   # ask the camera for the current frame

    if not success:
        print("Failed to grab frame.")
        break

    cv2.imshow("Day 2 - Webcam Test", frame)  # display that frame in a window

    # Step 3: check if 'q' was pressed; if so, exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Step 4: cleanup — release the camera and close windows
cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Change the window title to something personal (e.g. `"Taha's Webcam Feed"`)
2. Mirror the feed horizontally using `cv2.flip(frame, 1)` so it behaves like a mirror

### My completed task / code
Both practice tasks completed: personalized window title + mirrored feed using
`cv2.flip(frame, 1)`. Final version also fixes an ordering issue — `success` is
now checked *before* flipping, so the program won't crash trying to flip an
invalid/empty frame if the camera ever fails to read.

```python
import cv2
cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")
while True:
    success, frame = cap.read()
    if not success:
        print("Wasn't able to capture the frame")
        break
    frame = cv2.flip(frame, 1)
    cv2.imshow("Day1-- Taha's Webcam Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Notes / things that tripped me up
- `cv2.flip()` doesn't modify `frame` in place — it returns a new flipped image,
  which must be reassigned back with `frame = cv2.flip(frame, 1)` or the flip
  has no effect.
- Learned to always validate data (`if not success`) *before* operating on it,
  not after — otherwise operating on invalid data can crash the program. This
  matters again in Day 3 when checking if a hand was actually detected before
  reading its landmarks.

---

## Extra Skill — Git & GitHub (assigned by boss, learned alongside the project)

### Concept learned
- **Git** = a tool that tracks versions/changes of your code over time on your own PC
- **GitHub** = an online service that stores/backs up your Git project so it's accessible
  from anywhere and visible to others (like a cloud copy of your project's history)
- A **commit** = a saved checkpoint of your code at a point in time, with a short
  message describing what changed
- **Push** = uploading your local commits to GitHub

### One-time setup completed
1. Created GitHub account (`tahasiddiquiiii582`)
2. Installed Git for Windows
3. Configured identity:
   ```
   git config --global user.name "Taha Siddiqui"
   git config --global user.email "faheem1998javed@gmail.com"
   ```
4. Created repository: `https://github.com/tahasiddiquiiii582/GestureDetectionProgram`
5. Connected local project folder to GitHub and pushed for the first time:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/tahasiddiquiiii582/GestureDetectionProgram.git
   git push -u origin main
   ```

### Daily routine going forward (the actual habit)
At the end of every coding session, run these 3 commands:
```
git add .
git commit -m "Day X: [short description of what was done]"
git push
```

### Notes / things that tripped me up
- Had to fully close and reopen VS Code after installing Git for the terminal to
  recognize the `git` command (PATH wasn't refreshed in the already-open terminal)
- First `git push` required signing in to GitHub via a browser popup — this is a
  one-time authentication step, shouldn't be needed again on this machine
- The `LF will be replaced by CRLF` warning during `git add` is harmless — just a
  line-ending difference note between Windows and Unix systems, not an error

### First real daily-push practice — completed successfully ✅
Ran the full daily routine for the first time on this journal file itself:
```
git add .
git commit -m "Day 1: webcam capture practice + Git/GitHub setup notes"
git push
```
Result: commit `cb04e21` pushed successfully to `main` on GitHub. Confirmed the
full add → commit → push cycle works end-to-end and will be repeated daily
going forward as each day's task is completed.

---

## Day 3 — Detecting Hands with MediaPipe

### Concept learned
MediaPipe is a pre-trained ML model (built by Google) that looks at an image and
finds hands in it, returning 21 specific landmark points per hand (fingertips,
knuckles, wrist, etc.) as pixel coordinates. It's not built/trained from scratch —
it's used as-is. The workflow each frame: feed it an image → ask it to process →
read back whether a hand was found and where its points are.

### Key building blocks
- `mp.solutions.hands.Hands()` — creates the hand-detection engine. Created ONCE,
  outside the main loop — not every frame (wasteful otherwise).
- `hands.process(image)` — runs detection on one frame. Requires **RGB**, but
  OpenCV frames are **BGR** — must convert first with `cv2.cvtColor()`.
- `results.multi_hand_landmarks` — `None` if no hand found, otherwise a **list**
  with one entry per detected hand (handles 1 or 2 hands automatically via a loop).
- `mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)` —
  draws the 21 points + connecting skeleton lines directly onto `frame`.
  Important: this modifies `frame` **in place** — no reassignment (`frame = ...`)
  needed, unlike `cv2.flip()` which *returns* a new image instead.
- `mp_hands.HAND_CONNECTIONS` — tells the drawing function which landmark pairs
  should be connected by a line (e.g. knuckle-to-knuckle), forming a skeleton
  shape instead of floating dots.

### Code — Day 3 (built on top of Day 2's file)
```python
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")
while True:
    success, frame = cap.read()
    if not success:
        print("Wasn't able to capture the frame")
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Day2-- Taha's Webcam Feed (hand detection test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Add MediaPipe hand detection on top of the Day 2 webcam loop
2. Print how many hands are currently detected each frame using
   `len(result.multi_hand_landmarks)`

### My completed task / code
Both tasks completed successfully. Confirmed working with clean single-hand
tracking — 21 landmark dots + skeleton lines rendering correctly, hand-count
printing to terminal every frame while a hand is visible. Ran using the ▶ Run
button in VS Code (confirmed using Python 3.11 correctly, shown in status bar).

### Notes / things that tripped me up
- Learned the difference between functions that **return** a new value (need
  reassignment, e.g. `frame = cv2.flip(frame, 1)`) vs. functions that **mutate
  in place** (no reassignment, e.g. `mp_drawing.draw_landmarks(frame, ...)`)
- Confirmed the ▶ Run button correctly uses Python 3.11 by default now, so
  `py -3.11` prefix isn't strictly required anymore for this project (but still
  useful to know for direct terminal commands)

---

## Day 4 — Extracting Landmark Coordinates

### Concept learned
`draw_landmarks()` handles reading + drawing landmark data automatically, but to
actually *use* that data (for pinch detection, drawing trails, etc.) the raw
coordinates need to be read directly. MediaPipe gives coordinates as
**normalized values** (0 to 1) representing position as a percentage of the
frame — not actual pixels. This makes detection resolution-independent (same
data works on any camera size), but means a conversion step is required before
using OpenCV to draw at that position:
```
pixel_x = normalized_x × frame_width
pixel_y = normalized_y × frame_height
```

### Key building blocks
- `hand_landmarks.landmark` — a list of 21 raw points, each with `.x`, `.y`
  (and `.z`, depth — not used yet)
- `frame.shape` — returns `(height, width, channels)`, used to get the
  dimensions needed for the pixel conversion
- Landmark index numbers are fixed conventions: index **8** = index fingertip,
  index **4** = thumb tip (memorizing key indices as needed, not all 21 yet)

### Code — Day 4 (built on top of Day 3's file)
```python
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7
)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")
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
        print(f"Hands Found: {len(result.multi_hand_landmarks)}")
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            print(f"index fingertip at : {landmark_list[8]}")
            print(f"thumb fingertip at : {landmark_list[4]}")

    cv2.imshow("Day2-- Taha's Webcam Feed (hand detection test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Convert all 21 normalized landmark points to pixel coordinates each frame
2. Print the index fingertip's pixel position (landmark 8)
3. Challenge: also print the thumb tip's pixel position (landmark 4)

### My completed task / code
All 3 tasks completed correctly in one pass, including the thumb-tip challenge
without needing extra guidance. Confirmed both fingertip coordinates print and
update live as the hand moves.

### Notes / things that tripped me up
- Accidentally deleted/modified the working file mid-session — recovered it
  instantly using `git checkout -- <filename>.py`, which restores a file back
  to its state from the last commit. First real hands-on proof of why the
  daily Git habit matters (this would have meant redoing all of Day 1–3's
  code from scratch otherwise).
- Learned that `landmark_list` gets rebuilt fresh inside the per-hand loop —
  fine for single-hand use now, but will need separate storage per hand once
  working with two hands later (needed for the Week 4 two-hand gesture).

---

## Day 5 — Identifying Wrist & Middle Knuckle (Palm-Size Reference)

### Concept learned
Detecting a "pinch" using raw pixel distance between thumb and index tip is
unreliable — the same physical pinch produces a small pixel gap when the hand
is far from the camera, and a large pixel gap when close. The fix: measure the
pinch distance **relative to the size of the hand itself**, using a stable
reference "ruler" that scales proportionally with hand distance — the
wrist-to-middle-knuckle distance. This doesn't change based on finger position,
only based on how close/far the whole hand is.

### Key landmarks needed
- Landmark **0** → wrist
- Landmark **9** → base knuckle of the middle finger

### Code — Day 5 (built on top of Day 4's file)
```python
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
        print(f"Hands Found: {len(result.multi_hand_landmarks)}")
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            print(f"wrist at : {wrist}")
            print(f"middle knuckle at : {middle_knuckle}")
            print(f"index fingertip at : {index_tip}")
            print(f"thumb fingertip at : {thumb_tip}")
            print(f"palm size is : {palm_size}")

    cv2.imshow("Day2-- Taha's Webcam Feed (hand detection test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Extract wrist (landmark 0) and middle knuckle (landmark 9) coordinates
2. Challenge: calculate the straight-line distance between them using the
   Pythagorean theorem via `math.sqrt()`, and print it as `palm_size`

### My completed task / code
Both tasks completed independently, correctly applying the distance formula
without needing the answer given directly. Verified behavior via a live test
with two hands in frame simultaneously:
- Palm size stayed stable (~78–92) while fingers moved around a lot —
  confirms it's independent of finger position
- Palm size increased (~98–104) as the hand moved closer to the camera later
  in the test — confirms it correctly scales with distance

### Notes / things that tripped me up
- None — clean implementation on the first attempt, including correctly
  unpacking tuples (`x1, y1 = wrist`) before applying the formula

---

## Day 6 — Building the Normalized Pinch Detector

### Concept learned
Combining Day 4's coordinates and Day 5's palm-size reference into the actual
"hard part" technique: dividing raw pinch distance by palm size cancels out
the effect of hand distance from the camera, because both values shrink/grow
proportionally together. The resulting `pinch_ratio` stays consistent for the
same physical pinch regardless of how close/far the hand is. A **threshold**
(a manually chosen cutoff number) then converts that continuous ratio into a
binary decision: PINCHED or OPEN.

### Formula
```
pinch_ratio = pinch_distance / palm_size
```
Threshold picked by testing on real data, not calculated — this is a
calibration step, not a formula.

### Code — Day 6 (built on top of Day 5's file)
```python
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
        print(f"Hands Found: {len(result.multi_hand_landmarks)}")
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            x3, y3 = thumb_tip
            x4, y4 = index_tip
            pinch_distance = math.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2)

            pinch_ratio = pinch_distance / palm_size

            if pinch_ratio < 0.4:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

            print(f"pinch ratio : {pinch_ratio:.2f}---->{pinch_status}")

    cv2.imshow("Day6-- Taha's Webcam Feed (The hard part test)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Calculate `pinch_distance` between thumb tip and index tip
2. Normalize it: `pinch_ratio = pinch_distance / palm_size`
3. Set an initial threshold and test it live, tuning based on observed values

### My completed task / code
All tasks completed correctly on first attempt. Ran a live calibration test:
- **Pinched (steady):** ratio consistently ~0.03–0.13
- **Fully open (steady):** ratio consistently ~1.0–1.2
- **Mid-transition (finger opening/closing):** ratio passed through the
  ambiguous 0.3–0.6 range, as expected during actual motion
- **Conclusion:** kept the initial threshold of `0.4` — it sits safely in the
  gap between the two steady-state ranges, confirmed using real recorded data
  rather than guessing

### Notes / things that tripped me up
- Understood that a threshold is a calibration decision, not something with a
  single "correct" mathematical answer — it depends on the specific hand/
  camera setup and must be verified against real observed data
- Recognized that ambiguous ratio values during the actual pinch/release
  motion are expected and not a sign of a bug

### How the threshold was actually found (deeper explanation)
Initially unclear how "0.4" was decided, so broke it down step by step:

1. **The goal:** find one number that separates "pinched" from "not pinched" —
   not a formula, just a dividing line (like deciding a height cutoff for
   "short" vs "tall").

2. **Looked only at the steady extremes** in the recorded data (ignored the
   messy in-between/transition frames for now):
   - Steady **pinched** state → ratio consistently clustered around **0.03–0.13**
   - Steady **open** state → ratio consistently clustered around **1.0–1.2**

3. **Noticed the gap:** between roughly 0.15 and 0.9, the ratio almost never
   appeared during steady states — that whole range was empty except for the
   brief instants where fingers were physically mid-motion between pinched
   and open (which naturally has to pass through those in-between values).

4. **Any number in that empty gap would work as a threshold.** `0.4` (the
   original guess from the Day 6 code) happened to sit comfortably inside that
   gap — far enough from the pinched cluster (0.03–0.13) that small hand
   shake wouldn't falsely trigger "Not Pinched," and far enough from the open
   cluster (1.0–1.2) that it wouldn't falsely trigger "Pinched" either.

**Key takeaway:** the threshold wasn't calculated — it was *verified*. The
number 0.4 was a starting guess; running the program and checking where my
own hand's real numbers landed confirmed it was a safe choice. If the open-hand
numbers had instead come out closer to 0.3–0.5, that same 0.4 would have been
a bad pick sitting right inside the "open" cluster, and a smaller number
(e.g. 0.15) would have been needed instead.

---

## Day 7 — Smoothing Out the Flicker (Stability Buffer)

### Concept learned
A single frame's raw pinch reading can be unreliable during the actual motion
of pinching/releasing, since the ratio passes through ambiguous in-between
values. This causes "flickering" — the status rapidly switching back and forth
for a few frames even during one smooth motion. The fix: a **rolling history**
of the last N frames' raw readings, with the final status decided by
**majority vote** rather than trusting any single frame. This is a form of
smoothing/debouncing.

### Key building blocks
- `pinch_history = []` — created once, outside the loop, so it persists and
  accumulates across frames
- `.append(value)` — adds the newest reading to the end of the list
- `.pop(0)` — removes the oldest reading once the list exceeds `buffer_size`,
  keeping it a fixed-size "sliding window"
- `.count(True)` — counts how many `True` values are currently in the list
- `buffer_size // 2` — integer division, used to check for "more than half"

### Code — Day 7 (built on top of Day 6's file, redundant duplicate
threshold check removed)
```python
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
buffer_size = 5

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
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            x3, y3 = thumb_tip
            x4, y4 = index_tip
            pinch_distance = math.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2)

            pinch_ratio = pinch_distance / palm_size
            is_pinched_now = pinch_ratio < 0.4

            pinch_history.append(is_pinched_now)
            if len(pinch_history) > buffer_size:
                pinch_history.pop(0)

            if pinch_history.count(True) > buffer_size // 2:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

            print(f"raw: {is_pinched_now} | smoothed: {pinch_status} | history: {pinch_history}")

    cv2.imshow("Day 7 - Smoothed Pinch Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Add rolling history + majority-vote smoothing on top of Day 6's pinch detection
2. Compare `raw` vs `smoothed` output while rapidly pinching/releasing
3. Challenge: test `buffer_size = 10` vs `5` and observe the tradeoff

### My completed task / code
All tasks completed, including finding and cleaning up a redundant duplicate
threshold check left over from Day 6 (the code worked either way since the
second calculation simply overwrote the first, but removing it made the logic
clearer). Ran a real comparison test between buffer sizes 5 and 10:

- **buffer_size = 5:** smoothed status lagged ~3 frames behind the real
  release before flipping to "Not Pinched"
- **buffer_size = 10:** smoothed status lagged ~8 frames behind before
  flipping — nearly triple the delay
- **Conclusion:** larger buffers are more resistant to flicker but introduce
  more response lag. Since Day 6's data already showed a clean, well-separated
  pinch/open range (not particularly noisy), a smaller buffer (5) is the
  better choice for this project — especially important for the upcoming
  drawing feature, where lag would cause the line to visibly overshoot past
  where the pinch was actually released. Decided to keep `buffer_size = 5`
  going forward.

### Notes / things that tripped me up
- Found and removed a leftover duplicate `if/else` threshold block from Day 6
  that was harmless but redundant (its result got immediately overwritten by
  the smoothed version)
- Directly observed the classic responsiveness-vs-stability tradeoff in
  smoothing/filtering — a general concept that shows up throughout
  programming, not just this project

### How the buffer/sliding-window logic actually works (deeper explanation)
Initially unclear how the buffer caused lag, so broke it down step by step:

**What a buffer is:** a small list that holds only the most recent N readings —
like a sticky note with a student's last 5 quiz scores, where each new score
added means the oldest one gets crossed off, always keeping exactly 5 numbers.

**The two-step mechanism each frame:**
```python
pinch_history.append(is_pinched_now)      # always add the new reading
if len(pinch_history) > buffer_size:      # once it's too big...
    pinch_history.pop(0)                  # ...remove the oldest one
```
This creates a "sliding window" — always showing the most recent N frames,
constantly forgetting anything older.

**Why bigger buffers cause more lag — the majority threshold changes:**
- `buffer_size = 5` → majority needed = `5 // 2 = 2`, so **3 out of 5** matching
  readings flips the vote
- `buffer_size = 10` → majority needed = `10 // 2 = 5`, so **6 out of 10**
  matching readings flips the vote

**Traced an actual release frame-by-frame for both sizes**, starting from a
list of all `True` (pinched) and feeding in new `False` readings one at a time:
- Buffer 5: `[T,T,T,T,T]` → `[T,T,T,T,F]` (4) → `[T,T,T,F,F]` (3) →
  `[T,T,F,F,F]` (2, flips) — **took 3 new False frames** to flip
- Buffer 10: needed to push through 6 new False frames before the count of
  True dropped from 10 down to below the majority of 5

**Key takeaway:** a bigger buffer doesn't just mean "a longer list" — it means
more old data has to get physically pushed out (via `.pop(0)`) before new
information can outnumber it and win the vote. That's the entire mechanism
behind the slowdown — same counting rule as buffer_size=5, just requiring more
matching consecutive frames to cross the higher threshold.

---

## Week 1 Checkpoint — Complete ✅
By the end of Day 7, the program reliably:
- Captures and displays webcam video (Day 1–2)
- Detects one or two hands live using MediaPipe (Day 3)
- Extracts and converts all 21 landmark coordinates to pixel positions (Day 4)
- Calculates a distance-independent palm-size reference (Day 5)
- Detects a pinch gesture normalized against hand size, tested and calibrated
  on real data (Day 6)
- Smooths the pinch detection against frame-to-frame flicker, with the
  buffer size choice backed by a real responsiveness-vs-stability test (Day 7)

Ready to move into Week 2: replacing MediaPipe's default drawing with a
custom-styled neon HUD.

---

## Day 8 — Building a Custom HUD (Part 1: Nodes & Skeleton)

### Concept learned
MediaPipe's `draw_landmarks()` was a convenience function doing two things
automatically: drawing a circle at each of the 21 points, and drawing lines
between the correct pairs of points to form a skeleton shape. Since all 21
pixel coordinates were already being extracted since Day 4, both of these can
be done manually instead — the first real step toward a custom-styled HUD
instead of MediaPipe's default plain look, as specifically called out in the
boss's reference video.

### Key building block
- `mp_hands.HAND_CONNECTIONS` — a list of landmark index pairs (e.g. `(5, 6)`)
  that MediaPipe has pre-determined should be visually connected to form a
  correct hand skeleton shape. Reused directly instead of building this
  mapping manually.

### Code — Day 8 (built on top of Day 7's file, `mp_drawing.draw_landmarks()`
replaced with manual drawing)
```python
import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands = 2,
    min_detection_confidence = 0.7
)
# mp_drawing no longer needed — drawing manually now

cap = cv2.VideoCapture(0)
print("Press 'q' to exit!")

pinch_history = []
buffer_size = 5

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
            landmark_list = []
            for lm in hand_landmarks.landmark:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmark_list.append((px, py))

            # draw connecting lines (the "skeleton") — drawn first
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = landmark_list[start_idx]
                end_point = landmark_list[end_idx]
                cv2.line(frame, start_point, end_point, (0, 255, 255), 2)  # yellow

            # draw nodes on top of the lines
            for point in landmark_list:
                cv2.circle(frame, point, 5, (255, 255, 0), -1)  # cyan

            wrist = landmark_list[0]
            middle_knuckle = landmark_list[9]
            index_tip = landmark_list[8]
            thumb_tip = landmark_list[4]

            x1, y1 = wrist
            x2, y2 = middle_knuckle
            palm_size = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            x3, y3 = thumb_tip
            x4, y4 = index_tip
            pinch_distance = math.sqrt((x4 - x3) ** 2 + (y4 - y3) ** 2)

            pinch_ratio = pinch_distance / palm_size
            is_pinched_now = pinch_ratio < 0.4

            pinch_history.append(is_pinched_now)
            if len(pinch_history) > buffer_size:
                pinch_history.pop(0)

            if pinch_history.count(True) > buffer_size // 2:
                pinch_status = "Pinched"
            else:
                pinch_status = "Not Pinched"

    cv2.imshow("Day 8 - Custom HUD (Shape Only)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Practice tasks assigned
1. Replace `mp_drawing.draw_landmarks()` with manual `cv2.line()` +
   `cv2.circle()` drawing using `mp_hands.HAND_CONNECTIONS`
2. Challenge: use two different colors for lines vs. dots

### My completed task / code
Both tasks completed successfully — first tested with matching magenta
lines/dots to confirm the skeleton shape was correct, then completed the
color challenge with yellow lines + cyan dots, a clean two-tone look.
Correctly unpacked `start_idx, end_idx` from each connection pair and looked
up their coordinates in `landmark_list`.

### Notes / things that tripped me up
- None — clean execution, correctly understood that `HAND_CONNECTIONS` is
  just a list of index pairs rather than something needing manual calculation

---

## Day 9 — Adding the Glow Effect

### Concept learned
A real "neon" glow is created by drawing shapes on a separate blank layer,
heavily blurring that layer (spreading the bright color outward into a soft
halo), then blending the blurred result back onto the real camera frame. A
sharp version is drawn again on top afterward so the shape keeps a crisp,
readable core in addition to the soft glow around it — matching how real neon
signs look (bright defined core + soft spreading light).

### Key building blocks
- `np.zeros_like(frame)` — creates a blank black canvas matching `frame`'s
  exact dimensions; first direct use of NumPy in the project
- Drawing on a separate `glow_layer` instead of `frame` directly, so the blur
  step doesn't affect the actual camera image
- `cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)` — spreads bright
  pixels outward; kernel size must be odd, bigger = softer/wider glow
- `cv2.add(frame, blurred_layer)` — merges the blurred glow's brightness onto
  the real frame

### Code — Day 9 (added to the Week 2 starter file)
```python
import numpy as np  # new import needed

glow_layer = np.zeros_like(frame)

for connection in mp_hands.HAND_CONNECTIONS:
    start_idx, end_idx = connection
    start_point = landmark_list[start_idx]
    end_point = landmark_list[end_idx]
    cv2.line(glow_layer, start_point, end_point, (0, 255, 255), 4)

for point in landmark_list:
    cv2.circle(glow_layer, point, 8, (255, 255, 0), -1)

blurred_layer = cv2.GaussianBlur(glow_layer, (25, 25), 0)
frame = cv2.add(frame, blurred_layer)

# sharp version drawn on top for a crisp core
for connection in mp_hands.HAND_CONNECTIONS:
    start_idx, end_idx = connection
    start_point = landmark_list[start_idx]
    end_point = landmark_list[end_idx]
    cv2.line(frame, start_point, end_point, (0, 255, 255), 2)

for point in landmark_list:
    cv2.circle(frame, point, 5, (255, 255, 0), -1)
```

### Practice tasks assigned
1. Add the glow-layer technique on top of the Day 8 skeleton
2. Challenge: compare blur kernel sizes (15,15) vs (45,45) and observe the
   difference in glow softness/spread

### My completed task / code
Glow effect implemented successfully — clear visible halo around the hand
skeleton in all tests. Initial kernel-size comparison (15 vs 45) looked
visually similar at first glance, which led to a useful debugging discussion:

- **Cause identified:** `cv2.add()` clips brightness at 255, so the bright
  central area of the glow can look similarly "maxed out" across different
  kernel sizes on top of a busy, textured camera background — masking the
  real difference, which mostly shows up in the fainter, harder-to-see outer
  fringe of the glow.
- **Fix/technique learned:** viewing the `blurred_layer` alone (via a separate
  `cv2.imshow()` call, before merging with the real frame) isolates the glow
  from the busy background and clipping effects, making the kernel-size
  difference clearly visible.
- **Key takeaway:** code can be working correctly even when a visual change
  is hard to perceive by eye against a distracting background — isolating
  the one variable being tested (e.g. viewing a layer alone, against plain
  black) is a useful general debugging technique, not just specific to this
  project.

### Notes / things that tripped me up
- Initially assumed no visible difference meant something was wrong with the
  blur code, when actually the code was correct and the issue was purely
  about how the comparison was being visually observed

---

## Day 10 — Fine-Tuning Glow Color & Intensity

### Concept learned
`cv2.add()` (used in Day 9) adds brightness directly with no control over
intensity, which can cause the glow to blow out into washed-out white patches
since the source shapes are drawn at full brightness (255). `cv2.addWeighted()`
solves this by giving each image a controllable multiplier before combining
them, acting as an intensity dial rather than an all-or-nothing blend. Also
learned a layered-glow technique: combining two different blur strengths (a
tight bright inner glow + a soft wide outer halo) produces a richer effect
than a single blur pass alone.

### Key building blocks
- `cv2.addWeighted(image1, alpha, image2, beta, gamma)` — blends two images
  using this formula per pixel: `(image1 × alpha) + (image2 × beta) + gamma`
  - `alpha` = how much of image1 to keep (kept at 1.0 — full camera frame)
  - `beta` = how much of image2 (the glow) to let blend in — the actual
    intensity control
  - `gamma` = flat brightness offset, left at 0
- Two-blur-layer technique: blur the same glow shape twice at different
  kernel sizes, then combine both results into one layered glow before
  blending onto the frame

### Code — Day 10 (replacing Day 9's blend section)
```python
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
combined_glow = cv2.addWeighted(glow_small, 0.7, glow_large, 0.5, 0)

frame = cv2.addWeighted(frame, 1.0, combined_glow, 0.6, 0)  # final chosen intensity

for connection in mp_hands.HAND_CONNECTIONS:
    start_idx, end_idx = connection
    start_point = landmark_list[start_idx]
    end_point = landmark_list[end_idx]
    cv2.line(frame, start_point, end_point, (0, 255, 255), 2)

for point in landmark_list:
    cv2.circle(frame, point, 5, (255, 255, 0), -1)
```

### Practice tasks assigned
1. Replace Day 9's `cv2.add()` blend with weighted, two-blur-layer blending
2. Challenge: compare `beta` values 0.4 vs 1.2, then pick a final intensity

### My completed task / code
Reused the "view glow layer alone" debugging technique from Day 9 (applied
independently, without being told to reuse it) to clearly compare kernel
sizes/intensities against a plain black background. Test screenshots showed
a clear, obvious difference this time — tighter/separated halos at lower
settings vs. wider/merged halos at higher settings. Landed on **beta = 0.6**
as the final chosen intensity — a balanced middle value giving visible glow
without washing out into solid white.

### Notes / things that tripped me up
- None — correctly understood alpha/beta/gamma roles after a worked numeric
  example, and successfully self-applied the prior day's debugging technique
  without needing it re-suggested

---

## Day 11 — Testing with Two Hands + Measuring Performance

### Concept learned
A live tracking/drawing program needs to actually run fast enough to feel
responsive, not just look correct in a screenshot. FPS (Frames Per Second)
measures this: record the time before and after processing a frame, calculate
how long it took, and `fps = 1 / time_taken`. Roughly 20-30+ FPS feels smooth
for real-time interaction; under ~15 FPS starts to feel laggy.

### Key building blocks
- `time.time()` — returns the current clock time, used to measure elapsed
  time between frames
- `cv2.putText(image, text, position, font, font_scale, color, thickness)` —
  draws text directly onto a frame; used here to show a live FPS counter
- `cap.set(cv2.CAP_PROP_FRAME_WIDTH, value)` / `cap.set(cv2.CAP_PROP_FRAME_HEIGHT, value)`
  — attempts to configure the webcam's capture resolution

### Code — Day 11 (FPS measurement added)
```python
import time  # new import

prev_frame_time = 0  # before the loop

# ...inside the main loop, after all per-frame processing...
current_frame_time = time.time()
time_taken = current_frame_time - prev_frame_time
fps = 1 / time_taken if time_taken > 0 else 0
prev_frame_time = current_frame_time

cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
```

### Practice tasks assigned
1. Add FPS measurement + on-screen display
2. Test and compare FPS with one hand vs. two hands in frame
3. Investigate if FPS is lower than expected, and why

### My completed task / code
Ran a full diagnostic investigation across multiple isolated tests:

| Test | Result |
|---|---|
| One hand, full HUD (glow + prints) | ~9-12 FPS |
| Two hands, full HUD | ~10-12 FPS (no meaningful difference vs. one hand) |
| Prints disabled, glow enabled | ~9-12 FPS (no change — prints ruled out as a factor) |
| Prints disabled, glow disabled | ~10-19 FPS (some improvement, but not dramatic) |
| Prints disabled, glow enabled, lower camera resolution (480x360) | ~9-13 FPS (no meaningful improvement) |

**Root cause identified:** MediaPipe's hand-detection neural network internally
resizes input frames to its own fixed, small size before running inference,
regardless of the camera's actual capture resolution. This means the
computationally expensive part (running the detection model) costs roughly
the same no matter what resolution the webcam captures at — so lowering
resolution mostly reduces the cost of secondary operations (flip, color
conversion, blur) rather than the real bottleneck.

**Conclusion:** the bottleneck is genuinely the cost of running MediaPipe's
two-hand detection model on CPU (no GPU acceleration) — a hardware/library
limitation, not a bug in the code. 9-19 FPS is a realistic, expected range
for this setup. Accepted this as the current baseline rather than continuing
to chase further optimization at this stage, since it's sufficient for
testing gesture/drawing logic going forward. Possible future options if
performance ever becomes a practical blocker: reduce to 1-hand detection if a
feature doesn't need two hands, or use GPU acceleration.

### Notes / things that tripped me up
- Initially assumed hand count and/or glow effect were the main performance
  factors; testing disproved both as the *primary* cause, revealing a deeper
  bottleneck (CPU-bound neural network inference) that isn't fixable through
  simple code changes like resolution or print removal
- Practiced the general engineering process of forming a hypothesis, testing
  it in isolation, and updating the conclusion when the data didn't match
  the initial assumption

---

## Day 12 — *(pending)*
