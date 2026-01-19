"""
Flask server application for the snooker camera system.
This application provides routes to capture images from the camera and stream live video.
Run this python file to start the Flask server and access the camera functionalities (http://localhost:5000/)
"""
# This needs to be first beucase reasons :D
import eventlet
eventlet.monkey_patch()



import flask
import cv_module
from pathlib import Path
from flask_socketio import SocketIO
import socket_handlers

IMAGES_FOLDER = Path("static/images")


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "TODO: Set a secure secret key for production"
socketio = SocketIO(app, cors_allowed_origins="*")
socket_handlers.register_socket_events(socketio)

##################################### ROUTES #####################################
# Route for the index page
@app.route("/")
def index():
    """
    Render the index page of the Flask application.
    This page serves as the main entry point for the application.
    Returns:
        str: Rendered HTML template for the index page.
    """
    # Render the index.html template
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


# Route to get the positions of the balls on the table. This will be rewritten to use sockets soon
@app.route("/get-ball-positions")
def get_ball_positions():
    # Get the ball positions from the cv_module
    positions = cv_module.get_ball_positions()
    
    if positions:
        serializable_balls = []
        for ball in positions:
            regular_int_ball = (ball[0], ball[1], ball[2])  # Convert to int for JSON serialization
            serializable_balls.append(regular_int_ball)

    print(f"Positions: {positions}")
    if positions is None:
        return "Error getting ball positions", 500
    if not positions:
        return flask.jsonify({"message": "No balls detected"}), 200

    # Return the positions as a JSON response
    return flask.jsonify(serializable_balls), 200


# Route to get the live video stream from the camera
@app.route("/get-live-video")
def get_live_video():
    # Get the live video generator from the cv_module, and if it fails, return an error response
    video_generator = cv_module.get_live_video()
    if video_generator is None:
        return "Error starting live video stream", 500
    
    # Return the video stream as a multipart response (continuous stream of JPEG images)
    return flask.Response(video_generator, mimetype='multipart/x-mixed-replace; boundary=frame')


# Route to capture and save image of the table
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
    
##################################### ROUTES #####################################



if __name__ == "__main__":
    print("Flask server is running on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

