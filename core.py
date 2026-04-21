import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time  
from robot_3d import send_hand_data

last_time = 0
# =========================
# MediaPipe setup
# =========================
base_options = python.BaseOptions(model_asset_path='./hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.HandLandmarker.create_from_options(options)

# =========================
# Tkinter setup (Two Windows)
# =========================
root = tk.Tk()
root.title("Hand Tracking - Camera Feed")

screen_width = root.winfo_screenwidth()
fixed_height = 600

root.geometry(f"{800}x{fixed_height}+0+0")

video_label = tk.Label(root, bg="black")
video_label.pack(expand=True, fill="both")

HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),
    (0,5), (5,6), (6,7), (7,8),
    (9,10), (10,11), (11,12),
    (13,14), (14,15), (15,16),
    (0,17), (17,18), (18,19), (19,20),
    (5,9), (9,13), (13,17)
]

cap = cv2.VideoCapture(0)

# =========================
# Helper Functions
# =========================
def draw_manual(image, result):
    if not result.hand_landmarks: return image
    h, w, _ = image.shape
    for landmarks in result.hand_landmarks:
        for landmark in landmarks:
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(image, (cx, cy), 8, (0, 255, 0), -1)
        for start_idx, end_idx in HAND_CONNECTIONS:
            start, end = landmarks[start_idx], landmarks[end_idx]
            pt1 = (int(start.x * w), int(start.y * h))
            pt2 = (int(end.x * w), int(end.y * h))
            cv2.line(image, pt1, pt2, (255, 0, 0), 3)
    return image

def get_fingers_status(landmarks):
    tips_ids, pip_ids = [8, 12, 16, 20], [6, 10, 14, 18]
    fingers_open = [1 if landmarks[tip].y < landmarks[pip].y else 0 for tip, pip in zip(tips_ids, pip_ids)]
    fingers_open.append(1 if landmarks[4].x > landmarks[3].x else 0)
    return fingers_open

# =========================
# Main Loop Function
# =========================
def update_frame():
    global last_time
    ret, frame = cap.read()
    if not ret:
        root.after(15, update_frame)
        return

    frame = cv2.flip(frame, 1)

    window_w = root.winfo_width()
    window_h = root.winfo_height()
    if window_w > 1 and window_h > 1:
        frame = cv2.resize(frame, (window_w, window_h))

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    hand_present, status_text, fingers_count = "No", "Closed", 0

    if result.hand_landmarks:
        hand_present = "Yes"
        landmarks = result.hand_landmarks[0]
        fingers_list = get_fingers_status(landmarks)
        fingers_count = sum(fingers_list)
        status_text = "Open" if fingers_count >= 3 else "Closed"

        wrist = landmarks[0]
        last_time = send_hand_data(
            wrist.x,
            wrist.y,
            last_time
        )
        
        frame = draw_manual(frame, result)

    # UI Overlay
    cv2.rectangle(frame, (10, 10), (400, 160), (0, 0, 0), -1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"Hand Detected: {hand_present}", (20, 45), font, 1, (0, 255, 0) if hand_present == "Yes" else (0, 0, 255), 2)
    cv2.putText(frame, f"Hand State: {status_text}", (20, 90), font, 1, (0, 255, 0) if status_text == "Open" else (0, 0, 255), 2)
    cv2.putText(frame, f"Fingers: {fingers_count}", (20, 135), font, 1, (255, 255, 0), 2)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img_rgb)
    imgtk = ImageTk.PhotoImage(image=im_pil)

    video_label.configure(image=imgtk)
    video_label.imgtk = imgtk

    root.after(10, update_frame)

if __name__ == "__main__":
    update_frame()
    root.mainloop()
    cap.release()