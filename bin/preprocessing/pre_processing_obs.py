import os
import traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import datetime
from datetime import timedelta
import ephem
from aero.settings import COLUMNS , SUB_COLUMNS_DICT , DATA_PATH , OBS_PATH , DOCS_PATH , latitude , longitude 


def findCorruptedFiles(folder_path, columns=COLUMNS):
    files = os.listdir(folder_path)
    corruptedFiles = []
    
    for file in files:
        with open(f"{folder_path}/{file}", 'r') as infile:
            try:
                #check if we can read all the lines
                lines = infile.read().split("\n")

                #check if there is no trailing digits
                for i, line in enumerate(lines):
                    if len(line.split(" ")) > len(columns):
                        raise Exception(f"trailing_digits at line {i+1}")
            except Exception as e: 
                print(f"{file}, {str(e)}")
                

def combineFiles(folder_path, result_file_name=DATA_PATH / "combined_file.txt", columns=COLUMNS):
    files = os.listdir(folder_path)

    with open(result_file_name, 'w') as outfile:
        s = " ".join(columns) + "\n"
        outfile.write(s)
    
    with open(result_file_name, 'a') as outfile:
        for file in files:
            with open(f"{folder_path}/{file}", 'r') as infile:
                lines = infile.read().split("\n")
                for line in lines:
                    if len(line) > 1:
                        outfile.write(line.rstrip("\n") + " " + file + "\n")
                        

def formatData(fileName=DATA_PATH / "combined_file.txt", columns=COLUMNS, sub_columns_dict=SUB_COLUMNS_DICT):
    df = pd.read_csv(fileName, sep=" ", dtype=str)

    for column in sub_columns_dict:
        vals = df[column].values

        for i, sub_column in enumerate(sub_columns_dict[column]):
            sub_vals = [list(val)[i] for val in vals]
            df[f"{column}_{sub_column}"] = sub_vals

        df = df.drop(columns=[column])

    return df


# Créer un objet d'observation pour les calculs astronomiques
obs = ephem.Observer()
obs.lat = str(latitude)
obs.lon = str(longitude)


# Convertir l'heure en UTC
def convert_to_utc(row):
    # Extraire les valeurs des colonnes 'annee', 'mois', 'jour', 'heure' et 'minute'
    annee = int(row['annee'])
    mois = int(row['mois'])
    jour = int(row['jour'])
    heure = int(row['heure'])
    minute = int(row['minute'])

    # Créer un objet datetime avec le fuseau horaire local
    dt_local = datetime.datetime(annee, mois, jour, heure, minute)
    #print(dt_local)
    # Convertir l'heure en UTC
    dt_utc = dt_local.astimezone(datetime.timezone.utc)
    #print(dt_utc)
    # Récupérer les composantes de l'heure UTC
    annee_utc = dt_utc.year
    mois_utc = dt_utc.month
    jour_utc = dt_utc.day
    heure_utc = dt_utc.hour
    minute_utc = dt_utc.minute

    # Retourner les valeurs converties
    return annee_utc, mois_utc, jour_utc, heure_utc, minute_utc



# Fonction pour déterminer la nature (jour ou nuit) et les heures de lever et de coucher du soleil
 
def get_dates(row):
    dt = datetime.datetime(int(row['annee_utc']), int(row['mois_utc']), int(row['jour_utc']), 12, 0, 0)
    obs = ephem.Observer()  # Créer un objet Observer d'ephem
    obs.date = ephem.Date(dt)
    sunrise = obs.previous_rising(ephem.Sun())  # Heure du lever du soleil
    sunset = obs.next_setting(ephem.Sun())  # Heure du coucher du soleil

    sunrise_datetime = datetime.datetime.strptime(str(sunrise), '%Y/%m/%d %H:%M:%S')
    sunset_datetime = datetime.datetime.strptime(str(sunset), '%Y/%m/%d %H:%M:%S')

    dt = datetime.datetime(int(row['annee_utc']), int(row['mois_utc']), int(row['jour_utc']), int(row['heure_utc']), int(row['minute_utc']), 0)
    obs.date = ephem.Date(dt)
    obs_datetime = datetime.datetime.strptime(str(obs.date), '%Y/%m/%d %H:%M:%S')

    if sunrise_datetime < obs_datetime < sunset_datetime:
        nature = 'jour'
    else:
        nature = 'nuit'

    return nature, sunrise_datetime, sunset_datetime, obs_datetime


# Fonction pour calculer l'intervalle de temps entre l'heure d'observation et l'heure de lever du soleil 
def calculate_time_interval_obs_lever(row):
    obs.date = ephem.Date(row['date'] + timedelta(days=1))
    sunrise = obs.previous_rising(ephem.Sun())  # Heure du lever du soleil
    next_day_sunrise = datetime.datetime.strptime(str(sunrise), '%Y/%m/%d %H:%M:%S')
    #sunset = obs.previous_setting(ephem.Sun())  # Heure du coucher du soleil
    #next_day_sunset = datetime.strptime(str(sunset), '%Y/%m/%d %H:%M:%S')
    if row['date'] > row['date_coucher_soleil']:
        return (row['date'] - next_day_sunrise ).total_seconds() / 3600
    else:
        return (row['date'] - row['date_lever_soleil']).total_seconds() / 3600


# Fonction pour calculer l'intervalle de temps entre l'heure d'observation et l'heure de coucher du soleil
def calculate_time_interval_obs_coucher(row):
    obs.date = ephem.Date(row['date'] - timedelta(days=1))
    sunset = obs.previous_setting(ephem.Sun())  # Heure du coucher du soleil
    previous_day_sunset = datetime.datetime.strptime(str(sunset), '%Y/%m/%d %H:%M:%S')

    if row['date'] > row['date_lever_soleil']:
        return (row['date'] - row['date_coucher_soleil']).total_seconds() / 3600
    else:
        return (row['date'] - previous_day_sunset -  timedelta(days=1)).total_seconds() / 3600

    
#check for corrupted files
findCorruptedFiles(OBS_PATH)

#After solving the problems with the files that are bothering you, uncomment the code below and run it again.
#combine files
combineFiles(OBS_PATH)

#format data
df = formatData()


# Ne garder que les colonnes utiles
df = df[['gelee_blanche_vehicule_presence', 'annee', 'mois', 'jour', 'heure', 'minute']]


# Appliquer la conversion de temps au dataset
df[['annee_utc', 'mois_utc', 'jour_utc', 'heure_utc', 'minute_utc']] = df.apply(convert_to_utc, axis=1, result_type='expand')
# Supprimer les colonnes non UTC
df = df.drop(['annee', 'mois', 'jour', 'heure', 'minute'], axis=1)


# Ajouter les colonnes "jour_ou_nuit", "date_lever_soleil", "date_coucher_soleil" et "date_observation" au DataFrame existant
df['jour_ou_nuit'], df['date_lever_soleil'], df['date_coucher_soleil'], df['date'] = zip(*df.apply(get_dates, axis=1))


# Appliquer la fonction sur chaque ligne du DataFrame 
df['H_obs-H_lever_soleil'] = df.apply(calculate_time_interval_obs_lever, axis=1)
df['H_obs-H_lever_soleil'] = df['H_obs-H_lever_soleil'].astype(int)

# Appliquer la fonction sur chaque ligne du DataFrame
df['H_obs-H_coucher_soleil'] = df.apply(calculate_time_interval_obs_coucher, axis=1)
df['H_obs-H_coucher_soleil'] = df['H_obs-H_coucher_soleil'].astype(int)

# Sélection des colonnes spécifiées
selected_columns = ["gelee_blanche_vehicule_presence", "H_obs-H_lever_soleil", "H_obs-H_coucher_soleil", "heure_utc", "mois_utc", "date"]
df_predicteurs = df[selected_columns]

# Supprimer les lignes avec des valeurs manquantes
df_predicteurs.dropna(inplace=True)
# Suppprimer les doublons
df_predicteurs.drop_duplicates(inplace=True)

# enregistrer le fichier : avec un nom plus explicite dans le dossier donnees_mises_en_forme. 
df_predicteurs.to_csv(DOCS_PATH / "donnees_obs_predicteurs_temporels_gelee_blanche.csv", index=False)

# enregistrer le fichier des observations : uniquement les colonnes "gelee_blanche_vehicule_presence", "date"
df_obs = df_predicteurs[["gelee_blanche_vehicule_presence", "date"]]
df_obs.to_csv(DOCS_PATH / "obs_gelee_blanche.csv", index=False)