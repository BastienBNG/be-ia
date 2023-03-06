import json
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import requests
from flask import Flask, request
import pandas as pd
from pandas import json_normalize

app = Flask(__name__)

@app.route('/ia', methods=['POST'])
def ia():
    test_data = request.json
    identity_dict = json.loads(test_data[0]["Identity"])
    sport_dict = json.loads(test_data[0]["Sport"])
    self_eval_dict = json.loads(test_data[0]["Self_evaluation"])
    injuries_dict = json.loads(test_data[0]["Injuries"])
    training_stat_dict = json.loads(test_data[0]["Training_stat"])
    

    def years_since(date):
        """Retourne le nombre d'années entre la date spécifiée et aujourd'hui, multiplié par 10"""
        # Convertir la date en un objet datetime
        date_obj = datetime.strptime(date, '%Y/%m/%d')
        # Calculer la différence entre aujourd'hui et la date spécifiée, et multiplier par 10
        delta_years = (datetime.now() - date_obj).days / 365.25 * 20
        # Retourner le nombre d'années arrondi à deux décimales
        return round(delta_years, 2)




    def fit_label_encoder(data):
        le = LabelEncoder()
        le.fit(data)
        return le

    def string_to_features(string, le):
        return le.transform([string])[0]


    def date_to_days(date_str):
        date = datetime.strptime(date_str, '%Y/%m/%d')
        reference_date = datetime(1970, 1, 1)
        return (date - reference_date).days

    data = ['M','F','Jambe', 'Bras', 'Abdominaux','Poignet',"Genoux"]
    encoder = fit_label_encoder(data)


    # Charger les données d'entraînement à partir du fichier JSON
    with open('train_data2.json') as f:
        data = json.load(f)
    # Extraire les caractéristiques et la cible des données d'entraînement
    X_train = []
    y_train = []
    for athlete in data:
        # Extraire les caractéristiques pertinentes pour le calcul de l'indice de risque
        features = [years_since(athlete['Identity']['Birth_Date']), string_to_features(athlete['Identity']['Sex'], encoder), athlete['Identity']['Taille'],
                    years_since(athlete['Sport']['Date_of_last_competition']), years_since(athlete['Sport']['Date_of_last_training']), string_to_features(athlete['Sport']['Muscle_used_in_the_last_workout'], encoder), athlete['Sport']['Recovery_status'], athlete['Sport']['training_frequency_week'],
                    athlete['Self_evaluation']['Sleep'], athlete['Self_evaluation']['General_tiredness'], athlete['Self_evaluation']['Aches_pains'], athlete['Self_evaluation']['Mood_stress'], athlete['Self_evaluation']['Weight'],
                    years_since(athlete['Injuries']['Date']), string_to_features(athlete['Injuries']['Position'], encoder), athlete['Injuries']['Intensity'],
                    years_since(athlete['Training_stat']['Date']), athlete['Training_stat']['Duration_time'], athlete['Training_stat']['Intensity_of_last_training']]
        # Ajouter les caractéristiques et la cible à leur liste respective
        X_train.append(features)
        y_train.append(athlete['Score'])

    # Créer un objet de modèle MLP
    model = LinearRegression()

    

    # Entraîner le modèle avec les données d'entraînement
    model.fit(X_train, y_train)

    # Charger les données de test à partir du fichier JSON
    #with open('test_data2.json') as f:
        

    # Extraire les caractéristiques des données de test
    X_test = []
    for athlete in test_data:
        features = [years_since(identity_dict['Birth_Date']), string_to_features(identity_dict['Sex'], encoder), identity_dict['Taille'],
                    years_since(sport_dict['Date_of_last_competition']), years_since(sport_dict['Date_of_last_training']), string_to_features(sport_dict['Muscle_used_in_the_last_workout'], encoder), sport_dict['Recovery_status'], sport_dict['frequence_training_week'],
                    self_eval_dict['Sleep'], self_eval_dict['General_tiredness'], self_eval_dict['Aches_pains'], self_eval_dict['Mood_stress'], self_eval_dict['Weight'],
                    years_since(injuries_dict['Date']), string_to_features(injuries_dict['Position'], encoder), injuries_dict['Intensity'],
                    years_since(training_stat_dict['Date']), (training_stat_dict['Duration_time']//60), training_stat_dict['Intensity_of_last_training']]
        print(features)
        X_test.append(features)
    
    

    # Prédire les valeurs cibles des données de test
    y_pred = model.predict(X_test)

    # Imprimer les prédictions
    print(y_pred)

    athlete_id = identity_dict["Athlete_ID"]
    score = y_pred[0]

    json_pred = {
        "Athlete_ID": athlete_id,
        "Score": score
    }
    print(json_pred)
    url = 'http://127.0.0.1:8080/score'
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, json=json_pred, headers=headers)


    return 'IA success'

if __name__ == '__main__':
    app.run(port=2000)