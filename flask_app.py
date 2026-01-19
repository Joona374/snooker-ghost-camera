"""
Flask server application for the snooker camera system.
This application provides routes to capture images from the camera and stream live video.
Run this python file to start the Flask server and access the camera functionalities (http://localhost:5000/)
"""

import flask
import cv_module
from pathlib import Path


IMAGES_FOLDER = Path("static/images")

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")


# Route for getting a new (pre strike) image from the camera
@app.route("/get-image")
def get_image():
    # Get a picture from the cv_module, and if it fails, return an error response
    image_bytes = cv_module.get_picture()
    if image_bytes is None:
        print("Error capturing image from camera in /get-image")
        return "Error capturing image", 500
    


    # Return the image bytes as a response with the appropriate MIME type
    return flask.Response(image_bytes, mimetype='image/jpeg')


############### WIP ############### 
@app.route("/get-ball-positions")
def get_ball_positions():
    # Get the ball positions from the cv_module
    positions = cv_module.get_ball_positions()
    
    if positions:
        serializable_balls = []
        for ball in positions:
            regular_int_ball = (int(ball[0]), int(ball[1]), ball[2])  # Convert to int for JSON serialization
            serializable_balls.append(regular_int_ball)

    print(f"Positions: {positions}")
    if positions is None:
        return "Error getting ball positions", 500
    if not positions:
        return flask.jsonify({"message": "No balls detected"}), 200

    # Return the positions as a JSON response
    return flask.jsonify(serializable_balls), 200
############### WIP ############### 


# Route to get the live video stream from the camera
@app.route("/get-live-video")
def get_live_video():
    # Get the live video generator from the cv_module, and if it fails, return an error response
    video_generator = cv_module.get_live_video()
    if video_generator is None:
        return "Error starting live video stream", 500
    
    # Return the video stream as a multipart response (continuous stream of JPEG images)
    return flask.Response(video_generator, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/capture-table", methods=["POST"])
def capture_table():
    image_bytes = cv_module.get_picture()
    if image_bytes is None:
        return flask.jsonify({"error": "Error capturing image from camera"}), 500

    try:
        image_path = IMAGES_FOLDER / "table.jpg"
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        return flask.jsonify({"message": "Table image saved"}), 200
    except Exception as e:
        print(f"Error saving image: {e}")
        return flask.jsonify({"error": "Error saving image"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
