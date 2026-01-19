const captureButton = document.getElementById("capture-button");
const resetButton = document.getElementById("reset-button");
const helpButton = document.getElementById("help-icon");
const helpPopup = document.getElementById("help-popup");
const liveVideoImage = document.getElementById("live-video-img");
const overlayImage = document.getElementById("overlay-image");
const canvas = document.getElementById("canvas");
canvas.style.opacity = "1";
const zoomContainer = document.getElementById("zoom-container");
const zoomWrapper = document.getElementById("zoom-wrapper");


let isDragging = false;
let dragStart = { x: 0, y: 0 };
let dragStop = { x: 0, y: 0 };
let currentTranslate = { x: 0, y: 0 };

canvas.addEventListener("mousedown", (e) => {
  isDragging = true;
  dragStart = {
    x: e.clientX,
    y: e.clientY,
  };
  canvas.style.cursor = "grabbing";
});

canvas.addEventListener("mousemove", (e) => {
  if (!isDragging) return;

  e.preventDefault();
  const dx = e.clientX - dragStart.x;
  const dy = e.clientY - dragStart.y;

  let wrapperRect = zoomWrapper.getBoundingClientRect();
  let containerRect = zoomContainer.getBoundingClientRect();

  if (dx > 0) {
    // Left boundry check
    if (wrapperRect.left + dx >= 0) {
      currentTranslate.x = wrapperRect.width / 2 - containerRect.width / 2;
    } else {
      currentTranslate.x += dx;
    }
  } else if (dx < 0) {
    // Right boundry check
    if (wrapperRect.right + dx <= containerRect.width) {
      currentTranslate.x = -(wrapperRect.width / 2 - containerRect.width / 2);
    } else {
      currentTranslate.x += dx;
    }
  }

  if (dy > 0) {
    // Top boundary check
    if (wrapperRect.top + dy >= 0) {
      currentTranslate.y = wrapperRect.height / 2 - containerRect.height / 2;
    } else {
      currentTranslate.y += dy;
    }
  } else if (dy < 0) {
    // Bottom boundary check
    if (wrapperRect.bottom + dy <= containerRect.height) {
      currentTranslate.y = -(wrapperRect.height / 2 - containerRect.height / 2);
    } else {
      currentTranslate.y += dy;
    }
  }

  zoomWrapper.style.transform = `scale(${zoom}) translate(${currentTranslate.x / zoom}px, ${currentTranslate.y / zoom}px)`;
  dragStart = { x: e.clientX, y: e.clientY };
  const transform = window.getComputedStyle(zoomWrapper).transform;
  const values = transform.match(/matrix.*\((.+)\)/)[1].split(", ");
  const translateX = parseFloat(values[4]);
  const translateY = parseFloat(values[5]);
});

canvas.addEventListener("mouseup", (e) => {
  if (isDragging) {
    isDragging = false;
    canvas.style.cursor = "grab";
    const zoomWrapperRect = zoomWrapper.getBoundingClientRect();
  }
});

// Handle mouse leave to stop dragging if mouse leaves canvas
canvas.addEventListener("mouseleave", () => {
  if (isDragging) {
    isDragging = false;
    canvas.style.cursor = "grab";
  }
});

// Set canvas to match the zoom wrapper size dynamically
function updateCanvasSize() {
  const rect = zoomWrapper.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
}

// Initial canvas size setup
updateCanvasSize();
window.addEventListener("resize", updateCanvasSize);

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
  drawImageOnCanvas(); // Re-draw with updated transparency
});

zoomSlider.addEventListener("input", () => {
    zoom = parseFloat(zoomSlider.value);
    zoomWrapper.style.transform = `scale(${zoom}) translate(${currentTranslate.x / zoom}px, ${currentTranslate.y / zoom}px)`;

    const transform = window.getComputedStyle(zoomWrapper).transform;
    let zoomWrapperRect = zoomWrapper.getBoundingClientRect();
    let containerRect = zoomContainer.getBoundingClientRect();

    if (zoomWrapperRect.left > 0) {
      currentTranslate.x = zoomWrapperRect.width / 2 - containerRect.width / 2;
    }

    if (zoomWrapperRect.right < containerRect.width) {
      currentTranslate.x = -(
        zoomWrapperRect.width / 2 -
        containerRect.width / 2
      );
    }
    if (zoomWrapperRect.top > 0) {
      currentTranslate.y =
        zoomWrapperRect.height / 2 - containerRect.height / 2;
    }
    if (zoomWrapperRect.bottom < containerRect.height) {
      currentTranslate.y = -(
        zoomWrapperRect.height / 2 -
        containerRect.height / 2
      );
    }
    zoomWrapper.style.transform = `scale(${zoom}) translate(${currentTranslate.x / zoom}px, ${currentTranslate.y / zoom}px)`;

});

helpButton.addEventListener("click", () => {
  if (helpPopup.style.display === "none") {
    helpPopup.style.display = "block";
  } else {
    helpPopup.style.display = "none";
  }
});

// Draw image on canvas with current transparency
function drawImageOnCanvas() {
  if (!lastCapturedImage) return;

  // Update canvas size in case window was resized
  updateCanvasSize();

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const imgWidth = lastCapturedImage.naturalWidth;
  const imgHeight = lastCapturedImage.naturalHeight;
  const canvasWidth = canvas.width;
  const canvasHeight = canvas.height;

  // Calculate scale to cover the canvas (same as CSS object-fit: cover)
  const scale = Math.max(canvasWidth / imgWidth, canvasHeight / imgHeight);

  const scaledWidth = imgWidth * scale;
  const scaledHeight = imgHeight * scale;

  // Center the image (crop equally from both sides)
  const offsetX = (canvasWidth - scaledWidth) / 2;
  const offsetY = (canvasHeight - scaledHeight) / 2;

  ctx.globalAlpha = transparency;
  ctx.drawImage(lastCapturedImage, offsetX, offsetY, scaledWidth, scaledHeight);
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
    } catch (error) {}
}

// Fetch image from backend
async function getImageUrl() {
    try {
      // Fetch the image from the backend
      const response = await fetch("/get-image");

      // If the response is not ok, throw an error
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Convert the response to a Blob (binary large object) and create a temporary URL for it
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);

      if (overlayImage.src.startsWith("blob:")) {
        URL.revokeObjectURL(overlayImage.src);
      }

      return imageUrl;
    } catch (error) {}
}

async function getBallPositions() {
    try {
      const response = await fetch("/get-ball-positions");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {}
}

// This function should be called to get the live video feed from the backend
function getLiveVideo() {}

// Add an event listener to the capture button to fetch the image when clicked
captureButton.addEventListener("click", () => {
  updateCapturedImage();
  latestPreshotPositions = getBallPositions();
});


// POST to capture and save image on server
async function captureAndSaveTableImage() {
    try {
      const response = await fetch("/capture-table", { method: "POST" });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
    } catch (error) {}
}

// CTRL+B triggers image capture from backend
document.addEventListener('keydown', async (event) => {
    if (event.ctrlKey && (event.key === 'b' || event.key === 'B')) {
        event.preventDefault();
        await captureAndSaveTableImage();
    }
});

// Reset everything
resetButton.addEventListener("click", () => {
  overlayImage.src =
    "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  updateCanvasSize(); // Update canvas size before clearing
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  lastCapturedImage = null;

  // Reset sliders to default
  transparencySlider.value = "0.5";
  zoomSlider.value = "1";
  transparency = 0.5;
  zoom = 1;
  currentTranslate = { x: 0, y: 0 };

  // Reset zoom
  currentTranslate = { x: 0, y: 0 };
  zoomWrapper.style.transform = "scale(1) translate(0px, 0px)";
});


function fetchLivePositions() {
    fetch("/get-ball-positions")
      .then((response) => response.json())
      .then((data) => {
        livePositions = data.body;
      })
      .catch((error) => {});
}

// "Call the function to get the live video feed when the page loads"
// getLiveVideo(); isnt actually implemented yet, but this is how you would call it
getLiveVideo();


// ############ NOT USED ANYMORE ############
// setInterval(() => {
//     console.log("Fetching live positions");
//     fetchLivePositions();
//     console.log("Live positions fetched:", livePositions);
// }, 2000); // Fetch live positions every second
// ############ NOT USED ANYMORE ############