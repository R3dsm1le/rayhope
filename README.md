# RayHope — Energy Awareness & Behavioral Optimization System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Thesis](https://img.shields.io/badge/Status-Thesis%20Artifact-blueviolet)

</div>

<div align="center">
  <b>Smart IoT analytics for residential energy efficiency — validated across real Swedish data, synthetic stress-testing, and Panamanian residential projections.</b>
</div>

---

# Overview

**RayHope** is an intelligent energy awareness system developed as the primary artifact of a software development thesis at the **Technological University of Panama**. It analyzes residential IoT lighting data to identify behavioral patterns, classify users into energy-efficiency archetypes, and deliver personalized recommendations through a gamified interface.

The system is validated in **three rigorous phases**:

1. **Real IoT Data** — Integration with Home Assistant APIs using actual sensor data from Sweden.
2. **Synthetic Stress-Testing** — K-Means clustering validation against theoretically defined behavioral archetypes.
3. **Statistical Projection** — Calibration for the Panamanian residential electricity context (ASEP tariff).

---

# Key Features

| Feature | Description |
|---------|-------------|
| **IoT Data Ingestion** | Real-time fetching and parsing of Home Assistant light entity states via REST API. |
| **6-Dimensional Feature Vector** | Custom algorithms extract `transition_efficiency`, `energy_priority`, `predictability`, `optimization_score`, `total_activity`, and `variability`. |
| **Behavioral Clustering** | K-Means (`k=3`) classifies users into **Water Guardians**, **Conscious Users**, or **Green Opportunity** profiles. |
| **Personalized Recommendations** | Cluster-specific advice grounded in behavioral science, optimized for the Panamanian cultural context. |
| **Gamification Engine** | Points, savings calculations (kWh & USD), and leaderboards with injunctive norms to drive sustainable behavior change. |
| **Academic Validation Suite** | Five independent statistical tests: feature validity, cluster consistency, elbow analysis, noise tolerance, and ground-truth accuracy. |
| **Modern Web Dashboard** | React 19 + Vite + Tailwind CSS frontend with Recharts data visualization. |
| **GDPR Compliance** | Phase 2 synthetic pipeline intentionally avoids real API calls to ensure privacy during stress-testing. |

---

# Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND                                      │
│               React 19 · Vite · Tailwind CSS · Recharts                     │
│                                (Port 5173)                                  │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                │ REST API
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                BACKEND                                      │
│                            FastAPI (Python)                                 │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │     Phase 1      │  │     Phase 2      │  │   Gamification &          │  │
│  │    Real Data     │  │    Synthetic     │  │   Recommendation Engine   │  │
│  │    Pipeline      │  │    Pipeline      │  │                           │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────────┘  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │ HOW / WHEN /     │  │    K-Means       │  │   Validation Suite        │  │
│  │ WHAT / WHY       │  │   Clustering     │  │   (5 Academic Tests)      │  │
│  │ Algorithms       │  │     (k = 3)      │  │                           │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────────┐
                    │      Home Assistant API      │
                    │      (Real IoT Sensors)      │
                    └──────────────────────────────┘
```
