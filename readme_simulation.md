# Fly-in — Roadmap du système de simulation des drones

## Objectif

Mettre en place progressivement le moteur de simulation en prenant en compte :

- les chemins possibles issus du graphe ;
- les zones et leurs métadonnées ;
- les connexions et leurs capacités ;
- le nombre de drones ;
- les zones restricted ;
- les priorités ;
- les situations de blocage.

Le moteur de simulation doit rester séparé du renderer Pygame.

### Architecture

```
Parsing
   |
   v
Network / Graph
   |
   v
PathFinder
   |
   v
Scheduler
   |
   v
Simulation
   |
   v
Renderer Pygame
```

---

## 1. Chemin le plus court

### Objectif

Chaque drone doit commencer par rechercher le chemin le plus court entre sa zone de départ et sa destination.

Le pathfinding fournit plusieurs chemins possibles.

Exemple :

```
START ---- A ---- B ---- GOAL
   \              /
    \---- C ------/
```

```python
paths = [
    ["START", "A", "B", "GOAL"],
    ["START", "C", "B", "GOAL"]
]
```

Le drone conserve son chemin :

```python
drone.path
drone.path_index
drone.current_hub
```

À chaque tour :

```
Position actuelle
       |
       v
Prochaine zone
       |
       v
Peut-on y aller ?
```

Si oui : `MOVE`

Sinon, on passe aux vérifications suivantes.

### À implémenter

- récupérer les paths du graphe ;
- les classer ;
- sélectionner le chemin le plus court ;
- attribuer un chemin au drone ;
- suivre `path_index`.

---

## 2. Capacité des zones

### Objectif

Une zone peut limiter le nombre de drones présents simultanément.

Exemple :

```python
hub.max_drones = 2
```

Si la zone contient déjà deux drones :

```
D1
D2
---
FULL
```

Alors :

```
D3 -> WAIT
```

### Vérification

```python
if next_hub.current_drones < next_hub.max_drones:
    # déplacement possible
else:
    # zone pleine
```

> Une zone pleine ne signifie pas automatiquement que le drone doit abandonner son chemin.
> Il faut ensuite rechercher une route alternative ou attendre.

---

## 3. Capacité des connexions

### Objectif

Une connexion peut limiter le nombre de drones pouvant l'utiliser.

Exemple :

```python
connection.max_capacity = 1
```

Si :

```
D1 ---------> A
```

utilise déjà la connexion :

```
D2 ---------> A   X
```

### Vérification

```python
if connection.current_drones < connection.max_capacity:
    # connexion disponible
else:
    # connexion pleine
```

### Important

Il faut vérifier deux ressources :

```
ZONE
+
CONNECTION
```

Le déplacement est autorisé uniquement lorsque les deux sont disponibles.

```
Zone disponible
      AND
Connexion disponible
      |
      v
    MOVE
```

---

## 4. Choix d'un autre path

### Objectif

Si le chemin principal est temporairement bloqué, le drone peut utiliser un autre chemin valide.

Exemple :

```
              A ---- B
             /        \
START -------           ------- GOAL
             \        /
              C ---- D
```

```python
path_1 = ["START", "A", "B", "GOAL"]
path_2 = ["START", "C", "D", "GOAL"]
```

Si :

```
A = FULL
```

Le scheduler peut essayer :

```
START -> C
```

### Ordre

1. chemin actuel
2. deuxième meilleur chemin
3. troisième meilleur chemin
4. ...

> Mais il ne faut pas forcément changer de chemin à chaque blocage temporaire.

Le scheduler doit comparer :

```
WAIT
```

avec :

```
ALTERNATIVE PATH
```

---

## 5. Plusieurs drones

### Objectif

Gérer plusieurs drones simultanément sans dépasser les capacités du réseau.

Exemple :

```
Nombre de drones = 4
A.max_drones = 2
```

Tour 1 :

```
D1 -> A
D2 -> A
D3 -> WAIT
D4 -> WAIT
```

Tour 2, si D1 et D2 quittent A :

```
D3 -> A
D4 -> A
```

### État recommandé

```python
class Drone:
    id
    current_hub
    path
    path_index
    state
    remaining_turns
```

États possibles :

```
WAITING
MOVING
TRANSIT
ARRIVED
BLOCKED
```

### Planification

Les décisions doivent être préparées avant d'appliquer les mouvements :

```
PLAN
  |
  +-- D1
  +-- D2
  +-- D3
  +-- D4
  |
  v
VALIDATE
  |
  v
APPLY MOVES
```

Cela évite qu'un drone traité plus tôt bénéficie artificiellement d'une capacité qui n'était pas disponible au début du tour.

---

## 6. Restricted = 2 tours

### Objectif

Une zone restricted possède un comportement particulier.

Le passage doit prendre deux tours selon les règles du projet.

Le drone doit donc posséder un état de transit :

```python
drone.state = "TRANSIT"
drone.remaining_turns = 2
```

Exemple :

```
Tour 1
D1 -> restricted
remaining_turns = 2

Tour 2
remaining_turns = 1

Tour 3
D1 arrive
```

> Le drone ne doit pas être considéré comme normalement installé dans la zone suivante pendant son transit.

---

## 7. Priority

### Objectif

Lorsque plusieurs drones veulent utiliser une même ressource limitée, il faut déterminer lequel est traité en premier.

Exemple :

```
D1 -> A
D2 -> A
D3 -> A
```

avec :

```python
A.max_drones = 1
```

Un seul drone peut avancer.

Prévoir une fonction dédiée :

```python
def get_priority(drone):
    ...
```

Puis :

```python
ordered_drones = sorted(
    drones,
    key=get_priority
)
```

> La règle exacte de priorité doit suivre les métadonnées et les règles du sujet.

---

## 8. Blocked

### Objectif

Un drone est `BLOCKED` lorsqu'il ne peut pas progresser pendant le tour et qu'aucune route alternative immédiate n'est disponible.

Exemple :

```
D1
 |
 v
A FULL
 |
 v
B FULL
 |
 v
C FULL
```

Alors :

```
D1 -> BLOCKED
```

> Mais BLOCKED ne signifie pas forcément une erreur.

Au tour suivant :

```
BLOCKED
   |
   v
recalculer
   |
   +--> MOVE
   |
   +--> ALTERNATIVE PATH
   |
   +--> WAIT
```

---

## Ordre général de décision

```
1. Drone arrivé ?
       |
       +-- oui --> ARRIVED
       |
       +-- non
            |
            v
2. Drone en transit ?
       |
       +-- oui --> update_transit()
       |
       +-- non
            |
            v
3. Quelle est la prochaine zone ?
            |
            v
4. Zone disponible ?
            |
            +-- oui
            |     |
            |     v
            |  5. Connexion disponible ?
            |     |
            |     +-- oui --> MOVE
            |     |
            |     +-- non --> alternative
            |
            +-- non --> alternative
                              |
                              v
                    autre path disponible ?
                       |
              +--------+--------+
              |                 |
             oui               non
              |                 |
              v                 v
         RE-ROUTE             WAIT
```

---

## Scheduler — Pseudo-code

```python
for drone in drones:

    if drone.state == ARRIVED:
        continue

    if drone.state == TRANSIT:
        update_transit(drone)
        continue

    next_hub = get_next_hub(drone)

    if can_move(drone, next_hub):
        schedule_move(drone, next_hub)
        continue

    alternative = find_alternative_path(drone)

    if alternative is not None:

        switch_path(drone, alternative)

        next_hub = get_next_hub(drone)

        if can_move(drone, next_hub):
            schedule_move(drone, next_hub)
        else:
            drone.state = BLOCKED

    else:
        drone.state = BLOCKED
```

---

## Organisation recommandée

```
simulation/
├── drone.py
├── pathfinder.py
├── scheduler.py
└── simulation.py
```

| Fichier | Responsabilité |
|---------|----------------|
| `drone.py` | État individuel du drone. |
| `pathfinder.py` | Chemins possibles. |
| `scheduler.py` | Décisions : capacité des zones, capacité des connexions, priorité, choix des chemins, blocages. |
| `simulation.py` | Tours et état global. |

---

## Ordre d'implémentation

### Phase 1 — Pathfinding
- récupérer les chemins ;
- les classer ;
- choisir le plus court ;
- attribuer le chemin au drone.

### Phase 2 — Zones
- compter les drones ;
- appliquer `max_drones` ;
- empêcher l'entrée dans une zone pleine.

### Phase 3 — Connexions
- compter les drones en transit ;
- appliquer `max_capacity` ;
- bloquer les connexions saturées.

### Phase 4 — Alternative paths
- rechercher un autre chemin ;
- vérifier sa faisabilité ;
- changer de route si nécessaire.

### Phase 5 — Plusieurs drones
- gérer les états individuels ;
- réserver les ressources ;
- planifier le tour ;
- appliquer les mouvements.

### Phase 6 — Restricted
- ajouter le transit ;
- ajouter `remaining_turns` ;
- gérer les deux tours.

### Phase 7 — Priority
- définir la priorité ;
- trier les demandes ;
- résoudre les conflits.

### Phase 8 — Blocked
- ajouter l'état `BLOCKED` ;
- réessayer au tour suivant ;
- détecter les situations sans progression.

---

## Critères de validation

| # | Test | Détail | Résultat attendu |
|---|------|--------|-------------------|
| 1 | Chemin simple | `START -> A -> GOAL` | Le drone doit suivre le chemin. |
| 2 | Zone pleine | `A.max_drones = 1`, `D1, D2 -> A` | `D1 -> A`, `D2 -> WAIT` |
| 3 | Connexion pleine | `connection.max_capacity = 1` | Un seul drone utilise la connexion. |
| 4 | Route alternative | A indisponible, B disponible | `D1 -> B` |
| 5 | Plusieurs drones | — | Aucune capacité ne doit être dépassée. |
| 6 | Restricted | — | Le passage doit respecter les deux tours. |
| 7 | Priority | — | Les conflits doivent être résolus de manière déterministe. |
| 8 | Blocked | — | Un drone bloqué doit pouvoir reprendre dès qu'une ressource devient disponible. |

---

## Principe fondamental

Le renderer Pygame **ne décide jamais** du déplacement.

- Le **moteur** décide : *« Le drone peut-il avancer ? »*
- La **simulation** décide : *« Quel est son état après ce tour ? »*
- **Pygame** affiche : *« Voilà l'état actuel du réseau. »*
