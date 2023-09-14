# aero  


Développer un modèle de prévision de gelée blanche véhicule pour Roissy.

## Architecture du Projet "aero"

### Dossiers et Fichiers

- aero/
  - __init__.py                  # Fichier d'initialisation du package aero
  - settings.py                  # Fichier de configuration et constantes du projet

- bin/
  - preprocessing/
    - pre_processing_obs.py      # Script de prétraitement des données d'observation
    - preprocessing_fichiers_grib.py # Script de collecte de données météorologiques depuis les fichiers grib
  - training/
    - train_with_random_forest.py # Scripts pour entraîner des modèles Random Forest

- images/                        # Dossier pour stocker les images du projet

- notebooks/
  - analyse_de_donnees_observations.ipynb    # Notebook d'analyse des données d'observation
  - entrainement_et_evaluation.ipynb         # Notebook d'entraînement et d'évaluation des modèles
  - score_previsionnistes.ipynb              # Notebook pour calculer les scores de prévision

- README.md                       # Description du projet


## Prétraitement des données


Les scripts ci dessous éffectuent tour à tour  : 

- [ ] **pre_processing_obs.py**

Collecte des données des fichiers observations situés dans **"/scratch/labia/tchoffoc/data/gelee_blanche_fichiers_corrects/"**. 

Ensuite traitements des données :suppréssion de données manquantes , ajout de nouveaux prédicteurs. finalement nous obtenons 2 nouveaux fichiers : **donnees_obs_predicteurs_temporels_gelee_blanche.csv**(fichier de colonnes : ['gelee_blanche_vehicule_presence', 'H_obs-H_lever_soleil',
       'H_obs-H_coucher_soleil', 'heure_utc', 'mois_utc', 'date'] ) et **obs_gelee_blanche.csv** (qui contient uniquement les prédicteurs **date** et **gelee_blanche_vehicule_presence**)  enregistrés tous les 2 dans le dossier : **"/scratch/labia/tchoffoc/data/donnees_mises_en_forme/"** 



- [ ] **pre_processing_fichiers_grib.py**

la  fonction **process_grib_files** traite des fichiers au format GRIB qui contiennent les données météorologiques, extrait les données de ces fichiers, les transforme en DataFrames, puis les concatène et les enregistre au format CSV. 

Nous appelons ensuite cette fonction sur l'ensemble des données d'entrée  et lui fournissons une sortie où elle stockera nos fichiers CSV. 
Nous obtenons en sortie les fichiers suivants : **donnees_fichiers_grib_2019_2020.csv ,donnees_fichiers_grib_2020_2021.csv ,  donnees_fichiers_grib_2021_2022.csv , donnees_fichiers_grib_2022_2023.csv**  
qui sont ici les données météorologiques pour l'ensemble des 4 années. Elles consisteront ici l'éssentiel de nos données d'entrainement. 
Tous ces fichiers sont enregistrés dans le même dossier que les précédents fichiers générés. 

### Comment lancer ces fichiers : 

tout d'abord ajouter cette ligne au .bashrc : 
       **export PYTHONPATH='/home/labia/tchoffoc/aero/'** là personnaliser à votre façon.
Se placer à la racine du projet et faire dans le terminal : \



`python  bin/preprocessing/pre_processing_obs.py` pour le fichier  **pre_processing_obs.py** \
`python  bin/preprocessing/pre_processing_fichiers_grib.py` pour le fichier pour **pre_processing_fichiers_grib** :


## Entrainement du modèle

Nous sommes partis dans un premier sur un modèle de Random Forest. 

- **Ensemble de données :**  \
Données issues de la jointure naturelle des données météoroligues et ceux du fichier **donnees_obs_predicteurs_temporels_gelee_blanche.csv** suivant la colonne **date**.

  - **Features** : ['sshf', 'r2', 'hcc', 'paramId_0', 'd2m', 'mcc', 't2m', 'str', 'u10',
       'slhf', 'prmsl', 'v10', 'lcc', 'ssr', 'H_obs-H_lever_soleil',
       'H_obs-H_coucher_soleil', 'heure_utc', 'mois_utc']

  - **Target** : "gelee_blanche_vehicule_precense" : booléen 

- **Données d'entrainement :** \
Nous utilisons ici les données du : 01/10/2019 au 31/05/2022 : données sur 3 ans. la 4ème année pour le test à la fin. 

Nous avons décidé d'implementer  une validation croisée personalisée afin d'optimiser les hyperparamètres de notre modèle qui sont : 

-  n_estimators :  il s'agit du nombre d'arbres dans la forêt
- class_weight : poids attribué à chaque classe 
-  min_sample_leaf : le nombre minimun d'echantillons requis dans une feuille pour que l'arbre continue de se diviser.

**Principe :** \
Sur les trois années  nous utilisons 2 annnées pour l'entrainement et une année pour la validation. celà fait donc 3 trains.
Pour chaque combinaison d'hyperparamètres, le modèle est formé sur les données d'entraînement, évalué sur les données de validation.  Les scores obtenus sur (predictions(train1,train2,train3) , valeurs réelles(train1,tran2,train3)) sont ensuite collectés pour sélectionner les meilleures combinaisons d'hyperparamètres.

 Précison , Recall et score-f1 calculés sur la classe 1. 

*  Analyse et interprétation 

Au terme de la validation croisée nous constatons que ce qui influence effectivement la performance du modèle est le paramètre min_sample_leaf  :
       
       - plus il est bas et plus on a une bonne précision 
       - pour un peu grand on a un bon recall 


Nous constatons que le paramètre n_estimators n'a pas une réelle importance sur les performance du modèle. 
En effet nous n'observons pas  une grande  variation des performances lorsque le nombre d'estimateurs varie.
Nous allons le fixer donc à une valeur par de 100 pour tous nos modèles.

     -  n_estimators = 100

Nous faisons tout de même varier les poids des classes.

Nous retenons 2 modèles : 

    - l'un qui maximise  la précision avec un score f1 >= à celui des prévisionnistes. 
![Capture d'écran](/images/modele_rf_precision_max.png)


`class_weights = {0: 1, 1: 5},
min_samples_leaf = 2,
n_estimators = 100
`

       - l'un qui maximise  le recall  avec un score f1 >= à celui des prévisionnistes.
![Capture d'écran](/images/modele_rf_recall_max.PNG)

`class_weights = {0: 1, 1: 25},
min_samples_leaf = 25,
n_estimators = 100`


### Comment lancer le fichier train_with_random_forest.py 

 Script qui  génère nos 2 modèles : 

     - rand_forest_precision_max.h5 et  rand_forest_recall_max.h5

Se placer à la racine du dossier principal et taper dans le terminal : 

`python  bin/training/train_wih_random_forest.py ` si .bashrc mis à jour 

## Test du modèle 

données de test la 4ème année : données du 01/10/2022 au 31/05/2023

       -   Matrice de confusion et rapport de classification pour les 2 différents modèles de random forest. 

- modèle de maximisation de la précision

![Capture d'écran](/images/matrice_confusion_rfp.png)


Rapport de classification : 

              precision    recall   f1-score    support

           0       0.97      0.97       0.97      5174
           1       0.67      0.68       0.68       421

    accuracy                            0.95      5595
    macro avg       0.82      0.83      0.82      5595
    weighted avg    0.95      0.95      0.95      5595


- modèle de maximisation du Recall


![Capture d'écran](/images/matrice_confusion_rfr.png)


Rapport de classification : 

              precision    recall  f1-score   support

           0       0.99      0.89      0.94      5018
           1       0.43      0.93      0.59       431

    accuracy                           0.90      5449
    macro avg       0.71      0.91     0.77      5449
    weighted avg    0.95      0.90     0.91      5449


