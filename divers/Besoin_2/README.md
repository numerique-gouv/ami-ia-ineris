# BESOIN 2 : IDENTIFICATION DE SOURCES DE POLLUTION ENVIRONNEMENTALES

## Description globale

Ce dossier contient tous les codes développées pour le compte du besoin 2. Nous allons dans ce qui suit expliquer le but de chaque fichier de ce dossier.

## Codes et Notebooks

### PYTHON

Le version de Python qui a été utilisé pour les scripts et notebook est le 3.7. Pour le bon fonctionnement des codes et notebooks suivants, il faut installer toutes les librairies présentes dans requirements.txt. Pour ce faire, il faut lancer la commande suivante avec la dernière version de pip :

```
pip install requirements.txt
```

### R

Pour les scripts en R, les bibliothèques qui ont été utilisées sont :
- data.table
- readxl
- yaml
- RPostgreSQL


## Dossier "DB_script"

L'ensemble des scripts se focalise sur la récupération des données et la formation de la base.

### extract_EPA_emission_data.R

Ce script permet de récupérer l'ensemble des données EPA Emission. Il extrait à partir des différents fichiers excels (DIOXDB\I-TEFs\DB_EXCEL) tous les substances et valeurs associés qui ont été détectées. Le fichier EPA est disponible sur ce [lien](https://drive.google.com/file/d/1-A10fkbXL9D0YIoDPZQn7b7HJXtl7vYd/view?usp=sharing).

### construction_base_epa_emission.R

Après avoir executé le premier script d'extraction, ce second script récupère les données puis les concaténe pour former une unique base de données.

### merge_dataset.py

Ce script se focalise sur la fusion des données EPA "Bruit de fond" et "Emission". Il se connecte directement à la base de données et fusionne les deux datasets pour en former qu'une seule base.



## Dossier "notebook"

Ce dossier "notebook" est composé de deux types de fichier :
- les notebooks au format "ipynb" qui contiennent l'ensemble des analyses, figures et graphiques du besoin 2
- les données utilisées par les notebooks au format "csv"
Par ailleurs, dans chacun de ces notebooks, la première cellule contient des informations pour faire tourner le notebook (données à utiliser et bibliothèques nécessaires) et la structure de celui-ci. Dans le cas, si les données INERIS ne sont pas disponibles, vous pouvez les trouver directement sur ce [lien](https://drive.google.com/file/d/13OzUZpmUHSWnDSfIaliTND_TrtWdiIQ5/view?usp=sharing).

### Notebooks d'explorations

Les notebooks d'explorations correspondent aux notebooks suivants :
- 1_Besoin_2_exploration_EPA_BDF.ipynb
- 2_Besoin_2_exploration_EPA_emission.ipynb
- 3_Besoin_2_exploration_Ineris.ipynb
- 3_bis_Besoin_2_Exploration_Ineris.ipynb

Ils se focalisent sur des analyses simples des données en entrée avec, par exemple, une analyses de la volumétrie ou la mise en place de boîtes à moustaches. 

### Notebooks sur les données EPA

Le second groupe de notebooks étudie les données EPA ("Bruit de fond" et "Emission") en essayant de regrouper les échantillons selon certaines variables (source d'émission, saison, type de sol) ou, au contraire, de trouver une nouvelle classification pour des classes très large. Les notebooks concernés sont :
- 4_Besoin_2_Classifieur_EPA_bdf.ipynb
- 5_Besoin_2_Classification_EPA_Emission_vs_BDF.ipynb
- 5_bis_Besoin_2_Classification_EPA_Emission_vs_BDF.ipynb

### Notebooks sur les données INERIS

Le dernier groupe de notebook analyse les données INERIS. Pour cela, des comparaisons avec les données EPA sont réalisées dans le premier notebook de la liste puis se focalise dans les notebooks suivants sur des comparaisons internes entre les échantillons INERIS. La liste de ces notebooks est la suivante :
- 6_Besoin_2_Comparaison_Ineris_vs_EPA.ipynb
- 7_Besoin_2_Profil_Ineris.ipynb
- 8_a_Besoin_2_Pistes_exploration_1.ipynb
- 8_b_Besoin_2_Pistes_exploration_2.ipynb