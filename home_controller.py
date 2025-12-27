from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    return render_template("index.html")

@home_bp.route("/recommend/crop")
def recommend_crop():
    return render_template("crop_recommend.html")

@home_bp.route("/detect/disease")
def detect_disease():
    return render_template("detect_disease.html")

@home_bp.route("/full/check")
def full_check():
    return render_template("full_check.html")