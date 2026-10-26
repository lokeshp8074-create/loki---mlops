"""Train GradeCast on reproducible synthetic student-mark data."""

from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "model.pkl"
FEATURE_NAMES = (
    "study_hours_per_week",
    "attendance_percentage",
    "previous_score",
)


def generate_dataset(sample_count: int = 1200, random_state: int = 42):
    """Return deterministic demonstration data; these are not real student records."""
    generator = np.random.default_rng(random_state)
    study_hours = generator.uniform(0, 40, sample_count)
    attendance = generator.uniform(50, 100, sample_count)
    previous_score = generator.uniform(0, 100, sample_count)
    noise = generator.normal(0, 5, sample_count)

    marks = np.clip(
        0.9 * study_hours + 0.12 * attendance + 0.32 * previous_score + 6 + noise,
        0,
        100,
    )
    features = np.column_stack((study_hours, attendance, previous_score))
    return features, marks


def train_and_save(model_path: Path = MODEL_PATH) -> dict[str, float]:
    features, marks = generate_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        features, marks, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "mse": float(mean_squared_error(y_test, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, predictions))),
        "r2": float(r2_score(y_test, predictions)),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_NAMES}, model_path)

    print("Dataset: 1,200 reproducible synthetic demonstration records")
    print(f"Training rows: {len(x_train)} | Test rows: {len(x_test)}")
    print(f"Saved model: {model_path}")
    print("Test metrics:")
    for name, value in metrics.items():
        print(f"  {name.upper()}: {value:.4f}")
    return metrics


if __name__ == "__main__":
    train_and_save()