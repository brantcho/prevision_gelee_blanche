from pathlib import Path 

ROOT_PATH = Path("/scratch/labia/tchoffoc")
DATA_PATH = ROOT_PATH / "data"
OBS_PATH = DATA_PATH / "gelee_blanche_fichiers_corrects"
DOCS_PATH = ROOT_PATH / "donnees_mises_en_forme"
# chemins pour les fichiers de donnees meteo : fichiers grib
INPUT_PATH  = Path('/scratch/labia/tourniert/gelee_blanche/grib')
# chemin pour les donnees de sortie : fichiers csv
OUTPUT_PATH = DOCS_PATH 


# liste des fichiers csv dans le dossier DOCS_PATH
CSV_FILES = [
    "donnees_fichiers_grib_2019_2020.csv",
    "donnees_fichiers_grib_2020_2021.csv",
    "donnees_fichiers_grib_2021_2022.csv",
    "donnees_fichiers_grib_2022_2023.csv",
    "donnees_obs_predicteurs_temporels_gelee_blanche.csv"
] 

# hyperparamètres pour les modèle de  Random Forest mets les 2 dans des dictionnaires
# hyperparamètres pour maximiser la précision
RAND_FOREST_PRECISION_MAX = {
    "class_weight": {0: 1, 1: 5},
    "min_samples_leaf": 2,
    "n_estimators": 100
}
# hyperparamètres pour maximiser le rappel
RAND_FOREST_RECALL_MAX = {
    "class_weight": {0: 1, 1: 25},
    "min_samples_leaf": 25,
    "n_estimators": 100
}


# Coordonnées géographiques
latitude = 49.00810  # Latitude de Roissy
longitude = 2.55018  # Longitude de Roissy

# Constantes pour les colonnes et sous-colonnes
COLUMNS = [
    "annee",
    "mois",
    "jour",
    "heure",
    "minute",
    "gelee_blanche_vehicule",
    "gelee_blanche_chaussee",
    "gelee_blanche_herbe",
    "glace_au_sol",
    "neige_au_sol",
    "hauteur_neige_fraiche",
    "hauteur_neige_total",
    "file_name"
]

SUB_COLUMNS_DICT = {
    "gelee_blanche_vehicule": ["presence", "intensite", "lieu"],
    "gelee_blanche_chaussee": ["presence", "intensite", "lieu"],
    "glace_au_sol": ["presence", "lieu"],
    "neige_au_sol": ["presence", "forme"]
}