# Rapport de performances

## Objectif

Vérifier les exigences de la phase 2 du projet (guide de développement, point 5) :

- récupérer la liste des compétitions en moins de **5 secondes** ;
- mettre à jour le total de points en moins de **2 secondes**.

## Méthode

- Outil : Locust 2.47.0
- Scénario : `tests/performance/locustfile.py`. Un secrétaire se connecte et consulte la liste des compétitions (poids 3), achète une place (poids 1) et consulte le tableau public des points (poids 1).
- Charge : **6 utilisateurs** (valeur par défaut du guide), 1 nouvel utilisateur par seconde, durée de **1 minute**.
- Serveur : `python -m flask --app server run`, sans mode debug, en local.
- Environnement : Windows, Python 3.14.7.
- Date du test : 25 octobre 2026.

Commande utilisée :

```
python -m locust -f tests\performance\locustfile.py --host http://127.0.0.1:5000 --users 6 --spawn-rate 1 --run-time 1m --headless --html reports\performance_report.html --csv reports\performance
```

## Résultats

Temps de réponse en millisecondes.

| Requête | Nombre | Échecs | Moyenne | Médiane | 95e centile | Maximum |
|---|---|---|---|---|---|---|
| Page d'accueil (`/`) | 6 | 0 | 11 | 5 | 48 | 48 |
| Liste des compétitions (`/showSummary`) | 111 | 0 | 4 | 4 | 12 | 24 |
| Mise à jour des points (`/purchasePlaces`) | 33 | 0 | 8 | 4 | 25 | 115 |
| Tableau public (`/pointsDisplay`) | 30 | 0 | 4 | 3 | 9 | 15 |
| **Ensemble** | **180** | **0** | **5** | **4** | **15** | **115** |

Débit moyen : 3,12 requêtes par seconde.

## Comparaison avec les exigences

| Exigence | Limite | Temps maximal mesuré | Conforme |
|---|---|---|---|
| Liste des compétitions | 5 000 ms | 24 ms | Oui |
| Mise à jour des points | 2 000 ms | 115 ms | Oui |

## Limites de la mesure

- Le test est réalisé en local, avec le serveur de développement de Flask, donc sans temps de réseau.
- Les données sont en mémoire. Le club de test (Simply Lift) a 13 points et la limite est de 12 places par compétition, donc au plus 12 achats ont abouti. Les achats suivants ont été refusés avec un message d'erreur (réponse 200), ce qui est généralement plus rapide qu'un achat réussi. Il faut redémarrer le serveur avant chaque test.
- 6 utilisateurs correspondent à la charge demandée par le guide, ce n'est pas un test de charge maximale.
- À l'arrêt, Locust a affiché `ValueError: I/O operation on closed file` pendant l'écriture des fichiers CSV (problème connu sous Windows). Le test était terminé, le code de sortie est 0 et le rapport HTML a bien été généré.

## Fichiers

- `reports/performance_report.html` : rapport généré par Locust, avec graphiques.
- `reports/performance_stats.csv` : statistiques brutes.