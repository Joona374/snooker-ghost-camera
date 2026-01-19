const socket = io();

socket.emit("start-position-stream");

socket.on("ball-positions", (positions) => {
})