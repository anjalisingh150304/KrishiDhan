let videoStream = null;
let captureInterval = null;

let videoDevices = [];
let currentCameraIndex = 0;

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const resultBox = document.getElementById("diseaseResult");
const resultText = document.getElementById("resultText");

/* ---------------- UI HELPERS ---------------- */

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function toggleTheme() {
    document.body.classList.toggle("dark");
    document.body.classList.toggle("light");
}

/* ---------------- CAMERA LOGIC ---------------- */

async function loadVideoDevices() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    videoDevices = devices.filter(d => d.kind === "videoinput");

    // Prefer back camera if available
    const backIndex = videoDevices.findIndex(d =>
        d.label.toLowerCase().includes("back") ||
        d.label.toLowerCase().includes("rear") ||
        d.label.toLowerCase().includes("environment")
    );

    if (backIndex !== -1) {
        currentCameraIndex = backIndex;
    }

    // Hide switch button if only one camera
    if (videoDevices.length < 2) {
        document.getElementById("switchCamBtn").style.display = "none";
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

        document.getElementById("startCamBtn").disabled = true;
        document.getElementById("stopCamBtn").disabled = false;

        video.onloadedmetadata = () => {
            video.play();
            startSendingFrames();
        };

    } catch (err) {
        alert("Camera access denied");
        console.error(err);
    }
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    clearInterval(captureInterval);

    document.getElementById("startCamBtn").disabled = false;
    document.getElementById("stopCamBtn").disabled = true;
}

function switchCamera() {
    if (videoDevices.length < 2) return;

    stopCamera();

    currentCameraIndex =
        (currentCameraIndex + 1) % videoDevices.length;

    startCamera();
}

/* ---------------- FRAME SENDER ---------------- */

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
            resultBox.classList.remove("hidden");
            resultText.textContent =
                `${data.status || "Analyzing"}`
        })
        .catch(() => {});
    }, 1500);
}
