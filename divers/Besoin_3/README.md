# BESOIN 3 : CARACTÉRISATION DE SOURCES DE POLLUTION DE L'AIR

## Description globale

Ce dossier contient tous les codes développées pour le compte du besoin 3. Pour le bon fonctionnement des différents codes il est necessaire d'inclure dans le dossier un fichier de config incluant les différents accès dans `conf/project_config.yml`.

Nous allons dans ce qui suit expliquer le but de chaque fichier de ce dossier ainsi que quelques exemples d'utilisation.

## Codes et Notebooks

Tout d'abord pour le bon fonctionnement des codes et notebooks suivants il faut installer toutes les librairies présentes dans requirements.txt. Pour ce faire, il faut lancer la commande suivante avec la dernière version de pip :

```
pip install requirements.txt
```

### queries.py

Ce script contient les différentes requêtes SQL pour créer l'ensemble des tables de notre base de données Postgres que nous avons mis en place. Le but de cette BDD est de stocker les résultats des regresseurs mis en place. Ce stockage nous a facilité l'exploitation et la visualisation des données ur le dashboard temps réel. Un schéma de données détaillé a été crée il peut être consulté sur [ce lien](https://docs.google.com/spreadsheets/d/1mbt_d9gjwe7ri43_dl1RgkTNej63654jKYfW58e9BQ8/edit?usp=sharing).

### create_db.py

Ce script contient l'ensemble des fonctions crées pour récupérer des fichiers depuis le dépôt de données owncloud, lancer une CMB sur une période donnée à l'aide de Lasso ou ODR et stocker ses résultats dans la base de données, calculer la reconstitution du signal ainsi que l'erreur commise par la CMB. L'ensemble de ces fonctions sont utilisées dans le fichiers `heka/tasks/run_cmb/src/run_cmb.py`. La [note technique](https://drive.google.com/file/d/1DGXGSbXNFyN_gR5uG7rM7C7cAqbA9C7E/view?usp=sharing) explique la pipeline entière des données.


### CMB_timeseries.ipynb

Ce notebook présente les résultats préliminaires du test d'une méthode CMB qui inclut une vision timeseries. Cette méthode est expliquée dans la [note technique](https://drive.google.com/file/d/1DGXGSbXNFyN_gR5uG7rM7C7cAqbA9C7E/view?usp=sharing).
Pour ce test, il faut avoir les identifiants de la BDD postgres (user, password, host, database_name) qu'il faut renseigner directement dans l'entête du notebook.
Ce notebook utilise aussi les profils de pollution d'une banque d'une dizaine de polluants. Ces deniers sont stockés dans le fichier `pmf_profiles.xlsx`.
