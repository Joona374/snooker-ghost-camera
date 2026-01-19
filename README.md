# Snooker Ghost Camera

A real-world "ghost camera" system for snooker, inspired by professional TV broadcasts. Built with a Raspberry Pi and wide-angle camera, this system helps players accurately reset balls after a "foul and a miss" call by overlaying a captured pre-shot image onto a live video feed.

**This is a student project, but it is currently deployed and in use at a local snooker hall in Finland.**
---

## Overview

We built this system during a summer school program (an unpaid internship format where the school acts as the employer). The goal was to create a practical tool that bridges software and physical hardware that solve a real customer need with a working product.

### The Problem

In snooker, when a player commits a foul and is called for a "miss," balls the balls may need to be reset to their previous positions. Without any visual reference, this becomes guesswork. Professional competitions solve this with expensive ghost camera systems that overlay previous ball positions.

### Our Solution
We created an affordable ghost camera system consisting of:

- A **Raspberry Pi** with a **wide-angle camera** mounted above the snooker table
- A website interface for players to interact with the system either on a screen provided next to the table or via their own mobile devices
- A **Flask web server** streaming live video to the web interface
- A simple **capture/overlay system** that allows capturing a frame before a shot, then overlaying it (with adjustable transparency and zoom) on the live feed
- Players can visually compare the overlay with the current table state and reset balls accurately

### Hardware Setup

- Raspberry Pi (running the Flask server)
- Wide-angle camera (to capture the full table)
- Monitor/display positioned next to the table for players to view

---

## Features

### Working Features

- **Live video streaming** via MJPEG stream from the camera
- **Pre-shot capture** — freeze the table state before a shot
- **Transparent overlay** — adjust overlay transparency in real-time to compare positions
- **Zoom and pan** — zoom into specific areas of the table for precise ball placement
- **Touch-friendly controls** — designed to work on a touchscreen display or mobile device
- **WebSocket infrastructure** — real-time communication between server and client

### Work in Progress (Potential for Further Development)

The codebase includes a partially implemented **ball tracking system** that could be extended:

- **Ball detection pipeline** (`detect_balls.py`, `ball_recognition_test.py`) — uses OpenCV's HoughCircles to detect ball positions and HSV color masking to identify ball colors
- **Real-time position streaming** — WebSocket handlers are in place to stream ball positions to the frontend
- **Color detection** — working logic to identify red, black, white, yellow, green, blue, and brown balls

The original vision included visual aids like arrows or "traffic light" indicators showing how close each ball is to its original position. The backend pipeline for this is largely functional, but the frontend visualization wasn't completed due to time constraints. This could be a good starting point for someone wanting to extend the project.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, Flask-SocketIO |
| Computer Vision | OpenCV (HoughCircles, HSV color detection, image processing) |
| Real-time Communication | Socket.IO with Eventlet |
| Frontend | Vanilla JavaScript, HTML5 Canvas |
| Hardware | Raspberry Pi, wide-angle camera |

### Key Libraries

```
opencv-python==4.11.0.86    # Image capture, ball detection, video streaming
Flask==3.1.1                # Web server and routing
Flask-SocketIO==5.5.1       # WebSocket support for real-time updates
eventlet==0.40.0            # Async support for concurrent video streaming
numpy==2.2.6                # Image array manipulation
```

---

## How It Works

### Image Overlay System

1. Player presses **Capture** before a shot => server grabs a frame from the camera
2. The captured frame is sent to the frontend and drawn on an HTML5 canvas
3. The canvas is layered over the live video stream with adjustable transparenc
4. Player adjusts transparency/zoom to compare and reset balls

### Ball Detection (Experimental)

1. Frames are converted to grayscale and preprocessed (blur, contrast adjustment)
2. `cv2.HoughCircles` detects circular objects (balls)
3. For each detected circle, the average color of the region is extracted
4. Color is matched against predefined HSV ranges to identify the ball type
5. Positions are serialized and can be streamed via WebSocket to the client

---

## Individual Contributions

This was a group project. My responsibilities included:

### Backend Development

- Designed and implemented the Flask server architecture (`flask_app.py`)
- Implemented WebSocket handlers for real-time ball position streaming both on the backend and frontend (`socket_handlers.py`, `static/js/socket.js`)

### Computer Vision (Supporting Role)

Collaborated with a teammate who led the CV development. My contributions included pair programming, debugging, and helping integrate the CV pipeline with the rest of the system:

- Camera module for image capture and MJPEG video streaming (`cv_module.py`)
- Ball detection logic using OpenCV's HoughCircles (`detect_balls.py`, `ball_recognition_test.py`)
- Utility functions for camera calibration and testing (`utils.py`)

### Technical Coordination & Communication

- Acted as the technical coordinator for the team
- Primary point of contact with the client (snooker hall) and school supervisors
- Helped integrate the frontend with the backend API
- Assisted teammates with debugging and troubleshooting, particularly on the frontend side

---

## Running the Project

### Requirements

- Python 3.x
- A camera (USB webcam or Raspberry Pi camera module)

### Installation

```bash
# Clone the repository
git clone https://github.com/Joona374/snooker-ghost-camera.git
cd snooker-ghost-camera

# Install dependencies
pip install -r requirements.txt

# Run the server
python flask_app.py
```

The server will start at `http://localhost:5000`. Open this URL in a browser to access the interface.

---

## Project Structure

```
├── flask_app.py          # Main Flask server with routes
├── cv_module.py          # Camera handling and video streaming
├── detect_balls.py       # Ball detection using HoughCircles
├── ball_recognition_test.py  # Experimental ball tracking tests
├── socket_handlers.py    # WebSocket event handlers
├── utils.py              # Helper functions for testing/calibration
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/style.css     # UI styling
│   ├── js/
│   │   ├── script.js     # Main frontend logic
│   │   ├── socket.js     # WebSocket client
│   │   └── mobileTouch.js
│   └── images/
└── templates/
    └── index.html        # Main UI template
```

---

## Acknowledgments

This project was developed as part of a summer school program. Thanks to my teammates who worked on the CV, frontend and UI design, and to the local snooker hall for letting us install and test the system on a real table.

---

## License

This project was created for educational purposes. Feel free to use it as a reference or starting point for similar projects.
