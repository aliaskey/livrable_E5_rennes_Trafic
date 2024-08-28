import plotly.express as px
import numpy as np

def create_figure(data):
    fig_map = px.scatter_mapbox(
        data,
        title="Traffic en temps réel",
        color="traffic",
        lat="lat",
        lon="lon",
        color_discrete_map={'freeFlow': 'green', 'heavy': 'orange', 'congested': 'red'},
        zoom=10,
        height=500,
        mapbox_style="carto-positron"
    )
    
    return fig_map

def prediction_from_model(model, hour_to_predict):
    # Assurez-vous que la longueur de input_pred correspond à la taille attendue par le modèle
    input_pred = np.array([0] * 24)  # Assurez-vous que la taille est correcte (24 dans ce cas)
    
    # Validez que hour_to_predict est bien un nombre entier et qu'il est dans la plage correcte
    if 0 <= int(hour_to_predict) < 24:
        input_pred[int(hour_to_predict)] = 1
    else:
        raise ValueError(f"Hour to predict must be between 0 and 23, got {hour_to_predict}")
    
    # Utilisez np.expand_dims pour ajouter une dimension batch (1, 24)
    input_pred = np.expand_dims(input_pred, axis=0)
    
    # Prédiction
    cat_predict = np.argmax(model.predict(input_pred))
    
    return cat_predict