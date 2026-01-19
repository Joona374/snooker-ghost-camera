import cv2
import numpy as np


def get_ball_positions(frame):
    """
    Detect centers of balls in the frame using HoughCircles
    Returns list of (x, y, color) tuples
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Adjust brightness and contrast
    adjusted_gray = cv2.convertScaleAbs(gray, alpha=1.4, beta=10)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(adjusted_gray, (3, 3), 3)

    # Use HoughCircles to detect circular objects
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT_ALT,  # Alternative Hough gradient method - more accurate
        dp=1.5,  # Inverse ratio of the accumulator resolution to the image resolution
        minDist=20,  # Minimum distance between the centers of the detected circles
        param1=200,  # Higher threshold for the internal Canny edge detector
        param2=0.9,  # Accumulator threshold for the circle centers (0.0-1.0 for ALT version)
        minRadius=20,  # Minimum circle radius to be detected
        maxRadius=30,  # Maximum circle radius to be detected
    )

    ball_centers = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            ball_centers.append((x, y, 25))

    balls_with_color = detect_color_from_balls(ball_centers, frame)

    return balls_with_color


def test_get_ball_positions(frame):
    """
    Detect centers of balls in the frame using HoughCircles
    Returns list of (x, y, color) tuples
    """
    # Convert to HSV color space and increase brightness
    # This helps in detecting colored balls more effectively
    # Increase brightness by adding a constant value to the V channel 
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame_hsv[:, :, 2] = np.clip(frame_hsv[:, :, 2] + 150, 0, 255)

    # Convert the difference to grayscale
    gray = cv2.cvtColor(frame_hsv, cv2.COLOR_BGR2GRAY)

    # Add blur to reduce noise
    # Using median blur to preserve edges while reducing noise
    gray_blur = cv2.medianBlur(gray, 5)
    cv2.imshow("Gray Blur", gray_blur)

    # Use HoughCircles to detect circular objects
    circles = cv2.HoughCircles(
        gray_blur,
        cv2.HOUGH_GRADIENT_ALT,  # Alternative Hough gradient method - more accurate
        dp=1.5,  # Inverse ratio of the accumulator resolution to the image resolution
        minDist=18,  # Minimum distance between the centers of the detected circles
        param1=100,  # Higher threshold for the internal Canny edge detector
        param2=0.9,  # Accumulator threshold for the circle centers (0.0-1.0 for ALT version)
        minRadius=20,  # Minimum circle radius to be detected
        maxRadius=30,  # Maximum circle radius to be detected
    )

    ball_centers = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            ball_centers.append((x, y, 25))

    balls_with_color = detect_color_from_balls(ball_centers, frame)

    return balls_with_color



def detect_color_from_balls(ball_centers, frame):
    """
    Detect the color of the balls in the frame.
    Returns a list of tuples with (x, y, average_color).
    """
    if not ball_centers:
        return []

    color_info = []
    for x, y, r in ball_centers:
        # Ensure the center is within the image bounds
        h, w = frame.shape[:2]
        x1, y1 = max(x - 10, 0), max(y - 10, 0)
        x2, y2 = min(x + 10, w), min(y + 10, h)
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue
        avg_color = tuple(int(c) for c in np.mean(roi, axis=(0, 1)))
        color_info.append((int(x), int(y), check_color_in_range(avg_color)))

    return color_info


def check_color_in_range(color):
    """
    Check if the given color is within the defined ranges for colored balls.
    Args:
        color (tuple): A tuple representing the BGR color (B, G, R).
    Returns color name if color is detected, otherwise False.
    """
    # Define color ranges (you can adjust these based on your balls)
    color_ranges = {
        "red": [(np.array([160, 120, 235]), np.array([180, 200, 255]))],
        "brown": [(np.array([160, 170, 167]), np.array([179, 200, 240]))],
        "green": [(np.array([91, 90, 100]), np.array([111, 255, 255]))],
        "blue": [(np.array([111, 0, 0]), np.array([131, 255, 255]))],
        "yellow": [(np.array([19, 70, 0]), np.array([39, 255, 255]))],
        "black": [(np.array([130, 36, 70]), np.array([190, 100, 149]))],
        "white": [(np.array([0, 0, 200]), np.array([20, 20, 255]))],
    }

    # Convert average color to HSV format
    avg_color_hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]

    for color_name, ranges in color_ranges.items():
        for lower, upper in ranges:
            if np.all(avg_color_hsv >= lower) and np.all(avg_color_hsv <= upper):
                return color_name

    return "Color"


def detect_from_video():
    """
    Detect colored balls in real-time video
    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    print("Press 'q' to quit")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Detect ball positions
        ball_positions = test_get_ball_positions(frame)
        if not ball_positions:
            # print("No balls detected")
            continue

        # Draw circles on the detected ball positions
        frame = write_label_on_ball(ball_positions, frame)

        # Show the frame with detected balls
        cv2.imshow("Colored Ball Detection - Live Video", frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()


def write_label_on_ball(ball_centers, frame):
    """
    Draw circles of the average color at each detected ball center.
    Each circle has radius 10 pixels and thickness 2 pixels.
    """
    for x, y, color in ball_centers:
        # Ensure the center is within the image bounds
        h, w = frame.shape[:2]
        x1, y1 = max(x - 10, 0), max(y - 10, 0)
        x2, y2 = min(x + 10, w), min(y + 10, h)
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue
        avg_color = tuple(int(c) for c in np.mean(roi, axis=(0, 1)))

        # Convert average color to HSV format
        avg_color_hsv = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_BGR2HSV)[0][0]

        # Add label with average color
        cv2.putText(
            frame,
            f"{color}, {avg_color_hsv}",
            (x, y + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            avg_color,
            2,
        )

        # Draw the circle with the average color
        cv2.circle(frame, (x, y), 25, (0, 255, 0), 2)
    return frame


if __name__ == "__main__":
    """
    detect_from_video() -> get_ball_positions() -> detect_color_from_balls() -> check_color_in_range()
                     |---> write_label_on_ball()

    get_ball_positions() -> detect_color_from_balls() -> check_color_in_range()
    """
    detect_from_video()
