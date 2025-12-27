let videoStream = null;
let captureInterval = null;

let videoDevices = [];
let currentCameraIndex = 0;

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const diseaseStatus = document.getElementById("diseaseStatus");
const cameraStatus = document.getElementById("cameraStatus");

/* ================== FULL CHECK FLOW ================== */

function startFullCheck() {
    const btn = document.getElementById("startFullCheckBtn");
    const loader = document.getElementById("fullLoader");
    const loaderText = document.getElementById("loaderText");
    const result = document.getElementById("fullResult");
    const cropTable = document.getElementById("fullCropTable");

    btn.disabled = true;
    loader.classList.remove("hidden");
    result.classList.add("hidden");
    cropTable.innerHTML = "";

    loaderText.textContent = "Reading soil sensors & recommending crops…";

    fetch("/api/recommend-crops", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Language": getLanguage()
        }
    })
    .then(res => res.json())
    .then(data => {
        data.recommendations.forEach(crop => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${capitalize(crop.crop)}</td>
                <td>${scoreToLabel(crop.confidence)}</td>
            `;
            row.style.cursor = "pointer";
            row.onclick = () => showFullCropDetails(crop.crop);
            cropTable.appendChild(row);
        });

        result.classList.remove("hidden");

        loaderText.textContent = "Starting camera for disease detection…";
        startCamera();

        loader.classList.add("hidden");
        btn.disabled = false;
    })
    .catch(err => {
        console.error(err);
        alert("Full check failed");
        loader.classList.add("hidden");
        btn.disabled = false;
    });
}

/* ================== CAMERA HANDLING ================== */

async function loadVideoDevices() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    videoDevices = devices.filter(d => d.kind === "videoinput");

    // Prefer back camera
    const backIndex = videoDevices.findIndex(d =>
        d.label.toLowerCase().includes("back") ||
        d.label.toLowerCase().includes("rear") ||
        d.label.toLowerCase().includes("environment")
    );

    if (backIndex !== -1) {
        currentCameraIndex = backIndex;
    }

    if (videoDevices.length > 1) {
        document.getElementById("switchCamBtn").style.display = "inline-flex";
    }
}

async function startCamera() {
    try {
        if (videoDevices.length === 0) {
            await loadVideoDevices();
        }

        const deviceId = videoDevices[currentCameraIndex]?.deviceId;

        videoStream = await navigator.mediaDevices.getUserMedia({
            video: deviceId
                ? { deviceId: { exact: deviceId } }
                : { facingMode: "environment" }
        });

        video.srcObject = videoStream;
        cameraStatus.textContent = "📡 Camera active — scanning leaf…";

        video.onloadedmetadata = () => {
            video.play();
            startSendingFrames();
        };

    } catch (err) {
        console.error(err);
        cameraStatus.textContent = "Camera access denied";
    }
}

function switchCamera() {
    if (videoDevices.length < 2) return;

    stopCamera();
    currentCameraIndex = (currentCameraIndex + 1) % videoDevices.length;
    startCamera();
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(t => t.stop());
        videoStream = null;
    }
    clearInterval(captureInterval);
}

/* ================== FRAME SENDER ================== */

function startSendingFrames() {
    const ctx = canvas.getContext("2d");

    captureInterval = setInterval(() => {
        if (!video.videoWidth) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        const imageData = canvas.toDataURL("image/jpeg");

        fetch("/api/detect-disease", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ frame: imageData })
        })
        .then(res => res.json())
        .then(data => {
            diseaseStatus.textContent =
                `${data.status} || ${data.label || ""} || ${Math.round((data.confidence || 0) * 100)}%`;
        })
        .catch(() => {});
    }, 1500);
}

/* ================== CROP DETAILS ================== */

function showFullCropDetails(cropName) {
    const box = document.getElementById("fullCropDetails");
    const title = document.getElementById("fullDetailTitle");
    const list = document.getElementById("fullDetailList");

    title.textContent = `🌾 ${capitalize(cropName)} – Soil & Fertilizer Advice`;
    list.innerHTML = "";

    fetch("/api/fertilizer-advice", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Language": getLanguage()
        },
        body: JSON.stringify({ crop: cropName })
    })
    .then(res => res.json())
    .then(data => {
        data.fertilizer_advice.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            list.appendChild(li);
        });

        box.classList.remove("hidden");
        box.scrollIntoView({ behavior: "smooth" });
    })
    .catch(err => {
        console.error(err);
        alert("Failed to load crop details");
    });
}

/* ================== UTILITIES ================== */

function capitalize(t) {
    return t.charAt(0).toUpperCase() + t.slice(1);
}

function scoreToLabel(s) {
    if (s >= 0.7) return "High";
    if (s >= 0.5) return "Medium";
    return "Low";
}

function getLanguage() {
    return localStorage.getItem("lang") || "en";
}
