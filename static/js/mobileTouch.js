(function () {
  const zoomWrapper = document.getElementById("zoom-wrapper");
  const zoomSlider = document.getElementById("zoom-slider");
  const captureButton = document.getElementById("capture-button");
  const resetButton = document.getElementById("reset-button");
  const helpIcon = document.getElementById("help-icon");

  // Mobile UI buttons
  const mCapture = document.getElementById("m-capture");
  const mReset = document.getElementById("m-reset");
  const mHelp = document.getElementById("m-help");

  // Wire mobile buttons to existing controls (fallback to click events)
  if (mCapture)
    mCapture.addEventListener("click", () =>
      (captureButton || mCapture).click()
    );
  if (mReset)
    mReset.addEventListener("click", () => (resetButton || mReset).click());
  if (mHelp) mHelp.addEventListener("click", () => (helpIcon || mHelp).click());
  // Note: zoom in/out buttons removed for mobile — pinch-to-zoom is used instead

  // Touch gesture state
  let lastTouch = 0;
  let touchStartTime = 0;
  let longPressTimer = null;

  // Double-tap detection for reset
  zoomWrapper.addEventListener(
    "touchend",
    (ev) => {
      const now = Date.now();
      if (now - lastTouch < 300) {
        // double-tap -> reset
        if (resetButton) resetButton.click();
      }
      lastTouch = now;
    },
    { passive: true }
  );

  // Long-press to capture (500ms)
  zoomWrapper.addEventListener(
    "touchstart",
    (ev) => {
      touchStartTime = Date.now();
      if (ev.touches.length === 1) {
        longPressTimer = setTimeout(() => {
          if (captureButton) captureButton.click();
        }, 500);
      }
      // pinch start handled below
    },
    { passive: true }
  );

  zoomWrapper.addEventListener(
    "touchmove",
    (ev) => {
      // if the finger moves we cancel long-press
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        longPressTimer = null;
      }
    },
    { passive: true }
  );

  zoomWrapper.addEventListener("touchcancel", () => {
    if (longPressTimer) clearTimeout(longPressTimer);
  });

  // Pinch to zoom
  let pinchStartDist = 0;
  let pinchStartZoom = 1;
  function distanceBetween(t1, t2) {
    const dx = t2.clientX - t1.clientX;
    const dy = t2.clientY - t1.clientY;
    return Math.hypot(dx, dy);
  }

  zoomWrapper.addEventListener(
    "touchstart",
    (e) => {
      if (e.touches.length === 2) {
        pinchStartDist = distanceBetween(e.touches[0], e.touches[1]);
        pinchStartZoom = zoomSlider ? parseFloat(zoomSlider.value) : 1;
        if (longPressTimer) {
          clearTimeout(longPressTimer);
          longPressTimer = null;
        }
      }
    },
    { passive: true }
  );

  zoomWrapper.addEventListener(
    "touchmove",
    (e) => {
      if (e.touches.length === 2 && pinchStartDist > 0) {
        const d = distanceBetween(e.touches[0], e.touches[1]);
        const scale = d / pinchStartDist;
        const newZoom = Math.min(
          parseFloat(zoomSlider.max),
          Math.max(parseFloat(zoomSlider.min), pinchStartZoom * scale)
        );
        if (zoomSlider) {
          zoomSlider.value = newZoom;
          zoomSlider.dispatchEvent(new Event("input"));
        }
      }
    },
    { passive: true }
  );

  zoomWrapper.addEventListener("touchend", (e) => {
    if (e.touches.length < 2) {
      pinchStartDist = 0;
    }
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
  });

  // Single-finger pan: reuse existing pointer drag logic if present, otherwise implement simple translate
  let isPanning = false;
  let panStart = { x: 0, y: 0 };
  let wrapperPos = { x: 0, y: 0 };

  // try to use pointer events for pan (works for stylus/mouse/touch)
  zoomWrapper.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "touch") {
      isPanning = true;
      zoomWrapper.setPointerCapture(e.pointerId);
      panStart = { x: e.clientX, y: e.clientY };
    }
  });

  zoomWrapper.addEventListener("pointermove", (e) => {
    if (!isPanning) return;
    const dx = e.clientX - panStart.x;
    const dy = e.clientY - panStart.y;
    panStart = { x: e.clientX, y: e.clientY };
    wrapperPos.x += dx;
    wrapperPos.y += dy;
    zoomWrapper.style.transform = `translate(${wrapperPos.x}px, ${
      wrapperPos.y
    }px) scale(${zoomSlider ? zoomSlider.value : 1})`;
  });

  zoomWrapper.addEventListener("pointerup", (e) => {
    if (isPanning) {
      isPanning = false;
      try {
        zoomWrapper.releasePointerCapture(e.pointerId);
      } catch (_) {}
    }
  });
})();
