from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data_generation import generate_dataset
from .utils import CLASS_ORDER, FEATURE_COLUMNS, TARGET_COLUMN, dataset_path, model_bundle_path


@dataclass
class TrainingArtifacts:
    dataset: pd.DataFrame
    X_test: pd.DataFrame
    y_test_labels: np.ndarray
    logistic_model: Pipeline
    random_forest_model: Pipeline
    metrics: Dict[str, Dict[str, Any]]
    best_model_name: str


def _make_preprocessor(scale: bool) -> ColumnTransformer:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scaler", StandardScaler()))

    numeric_transformer = Pipeline(steps=numeric_steps)
    return ColumnTransformer(transformers=[("num", numeric_transformer, FEATURE_COLUMNS)])


def _evaluate_model(model: Pipeline, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict[str, Any]:
    y_pred = model.predict(X_test)
    labels = list(range(len(CLASS_ORDER)))

    metrics: Dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=labels).tolist(),
        "classification_report": classification_report(
            y_test,
            y_pred,
            labels=labels,
            target_names=CLASS_ORDER,
            zero_division=0,
            output_dict=True,
        ),
    }
    return metrics


def train_models(n_samples: int = 1000, random_state: int = 42) -> TrainingArtifacts:
    dataset = generate_dataset(n_samples=n_samples, random_state=random_state)
    dataset.to_csv(dataset_path(), index=False)

    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]
    label_mapping = {label: index for index, label in enumerate(CLASS_ORDER)}
    y_encoded = y.map(label_mapping).to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        random_state=random_state,
        stratify=y_encoded,
    )

    logistic_model = Pipeline(
        steps=[
            ("preprocessor", _make_preprocessor(scale=True)),
            (
                "classifier",
                LogisticRegression(max_iter=1000, random_state=random_state),
            ),
        ]
    )

    random_forest_model = Pipeline(
        steps=[
            ("preprocessor", _make_preprocessor(scale=False)),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=9,
                    min_samples_split=6,
                    min_samples_leaf=2,
                    random_state=random_state,
                ),
            ),
        ]
    )

    logistic_model.fit(X_train, y_train)
    random_forest_model.fit(X_train, y_train)

    logistic_metrics = _evaluate_model(logistic_model, X_test, y_test)
    rf_metrics = _evaluate_model(random_forest_model, X_test, y_test)

    metrics = {
        "Logistic Regression": logistic_metrics,
        "Random Forest": rf_metrics,
    }

    best_model_name = max(metrics, key=lambda name: metrics[name]["accuracy"])

    return TrainingArtifacts(
        dataset=dataset,
        X_test=X_test,
        y_test_labels=np.array([CLASS_ORDER[index] for index in y_test]),
        logistic_model=logistic_model,
        random_forest_model=random_forest_model,
        metrics=metrics,
        best_model_name=best_model_name,
    )


def save_bundle(artifacts: TrainingArtifacts) -> Dict[str, Any]:
    bundle = {
        "dataset_preview": artifacts.dataset.head(10),
        "label_classes": CLASS_ORDER,
        "logistic_model": artifacts.logistic_model,
        "random_forest_model": artifacts.random_forest_model,
        "metrics": artifacts.metrics,
        "best_model_name": artifacts.best_model_name,
        "feature_importances": _extract_feature_importances(artifacts.random_forest_model),
    }
    joblib.dump(bundle, model_bundle_path())
    return bundle


def load_bundle() -> Dict[str, Any]:
    return joblib.load(model_bundle_path())


def train_and_save(n_samples: int = 1000, random_state: int = 42) -> Dict[str, Any]:
    artifacts = train_models(n_samples=n_samples, random_state=random_state)
    return save_bundle(artifacts)


def _extract_feature_importances(model: Pipeline) -> Dict[str, float]:
    classifier = model.named_steps["classifier"]
    importances = classifier.feature_importances_
    return {feature: round(float(importance), 4) for feature, importance in zip(FEATURE_COLUMNS, importances)}


def build_model_comparison_figure(metrics: Dict[str, Dict[str, Any]]):
    comparison_df = pd.DataFrame(
        {
            model_name: {
                "Accuracy": values["accuracy"],
                "Precision": values["precision"],
                "Recall": values["recall"],
                "F1-Score": values["f1_score"],
            }
            for model_name, values in metrics.items()
        }
    ).T

    fig, ax = plt.subplots(figsize=(8, 4.5))
    comparison_df.plot(kind="bar", ax=ax)
    ax.set_title("Model Performance Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig


def build_confusion_matrix_figure(confusion_matrix_values, class_names, title: str):
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(confusion_matrix_values, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    return fig


def build_feature_importance_figure(feature_importances: Dict[str, float]):
    importance_df = pd.DataFrame(
        {
            "Feature": list(feature_importances.keys()),
            "Importance": list(feature_importances.values()),
        }
    ).sort_values(by="Importance", ascending=False)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(data=importance_df, x="Importance", y="Feature", palette="viridis", ax=ax)
    ax.set_title("Random Forest Feature Importance")
    ax.set_xlabel("Importance")
    ax.set_ylabel("Feature")
    plt.tight_layout()
    return fig


def predict_single(model_bundle: Dict[str, Any], input_df: pd.DataFrame, model_name: str) -> Tuple[str, np.ndarray]:
    chosen_model = model_bundle["logistic_model"] if model_name == "Logistic Regression" else model_bundle["random_forest_model"]
    prediction_encoded = chosen_model.predict(input_df)[0]
    probabilities = chosen_model.predict_proba(input_df)[0]
    predicted_label = model_bundle["label_classes"][prediction_encoded]
    return predicted_label, probabilities


def bundle_summary_as_json(bundle: Dict[str, Any]) -> str:
    summary = {
        "best_model_name": bundle["best_model_name"],
        "metrics": bundle["metrics"],
        "feature_importances": bundle["feature_importances"],
    }
    return json.dumps(summary, indent=2)
