import os
import joblib
import numpy as np
import warnings

# External helpers (from your project)
from utilities.utils import check_parameters
from utilities.parameters import thresholds, fertilizers

class CropService:
    """
    Crop recommendation service.
    Uses RandomForest + scaler + domain rules.
    """

    def __init__(self, model_path, scaler_path, targets_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Crop model not found: {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler not found: {scaler_path}")
        if not os.path.exists(targets_path):
            raise FileNotFoundError(f"Targets not found: {targets_path}")

        # Load models ONCE
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.targets = joblib.load(targets_path)

    # --------------------------------------------------
    # MAIN ENTRY: Recommend crops from soil parameters
    # --------------------------------------------------
    def recommend_crops(self, soil_data, top_k=3):
        """
        soil_data = {
            'N': float,
            'P': float,
            'K': float,
            'temperature': float,
            'humidity': float,
            'ph': float,
            'rainfall': float
        }
        """

        feature_order = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        feature_vector = [[soil_data[f] for f in feature_order]]

        # Scale
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            scaled = self.scaler.transform(feature_vector)

        # Predict probabilities
        probs = self.model.predict_proba(scaled)[0]
        class_ids = self.model.classes_

        results = []
        for idx, prob in enumerate(probs):
            if prob <= 0:
                continue

            class_id = class_ids[idx]
            crop_name = self.targets.get(
                class_id,
                self.targets.get(str(class_id), "Unknown")
            )

            results.append({
                "crop": crop_name,
                "confidence": round(float(prob), 3)
            })

        # Sort and return top K
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:top_k]

    # --------------------------------------------------
    # OPTIONAL: Fertilizer advice for selected crop
    # --------------------------------------------------
    def fertilizer_advice(self, crop_name, soil_data):
        """
        crop_name: string
        soil_data: same dict as above
        """

        soil_params = {
            'N': soil_data['N'],
            'P': soil_data['P'],
            'K': soil_data['K'],
            'ph': soil_data['ph'],
            'temperature': soil_data['temperature'],
            'humidity': soil_data['humidity']
        }

        recs = check_parameters(
            crop_name.lower(),
            soil_params,
            thresholds,
            fertilizers
        )

        return recs or []
