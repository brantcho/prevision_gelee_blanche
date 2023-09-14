import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib   

from aero.settings import DOCS_PATH , CSV_FILES , RAND_FOREST_PRECISION_MAX , RAND_FOREST_RECALL_MAX

# fonction pour lire les fichiers csv dans CSV_FILES contenues dans DOCS_PATH : df0 , df1 , df2 , df3 , y 
[ df0 , df1 , df2 , df3 , y ] = [ pd.read_csv(DOCS_PATH / file) for file in CSV_FILES ]

# Concaténer les DataFrames df0, df1 df2 , df3  en un seul DataFrame df_final , pas de colonne d'index 
df_final = pd.concat([df0, df1, df2, df3], ignore_index=True)

# Fusionner les DataFrames df_final et y en utilisant la colonne "date" comme clé de fusion 
df_merged = pd.merge(df_final, y, on="date", how="inner")

# supprimer les lignes avec des valeurs manquantes
df_merged = df_merged.dropna() 

# selection des données d'entrainement et de test (X_train , X_test , y_train , y_test) : l'entrainement c'est les dates entre 01/10/2019 et 31/05/2022 et le test c'est les dates entre 01/10/2022 et 31/05/2023
X_train = df_merged.loc[(df_merged["date"] >= "2019-10-01") & (df_merged["date"] <= "2022-05-31")].drop(["date", "gelee_blanche_vehicule_presence"], axis=1)
X_test = df_merged.loc[(df_merged["date"] >= "2022-10-01") & (df_merged["date"] <= "2023-05-31")].drop(["date", "gelee_blanche_vehicule_presence"], axis=1)
y_train = df_merged.loc[(df_merged["date"] >= "2019-10-01") & (df_merged["date"] <= "2022-05-31"), "gelee_blanche_vehicule_presence"]
y_test = df_merged.loc[(df_merged["date"] >= "2022-10-01") & (df_merged["date"] <= "2023-05-31"), "gelee_blanche_vehicule_presence"]

# Créez le modèle Random Forest avec les paramètres donnés : maximisation de la précision avec un score f1 >= 0.66 pendant l'entrainement
rand_forest_precision_max = RandomForestClassifier(class_weight=RAND_FOREST_PRECISION_MAX["class_weight"], 
                                                   min_samples_leaf=RAND_FOREST_PRECISION_MAX["min_samples_leaf"], 
                                                   n_estimators=RAND_FOREST_PRECISION_MAX["n_estimators"], 
                                                   n_jobs=10)

# Créez le modèle Random Forest avec les paramètres donnés : maximisation du rappel avec un score f1 >= 0.66 pendant l'entrainement
rand_forest_recall_max = RandomForestClassifier(class_weight=RAND_FOREST_RECALL_MAX["class_weight"],
                                                min_samples_leaf=RAND_FOREST_RECALL_MAX["min_samples_leaf"], 
                                                n_estimators=RAND_FOREST_RECALL_MAX["n_estimators"], 
                                                n_jobs=10)

# Entraînez les modèles sur l'ensemble des données df_merged (X_train + X_test) et y
rand_forest_precision_max.fit(df_merged.drop(["date", "gelee_blanche_vehicule_presence"], axis=1), df_merged["gelee_blanche_vehicule_presence"])
rand_forest_recall_max.fit(df_merged.drop(["date", "gelee_blanche_vehicule_presence"], axis=1), df_merged["gelee_blanche_vehicule_presence"])

# sauvegarder les modèle avec joblib
joblib.dump(rand_forest_precision_max, DOCS_PATH / "rand_forest_precision_max.h5")
joblib.dump(rand_forest_recall_max, DOCS_PATH / "rand_forest_recall_max.h5")