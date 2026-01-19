import cv2
import time
import detect_balls
import numpy as np

cap: cv2.VideoCapture | None = None
_latest_frame: np.ndarray | None = None

def get_camera():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("❌ Failed to open camera.")
            exit()
        if cap.isOpened():
            print("Camera initialized successfully")
        else:
            print("Failed to initialize camera")
    return cap


def get_picture():
    """
    Capture a picture from the camera.
    Returns:
        bytes: The captured image as bytes.
        np.ndarray: The captured image as a NumPy array.
    """
    global _latest_frame

    camera = get_camera()
    if not camera.isOpened():
        print("Camera not available")
        return None

    # time.sleep(0.5)
    ret, frame = camera.read()
    if not ret:
        print("Cap is not returning a frame")
        return None
    
    flip = cv2.flip(frame, 1)
    _latest_frame = flip.copy()  # Store the latest frame for further processing

    ret, buffer = cv2.imencode('.jpg', flip)
    if not ret:
        print("Flip is not returning buffer")
        return None
    
    return buffer.tobytes()


def get_live_video():
    global _latest_frame

    camera = get_camera()
    if not camera.isOpened():
        print("Cannot open camera")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        flip = cv2.flip(frame, 1)
        _latest_frame = flip.copy()
        
        ret, buffer = cv2.imencode('.jpg', flip)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def get_empty_table():
    # Placeholder for empty table retrieval logic
    return "Empty table data"


############### WIP ###############
def get_ball_positions():
    if _latest_frame is not None:
        latest_position = detect_balls.get_ball_positions(_latest_frame)
        return latest_position
    else:
        print("No frame available to get ball positions")
        return None
############### WIP ###############
