from flask_socketio import SocketIO
import eventlet
import random # JUST FOR TESTING
import cv_module

streaming_started = False

def register_socket_events(socketio: SocketIO):

    @socketio.on('connect')
    def handle_connect():
        print("Client connected")

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on("start-position-stream")
    def handle_start_position_stream():
        print("Start position stream event received")
        global streaming_started
        if streaming_started:
            print("Position stream already started")
            return
        
        print("Start mock stream")
        streaming_started = True

        def streaming_loop():
            while True:
                # Send actual balls from camera
                ball_positions = cv_module.get_ball_positions()
                if ball_positions:
                    serializable_balls = []
                    for ball in ball_positions:
                        regular_int_ball = (int(ball[0]), int(ball[1]), ball[2])  # Convert to int for JSON serialization
                        serializable_balls.append(regular_int_ball)

                    socketio.emit("ball-positions", serializable_balls)
                eventlet.sleep(0.05)

        eventlet.spawn(streaming_loop)
