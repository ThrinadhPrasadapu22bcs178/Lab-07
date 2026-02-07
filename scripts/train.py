import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json
import os

def train():
    # Load dataset (using UCI wine quality dataset as an example)
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    try:
        data = pd.read_csv(url, sep=';')
    except Exception as e:
        print(f"Error loading data: {e}")
        # fallback to dummy data if network fails
        data = pd.DataFrame(np.random.rand(100, 12), columns=[
            'fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar',
            'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density',
            'pH', 'sulphates', 'alcohol', 'quality'
        ])

    X = data.drop('quality', axis=1)
    y = data['quality']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"MSE: {mse}")
    print(f"R2: {r2}")

    # Ensure artifacts directory exists
    os.makedirs('app/artifacts', exist_ok=True)

    # Save model
    joblib.dump(model, 'app/artifacts/model.pkl')

    # Save metrics
    metrics = {
        "MSE": float(mse),
        "R2": float(r2)
    }
    with open('app/artifacts/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    train()
