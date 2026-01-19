const captureButton = document.getElementById("capture-button");
const resetButton = document.getElementById("reset-button");
const liveVideoImage = document.getElementById("live-video-img");
const overlayImage = document.getElementById("overlay-image");
const canvas = document.getElementById("canvas");
canvas.style.opacity = "1";
const zoomContainer = document.getElementById("zoom-container");

canvas.width = 800;
canvas.height = 600;
const ctx = canvas.getContext("2d");

let latestPreshotPositions = null;
let livePositions = null;

// Get sliders
const transparencySlider = document.getElementById("transparency-slider");
const zoomSlider = document.getElementById("zoom-slider");

// Initialize values
let transparency = parseFloat(transparencySlider.value);
let zoom = parseFloat(zoomSlider.value);
let lastCapturedImage = null; // store last image for live updates

// Event listeners for sliders
transparencySlider.addEventListener("input", () => {
    transparency = parseFloat(transparencySlider.value);
    console.log("Transparency set to:", transparency);
    drawImageOnCanvas(); // Re-draw with updated transparency
});

zoomSlider.addEventListener("input", () => {
    zoom = parseFloat(zoomSlider.value);
    zoomContainer.style.transform = `scale(${zoom})`;
    zoomContainer.style.transformOrigin = "top left";
});

// Draw image on canvas with current transparency
function drawImageOnCanvas() {
    if (!lastCapturedImage) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const drawWidth = canvas.width;
    const drawHeight = canvas.height;
    const offsetX = 0;
    const offsetY = 0;

    ctx.globalAlpha = transparency;
    ctx.drawImage(lastCapturedImage, offsetX, offsetY, drawWidth, drawHeight);
    ctx.globalAlpha = 1.0;
}

// Update overlay and draw on canvas
async function updateCapturedImage() {
    try {
        const imageUrl = await getImageUrl();
        if (!imageUrl) return;

        overlayImage.src = imageUrl;
        lastCapturedImage = new Image();
        lastCapturedImage.onload = () => drawImageOnCanvas();
        lastCapturedImage.src = imageUrl;

        console.log("Image updated successfully");
    } catch (error) {
        console.error("Error fetching image:", error);
    }
}

// Fetch image from backend
async function getImageUrl() {
    try {
        console.log("Fetching image from server");
        // Fetch the image from the backend
        const response = await fetch("/get-image");

        // If the response is not ok, throw an error
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Convert the response to a Blob (binary large object) and create a temporary URL for it
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        if (overlayImage.src.startsWith('blob:')) {
            URL.revokeObjectURL(overlayImage.src);
        }

        return imageUrl;
    } catch (error) {
        console.error("Error fetching image:", error);
    }
}

async function getBallPositions() {
    try {
        console.log("Fetching ball positions from server");
        const response = await fetch("/get-ball-positions");

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Ball positions:", data);
        return data;
    } catch (error) {
        console.error("Error fetching ball positions:", error);
    }
}

// This function should be called to get the live video feed from the backend
function getLiveVideo() {
    console.log("Get live-video from backend and show it");
}

// Add an event listener to the capture button to fetch the image when clicked
captureButton.addEventListener("click", () => {
    console.log("Capture button clicked: getting image from server");
    updateCapturedImage();
    latestPreshotPositions = getBallPositions();
});


// POST to capture and save image on server
async function captureAndSaveTableImage() {
    try {
        console.log("Sending request to capture and save table image");
        const response = await fetch("/capture-table", { method: 'POST' });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log(result.message);
    } catch (error) {
        console.error("Error capturing and saving table image:", error);
    }
}

// CTRL+B triggers image capture from backend
document.addEventListener('keydown', async (event) => {
    if (event.ctrlKey && (event.key === 'b' || event.key === 'B')) {
        event.preventDefault();
        console.log('CTRL+B pressed');
        await captureAndSaveTableImage();
    }
});

// Reset everything
resetButton.addEventListener("click", () => {
    console.log("Reset button clicked");

    overlayImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    lastCapturedImage = null;

    // Reset sliders to default
    transparencySlider.value = "0.5";
    zoomSlider.value = "1";
    transparency = 0.5;
    zoom = 1;
    zoomContainer.style.transform = "scale(1)";

    console.log("Overlay image and canvas cleared");
});

function fetchLivePositions() {
    fetch("/get-ball-positions")
        .then(response => response.json())
        .then(data => {
            livePositions = data.body;
        })
        .catch(error => {
            console.error("Error fetching live positions:", error);
        });
}

// "Call the function to get the live video feed when the page loads"
// getLiveVideo(); isnt actually implemented yet, but this is how you would call it
getLiveVideo();
setInterval(() => {
    console.log("Fetching live positions");
    fetchLivePositions();
    console.log("Live positions fetched:", livePositions);
}, 2000); // Fetch live positions every second