import cv2
from time import sleep


def set_brightness_contrast(frame):
    """
    Adjust brightness and contrast of the frame.
    Returns the adjusted frame.
    """

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Add trackbars for brightness and contrast
    def nothing(x):
        pass
    cv2.namedWindow("Adjustments")
    cv2.createTrackbar("Brightness", "Adjustments", 100, 200, nothing)
    cv2.createTrackbar("Contrast", "Adjustments", 100, 200, nothing)

    while True:
        # Get trackbar positions
        brightness = cv2.getTrackbarPos("Brightness", "Adjustments") - 100
        contrast = cv2.getTrackbarPos("Contrast", "Adjustments") - 100

        # Adjust brightness and contrast
        adjusted_frame = cv2.convertScaleAbs(frame, alpha=1 + contrast / 100.0, beta=brightness)

        # Show the adjusted frame
        cv2.imshow("Adjusted Frame", adjusted_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Contrast: {1 + contrast / 100.0}, Brightness: {brightness}")
            break

    cv2.destroyAllWindows()


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






