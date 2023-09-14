import xarray as xr
import pandas as pd
import random
import glob
from aero.settings import INPUT_PATH, OUTPUT_PATH

def process_grib_files(input_path, output_path, year_start, year_end):
    # Liste pour stocker les noms des fichiers qui n'ont pas pu être ouverts
    fichiers_non_ouverts = []

    # Liste pour stocker les DataFrames individuels
    dfs = []

    # Parcourir les années spécifiées
    for year in range(year_start, year_end):
        # Chemin d'accès aux fichiers GRIB pour l'année en cours
        chemin_grib = f'{input_path}/{year}_{year+1}/'

        # Parcourir les dates de l'année (du 1er octobre au 31 mai)
        date_debut = pd.to_datetime(f"{year}100112", format="%Y%m%d%H")
        date_fin = pd.to_datetime(f"{year+1}053112", format="%Y%m%d%H")

        for date_actuelle in pd.date_range(date_debut, date_fin, freq='D'):
            date_str = date_actuelle.strftime("%Y%m%d%H")

            # Utiliser glob pour obtenir la liste des fichiers GRIB pour la date actuelle
            fichiers_grib = glob.glob(f'{chemin_grib}{date_str}*.grib')

            # Créer une liste pour stocker les DataFrames pour cette date
            dfs_date = []

            # Traiter chaque fichier GRIB de la liste
            for fichier in fichiers_grib:
                try:
                    # Ouvrir le fichier GRIB en utilisant xarray
                    ds = xr.open_dataset(fichier, engine='cfgrib')

                    # Sélectionner une latitude et une longitude aléatoire
                    latitude = random.randint(0, 3)
                    longitude = random.randint(0, 5)

                    # Obtenir la liste des variables dans le fichier GRIB
                    variables = list(ds.data_vars)

                    # Créer un DataFrame pour chaque fichier GRIB
                    df = pd.DataFrame()

                    for variable in variables:
                        valeurs_variable = ds[variable].isel(latitude=latitude, longitude=longitude).values.flatten()
                        df[variable] = valeurs_variable

                    # Fermer le fichier GRIB ouvert
                    ds.close()

                    # Ajouter le DataFrame à la liste des DataFrames pour cette date
                    dfs_date.append(df)

                except Exception as e:
                    fichiers_non_ouverts.append(fichier)
                    continue

            # Répéter la date pour chaque pas de temps
            nb_pas_temps = len(ds['step'])
            heures = [i for i in range(nb_pas_temps)]
            dates = [date_actuelle + pd.DateOffset(hours=heure) for heure in heures]
            df_date = pd.DataFrame()
            # Ajouter la colonne "date" au DataFrame pour cette date
            df_date['date'] = dates
            dfs_date.append(df_date)

            # Concaténer tous les DataFrames pour cette date en un seul DataFrame
            df = pd.concat(dfs_date, axis=1)

            # Ajouter le DataFrame de cette date à la liste globale des DataFrames
            dfs.append(df)

        # Concaténer tous les DataFrames en un seul DataFrame final
        df_final = pd.concat(dfs, axis=0)
        df_final.dropna(inplace=True)
        df_final.reset_index(drop=True, inplace=True)
        
        # Enregistrer les noms des fichiers non ouverts dans un fichier texte
        with open(f'{output_path}/fichiers_non_ouverts.txt', 'w') as f:
            for fichier in fichiers_non_ouverts:
                f.write(fichier + '\n')

        # Enregistrer le DataFrame final au format CSV
        output_file = f'{output_path}/{year}_{year+1}.csv'
        df_final.to_csv(output_file, index=False)
        dfs = []

process_grib_files(INPUT_PATH, OUTPUT_PATH, 2019, 2023)    