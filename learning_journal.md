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

## Day 4 — *(pending)*
