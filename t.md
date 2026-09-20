# Explication complète de `simulation.py`

## Vue d'ensemble

`Simulation` résout un problème d'ordonnancement : plusieurs drones doivent
aller de `start_hub` à `end_hub` en empruntant des chemins (fournis par
l'algorithme de Yen), sans jamais dépasser :

- la **capacité d'une arête** (combien de drones peuvent traverser une
  connexion en même temps) ;
- la **capacité d'un hub** (combien de drones peuvent stationner sur un hub
  à un instant donné).

Le temps est discrétisé en **tours** (entiers).

## Structures de données

```python
self.node_reservations: dict[str, dict[int, int]]
# {nom_hub: {tour: nb_drones_présents}}

self.edge_reservations: dict[tuple[str, str], dict[int, int]]
# {(hub1, hub2): {tour: nb_drones_en_transit}}
```

Ce sont des **compteurs d'occupation** : à chaque tour, on sait combien de
drones utilisent une arête ou occupent un hub. C'est ça qui permet de
détecter les conflits.

```python
self.drones: list[DroneState]          # état final de chaque drone (id + chemin)
self.route_order: list[int]            # index du chemin choisi, par drone
self.scheduled_routes: list[...]       # (chemin, mouvements) par drone — utilisé par le rendu pygame
```

## `__init__`

Deux façons de construire une `Simulation` :

- avec un `Graph` déjà construit ;
- avec une liste de `(distance, chemin)` (sortie de `Graph.yen`) → dans ce
  cas, elle reconstruit elle-même un graphe interne (en filtrant les hubs
  `"blocked"`), et garde les chemins dans `self.all_path` pour
  `run_from_all_path`.

## Les briques de bas niveau

**`_travel_time(destination)`** : combien de tours pour atteindre
`destination` → **2 tours** si zone `"restricted"`, sinon **1 tour**.

**`_edge_capacity(first, second)`** : cherche la `Connection` correspondante
(peu importe le sens) et retourne son `max_capacity`.

**`_can_schedule(first, second, departure, arrival)`** : vérifie si un trajet
est possible sans dépasser les capacités :

```python
# 1. L'arête est-elle pleine à un moment donné entre departure et arrival ?
edge_is_full = any(
    edge_times.get(turn, 0) >= edge_capacity
    for turn in range(departure, arrival)
)
if edge_is_full:
    return False

# 2. Le hub d'arrivée a-t-il de la place au tour d'arrivée ?
#    (sauf si c'est le hub final : pas de limite de "parking" là-bas)
if second == self.end_name:
    return True
return reserved < capacity
```

**`_reserve(...)`** : incrémente les compteurs de `edge_reservations` pour
chaque tour du trajet.

**`_reserve_node_occupancy(movements, max_turns)`** : marque un hub comme
"occupé" depuis l'arrivée du drone jusqu'à son prochain départ (ou jusqu'à
la fin de la simulation si c'est sa dernière étape avant l'arrivée finale).
C'est ce qui simule un drone qui **stationne** sur un hub intermédiaire en
attendant son prochain trajet.

## Le planificateur d'un seul chemin : `_schedule_path`

C'est l'algorithme glouton central, pour **un** drone sur **un** chemin
donné :

```
pour chaque tour de départ possible (de earliest_start à max_turns) :
    pour chaque tronçon (first, second) du chemin :
        départ = dès que possible
        tant que ça ne rentre pas (_can_schedule == False) :
            décale le départ d'un tour
        si on dépasse max_turns → chemin invalide, on essaie un départ suivant
    si tout le chemin tient → réserve tout, retourne les events
retourne None  # aucun tour de départ ne marche
```

C'est glouton **au niveau des tronçons** : pour chaque étape, il retarde le
départ juste ce qu'il faut pour éviter le conflit, sans anticiper les
conflits plus loin dans le chemin (pas de vrai backtracking intra-chemin).

Le retour `events` encode, pour chaque tour, ce qui se passe :

- si le tronçon dure 2 tours (zone restreinte) → un événement `"hub1-hub2"`
  au tour intermédiaire (le drone est "en transit visible") ;
- toujours → un événement au tour d'arrivée avec le nom du hub atteint.

## L'ordonnancement multi-drones : `run_from_all_path` + `_choose_best_path`

Boucle **drone par drone** :

```
pour chaque drone (1 à nb_drones) :
    choice = _choose_best_path(paths, max_steps)   # teste TOUS les chemins candidats
    si aucun chemin ne marche → RuntimeError
    réserve réellement le chemin gagnant (impacte les drones suivants)
    enregistre le drone (DroneState, scheduled_routes, events)
```

**`_choose_best_path`** teste chaque chemin candidat sur une **simulation
jetable** :

```
pour chaque chemin candidat :
    trial = Simulation(...)                          # instance temporaire
    trial.node_reservations = copie des réservations réelles
    trial.edge_reservations = copie des réservations réelles
    scheduled = trial._schedule_path(chemin, 0, max_steps)
    garde le chemin qui finit le plus tôt (max(scheduled) le plus petit)
retourne le meilleur chemin trouvé
```

Pourquoi une copie et pas l'état réel directement ? Pour pouvoir **comparer
plusieurs chemins sans polluer** les réservations tant qu'on n'a pas décidé
lequel garder. Une fois le gagnant choisi, on réserve **pour de vrai** sur
`self`.

C'est ce mécanisme qui fait que le drone 2 "voit" que le drone 1 a déjà pris
tel chemin à tel horaire, et s'adapte en conséquence (éventuellement en
prenant un autre chemin, ou en décalant son départ).

## `render_terminal`

Affichage brut : pour chaque tour trié, imprime les événements de ce tour
séparés par des espaces, puis le tour maximum.

## Le point faible restant

C'est un **glouton séquentiel** : le drone 1 est planifié sans savoir ce
dont le drone 5 aura besoin. Ça donne de bons résultats en pratique (comme
montré par les tests), mais ce n'est pas garanti optimal globalement — un
ordre de planification différent (par ex. trier par longueur de chemin, ou
par contrainte) pourrait donner un meilleur résultat dans certains cas.

Pistes d'amélioration possibles :

1. **Trier les drones intelligemment** avant de les planifier (par ex. les
   chemins les plus contraints/longs en premier), plutôt que dans l'ordre
   `D1, D2, D3...`.
2. **Backtracking limité** : si un drone ne trouve aucun chemin faisable,
   revenir en arrière et réessayer un chemin différent pour un drone
   précédent — plus coûteux, mais peut débloquer des cas où le glouton pur
   échoue.
