# Explainable Health Risk Assessment Project

A mini-project for CSE students that predicts **Low / Moderate / High** health risk using:
- Diet Score
- Sleep Hours
- Physical Activity Level
- BMI
- Engineered Health Risk Score (HRS)

## Features
- Synthetic dataset generation (1000 records)
- HRS feature engineering
- Logistic Regression and Random Forest models
- Accuracy, Precision, Recall, F1-score, Confusion Matrix
- Random Forest feature importance
- BMI category interpretation
- User-specific recommendations
- **Diet Score Calculator** from food habits
- **BMI Auto Calculator** from height and weight
- **Daily Calorie Requirement Estimator**
- **Health alerts** for BMI, sleep, blood pressure, blood sugar, smoking, stress, and screen time
- **User history tracking** with saved predictions and trend charts
- **What-If Risk Simulation** for improvement analysis
- **PDF + Text report generation**
- **English + Hindi multilingual interface** with Hindi health guidance
- **Persistent language preference** for authenticated backend users
- **Check It and Eat It**: upload a food image, estimate approximate calories, and get an eat / avoid suggestion
- **Period Cycle Detection Phase**: estimate approximate menstrual, follicular, ovulation, and luteal phase dates with body-change guidance
- Streamlit dashboard

## Additional Contextual Inputs Added
These inputs are now captured for richer guidance and reporting:
- Age
- Gender
- Blood Pressure (Systolic / Diastolic)
- Blood Sugar
- Smoking Habit
- Screen Time
- Stress Level
- Height and Weight

> Note: The core ML model still predicts risk using Diet Score, Sleep Hours, Physical Activity Level, BMI, and HRS. The extra parameters improve alerts, recommendations, history analysis, and reports.

## Project Structure
```text
health_risk_project/
│-- app.py
│-- train.py
│-- requirements.txt
│-- README.md
│-- PRESENTATION_VIVA_GUIDE.md
│-- data/
│-- models/
│-- reports/
│-- src/
    │-- __init__.py
    │-- alerts.py
    │-- data_generation.py
    │-- features.py
    │-- food_calorie_db.py
    │-- food_checker.py
    │-- history.py
    │-- modeling.py
    │-- pdf_reporting.py
    │-- period_cycle.py
    │-- recommendations.py
    │-- reporting.py
    │-- translations.py
    │-- utils.py
    │-- wellness_tools.py
```

## Installation
Open terminal inside `health_risk_project` and run:

```bash
python -m pip install -r requirements.txt
```

## Step 1: Train the Models
```bash
python train.py
```
This will:
- generate the dataset
- train Logistic Regression and Random Forest
- save the trained model bundle in `models/`

## Step 2: Run the Dashboard
```bash
streamlit run app.py
```

## How to Use the App
1. Select a language from the sidebar.
2. Select a prediction model from the sidebar.
3. Choose whether to:
   - manually enter Diet Score, or
   - calculate Diet Score from food habits.
4. Choose whether to:
   - manually enter BMI, or
   - calculate BMI from height and weight.
5. Enter additional contextual values:
   - age
   - gender
   - blood pressure
   - blood sugar
   - smoking habit
   - screen time
   - stress level
6. Click **Predict Health Risk**.
7. View:
   - HRS score
   - predicted risk category
   - BMI category
   - explainability text
   - recommendations
   - diet score breakdown
   - calorie guidance
   - health alerts
   - saved user history and trend charts
   - what-if simulation result
   - model comparison chart
   - confusion matrices
   - feature importance chart
8. Download the report as **PDF** or **TXT**.

## HRS Formula
The engineered Health Risk Score is computed as:

```text
HRS = 0.25(Diet Risk) + 0.20(Sleep Risk) + 0.20(Activity Risk) + 0.35(BMI Risk)
```

The result is scaled to 0-100.

## Diet Score Logic
The diet score is calculated from:
- fruits and vegetables intake
- water intake
- breakfast regularity
- protein intake frequency
- junk food frequency
- sugary drink frequency

The final score is scaled to **0-100**, where a higher score indicates healthier dietary habits.

## Calorie Estimation Logic
Daily calories are estimated using a BMR-based formula and activity multiplier:
- BMR from age, gender, height, and weight
- maintenance calories from activity level
- weight-loss and weight-gain target calories

## User History Tracking
Every new prediction can be saved automatically in `data/prediction_history.csv`.
The dashboard visualizes:
- HRS trend over time
- BMI trend over time
- saved risk category distribution

## GitHub Push
Inside the project folder, run:

```bash
git init
git add .
git commit -m "Initial commit - health risk assessment project"
```

Then create an empty GitHub repository and connect it:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Render Deployment
This project already includes:
- `render.yaml`
- `runtime.txt`
- `requirements.txt`

### Render Steps
1. Push the project to GitHub.
2. Open **Render Dashboard**.
3. Click **New +** → **Blueprint** or **Web Service**.
4. Connect your GitHub repository.
5. If using Blueprint, Render will read `render.yaml` automatically.
6. If using Web Service manually, use:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
7. Deploy the app.

## Important Note
This system is for academic demonstration and early lifestyle-based risk estimation only. It is **not a medical diagnosis tool**.
