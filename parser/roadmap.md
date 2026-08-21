# Roadmap complet — Projet Fly-in

## 1. Compréhension du projet

Avant de commencer l'implémentation, il est nécessaire de comprendre précisément le fonctionnement du système.

### Concepts principaux

* `Hub`
* `Connection`
* `Drone`
* `Network`
* `Graph`
* `Path`
* `Turn`

### Règles principales

* Les connexions sont bidirectionnelles.
* Une zone `normal` coûte 1 tour.
* Une zone `priority` coûte 1 tour et doit être privilégiée lors du pathfinding.
* Une zone `restricted` coûte 2 tours.
* Une zone `blocked` est inaccessible.
* Les zones possèdent une capacité `max_drones`.
* Les connexions peuvent posséder une capacité `max_link_capacity`.
* Plusieurs drones peuvent se déplacer simultanément.
* Les conflits et les deadlocks doivent être évités.

---

# 2. Parser

Le parser constitue la première couche fonctionnelle du projet.

## 2.1 Lecture du fichier

```text
Fichier
   |
   v
Lecture
   |
   v
Suppression des commentaires
   |
   v
Suppression des lignes vides
```

## 2.2 Parsing des éléments

Le parser doit gérer :

* `nb_drones`
* `start_hub`
* `end_hub`
* `hub`
* `connection`

## 2.3 Parsing des métadonnées

Exemple :

```text
hub: A 2 3 [zone=restricted color=red max_drones=2]
```

Doit produire un objet équivalent à :

```python
Hub(
    name="A",
    x=2,
    y=3,
    zone_type="restricted",
    color="red",
    max_drones=2,
)
```

## 2.4 Validation

Le parser doit notamment vérifier :

* `nb_drones` est un entier positif ;
* il existe exactement un `start_hub` ;
* il existe exactement un `end_hub` ;
* les noms des hubs sont uniques ;
* les coordonnées sont des entiers ;
* les types de zones sont valides ;
* les capacités sont des entiers positifs ;
* les connexions référencent des hubs existants ;
* les connexions dupliquées sont interdites ;
* les métadonnées respectent la syntaxe attendue ;
* les erreurs indiquent la ligne concernée et leur cause.

### Objectif

Pouvoir exécuter :

```python
network = parser.parse()
```

et obtenir un objet `Network` entièrement validé.

---

# 3. Modélisation orientée objet

Les différentes entités du projet doivent être représentées par des classes clairement séparées.

```text
Network
 ├── Hub
 ├── Connection
 └── Drone
```

L'architecture évoluera ensuite vers :

```text
Network
   |
   v
Graph
   |
   v
PathFinder
   |
   v
Scheduler
   |
   v
Simulator
```

Exemple :

```python
@dataclass
class Hub:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1
```

Cette séparation permet de conserver une responsabilité claire pour chaque composant.

---

# 4. Construction du graphe

Une fois le fichier parsé, le `Network` doit être transformé en structure de graphe.

Exemple :

```text
A-B
A-C
B-D
C-D
```

Devient :

```python
{
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C"],
}
```

Créer une classe dédiée :

```python
class Graph:
    ...
```

Elle pourra notamment gérer :

```python
add_hub()
add_connection()
get_neighbors()
```

Aucune bibliothèque spécialisée de graphes ne doit être utilisée, conformément aux contraintes du projet.

---

# 5. Pathfinding avec BFS

La première implémentation de pathfinding doit rester simple.

### Objectif

Trouver un chemin entre :

```text
START
  |
  v
  ?
  |
  v
END
```

en minimisant le nombre de zones traversées.

Exemple de résultat :

```python
[
    "START",
    "B",
    "D",
    "END",
]
```

Créer une classe :

```python
class PathFinder:
    def find_shortest_path(...):
        ...
```

### Objectif de cette phase

Obtenir un BFS fonctionnel avant d'introduire les coûts des zones.

---

# 6. Pathfinding pondéré

Le BFS ne suffit plus lorsque les zones possèdent des coûts différents.

Les coûts définis par le sujet sont :

```text
normal       1
priority     1
restricted   2
blocked      inaccessible
```

Il faut donc rechercher le chemin ayant le coût total minimal plutôt que simplement le nombre minimal de zones.

### Exemple

Chemin 1 :

```text
A -> B -> C

1 + 2 = 3
```

Chemin 2 :

```text
A -> D -> E -> C

1 + 1 + 1 = 3
```

À ce stade, un algorithme comme Dijkstra devient pertinent.

---

# 7. Gestion des zones `priority`

Les zones `priority` ont un coût de 1 tour, mais doivent être privilégiées lors du pathfinding.

Il faut donc définir une stratégie de sélection permettant de départager plusieurs chemins ayant un coût similaire.

Exemple conceptuel :

```text
Critère principal :
    coût total

Critère secondaire :
    préférence pour les zones priority
```

Cette logique doit être intégrée au système de comparaison des chemins.

---

# 8. Recherche de plusieurs chemins

L'objectif du projet n'est pas uniquement de trouver le meilleur chemin.

Il faut également être capable de distribuer les drones sur plusieurs chemins afin d'améliorer le débit global.

Exemple :

```text
             B ----- C
            /         \
START ----- A           END
            \         /
             D ----- E
```

Deux chemins possibles :

```text
Path 1:
START -> A -> B -> C -> END

Path 2:
START -> A -> D -> E -> END
```

Puis répartir les drones :

```text
D1 -> Path 1
D2 -> Path 2
D3 -> Path 1
D4 -> Path 2
```

---

# 9. Gestion des capacités

## 9.1 Capacité des zones

Chaque zone possède :

```text
max_drones
```

La valeur par défaut est `1`.

Exemple :

```text
Hub A
capacity = 2
occupancy = 1
```

Il reste donc une place disponible.

## 9.2 Capacité des connexions

Chaque connexion possède :

```text
max_link_capacity
```

La valeur par défaut est `1`.

Exemple :

```text
Connection A-B
capacity = 2
drones en transit = 1
```

Une place reste disponible.

---

# 10. Gestion des tours

Introduire une représentation d'un tour de simulation :

```python
class Turn:
    ...
```

Chaque tour représente l'état du réseau à un instant donné.

Exemple :

```text
Turn 1

D1 -> A
D2 -> A
D3 attend
```

Puis :

```text
Turn 2

D1 -> B
D2 -> C
D3 -> A
```

Chaque mouvement doit être vérifié avant d'être exécuté.

---

# 11. Gestion des zones `restricted`

Une zone `restricted` nécessite deux tours pour être atteinte.

Le drone occupe donc temporairement la connexion pendant son déplacement.

Exemple conceptuel :

```text
START
  |
  |
  v
  A -------- B
       2 tours
```

Le drone ne peut pas simplement rester sur la connexion en attendant une place.

Il faut donc représenter son état.

Exemple :

```python
class DroneState:
    AT_HUB
    IN_TRANSIT
    WAITING
    DELIVERED
```

---

# 12. Scheduler

Le scheduler constitue l'une des parties centrales du projet.

Son rôle est de déterminer :

> Quel drone doit se déplacer, vers quelle destination et à quel tour ?

Exemple :

```text
D1 -> Path A
D2 -> Path B
D3 -> Path A
D4 -> attendre
```

Le scheduler doit respecter :

* les capacités des zones ;
* les capacités des connexions ;
* les chemins disponibles ;
* les mouvements simultanés ;
* les conflits ;
* les deadlocks ;
* les coûts de déplacement.

---

# 13. Simulation

Créer une classe responsable de l'exécution de la simulation :

```python
class Simulator:
    ...
```

Structure conceptuelle :

```python
while not all_delivered():

    evaluate_moves()

    validate_capacity()

    execute_moves()

    update_drones()

    print_turn()
```

Chaque tour doit produire un état valide du réseau.

---

# 14. Optimisation

L'optimisation doit commencer uniquement lorsque la simulation est correcte.

Les éléments à mesurer sont notamment :

```text
Nombre total de tours
Nombre de drones
Nombre de chemins
Temps d'exécution
Utilisation mémoire
```

## Optimisations possibles

### Cache des chemins

```python
path_cache[start][end]
```

Éviter de recalculer les mêmes chemins.

### Réutilisation du pathfinding

Conserver les résultats déjà calculés lorsqu'ils restent valides.

### Distribution des drones

Améliorer la répartition des drones entre les différents chemins.

### Optimisation de la simulation

Éviter les calculs inutiles à chaque tour.

---

# 15. Visualisation

Commencer par une représentation dans le terminal.

Exemple :

```text
Turn 1

D1 -> roof1
D2 -> corridorA

Turn 2

D1 -> roof2
D2 -> tunnelB

Turn 3

D1 -> goal
D2 -> goal
```

Ensuite, il est possible d'ajouter :

* couleurs ;
* état des hubs ;
* position des drones ;
* connexions ;
* capacités ;
* état des zones.

Le sujet autorise une visualisation terminale ou graphique.

---

# 16. Tests

Créer une structure dédiée :

```text
tests/
├── test_parser.py
├── test_graph.py
├── test_pathfinding.py
├── test_scheduler.py
├── test_simulator.py
└── test_edge_cases.py
```

## Cas à tester

```text
Fichier vide
nb_drones invalide
Hub dupliqué
Start dupliqué
End dupliqué
Connexion inconnue
Connexion dupliquée
Métadonnées invalides
max_drones = 0
max_link_capacity = 0
Zone blocked
Aucun chemin
Deadlock
Grand nombre de drones
```

Les tests doivent également couvrir les cas limites.

---

# 17. Qualité et validation du projet

Effectuer régulièrement les vérifications suivantes :

```bash
flake8 .
```

Puis :

```bash
mypy . \
    --warn-return-any \
    --warn-unused-ignores \
    --ignore-missing-imports \
    --disallow-untyped-defs \
    --check-untyped-defs
```

Et idéalement :

```bash
mypy . --strict
```

Le projet doit également intégrer :

* des annotations de type ;
* des docstrings ;
* une gestion propre des exceptions ;
* des context managers ;
* un `.gitignore` ;
* un `Makefile`.

---

# 18. Benchmark

Tester l'algorithme sur plusieurs catégories de maps :

```text
Easy
Medium
Hard
Challenger
```

Objectifs du sujet :

```text
Easy       < 10 tours
Medium     10–30 tours
Hard       < 60 tours
Challenger ≈ 45 tours
```

Le challenger est optionnel et sert principalement à mesurer les capacités d'optimisation.

---

# Ordre de développement recommandé

Le projet doit être développé progressivement :

```text
                         MAP
                          |
                          v
                       PARSER
                          |
                          v
                       NETWORK
                          |
                          v
                        GRAPH
                          |
                          v
                         BFS
                          |
                          v
                       DIJKSTRA
                          |
                          v
                     MULTI-PATH
                          |
                          v
                      SCHEDULER
                          |
                          v
                     SIMULATOR
                          |
                          v
                      OPTIMIZE
                          |
                          v
                     VISUALIZER
```

## Prochain objectif

Pour le moment, il n'est pas nécessaire de travailler sur le scheduler ou l'optimisation.

Le prochain milestone doit être :

```text
Map valide
    |
    v
Parser
    |
    v
Network
    |
    v
Graph
    |
    v
BFS
    |
    v
Afficher le chemin START -> END
```

Une fois cette étape entièrement fonctionnelle et testée, passer à **Dijkstra**, puis à la gestion des **multi-paths**, et enfin au **scheduling des drones**.
