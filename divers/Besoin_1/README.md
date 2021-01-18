# BESOIN 1 : IDENTIFICATION DE SUBSTANCES DANS DES PRELVÉS AQUEUX

## Description globale

Ce dossier contient tous les codes développées pour le compte du besoin 1. Pour le bon fonctionnement des différents codes (à part le notebook de training des modèles) il est necessaire d'inclure dans le dossier un fichier de config incluant les différents accès dans `conf/project_config.yml`.

Nous allons dans ce qui suit expliquer le but de chaque fichier de ce dossier ainsi que quelques exemples d'utilisation.

## Codes et Notebooks

Tout d'abords pour le bon fonctionnement des codes et notebooks suivants il faut installer toutes les librairies présentes dans requirements.txt. Pour ce faire, il faut lancer la commande suivante avec la dernière version de pip :

```
pip install requirements.txt
```

Pour la manipulation des fichiers du logiciel constructeur dont l'extension est .sdf , il faudrait aussi installer la librairie RDKit. Cette dernière ne pouvant pas être installée à l'aide de pip, nous redirigeons le lecteur vers [ce lien](https://www.rdkit.org/docs/Install.html) pour l'installer.


### Training_models.ipynb

Ce notebook présente une analyse exploratoire des données ainsi que les différents modèles entrainés et retenus pour le projet. Nous avons retenu en fin de projet deux modèles. La [note technique](https://drive.google.com/file/d/1DGXGSbXNFyN_gR5uG7rM7C7cAqbA9C7E/view?usp=sharing) comprends une bonne explication de notre démarche d'obtention du dataset d'entraînement ainsi que plusieurs commentaires sur les différents graphes présents sur ce notebook.

Pour que les performances du notebook soient reproduisibles nous incluons dans ce même dossier les données d'entraînement pour les deux modèles : 
* all_data_in_independant_mode_without_lvl_3.csv
* INERIS_data_in_indepndant_mode_without_lvl_3.csv

Ces données comprennent les scores de similarité de recherche de molécules dans des fichiers mzml. Les molécules ainsi que les sites de prélèvement des fichiers mzml ont été anonymisés en utilisant des id_molecule et id_mzml.
La [note technique](https://drive.google.com/file/d/1DGXGSbXNFyN_gR5uG7rM7C7cAqbA9C7E/view?usp=sharing) explique les différentes caractéristiques de ces ensembles de données.

### queries.py

Ce script contient les différentets requêtes SQL pour créer l'ensemble des tables de notre base de données Postgres que nous avions mis en place. Le but de cette BDD est de faciliter l'exploitation des données extraits des fichiers mzml en les stockant dans une base de données relationnelle plutôt que de devoir les extraire à chaque fois. Un schéma de données détaillé a été crée il peut être consulté sur [ce lien](https://docs.google.com/spreadsheets/d/1TqPdfl_ilPgvDi2MUsKZfhdqzLQvKiOTs1I44njSbkI/edit#gid=0).

### create_db.py

Ce script contient l'ensemble des fonctions crées pour traiter les fichiers mzml lors d'une recherche d'une molécule donnée dans un fichier mzml. Les différentes fonctions contiennent des doc strings expliquant ce qu'elles font. L'ensemble de ces fonctions sont utilisées dans les fichiers `heka/tasks/launch_analysis/src/launch_analysis.py` et `heka/tasks/upload_mzml/src/uplaod_mzml.py` . La [note technique](https://drive.google.com/file/d/1DGXGSbXNFyN_gR5uG7rM7C7cAqbA9C7E/view?usp=sharing) explique la pipeline entière des données.
