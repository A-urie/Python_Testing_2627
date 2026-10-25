# Intro
```
Hey,

Je viens de recevoir le rapport de QA pour la phase 1 du projet. Il y a plusieurs bogues, dont un qui fait planter l'application ! 
Malheureusement, je ne suis pas au bureau pour les prochains jours (un de mes enfants est tombé malade ce week-end). 
Je ne sais pas encore quand je pourrai être là dans la semaine. Pourriez-vous prendre en charge la mise en œuvre du projet ? 
Vous devrez régler les bogues de la phase 1 et mettre en œuvre les éléments de la phase 2 (j'ai ajouté le travail de la phase 2 et les bogues de la section “issues” du repo). 

Vous devrez cloner et forker le repo et le mettre en place sur votre machine locale (tout ce dont vous avez besoin se trouve dans le fichier README). 
Ensuite, passez en revue les bogues dans la section des problèmes, puis essayez de reproduire les problèmes sur votre machine locale pour résoudre les bogues et ajouter la gestion des erreurs. 
Pour gagner du temps de configuration, nous utilisons Flask et JSON pour éviter d'utiliser une base de données. 
La plupart des outils dont vous aurez besoin se trouvent dans le fichier requirements.txt dans le repo, 
mais vous devrez installer Flask et notre framework de test préféré, pytest, ainsi que notre outil de test de performance, Locust. 

Vous devrez également préparer un rapport de test et un rapport de performances, 
conformément au guide de développement à la fin des spécifications fonctionnelles ci-jointes. 
Veillez à suivre toutes les directives, car le QA nous reproche de ne pas respecter les normes. 
Vous devez tester de manière approfondie les résultats requis (à la fois les happy paths et les sad paths) pour toutes les fonctionnalités de l'application.  
Je vous encourage également à adopter une approche de TDD, car cela vous aidera à rationaliser votre travail. 

Une fois que vous aurez terminé, nous ferons un examen de ce que vous avez dans la branche QA du code. 
Nous examinerons les rapports et la manière dont vous avez résolu les problèmes, 
nous examinerons votre code et nous testerons la couverture de la nouvelle fonctionnalité. 

Merci !

```

## 1. Why

This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

## 2. Getting Started

Ce projet utilise les technologies suivantes :

* Python 3.x (testé avec Python 3.14.7)
* [Flask](https://flask.palletsprojects.com/) : contrairement à Django, Flask permet d'ajouter uniquement ce dont on a besoin.
* Un [environnement virtuel](https://docs.python.org/3/library/venv.html) (module `venv`, fourni avec Python) : il permet d'installer les bons paquets sans modifier le Python de la machine.

## 3. Installation

1. Cloner le dépôt, puis se placer dans le dossier :

   ```
   git clone https://github.com/A-urie/Python_Testing_2627.git
   cd Python_Testing_2627
   ```

2. Créer l'environnement virtuel :

   ```
   python -m venv venv
   ```

3. Activer l'environnement virtuel. L'invite de commande doit afficher `(venv)`. Pour le désactiver : `deactivate`.

   * Windows (PowerShell) : `.\venv\Scripts\Activate.ps1`
   * macOS et Linux : `source venv/bin/activate`

4. Installer les dépendances :

   ```
   pip install -r requirements-dev.txt
   ```

   `requirements.txt` contient uniquement ce qui est nécessaire à l'application. `requirements-dev.txt` l'inclut et ajoute les outils de développement : pytest, pytest-cov, Locust et flake8. Si une dépendance est ajoutée, il faut mettre à jour ces fichiers (par exemple avec `pip freeze`).

5. Lancer l'application :

   ```
   python -m flask --app server run
   ```

   L'application indique l'adresse à ouvrir dans le navigateur (par défaut `http://127.0.0.1:5000`). Pour se connecter, utiliser une adresse électronique de `clubs.json`, par exemple `john@simplylift.co`.

   Le tableau public des points, accessible sans connexion, se trouve à l'adresse `/pointsDisplay`.

## 4. Current Setup

The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:

* `competitions.json` - list of competitions
* `clubs.json` - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

Remarques :

* Les données sont chargées en mémoire au démarrage. Les achats de places ne sont pas écrits dans les fichiers JSON : redémarrer le serveur remet tout à zéro.
* Les dates des compétitions sont en 2027, car les réservations dans des compétitions passées sont refusées. Elles devront être mises à jour quand elles seront dépassées.

## 5. Testing

Les tests utilisent [pytest](https://docs.pytest.org/). Ils sont rangés par type, comme le demande le guide de développement :

| Dossier | Contenu |
|---|---|
| `tests/unit/` | tests unitaires de la logique (42 tests) |
| `tests/integration/` | tests des routes Flask (21 tests) |
| `tests/performance/` | scénario Locust |
| `tests/conftest.py` | fixtures partagées |

Lancer les tests :

```
python -m pytest -v
```

Mesurer la couverture avec [coverage](https://coverage.readthedocs.io/) (via pytest-cov) :

```
python -m pytest --cov=server --cov-report=term-missing
```

Résultat actuel : **63 tests réussis**, couverture de `server.py` de **99 %** (objectif : 60 %). La seule ligne non couverte est le lancement manuel `app.run(...)`.

Tests de performance avec [Locust](https://locust.io/), 6 utilisateurs. Lancer d'abord le serveur dans un terminal (`python -m flask --app server run`), puis dans un second terminal :

```
python -m locust -f tests\performance\locustfile.py --host http://127.0.0.1:5000 --users 6 --spawn-rate 1 --run-time 1m --headless --html reports\performance_report.html --csv reports\performance
```

## 6. Flake8 Report

Commande :

```
python -m flake8 server.py tests --count --statistics
```

Résultat actuel : **0 problème**, avec la configuration par défaut de flake8 (lignes de 79 caractères maximum).

Au départ, flake8 signalait **74 problèmes de style**, corrigés sur la branche `improvement/flake8-compliance` :

| Code | Description | Nombre |
|---|---|---|
| E501 | ligne trop longue | 28 |
| E302 | deux lignes vides attendues | 18 |
| E231 | espace manquant après une virgule | 12 |
| W292 | pas de retour à la ligne en fin de fichier | 5 |
| E111 | indentation qui n'est pas un multiple de 4 | 4 |
| E117 | indentation excessive | 2 |
| E303 | trop de lignes vides | 2 |
| W293 | ligne vide contenant des espaces | 2 |
| W291 | espaces en fin de ligne | 1 |
| **Total** | | **74** |

## 7. Conventions de travail

Elles suivent le guide de développement des spécifications fonctionnelles.

* `main` est la source de vérité : on n'y fusionne qu'avec tous les tests réussis.
* Une branche par bogue, fonctionnalité ou amélioration, nommée `<bug|feature|improvement>/nom-descriptif` (exemple : `bug/overbooking`).
* Chaque correction commence par un test qui échoue (approche TDD).
* La branche `QA` est créée à partir de `main` pour la revue de code et n'est jamais fusionnée dans `main`.

## 8. Rapports

* [Rapport de test](reports/test_report.md)
* [Rapport de performances](reports/performance_report.md) (rapport Locust complet : `reports/performance_report.html`)