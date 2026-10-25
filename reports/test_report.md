# Rapport de test

## Résumé

| Indicateur | Valeur |
|---|---|
| Tests exécutés | **63** |
| Tests réussis | **63** |
| Tests échoués | 0 |
| Tests d'intégration | 21 |
| Tests unitaires | 42 |
| Tests fonctionnels | 0 |
| Couverture de `server.py` | **99 %** (objectif du guide : 60 %) |
| Durée d'exécution | moins d'une seconde |

Le guide de développement demande deux fois plus de tests unitaires que de tests d'intégration ou fonctionnels : 42 tests unitaires pour 21 tests d'intégration, soit exactement le double.

## Environnement

- Python 3.14.7, pytest 9.1.1, pytest-cov 7.1.0
- Date : 25 octobre 2026

## Organisation des tests

| Dossier | Contenu |
|---|---|
| `tests/unit/test_logic.py` | Fonctions isolées : `parsePlaces`, `getPurchaseError`, `isPast`, `loadClubs`, `loadCompetitions` et la constante `MAX_PLACES_PER_COMPETITION`. |
| `tests/integration/test_routes.py` | Routes Flask testées avec le client de test. |
| `tests/conftest.py` | Fixtures partagées : `client` et `sample_data` (données de test fixes, indépendantes des fichiers JSON). |
| `tests/performance/locustfile.py` | Scénario de performance (voir `reports/performance_report.md`). |

## Commande d'exécution

```
python -m pytest -v
python -m pytest --cov=server --cov-report=term-missing
```

## Tests par fonctionnalité

| Fonctionnalité | Chemins nominaux | Chemins d'erreur | Tests |
|---|---|---|---|
| Connexion (`/showSummary`) | email connu | email inconnu sans plantage, message d'erreur affiché | 3 |
| Réservation (`/book`) | page de réservation d'une compétition valide | compétition inconnue, club inconnu, compétition passée | 4 |
| Achat (`/purchasePlaces`) | déduction des points et des places | points insuffisants, plus de 12 places, 12 places cumulées dépassées, plus de places que disponible, compétition inconnue, club inconnu, nombre invalide (vide, texte, zéro, négatif), compétition passée | 12 |
| Tableau public (`/pointsDisplay`) | page publique listant tous les clubs, sans emails | | 1 |
| Déconnexion (`/logout`) | redirection vers l'accueil | | 1 |
| Logique métier (unitaire) | valeurs valides, cas limites | valeurs invalides, erreurs de date | 42 |

## Bogues corrigés

Chaque bogue a été traité sur sa propre branche, avec un test écrit avant la correction (approche TDD).

| Bogue | Branche |
|---|---|
| Lancer `server.py` ne démarrait pas le serveur | `bug/flask-app-startup` |
| Email inconnu : plantage (`IndexError`) | `bug/unknown-email-crash` |
| Les points du club n'étaient pas déduits après un achat | `bug/points-not-deducted` |
| Achat possible au-delà des points du club | `bug/points-overspend` |
| Plus de 12 places réservables dans une compétition | `bug/max-12-places` |
| Surréservation : plus de places achetées que disponibles | `bug/overbooking` |
| Club ou compétition inconnu(e) : plantage dans `book` et `purchasePlaces` | `bug/unknown-club-or-competition` |
| Nombre de places invalide (vide, texte, zéro, négatif) | `bug/invalid-places-number` |
| Réservation possible dans une compétition passée | `bug/past-competitions` |

Phase 2 : `feature/points-board` (tableau public des points) et `feature/performance-tests` (tests Locust).

## Couverture

`server.py` : 92 instructions, 1 non couverte (99 %). La seule ligne non couverte est `app.run(debug=True)`, le lancement manuel du serveur, qui ne se teste pas automatiquement.

## Limites connues

- Aucun test fonctionnel automatisé (parcours complet dans un navigateur). Le parcours de réservation et la page du tableau public ont été vérifiés manuellement.
- Les données sont gardées en mémoire. Le suivi des 12 places maximum par club et par compétition (`bookedPlaces`) est remis à zéro au redémarrage du serveur, comme les points et les places des compétitions.
- Les dates des compétitions dans `competitions.json` ont été repoussées à 2027 pour que les réservations restent possibles. Elles devront être mises à jour quand ces dates seront passées.