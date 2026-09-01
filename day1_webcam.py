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