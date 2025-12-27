from flask import Blueprint, jsonify, request
import base64
import cv2
import numpy as np
import random

from services.model_service import get_data

api_bp = Blueprint("api", __name__)

disease_service = None
crop_service=None
sensor_service=None
translator_service=None



def init_disease_controller(service):
    """
    Dependency injection.
    Called once from app.py to attach the service.
    """
    global disease_service
    disease_service = service

def init_crop_controller(crop_srv, sensor_srv):
    """
    Inject CropService instance.
    Called once from app.py
    """
    global crop_service,sensor_service

    crop_service = crop_srv
    sensor_service=sensor_srv

def init_crop_controller_with_translator(crop_srv, sensor_srv,translate_srv):
    global crop_service, sensor_service, translation_service
    crop_service = crop_srv
    sensor_service = sensor_srv
    translation_service = translate_srv

def get_lang(request):
    return request.headers.get("X-Language", "en")



@api_bp.route("/data")
def api_data():
    data = get_data()
    return jsonify(data)

@api_bp.route("/read-soil", methods=["GET"])
def read_soil():
    if not sensor_service:
        return jsonify({"error": "Sensor service not initialized"}), 500

    soil = sensor_service.read_soil()
    return jsonify(soil)

@api_bp.route("/detect-disease", methods=["POST"])
def detect_disease():
    """
    Receives one frame from frontend,
    sends it to DiseaseService,
    returns ML result as JSON.
    """

    # 1. Read request JSON
    data = request.get_json()

    if not data or "frame" not in data:
        return jsonify({
            "error": "No frame received"
        }), 400

    try:
        # 2. Decode base64 image
        frame_data = data["frame"]

        # Remove data:image/jpeg;base64,
        header, encoded = frame_data.split(",", 1)

        image_bytes = base64.b64decode(encoded)

    
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({
                "error": "Invalid image"
            }), 400

        # 3. Read crop context (optional)
        crop = data.get("crop", "TOMATO")

      
        # 4. Call ML service
        result = disease_service.detect_disease(
            frame=frame,
            crop=crop
        )

      
        # 5. Return JSON response
        return jsonify(result)

    except Exception as e:
        print("Disease detection error:", e)
        return jsonify({
            "error": "Processing failed"
        }), 500
    
@api_bp.route("/recommend-crops", methods=["POST"])
def recommend_crops():
    """
    Expects JSON:
    {
        "N": 40,
        "P": 40,
        "K": 40,
        "temperature": 25,
        "humidity": 50,
        "ph": 6.5,
        "rainfall": 100
    }
    """

    if not crop_service or not sensor_service:
        return jsonify({"error": "Services not initialized"}), 500

    #Read real sensor data here
    soil_data = sensor_service.read_soil()

    lang = get_lang(request)
    recommendations = crop_service.recommend_crops(soil_data)

    if lang != "en":
        for rec in recommendations:
            if "crop" in rec:
                rec["crop"] = translation_service.translate_text(
                    rec["crop"],
                    lang
                )

            # OPTIONAL: if you add text labels later
            if "label" in rec:
                rec["label"] = translation_service.translate_text(
                    rec["label"],
                    lang
                )

   

    return jsonify({
        "soil":  soil_data,
        "recommendations": recommendations,
        "language": lang
    })

# --------------------------------------------------
# POST /api/fertilizer-advice
# --------------------------------------------------
@api_bp.route("/fertilizer-advice", methods=["POST"])
def fertilizer_advice():
    """
    Expects JSON:
    {
        "crop": "rice",
    }
    """

    if not crop_service:
        return jsonify({"error": "Crop service not initialized"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    crop = data.get("crop")
    soil = sensor_service.read_soil()

    lang = get_lang(request)


    try:
        soil_data = {
            "N": float(soil["N"]),
            "P": float(soil["P"]),
            "K": float(soil["K"]),
            "temperature": float(soil["temperature"]),
            "humidity": float(soil["humidity"]),
            "ph": float(soil["ph"]),
            "rainfall": float(soil.get("rainfall", 0))
        }
    except Exception:
        return jsonify({"error": "Invalid soil parameters"}), 400

    advice = crop_service.fertilizer_advice(
        crop_name=crop,
        soil_data=soil_data
    )

    translated_advice = translation_service.translate_list(advice, lang)

    return jsonify({
        "crop": crop,
        "fertilizer_advice": translated_advice
    })

@api_bp.route("/full-check", methods=["POST"])
def run_full_check():
    """
    Performs:
    1. Sensor read
    2. Crop recommendation
    """

    soil = sensor_service.read_soil()
    crops = crop_service.recommend_crops(soil)

    return jsonify({
        "soil": soil,
        "recommended_crops": crops,
        "disease_status": "Camera required"
    })