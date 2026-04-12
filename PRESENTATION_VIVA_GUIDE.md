# Presentation and Viva Guide

## 1. One-Line Project Introduction
This project predicts a user's health risk level using explainable machine learning and also includes diet scoring, calorie estimation, health alerts, history tracking, and PDF report generation.

## 2. Problem Statement
Many people do not recognize health risk early. A lightweight system that combines lifestyle inputs, engineered scoring, contextual health parameters, and ML can help estimate risk and support preventive healthcare.

## 3. Objective
- Predict health risk as Low, Moderate, or High
- Compute Health Risk Score (HRS)
- Compare Logistic Regression and Random Forest
- Explain the prediction using feature importance and simple text
- Provide recommendations through an interactive dashboard
- Add practical wellness tools such as diet score calculation and calorie estimation
- Add health alerts, user history tracking, and professional PDF reporting
- Let the user test improvement scenarios with what-if simulation

## 4. Core Prediction Inputs
- Diet Score
- Sleep Hours
- Physical Activity Level
- BMI
- HRS

## 5. Additional Contextual Inputs Added
- Age
- Gender
- Blood Pressure
- Blood Sugar
- Smoking Habit
- Screen Time
- Stress Level
- Height and Weight

## 6. Important Note for Viva
Say this clearly:

> The machine learning prediction model is trained on the core health factors: diet score, sleep hours, physical activity, BMI, and engineered HRS. The newly added parameters such as age, blood pressure, sugar level, smoking habit, screen time, and stress level are currently used to enrich alerts, recommendations, report generation, and user history analysis.

This is the correct technical explanation and sounds professional.

## 7. New Practical Features Added
- **Diet Score Calculator** from food habits
- **BMI auto-calculation** using height and weight
- **Daily calorie estimator** using BMR logic
- **Health alerts** based on BMI, sleep, blood pressure, blood sugar, smoking, screen time, and stress
- **User history tracking** using saved predictions and trend charts
- **PDF report generation** for professional output
- **What-if simulation** to see how risk changes if the user improves health factors
- **HRS contribution breakdown** to show which component contributes more to the final score

## 8. Why These Features?
- Diet affects overall wellness and metabolism
- Sleep affects recovery and chronic risk
- Physical activity reduces health complications
- BMI indicates body weight health status
- Blood pressure and blood sugar strengthen practical health interpretation
- Smoking, screen time, and stress improve behavioral relevance
- User history makes the system look like a monitoring platform
- PDF reporting improves professionalism in the demo

## 9. Methodology
1. Generate / collect dataset
2. Preprocess features
3. Compute HRS
4. Train Logistic Regression and Random Forest
5. Evaluate using accuracy, precision, recall, F1-score, confusion matrix
6. Use feature importance for explainability
7. Add diet score and calorie calculators
8. Add health alerts and history tracking
9. Show results in Streamlit dashboard
10. Generate PDF and text reports
11. Allow what-if simulation and trend analysis

## 10. Why Logistic Regression?
- Simple baseline classifier
- Easy to explain
- Good for linear decision boundaries

## 11. Why Random Forest?
- Handles non-linear patterns well
- More robust than a single decision tree
- Gives feature importance for explainability

## 12. Difference Between HRS and ML Prediction
- **HRS** is a rule-based weighted score designed using health logic.
- **ML prediction** learns patterns from data to classify risk automatically.

## 13. How to Explain the Diet Score Calculator
> Instead of asking the user to enter a random diet score manually, I added a diet assessment module that computes the score from food habits like fruits and vegetables intake, water intake, breakfast regularity, protein intake, junk food frequency, and sugary drink frequency.

## 14. How to Explain the Calorie Estimator
> I added a calorie estimation module using the BMR concept. It takes age, gender, height, weight, and activity type to estimate maintenance calories. This makes the system more practical for lifestyle guidance.

## 15. How to Explain Health Alerts
> I added a health alert layer that checks values like BMI, sleep, blood pressure, blood sugar, smoking habit, screen time, and stress. These alerts make the system more relevant for preventive healthcare discussion.

## 16. How to Explain User History Tracking
> Every prediction can be stored in a CSV file. The dashboard then visualizes history through trend charts such as HRS over time and BMI over time. This makes the project look like a monitoring system rather than just a one-time predictor.

## 17. How to Explain PDF Report Generation
> I added PDF report generation to make the system output more professional. The report includes input details, predicted risk, HRS, alerts, recommendations, and explanation.

## 18. How to Explain the What-If Simulation
> The what-if simulation helps the user understand how improving lifestyle values such as sleep, BMI, or activity can change the predicted health risk. So the project is not just predictive but also supportive for decision making.

## 19. Expected Demo Flow
1. Open app
2. Select model
3. Use diet score calculator
4. Enter sleep, activity, and contextual health parameters
5. Calculate BMI from height and weight or enter BMI manually
6. Click predict
7. Show HRS score and predicted category
8. Show BMI category and calorie guidance
9. Show alerts and recommendations
10. Show history trend chart
11. Run what-if simulation
12. Show comparison chart and confusion matrix
13. Download PDF report

## 20. Common Viva Questions and Answers

### Q1. Why did you choose this project?
Because healthcare analytics is relevant, impactful, and suitable for applying machine learning in a practical and explainable way.

### Q2. Is the dataset real?
Currently the project uses a realistic simulated dataset for academic purposes. The framework can later be extended to real wearable or clinical datasets.

### Q3. Why did you normalize features in HRS?
Because each feature has a different range, and normalization brings them to a common scale before weighted aggregation.

### Q4. Why compare two models?
To show scientific evaluation and identify which model performs better for this classification task.

### Q5. What is the role of confusion matrix?
It shows how many predictions are correct and where misclassifications happen across Low, Moderate, and High classes.

### Q6. What is feature importance?
It indicates which features contribute most to model decisions, especially in Random Forest.

### Q7. Why did you add extra inputs like age, BP, sugar, smoking, and stress?
To improve real-world relevance. These values are currently used for alerts, reporting, recommendations, and user monitoring, while the ML model prediction still uses the core trained features.

### Q8. Why did you add history tracking?
To make the system useful for repeated monitoring and visual trend analysis.

### Q9. Why is PDF report generation useful?
It provides a professional summary output that can be downloaded and shared.

### Q10. What are the limitations?
The dataset is synthetic, only a limited set of prediction features are used in model training, and the system is not a substitute for professional diagnosis.

### Q11. Future scope?
- Real-time wearable integration
- More health parameters in the trained model
- Real medical datasets
- Advanced explainability methods such as SHAP
- Cloud deployment
- User login and secure profile-based health tracking

## 21. Final Conclusion Line
This project demonstrates that a lightweight, explainable, and user-centric ML system can support early health risk assessment, lifestyle awareness, monitoring, and preventive decision support in smart healthcare.
