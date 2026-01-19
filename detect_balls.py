from pprint import pprint
import cv2
import numpy as np
from time import sleep


def capture_image(filename="captured_photo.jpg"):
    """
    Capture an image from the camera and save it to a file
    """
    camera = cv2.VideoCapture(0)
    sleep(0.3)  # Allow camera to warm up
    if not camera.isOpened():
        print("Error: Could not open camera")
        return
    ret, frame = camera.read()
    camera.release()
    if not ret:
        print("Error: Could not read frame from camera")
        return
    # Save the captured frame to a file
    if cv2.imwrite(filename, frame) is False:
        print(f"Error: Could not save image to {filename}")
        return
    print(f"Photo saved as {filename}")


def crop_image(image_path, crop_area, output_path="cropped_image.jpg"):
    """
    Crops an image based on the given crop area and saves the cropped image.

    Args:
        image_path (str): Path to the input image.
        crop_area (tuple): A tuple (x, y, width, height) defining the crop area.
        output_path (str): Path to save the cropped image. Defaults to "cropped_image.jpg".
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from {image_path}")
        return

    x, y, w, h = crop_area
    cropped_image = image[y : y + h, x : x + w]

    if cropped_image.size == 0:
        print("Error: Crop area is invalid.")
        return

    # Save the cropped image
    cv2.imwrite(output_path, cropped_image)
    print(f"Cropped image saved to {output_path}")

    # Optionally display the cropped image
    cv2.imshow("Cropped Image", cropped_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_video():
    """
    Display live video feed from the camera.
    Press 'q' to quit.
    """
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    print("Press 'q' to quit")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame")
            break

        cv2.imshow("Video Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


def show_cropped_video():
    """
    Display live video feed from the camera with adjustable crop area using trackbars.
    Press 'q' to quit, 'k' to print current crop area.
    """

    def nothing(x):
        pass

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    # Get frame dimensions
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create window and trackbars
    cv2.namedWindow("Cropped Video Feed")
    cv2.createTrackbar("X", "Cropped Video Feed", 0, width, nothing)
    cv2.createTrackbar("Y", "Cropped Video Feed", 0, height, nothing)
    cv2.createTrackbar("Width", "Cropped Video Feed", width, width, nothing)
    cv2.createTrackbar("Height", "Cropped Video Feed", height, height, nothing)

    print("Press 'q' to quit, 'k' to print current crop area")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame")
            break

        x = cv2.getTrackbarPos("X", "Cropped Video Feed")
        y = cv2.getTrackbarPos("Y", "Cropped Video Feed")
        w = cv2.getTrackbarPos("Width", "Cropped Video Feed")
        h = cv2.getTrackbarPos("Height", "Cropped Video Feed")

        # Check boundaries to avoid going out of frame
        w = min(w, width - x)
        h = min(h, height - y)

        if w > 0 and h > 0:
            cropped_frame = frame[y : y + h, x : x + w]
            cv2.imshow("Cropped Video Feed", cropped_frame)
        else:
            # If width or height is zero or less, show original frame
            cv2.imshow("Cropped Video Feed", frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord("k"):
            print(f"Current crop area: ({x}, {y}, {w}, {h})")
        elif key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


def detect_balls_in_photo(image_path="captured_photo.jpg"):
    """
    Detect ball centers in a static image file
    Returns list of (x, y, radius) tuples and displays the result
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from {image_path}")
        return []

    print(f"Analyzing image: {image_path}")
    print(f"Image size: {image.shape}")

    # Detect ball centers using the existing function
    ball_centers = detect_ball_centers(image)

    # Create a copy for display
    display_image = image.copy()

    # Draw detected circles on the image
    for i, (x, y, r) in enumerate(ball_centers):
        # Draw the circle outline
        cv2.circle(display_image, (x, y), r, (0, 255, 0), 2)
        # Draw the center point
        cv2.circle(display_image, (x, y), 2, (0, 255, 0), 3)
        # Add text with coordinates
        cv2.putText(
            display_image,
            f"Ball {i+1}: ({x},{y})",
            (x - 40, y - r - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

    # Display the result
    cv2.imshow("Ball Detection - captured_photo.jpg", display_image)

    # Print results to console
    print(f"Found {len(ball_centers)} balls:")
    for i, (x, y, r) in enumerate(ball_centers):
        print(f"  Ball {i+1}: Center=({x}, {y}), Radius={r}")

    print("Press any key to close the image window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return ball_centers


def detect_colored_balls_in_photo(image_path="captured_photo.jpg"):
    """
    Detect colored ball centers in a static image using color segmentation
    Returns list of (x, y, color) tuples
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from {image_path}")
        return []

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define color ranges (same as in ball_detect.py)
    color_ranges = {
        "red": [
            (np.array([0, 150, 100]), np.array([10, 255, 255])),
            (np.array([160, 150, 100]), np.array([179, 255, 255])),
        ],
        "green": [(np.array([32, 74, 0]), np.array([105, 255, 255]))],
        "blue": [(np.array([96, 74, 100]), np.array([131, 255, 255]))],
        "yellow": [(np.array([20, 100, 100]), np.array([30, 255, 255]))],
        "white": [(np.array([0, 0, 241]), np.array([178, 53, 255]))],
        "black": [(np.array([114, 22, 0]), np.array([179, 255, 101]))],
    }

    ball_centers = []
    display_image = image.copy()

    for color, ranges in color_ranges.items():
        # Create mask for this color
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        if color == "blue":
            # Show mask for color on
            cv2.imshow(f"Mask - {color}", mask)

        # Apply morphological operations to clean up the mask

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000 and area < 2000:  # Filter small objects
                # Check if contour is roughly circular
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter**2)
                    if circularity > 0.7:  # Threshold for circularity
                        # Calculate center
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            ball_centers.append((cx, cy, color))

    # Draw colored ball centers
    color_map = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255),
        "black": (255, 255, 255),
        "white": (0, 0, 0),
    }

    for i, (x, y, color) in enumerate(ball_centers):
        cv2.circle(display_image, (x, y), 8, color_map.get(color, (255, 255, 255)), -1)
        cv2.putText(
            display_image,
            f"{color}({x},{y})",
            (x - 30, y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            color_map.get(color, (255, 255, 255)),
            1,
        )

    # Display the result
    cv2.imshow("Colored Ball Detection - captured_photo.jpg", display_image)

    # Print results
    print(f"Found {len(ball_centers)} colored balls:")
    for i, (x, y, color) in enumerate(ball_centers):
        print(f"  {color.capitalize()} ball: Center=({x}, {y})")

    print("Press any key to close the image window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return ball_centers


def detect_colored_balls_in_video():
    """
    Detect colored ball centers in real-time video using color segmentation
    """
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    # Define color ranges (same as in detect_colored_balls_in_photo)
    color_ranges = {
        "red": [
            (np.array([0, 150, 100]), np.array([10, 255, 255])),
            (np.array([160, 150, 100]), np.array([179, 255, 255])),
        ],
        "green": [(np.array([32, 74, 0]), np.array([105, 255, 255]))],
        "blue": [(np.array([96, 74, 100]), np.array([131, 255, 255]))],
        "yellow": [(np.array([20, 100, 100]), np.array([30, 255, 255]))],
        "white": [(np.array([0, 0, 241]), np.array([178, 53, 255]))],
        "black": [(np.array([114, 22, 0]), np.array([179, 255, 101]))],
    }

    # Color map for drawing
    color_map = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255),
        "black": (255, 255, 255),
        "white": (0, 0, 0),
    }

    print("Press 'q' to quit, 'c' to print current ball positions")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        ball_centers = []
        display_frame = frame.copy()

        for color, ranges in color_ranges.items():
            # Create mask for this color
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

            # Find contours
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000 and area < 2000:  # Filter small objects
                    # Check if contour is roughly circular
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter**2)
                        if circularity > 0.7:  # Threshold for circularity
                            # Calculate center
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                ball_centers.append((cx, cy, color))

        # Draw colored ball centers on the frame
        for x, y, color in ball_centers:
            cv2.circle(
                display_frame, (x, y), 8, color_map.get(color, (255, 255, 255)), -1
            )
            cv2.putText(
                display_frame,
                f"{color}({x},{y})",
                (x - 30, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color_map.get(color, (255, 255, 255)),
                1,
            )

        # Show ball count on frame
        cv2.putText(
            display_frame,
            f"Balls detected: {len(ball_centers)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Colored Ball Detection - Live Video", display_frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("c"):
            print(f"\nCurrent frame - Found {len(ball_centers)} balls:")
            for i, (x, y, color) in enumerate(ball_centers):
                print(f"  {color.capitalize()} ball: Center=({x}, {y})")

    camera.release()
    cv2.destroyAllWindows()


def detect_ball_centers(frame):
    """
    Detect centers of balls in the frame using HoughCircles
    Returns list of (x, y, radius) tuples
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (7, 7), 1)

    # Use HoughCircles to detect circular objects
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,  # Inverse ratio of accumulator resolution
        minDist=20,  # Minimum distance between circle centers
        param1=28,  # Upper threshold for edge detection
        param2=30,  # Accumulator threshold for center detection
        minRadius=20,  # Minimum circle radius
        maxRadius=33,  # Maximum circle radius
    )

    ball_centers = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            ball_centers.append((x, y, r))

    return ball_centers


def make_mask_from_ball_centers(ball_centers, frame):
    """
    Create a mask from detected ball centers
    Returns a binary mask where balls are white and background is black
    """
    if not ball_centers:
        return None

    # Create an empty mask
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    centers = set()  # To avoid duplicate centers

    for x, y, r in ball_centers:
        if r > 7 and r < 30:
            cv2.circle(mask, (x, y), r, 255, -1)  # Fill circle with white
            centers.add((x, y, r))

    return mask, centers


def put_color_circle_on_ball_centers(ball_centers, frame):
    """
    Draw circles of the average color at each detected ball center.
    Each circle has radius 10 pixels and thickness 2 pixels.
    """
    for x, y, r in ball_centers:
        # Ensure the center is within the image bounds
        h, w = frame.shape[:2]
        x1, y1 = max(x - 10, 0), max(y - 10, 0)
        x2, y2 = min(x + 10, w), min(y + 10, h)
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            continue
        avg_color = tuple(int(c) for c in np.mean(roi, axis=(0, 1)))
        #Convert average color to HSV format
        avg_color_hsv = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_BGR2HSV)[0][0]
         # Add label with average color
        cv2.putText(
            frame,
            f"{avg_color_hsv}, {check_color_in_range(avg_color)}",
            (x, y + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            avg_color,
            2,
        )

        # Draw the circle with the average color
        cv2.circle(frame, (x, y), 25, (0, 255, 0), 2)
    return frame


def show_video_with_ball_centers():
    """
    Display live video feed from the camera.
    Press 'q' to quit.
    """
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    print("Press 'q' to quit")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        ball_centers = detect_ball_centers(frame)
        img = put_color_circle_on_ball_centers(ball_centers, frame)
        cv2.imshow("Video Feed", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


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
        avg_color_hsv = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_BGR2HSV)[0][0]
        color_info.append((x, y, check_color_in_range(avg_color)))

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
        'red': [(np.array([160, 111, 167]), np.array([179, 155, 255]))],
        'brawn': [(np.array([160, 150, 167]), np.array([179, 255, 255]))],
        'green': [(np.array([91, 90, 100]), np.array([111, 255, 255]))],
        'blue': [(np.array([111, 0, 0]), np.array([131, 255, 255]))],
        'yellow': [(np.array([19, 70, 0]), np.array([39, 255, 255]))],
        'black': [(np.array([130, 36, 77]), np.array([174, 75, 149]))],
        'white': [(np.array([0, 0, 200]), np.array([20, 20, 255]))]
    }

    #Convert average color to HSV format
    avg_color_hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]

    for color_name, ranges in color_ranges.items():
        for lower, upper in ranges:
            if np.all(avg_color_hsv >= lower) and np.all(avg_color_hsv <= upper):
                return color_name

    return "Color"


def get_ball_positions(frame):
    """
    Detect centers of balls in the frame using HoughCircles
    Returns list of (x, y, radius) tuples
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (7, 7), 1)

    # Use HoughCircles to detect circular objects
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,  # Inverse ratio of accumulator resolution
        minDist=20,  # Minimum distance between circle centers
        param1=28,  # Upper threshold for edge detection
        param2=30,  # Accumulator threshold for center detection
        minRadius=20,  # Minimum circle radius
        maxRadius=33,  # Maximum circle radius
    )

    ball_centers = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            ball_centers.append((x, y, r))

    balls_with_color = detect_color_from_balls(ball_centers, frame)

    return balls_with_color


if __name__ == "__main__":
    # capture_image()
    # show_video()
    # show_cropped_video() # (72, 182, 1133, 590)
    # detect_colored_balls_in_photo("captured_photo.jpg")
    # image = cv2.imread("captured_photo.jpg")
    # centers = detect_ball_centers(image)
    # frame = put_color_circle_on_ball_centers(centers, image)
    # color_info = detect_color_from_balls(centers, image)
    # show_video_with_ball_centers()
    # if frame is not None:
    #     cv2.imshow("Balls", frame)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #     pprint(color_info)
    pass

