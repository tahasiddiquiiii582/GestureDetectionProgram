# Gesture Detection Program — Learning Journal
Personal record of each day's lesson, concepts learned, tasks completed, and code.
Following the 30-day roadmap (1 hour/day) to build the Air-Drawing HUD project.

---

## Day 1 — Basic Webcam Capture

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

    cv2.imshow("Day 1 - Webcam Test", frame)  # display that frame in a window

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
  will matter again in Day 2+ when checking if a hand was actually detected
  before reading its landmarks.

---

## Environment Setup Notes (for reference)
- Using Python 3.11 (not 3.14 — mediapipe compatibility issue) via `py -3.11`
- mediapipe pinned to `0.10.9` (versions ≥ ~0.10.3x and 1.x removed the legacy
  `solutions` API that `solutions.hands` depends on)
- Required Microsoft Visual C++ Redistributable (x64) installed to fix a
  `DLL load failed` error when importing mediapipe
- Run files with: `py -3.11 <filename>.py`
- Install packages with: `py -3.11 -m pip install <package>`

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

---

## Day 2 — *(pending)*
