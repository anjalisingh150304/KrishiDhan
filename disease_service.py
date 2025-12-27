import cv2
import numpy as np
import os


# GLOBAL THRESHOLDS
DISEASE_THRESHOLD = 0.40
HEALTHY_THRESHOLD = 0.15


class DiseaseService:
    """
    Stateless disease detection service.
    Accepts ONE frame and returns diagnosis.
    """

    def __init__(self, model_path, labels_path, tflite):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        if not os.path.exists(labels_path):
            raise FileNotFoundError(f"Labels not found: {labels_path}")

        # Load labels
        with open(labels_path, "r") as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Load TFLite model
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.input_type = self.input_details[0]["dtype"]


    # GREEN DOMINANCE CHECK (UNCHANGED)
    def _is_green_dominant(self, frame):
        h, w, _ = frame.shape
        center = frame[h // 3 : 2 * h // 3, w // 3 : 2 * w // 3]

        hsv = cv2.cvtColor(center, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv,
            np.array([35, 40, 40]),
            np.array([85, 255, 255])
        )

        return (np.count_nonzero(mask) / mask.size) > 0.25

   
    # MAIN ENTRY: Detect disease from frame
    def detect_disease(self, frame, crop="TOMATO"):
        """
        frame: OpenCV BGR image
        crop: TOMATO / POTATO / PEPPER (context)
        """

        # Crop relevance mapping
        crop_map = {
            "TOMATO": ["tomato"],
            "POTATO": ["potato", "tomato"],
            "PEPPER": ["pepper", "bell"]
        }

        compatible_crops = crop_map.get(crop.upper(), ["tomato"])

        # PREPROCESS (from your code)
        img = cv2.resize(frame, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.input_type == np.float32:
            img = img.astype(np.float32) / 255.0
        else:
            img = img.astype(np.uint8)

        img = np.expand_dims(img, axis=0)

        # -------------------------------
        # RUN MODEL
        self.interpreter.set_tensor(self.input_details[0]["index"], img)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]["index"])[0]

        # DEQUANTIZE (if needed)
        if output.dtype == np.uint8:
            scale, zero_point = self.output_details[0]["quantization"]
            if scale == 0:
                scale = 1
            output = (output.astype(np.float32) - zero_point) * scale

        # -------------------------------
        # FIND BEST RELEVANT LABEL
        # -------------------------------
        best_score = 0.0
        best_label = ""

        for i, score in enumerate(output):
            label = self.labels[i].lower()

            is_relevant = (
                any(c in label for c in compatible_crops)
                or "healthy" in label
            )

            if is_relevant and score > best_score:
                best_score = score
                best_label = label

        # -------------------------------
        # CLEAN LABEL TEXT (same idea)
        # -------------------------------
        clean_label = best_label.upper()
        for word in ["TOMATO", "POTATO", "PEPPER", "BELL", "PLANT", "LEAF", "_"]:
            clean_label = clean_label.replace(word, " ")

        clean_label = " ".join(clean_label.split())

     
        # DECISION LOGIC (UNCHANGED)
        if best_score > DISEASE_THRESHOLD and "HEALTHY" not in clean_label:
            return {
                "status": "DISEASED",
                "label": clean_label,
                "confidence": round(float(best_score), 2)
            }

        if best_score > HEALTHY_THRESHOLD and "HEALTHY" in clean_label:
            return {
                "status": "HEALTHY",
                "label": "HEALTHY",
                "confidence": round(float(best_score), 2)
            }

        if self._is_green_dominant(frame):
            return {
                "status": "HEALTHY",
                "label": "HEALTHY (Color Verified)",
                "confidence": 0.50
            }

        return {
            "status": "SCANNING",
            "label": "Place leaf in center",
            "confidence": 0.0
        }
