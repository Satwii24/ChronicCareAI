# ChronicCare AI – AI Agent for Chronic Disease Monitoring

## 🩺 Project Overview

**ChronicCare AI** is an AI-powered chronic disease monitoring system that continuously analyzes patient health-monitoring data, identifies concerning readings and trends, generates personalized health insights, and provides alerts for patients and healthcare providers.

The system uses **IBM watsonx.ai and IBM Granite 4-H Small** to generate easy-to-understand health summaries while a deterministic risk and trend engine performs the measurable monitoring logic.

> ⚠️ This project is a monitoring and decision-support prototype. It does not diagnose diseases, prescribe medicines, change medication doses, or replace healthcare professionals.

---

## 🎯 Problem Statement

Patients with chronic conditions such as diabetes, hypertension, and heart-related conditions require continuous monitoring.

However:

- Health readings may not be reviewed regularly.
- Abnormal patterns can be difficult to notice manually.
- Medication doses may be missed.
- Patients may not receive timely personalized guidance.
- Healthcare providers may lack a simple overview of patient trends.

ChronicCare AI aims to bridge the gap between continuous patient monitoring and timely patient-provider communication.

---

## 💡 Proposed Solution

ChronicCare AI provides an intelligent monitoring workflow that:

1. Accepts patient health-monitoring data.
2. Processes current health readings.
3. Calculates a monitoring risk score.
4. Detects changes and trends in historical readings.
5. Uses IBM Granite to generate a personalized explanation.
6. Displays results through a patient dashboard.
7. Provides a provider dashboard for monitoring patients.
8. Generates alerts when concerning patterns are detected.
9. Provides medication-adherence reminders and general lifestyle suggestions.

---

## 🏗️ System Architecture

```text
          Patient / Health Data
                   │
                   ▼
        ┌─────────────────────┐
        │   Data Processing   │
        │   Python + Pandas   │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Risk & Trend Engine │
        │  Risk Calculation   │
        │  Trend Detection    │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   IBM watsonx.ai    │
        │ Granite 4-H Small   │
        └──────────┬──────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ Personalized Insights │
       │   & Health Summary    │
       └───────────┬───────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
 ┌────────────────┐  ┌─────────────────┐
 │    Patient     │  │    Provider     │
 │   Dashboard    │  │    Dashboard    │
 └────────────────┘  └────────┬────────┘
                               │
                               ▼
                         Alerts / Actions
