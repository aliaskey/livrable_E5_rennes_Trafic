import os
from flask import Flask, render_template, request, jsonify
import flask_monitoringdashboard as dashboard
from flask_monitoringdashboard.database import session_scope, User
import plotly.graph_objs as go
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import logging
from src.get_data import GetData
from src.utils import create_figure, prediction_from_model
import datetime

# Chargement de la configuration du dashboard
dashboard.config.init_from(file=os.path.abspath('config.cfg'))
dashboard.config.monitor_level = 3
dashboard.config.enable_logging = True

# Configuration de l'application Flask
app = Flask(__name__)
dashboard.bind(app)

# Configuration du logging
logging.basicConfig(
    filename='app_errors.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialisation des données et du modèle
data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
data = data_retriever()

model = load_model('model.h5')

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        logging.info("Processing request on '/' route")
        fig_map = create_figure(data)
        graph_json = fig_map.to_json()

        if request.method == 'POST':
            selected_hour = request.form.get('hour')

            if model is not None and selected_hour:
                selected_hour = int(selected_hour)
                cat_predict = prediction_from_model(model, hour_to_predict=selected_hour)
                color_pred_map = {
                    0: ["Prédiction : Libre", "green"], 
                    1: ["Prédiction : Dense", "orange"], 
                    2: ["Prédiction : Bloqué", "red"]
                }
                text_pred, color_pred = color_pred_map.get(cat_predict, ["Prédiction inconnue", "gray"])
            else:
                text_pred, color_pred = "Modèle non disponible ou heure non spécifiée", "gray"

            logging.info(f"Returning prediction: {text_pred}")
            return render_template('index.html', graph_json=graph_json, text_pred=text_pred, color_pred=color_pred)

        logging.info("Rendering GET request")
        return render_template('index.html', graph_json=graph_json)

    except Exception as e:
        logging.error(f"Erreur lors du traitement de la requête : {e}")
        return "Une erreur est survenue", 500


@app.route('/dashboard/api/deploy_details', methods=['GET'])
def deploy_details_custom():
    try:
        logging.debug("Attempting to fetch deploy details...")
        with session_scope() as session:
            details = dashboard.get_deploy_details(session)
            logging.debug(f"Deploy details successfully retrieved: {details}")
            return jsonify(details), 200
    except Exception as e:
        logging.error(f"Failed to retrieve deploy details: {e}", exc_info=True)
        return jsonify({"error": "Error retrieving deploy details"}), 500

# Démarrage de l'application Flask
if __name__ == '__main__':
    logging.info('Starting the Flask app')
    app.run(debug=True)
