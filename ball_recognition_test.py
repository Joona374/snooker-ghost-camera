###### THIS IS JUST A TEST FOR IMPLEMENTING BALL TRACKING #######

import cv2
import numpy as np
import time

def find_color_balls(image: np.ndarray, color_ranges: dict) -> list:
    """
    Find colored balls in the image using color ranges and Hough Circle Transform.
    :param image: Input image (BGR format).
    :param color_ranges: Dictionary containing low and high HSV ranges for the wanted color.
    :return: List of detected circles with their positions and radii.
    """
    # Step 0: Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Step 1: Get color mask
    low_range1 = color_ranges["low1"]
    upper_range1 = color_ranges["high1"]
    mask1 = cv2.inRange(hsv_image, low_range1, upper_range1)

    # This is only used for red balls with split HSV range
    if "low2" in color_ranges and "high2" in color_ranges:
        low_range2 = np.array(color_ranges["low2"])
        upper_range2 = np.array(color_ranges["high2"])
        mask2 = cv2.inRange(hsv_image, low_range2, upper_range2)
        mask = cv2.bitwise_or(mask1, mask2) # Combine masks
    else:
        mask = mask1

    # Step 2: Clean the mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Step 3: Apply mask to image
    masked = cv2.bitwise_and(image, image, mask=mask)

    # Step 4: Convert to grayscale for HoughCircles
    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    
    # Step 5: Blur to improve circle detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 2)

    # Step 6: Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(
        blurred,                   # Input image (grayscale and blurred)
        cv2.HOUGH_GRADIENT,      # Detection method: HOUGH_GRADIENT is standard and effective
        dp=1.2,                  
        minDist=50,              # Minimum distance between the centers of detected circles.
        param1=100,              # This is the upper threshold for the internal Canny edge detector.
        param2=30,               # Threshold for center detection — lower = more sensitive (more false circles), higher = stricter (fewer but more confident circles).
        minRadius=20,            # Minimum circle radius (in pixels). Prevents detecting tiny noise blobs.
        maxRadius=29             # Maximum circle radius (in pixels). Prevents detecting giant false circles.
    )

    # Step 7: Convert circles to a list of dictionaries. Dict = one ball, List = all balls of this color
    circles_to_return = []
    if circles is not None:
        circles = np.around(circles[0]).astype(int) # Round and convert to int. circles[0] because HoughCircles returns a 3D array.
        for x, y, r in circles:
            circle_in_list = {"x": x, "y": y, "r": r}
            circles_to_return.append(circle_in_list)


    return circles_to_return

def get_ball_positions(image):
    """
    Get positions of colored balls in the image.
    :param image: Input image (BGR format).
    :return: Dictionary containing lists of detected circles for each color.
    """

    # RANGES FOR BALLS
    white_range = { # WORKS
        "low1": np.array([0, 0, 200]),
        "high1": np.array([180, 50, 255])
    }
    black_range = { # WORKS
        "low1": np.array([0, 0, 0]),
        "high1": np.array([180, 255, 60])
    }
    yellow_range = { # WORKS
        "low1": np.array([15, 100, 100]),
        "high1": np.array([55, 255, 255])
    }
    green_range = { # WORKS
        "low1": np.array([50, 50, 50]),
        "high1": np.array([110, 255, 220])
    }
    orange_range = { # WORKS
        "low1": np.array([1750, 0, 0]),
        "high1": np.array([180, 255, 255]),
        "low2": np.array([0, 0, 0]),
        "high2": np.array([10, 255, 255])
    }
    blue_range = { # WORKS
        "low1": np.array([110, 100, 50]),
        "high1": np.array([130, 255, 255])
    }
    purple_range = { # WORKS
        "low1": np.array([120, 130, 50]),
        "high1": np.array([170, 255, 230])
    }
    red_range = { # WORKS
        "low1": np.array([0, 150, 220]),
        "high1": np.array([10, 255, 255]),
        "low2": np.array([170, 150, 220]),
        "high2": np.array([180, 255, 255])
    }
    dark_red_range = { # WORKS
        "low1": np.array([0, 180, 50]),
        "high1": np.array([10, 255, 210]),
        "low2": np.array([160, 180, 50]),
        "high2": np.array([180, 255, 210])
    }

    # Create a dictionary to hold the detected circles for each color
    # Each color will have a list of circles, where each circle is a dictionary with keys "x", "y", and "r"
    circles_dict = {
        "white": find_color_balls(image, white_range),
        "black": find_color_balls(image, black_range),
        "yellow": find_color_balls(image, yellow_range),
        "green": find_color_balls(image, green_range),
        "orange": find_color_balls(image, orange_range),
        "blue": find_color_balls(image, blue_range),
        "purple": find_color_balls(image, purple_range),
        "red": find_color_balls(image, red_range),
        "dark_red": find_color_balls(image, dark_red_range),
    }

    return circles_dict


def test_ball_tracking(source: int | str = 0):
    """
    Test function to track balls in a video stream or static image.
    :param source: Camera index (int) or "i" for static image.
    :return: None
    """
    print("Starting ball tracking... Press 'ESC' to exit.")

    if source == "i":
        image = cv2.imread(r"static\images\WIN_20250526_13_14_01_Pro.jpg")
        print("Using static image for testing.")
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)

        ################################################################
        #### IGNORE THIS PART IF YOU ARE NOT JOONA ####
        #### THIS IS JUST FOR JOONA's PC TO WORK WITH THE CAMERA :D ####
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        time.sleep(2)

        if not cap.isOpened():
            print("❌ Failed to open camera.")
            exit()
        #### THIS IS JUST FOR JOONA's PC TO WORK WITH THE CAMERA :D ####
        #### IGNORE THIS PART IF YOU ARE NOT JOONA ####
        ################################################################

    # Read frames from the camera or image on loop
    while True:

        if source != "i":
            # Read a frame from the camera
            ret, frame = cap.read()
            if not ret:
                break
        else:
            # Use the static image instead of camera input
            frame = image.copy()

        n_of_circles = 0 # Just for counting the number of detected balls to see if the detection works / detects too many balls


        # get_ball_positions returns circles_dict which will contain the detected balls categorized by color.
        # Each ball is represented as a dictionary with keys "x", "y", and "r" for position and radius (INT).
        #   circles_dict = {
        #   "white": [{"x": x-coord, "y": y-coord, "r": radius}, {possibly another ball}, ],
        #   "black": [{"x": x-coord, "y": y-coord, "r": radius}, {possibly another ball}, ],
        #   ...  
        #   }
        circles_dict = get_ball_positions(frame)
        for color, balls in circles_dict.items():
                for ball in balls:
                        x = ball.get("x", 0)
                        y = ball.get("y", 0)
                        r = ball.get("r", 0)

                        cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
                        n_of_circles += 1

        # Display the number of detected balls for debugging
        print(f"Number of detected balls: {n_of_circles}")
        cv2.imshow("Detected Ball", frame)
        
        if cv2.waitKey(10) & 0xFF == 27:  # Exit on 'ESC' key
            break

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    # Run the test function to track balls
    # Use input parameter (int) for camera index or ("i") for static image
    test_ball_tracking(0)