"""GradeCast Flask application."""

import math
from pathlib import Path

import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "model.pkl"
FEATURES = (
    "study_hours_per_week",
    "attendance_percentage",
    "previous_score",
)
FEATURE_LIMITS = {
    "study_hours_per_week": (0, 40),
    "attendance_percentage": (0, 100),
    "previous_score": (0, 100),
}


def create_app(model_path: Path = MODEL_PATH) -> Flask:
    application = Flask(__name__)
    bundle = joblib.load(model_path)
    model = bundle["model"]
    application.config["GRADECAST_MODEL"] = model

    @application.get("/")
    def index():
        return render_template("index.html", values={}, errors={}, prediction=None)

    @application.get("/health")
    def health():
        return jsonify(status="ok", model_loaded=True)

    @application.post("/prediction")
    def prediction():
        is_json_request = request.is_json
        values = request.get_json(silent=True) if is_json_request else request.form
        errors: dict[str, str] = {}
        numeric_values: list[float] = []

        if values is None or not hasattr(values, "get"):
            errors["request"] = "Provide an object containing all three input values."
            values = {}
        for feature in FEATURES:
            raw_value = values.get(feature)
            if raw_value is None or str(raw_value).strip() == "":
                errors[feature] = "This value is required."
                continue
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                errors[feature] = "Enter a valid number."
                continue
            if not math.isfinite(value):
                errors[feature] = "Enter a finite number."
                continue

            minimum, maximum = FEATURE_LIMITS[feature]
            if not minimum <= value <= maximum:
                errors[feature] = f"Enter a value from {minimum} to {maximum}."
                continue
            numeric_values.append(value)

        if errors:
            if is_json_request:
                return jsonify(errors=errors), 400
            return render_template(
                "index.html", values=values, errors=errors, prediction=None
            ), 400

        estimate = float(model.predict(np.asarray([numeric_values]))[0])
        estimate = round(min(100.0, max(0.0, estimate)), 2)
        if is_json_request:
            return jsonify(prediction=estimate, unit="marks")
        return render_template(
            "index.html", values=values, errors={}, prediction=estimate
        )

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)