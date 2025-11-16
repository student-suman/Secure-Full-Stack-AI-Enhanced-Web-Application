# In train_anomaly_detector.py

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib
from app import app, db  # Import your app and db
from models import Verification # Import your Verification model
from datetime import datetime, timedelta

def prepare_data():
    """Fetches verification data and prepares it for the model."""
    print("Fetching data from database...")
    with app.app_context():
        # Fetch recent verification data (e.g., last 30 days, or all if you have less)
        # Adjust the filter as needed based on how much data you have
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        verifications = Verification.query.filter(Verification.verified_at >= thirty_days_ago).all()
        
        if not verifications:
             print("Not enough data to train. Need at least a few records.")
             return None

        print(f"Fetched {len(verifications)} records.")
        # Convert to DataFrame
        data = [{
            'method': v.verification_method,
            'result': v.verification_result,
            'hour': v.verified_at.hour, # Hour of the day might be indicative
            'ip_address': v.ip_address # We'll need to encode this
            # Add other potentially useful features like 'user_agent' if desired
        } for v in verifications]
        df = pd.DataFrame(data)

    print("Preprocessing data...")
    # --- Feature Engineering ---
    # Convert categorical features to numbers
    le_method = LabelEncoder()
    le_result = LabelEncoder()
    le_ip = LabelEncoder() # Simple IP encoding for this example

    df['method_encoded'] = le_method.fit_transform(df['method'])
    df['result_encoded'] = le_result.fit_transform(df['result'])
    df['ip_encoded'] = le_ip.fit_transform(df['ip_address'])

    # Select features for the model
    features = ['method_encoded', 'result_encoded', 'hour', 'ip_encoded']
    df_features = df[features]

    # Save the encoders to use them later during prediction
    joblib.dump(le_method, 'encoder_method.joblib')
    joblib.dump(le_result, 'encoder_result.joblib')
    joblib.dump(le_ip, 'encoder_ip.joblib')
    print("Encoders saved.")

    return df_features

def train_model(df_features):
    """Trains the Isolation Forest model."""
    print("Training Isolation Forest model...")
    # Contamination='auto' lets the model decide the anomaly threshold
    # You might need to adjust 'n_estimators' based on your data size
    model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    model.fit(df_features)
    print("Model training complete.")
    
    # Save the trained model
    joblib.dump(model, 'anomaly_model.joblib')
    print("Model saved as anomaly_model.joblib")

if __name__ == '__main__':
    prepared_data = prepare_data()
    if prepared_data is not None and not prepared_data.empty:
        train_model(prepared_data)
    else:
        print("Model training skipped due to insufficient data.")