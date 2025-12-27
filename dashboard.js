function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

function toggleTheme() {
    const body = document.body;
    const icon = document.querySelector(".theme-toggle i");

    if (body.classList.contains("dark")) {
        body.classList.replace("dark", "light");
        icon.className = "fa-solid fa-moon";
        localStorage.setItem("theme", "light");
    } else {
        body.classList.replace("light", "dark");
        icon.className = "fa-solid fa-sun";
        localStorage.setItem("theme", "dark");
    }
}

// Load saved theme
window.onload = () => {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.body.classList.add(savedTheme);

    const icon = document.querySelector(".theme-toggle i");
    icon.className = savedTheme === "dark"
        ? "fa-solid fa-sun"
        : "fa-solid fa-moon";
};



function checkSoil() {
    const btn = document.getElementById("checkSoilBtn");
    const loader = document.getElementById("loader");
    const result = document.getElementById("resultArea");
    const tableBody = document.getElementById("cropTableBody");
    const detailsBox = document.getElementById("cropDetails");

    btn.disabled = true;
    loader.classList.remove("hidden");
    result.classList.add("hidden");
    detailsBox.classList.add("hidden");
    tableBody.innerHTML = "";

    // Example soil data (replace with Pi sensor later)
    const soilData = {
        N: 40,
        P: 30,
        K: 25,
        temperature: 25,
        humidity: 55,
        ph: 6.5,
        rainfall: 100
    };

    fetch("/api/recommend-crops", {
        method: "POST",
         headers: {
            "Content-Type": "application/json",
            "X-Language":getLanguage()
            },
        body: JSON.stringify(soilData)
    })
    .then(res => res.json())
    .then(data => {

        const soil = data.soil;

    document.getElementById("soilN").textContent =
        soil.nitrogen_mgkg ?? soil.N ?? "--";

    document.getElementById("soilP").textContent =
        soil.phosphorus_mgkg ?? soil.P ?? "--";

    document.getElementById("soilK").textContent =
        soil.potassium_mgkg ?? soil.K ?? "--";

    document.getElementById("soilPH").textContent =
        soil.ph ?? "--";

    document.getElementById("soilTemp").textContent =
        soil.temperature_c ?? soil.temperature ?? "--";

    document.getElementById("soilMoisture").textContent =
        soil.moisture_pct ?? soil.humidity ?? "--";

        
        const crops = data.recommendations || [];

        crops.forEach(crop => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${capitalize(crop.crop)}</td>
                <td>Suitable</td>
                <td>Seasonal</td>
                <td>${scoreToLabel(crop.confidence)}</td>
            `;

            // 👉 CLICK TO SHOW DETAILS
            row.onclick = () => {
                console.log("row clicked")
                showCropDetails(crop.crop)
            }

            tableBody.appendChild(row);
        });

        loader.classList.add("hidden");
        result.classList.remove("hidden");
        btn.disabled = false;
    })
    .catch(err => {
        console.error(err);
        alert("Failed to analyze soil data");
        loader.classList.add("hidden");
        btn.disabled = false;
    });
}

function showCropDetails(cropName) {
    fetch("/api/fertilizer-advice", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Language":getLanguage()
            },
        body: JSON.stringify({ crop: cropName })
    })
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("detailList");
        const box = document.getElementById("cropDetails");

        list.innerHTML = "";
        data.fertilizer_advice.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            list.appendChild(li);
        });

        box.classList.remove("hidden");
        box.scrollIntoView({ behavior: "smooth" });
    });
}


function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function scoreToLabel(score) {
    if (score >= 0.7) return "High";
    if (score >= 0.5) return "Medium";
    return "Low";
}

function changeLanguage() {
    const lang = document.getElementById("languageSelect").value;
    localStorage.setItem("lang", lang);
   
    refreshCurrentView();
}

function refreshCurrentView() {
    const path = window.location.pathname;

    if (path.includes("/recommend/crop")) {
        checkSoil(); 
    } 
    else if (path.includes("/full/check")) {
        startFullCheck(); // re-run full check
    } 
    else if (path.includes("/detect/disease")) {
        // No reload needed; disease updates are live
        console.log("Language updated for disease view");
    }
}


function getLanguage() {
    console.log(localStorage.getItem("lang"))
    return localStorage.getItem("lang") || "en";
}
