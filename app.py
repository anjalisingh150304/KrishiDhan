from flask import Flask , render_template

from controllers.home_controller import home_bp
from controllers.model_controller import api_bp, init_crop_controller_with_translator,init_disease_controller,init_crop_controller

from services.disease_service import DiseaseService
from services.crop_service import CropService
from services.sensor_service import SensorService
from services.translation_service import TranslationService

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

def create_app():
    app = Flask(__name__)

    disease_service = DiseaseService(
        model_path="models/plant_disease_model.tflite",
        labels_path="data/class_names.txt",
        tflite=tflite
    )

    sensor_service = SensorService(simulate_on_fail=True)

    crop_service = CropService(
        model_path="models/random_forest.pkl",
        scaler_path="models/scaler.pkl",
        targets_path="models/targets.pkl"
    )

    translation_service=TranslationService()
    
    init_disease_controller(disease_service)
    init_crop_controller_with_translator(crop_service,sensor_service,translation_service)


    app.register_blueprint(home_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0' , ssl_context=('cert.pem','key.pem'))
