# Mine Rescue & Safety Monitoring System (MRSMS)
### Interactive Python Streamlit Subsurface Control & 3D Visualization Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58%2B-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-3D-cyan.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/Standard-MSHA%20%2F%20OSHA%20Title%2030-emerald.svg)](https://www.msha.gov/)

A mission-critical underground mine safety monitoring application designed for surface rescue command centers. Built using **Streamlit** and **Plotly 3D** for intuitive and robust visualization, tailored for Python developers and industrial operations.

---

## 🌟 Key Features

1. **🏔️ 3D Cave Disaster Management (Default Landing):**
   - Interactive 3D spatial perspective of underground mine tunnel drifts.
   - Gas rupture source mapping and multi-layered dynamic gas diffusion cloud.
   - Real-time gas escape vectors (Cyan) and positive-pressure ventilation paths (Green).
   - Live rescue team coordinates (Alpha, Bravo, Charlie) and sensor node health.

2. **📊 Predictive Gas Analytics & 10-Minute Projections:**
   - Interactive forward accumulation curves for **Methane (CH₄)**, **Carbon Monoxide (CO)**, **Sulphur Dioxide (SO₂)**, **Carbon Dioxide (CO₂)**, and **Oxygen (O₂)**.
   - Solid traces for real-time readings vs. dashed projected curves.
   - Accumulation rate velocity ($\Delta C / \Delta t$) and time-to-critical countdown timer.

3. **🧪 Multi-Gas Environmental Sensing Grid:**
   - Metric cards calibrated to MSHA & OSHA Title 30 regulatory safety limits.
   - Composite Tunnel Safety Index score ($0 - 100$) with dynamic penalty calculations.

4. **🚨 Automated High-Pitch Ambulance Siren (Audio Alarm):**
   - Automatically generates a procedural $650\text{ Hz} \leftrightarrow 1050\text{ Hz}$ wailing siren via Web Audio API whenever dangerous gas ceilings are crossed ($\text{CH}_4 \ge 10{,}000\text{ ppm}$ or $\text{CO} \ge 100\text{ ppm}$).
   - Includes one-click audio mute controls in the sidebar.

5. **📍 Subsurface Incident Protocol & Fracture Locations:**
   - Pinpoints exact underground drift locations (Sector 4 Sub-level B, Elevation $-420\text{ m}$).
   - Real-time incident alert log table with one-click **CSV Export**.

6. **⚙️ Real-time Hazard Simulator:**
   - Multi-scenario generator: `NORMAL`, `METHANE_SURGE`, `FIRE_OUTBREAK`, `CAVE_IN`.
   - Stochastic Brownian motion telemetry streaming.

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/nirmal-mugunth/MRSMS.git
cd MRSMS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit Dashboard
```bash
streamlit run MRSMS.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 📁 Project Architecture

```
MRSMS/
├── MRSMS.py               # Main Streamlit Dashboard Application
├── prediction_engine.py   # MSHA/OSHA Safety Calculations & 10m Forecast Logic
├── simulator.py           # Brownian Motion Telemetry & Hazard Scenario Engine
├── requirements.txt       # Python package dependencies
└── README.md              # Project documentation
```

---

## 🛡️ Regulatory Calibration Standards

| Gas / Parameter | Caution Threshold | Critical Evacuation Threshold |
| :--- | :--- | :--- |
| **Methane ($\text{CH}_4$)** | $5{,}000\text{ ppm}$ ($10\%\text{ LEL}$) | $10{,}000\text{ ppm}$ ($20\%\text{ LEL}$) |
| **Carbon Monoxide ($\text{CO}$)** | $35\text{ ppm}$ (8-hr TWA) | $100\text{ ppm}$ (Lethal Ceiling) |
| **Sulphur Dioxide ($\text{SO}_2$)** | $5\text{ ppm}$ | $20\text{ ppm}$ (IDLH Threshold) |
| **Carbon Dioxide ($\text{CO}_2$)** | $2{,}500\text{ ppm}$ | $5{,}000\text{ ppm}$ |
| **Oxygen ($\text{O}_2$)** | $< 19.5\%$ (Deficiency) | $\le 16.0\%$ (Asphyxiation) |
| **Roof Clearance** | $< 180\text{ cm}$ (Convergence) | $< 100\text{ cm}$ (Impending Cave-in) |

---

### Author
**nirmal-mugunth**
Developed for Mine Rescue & Surface Control Station Telemetry Operations.
