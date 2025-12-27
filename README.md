# 🚜 MITTIE: The Offline Smart Farming Assistant
> *Event:* Square Hacks 2025 (IIT Delhi)
> *Team:* KrishiDhan

---

## 📖 Project Overview
*MITTIE* is a hybrid agricultural assistant designed to bridge the gap between "Lab and Land." It empowers small-scale farmers in India with instant, data-driven insights without requiring internet connectivity.

### 🔴 The Problem
Indian farmers face two critical bottlenecks:
1.  *Delayed Soil Testing:* Lab reports take weeks, leading to blind fertilization and soil degradation.
2.  *Inaccessible Experts:* Diagnosing crop diseases requires experts who are often unreachable in remote villages.

### 🟢 The Solution
MITTIE provides a two-fold solution:
1.  *Offline Edge Device (Raspberry Pi):* A field-deployable unit that connects to industrial NPK sensors and runs Computer Vision models locally to provide instant soil analysis and disease remedies.
2.  *Public Web Platform:* A cloud-based interface for agricultural officers to analyze demo data and manage crop records from any device.

---

## ⚙️ How It Works (Hybrid Architecture)

### 1. The Offline Edge (For the Farmer)
* *Hardware:* Raspberry Pi 5 + NPK Soil Sensor (RS485) + Pi Camera.
* *Function:* Reads soil nutrients (Nitrogen, Phosphorus, Potassium) directly from the ground and detects plant diseases using an onboard camera.
* *AI Models:* Runs quantized *TensorFlow Lite* (MobileNetV2) and *Random Forest* models entirely on the device.
* *Output:* Displays results and chemical/organic remedies in local languages (*English, Hindi, Bengali*).

### 2. The Public Web Interface (For Accessibility)
* *Function:* Allows users without hardware to input soil parameters manually and receive crop recommendations.
* *Live Demo:* https://mitti-two.vercel.app/

---

## 🛠️ Tech Stack

### Hardware
* *Compute:* Raspberry Pi 5 (8GB)
* *Sensors:* Industrial NPK Soil Sensor (Modbus RS485)
* *Vision:* Raspberry Pi Camera Module 3
* *Connectivity:* USB-to-RS485 Serial Adapter

### Software & AI
* *Language:* Python 3.11
* *Edge AI:* TensorFlow Lite, OpenCV
* *ML Algorithms:* Random Forest Classifier (Scikit-Learn)
* *IoT Protocols:* Modbus RTU (Serial Communication)
* *Web Framework:* [Streamlit / Flask]

---

## 🚀 Setup & Installation

### Prerequisites
* Raspberry Pi running Raspberry Pi OS (64-bit).
* Python 3.9+ installed.
