# Fly-in — Roadmap de création du renderer Pygame

## Objectif

Construire progressivement l'interface graphique permettant de représenter le résultat du parsing et de la simulation.

Le renderer doit afficher :

- les plateformes représentant les hubs ;
- les noms des hubs ;
- les connexions ;
- les éléments restricted ;
- les drones ;
- les animations des drones ;
- la caméra ;
- le zoom ;
- l'état graphique de la simulation.

> **Le renderer ne doit pas décider des déplacements des drones.**
> Il reçoit les informations produites par la simulation et les affiche.

---

## 1. Initialisation de Pygame

### Objectif

Créer la fenêtre principale.

### Structure

```python
pygame.init()

self.screen = pygame.display.set_mode((1366, 700))
pygame.display.set_caption("Fly-in")

self.clock = pygame.time.Clock()
self.running = True
```

La boucle principale doit gérer :

- les événements ;
- la mise à jour ;
- le dessin ;
- les FPS.

---

## 2. Organisation des assets

Organisation recommandée :

```
asset/
├── platform/
│   └── 1_Industrial_Tileset_1B.png
│
└── drone/
    ├── Idle.png
    ├── Forward.png
    └── Back.png
```

Le renderer doit charger les assets au démarrage.

> Éviter de charger les images à chaque frame.

---

## 3. Découpage du tileset

Le tileset contient les éléments utilisés pour construire le réseau.

La fonction de découpage peut être :

```python
def load_tile(path, x, y, width, height):
    tileset = pygame.image.load(path).convert_alpha()

    tile = pygame.Surface(
        (width, height),
        pygame.SRCALPHA
    )

    tile.blit(
        tileset,
        (0, 0),
        pygame.Rect(x, y, width, height)
    )

    return tile
```

La plateforme principale utilise actuellement :

```python
x = 0
y = 0
width = 96
height = 32
```

Le petit élément utilisé pour restricted doit également être découpé depuis le même tileset.

---

## 4. Création des plateformes

Créer :

```
renderer/platform.py
```

Chaque hub du parsing correspond à une plateforme.

Exemple :

```python
for hub in self.network.hubs.values():

    platform = Platform(
        hub,
        self.platform_image
    )

    self.platforms.append(platform)
```

La classe `Platform` doit principalement gérer :

- son hub ;
- son image ;
- sa position ;
- son affichage.

---

## 5. Positionnement des plateformes

Les coordonnées du réseau doivent être converties en coordonnées Pygame.

Exemple :

```python
world_x = offset_x + hub.x * spacing_x
world_y = offset_y + hub.y * spacing_y
```

Prévoir :

```python
self.spacing_x
self.spacing_y
self.offset_x
self.offset_y
```

Cela permet de modifier facilement la distance entre les plateformes.

---

## 6. Espacement horizontal et vertical

Exemple :

```python
self.spacing_x = 300
self.spacing_y = 200
```

Si les plateformes sont trop proches :

```python
spacing_x += 50
spacing_y += 50
```

Si elles sont trop éloignées :

```python
spacing_x -= 50
spacing_y -= 50
```

L'objectif est d'avoir une représentation lisible du graphe.

---

## 7. Affichage du nom des hubs

Chaque plateforme doit afficher son nom en dessous.

```
          ┌───────────────┐
          │   PLATFORM    │
          └───────────────┘
                  |
                START
```

Le texte doit être positionné relativement à la plateforme.

Il doit également suivre :

- la caméra ;
- le zoom.

Prévoir une police :

```python
self.font = pygame.font.Font(None, 24)
```

Puis :

```python
text = self.font.render(
    hub.name,
    True,
    (255, 255, 255)
)
```

---

## 8. Création des connexions

Les connexions doivent être récupérées depuis le résultat du parsing.

Pour la première version, utiliser simplement :

```python
pygame.draw.line()
```

Exemple :

```python
pygame.draw.line(
    self.screen,
    color,
    start,
    end,
    width
)
```

Le point de départ et le point d'arrivée doivent être les centres des plateformes.

```python
platform_a.rect.center
platform_b.rect.center
```

Ainsi les connexions restent centrées même lorsque la taille des plateformes change.

---

## 9. Connexions et caméra

Les coordonnées des connexions doivent être calculées dans le système de coordonnées du monde.

Puis transformées par la caméra avant le dessin.

Conceptuellement :

```
world position
      |
      v
   Camera
      |
      v
screen position
      |
      v
   Pygame
```

---

## 10. Zone restricted

Une connexion vers une zone restricted doit utiliser le petit élément du tileset identifié précédemment.

Exemple :

```
Platform A -------- [restricted] -------- Platform B
```

Le sprite doit être placé au centre de la connexion.

Calcul :

```python
center_x = (start_x + end_x) / 2
center_y = (start_y + end_y) / 2
```

Le sprite doit également suivre :

- le zoom ;
- la caméra.

---

## 11. Création de la caméra

Créer :

```
renderer/camera.py
```

La caméra doit gérer :

- déplacement gauche ;
- déplacement droite ;
- déplacement haut ;
- déplacement bas.

Variables :

```python
self.x
self.y
```

Exemple :

```python
camera_x = world_x - self.camera.x
camera_y = world_y - self.camera.y
```

---

## 12. Contrôle de la caméra

Exemple :

```
←  déplacer vers la gauche
→  déplacer vers la droite
↑  déplacer vers le haut
↓  déplacer vers le bas
```

Dans `handle_events()` ou `update()` :

```python
keys = pygame.key.get_pressed()

if keys[pygame.K_LEFT]:
    self.camera.x -= speed

if keys[pygame.K_RIGHT]:
    self.camera.x += speed

if keys[pygame.K_UP]:
    self.camera.y -= speed

if keys[pygame.K_DOWN]:
    self.camera.y += speed
```

---

## 13. Système de zoom

Le zoom doit être appliqué à tous les éléments :

- plateformes
- connexions
- restricted
- textes
- drones

Variable :

```python
self.zoom = 1.0
```

Limites :

```python
self.min_zoom = 0.5
self.max_zoom = 2.0
```

Pas :

```python
self.zoom_step = 0.1
```

Exemple :

```
Z -> zoom -
X -> zoom +
```

---

## 14. Redimensionnement des plateformes

Le zoom doit également modifier la taille des plateformes.

Exemple :

```python
width = int(image.get_width() * zoom)
height = int(image.get_height() * zoom)
```

Puis :

```python
scaled_image = pygame.transform.scale(
    image,
    (width, height)
)
```

Le même principe doit être appliqué aux petits éléments restricted.

---

## 15. Épaisseur des connexions

L'épaisseur des connexions doit également suivre le zoom.

Exemple :

```python
width = max(1, int(base_width * self.zoom))
```

Ainsi :

```python
zoom = 0.5
```

donne une connexion plus fine.

Et :

```python
zoom = 2.0
```

donne une connexion plus épaisse.

---

## 16. Création du drone

Créer :

```
renderer/drone.py
```

Le drone doit être indépendant des plateformes.

Il doit connaître :

- son sprite ;
- sa position ;
- son animation ;
- son état ;
- éventuellement son hub actuel.

Pour commencer :

```
Idle.png
```

est suffisant.

Le drone doit apparaître au-dessus de la plateforme START.

---

## 17. Découpage de Idle.png

Le sprite `Idle.png` fait **192 x 48**.

Il contient quatre frames de **48 x 48**.

Découpage :

```
Frame 0 : x = 0
Frame 1 : x = 48
Frame 2 : x = 96
Frame 3 : x = 144
```

Chaque frame fait :

```python
width  = 48
height = 48
```

---

## 18. Animation Idle

L'animation doit suivre :

```
Frame 0
   |
   v
Frame 1
   |
   v
Frame 2
   |
   v
Frame 3
   |
   v
Frame 0
   |
   v
  ...
```

> Ne pas changer de frame à chaque appel de `draw()`. Utiliser un timer.

Exemple conceptuel :

```python
if current_time - last_update >= animation_delay:

    current_frame += 1

    if current_frame >= 4:
        current_frame = 0

    last_update = current_time
```

---

## 19. Position du drone

Le drone doit être placé au-dessus de la plateforme.

Exemple :

```python
drone_x = platform.center_x
drone_y = platform.top - drone_height
```

Il doit rester centré horizontalement sur la plateforme.

---

## 20. Drone et caméra

La position du drone doit être une position du monde.

Puis :

```python
screen_x = world_x - camera.x
screen_y = world_y - camera.y
```

Ainsi le drone bouge naturellement avec le reste du réseau lorsque la caméra se déplace.

---

## 21. Drone et zoom

Le sprite du drone doit également être redimensionné.

Exemple :

```python
width = int(48 * zoom)
height = int(48 * zoom)
```

Ainsi :

```python
zoom = 1.0
```

donne **48 x 48**, et :

```python
zoom = 2.0
```

donne **96 x 96**.

---

## 22. États visuels du drone

Le renderer peut recevoir l'état produit par la simulation.

Exemple :

```
WAITING
MOVING
TRANSIT
ARRIVED
BLOCKED
```

Correspondance initiale :

| État | Animation |
|------|-----------|
| WAITING | Idle |
| MOVING | Forward |
| TRANSIT | Forward |
| ARRIVED | Idle |
| BLOCKED | Idle |

---

## 23. Animation Forward

Lorsque la simulation indique `MOVING`, le renderer pourra utiliser `Forward.png`.

Même principe que `Idle.png` :

1. découper la spritesheet ;
2. récupérer les frames ;
3. gérer un timer ;
4. afficher la frame courante.

---

## 24. Déplacement graphique

Le drone ne doit pas se téléporter.

Si la simulation décide :

```
START -> A
```

le renderer doit effectuer une interpolation.

Exemple :

```
start_x
    |
    |\
    | \
    |  \
    |   \
    |    \
    v     v
  drone   A
```

Formule :

```python
x = start_x + (end_x - start_x) * progress
y = start_y + (end_y - start_y) * progress
```

avec `progress` allant de `0.0` à `1.0`.

---

## 25. Séparation Simulation / Renderer

Principe fondamental :

```
Simulation
     |
     | état
     v
  Renderer
     |
     v
   Pygame
```

Le renderer ne doit **pas** faire :

> « Quel est le meilleur chemin ? »

Il doit seulement recevoir :

> « Le drone va de A vers B. »

Puis afficher ce déplacement.

---

## 26. Boucle principale

Structure recommandée :

```python
while self.running:

    handle_events()

    simulation.update()

    camera.update()

    renderer.update()

    renderer.draw()

    clock.tick(60)
```

Chaque partie doit avoir une responsabilité claire.

---

## 27. Organisation finale

```
Fly-in/
│
├── parser/
│
├── models/
│
├── graph/
│
├── simulation/
│   ├── drone.py
│   ├── pathfinder.py
│   ├── scheduler.py
│   └── simulation.py
│
├── renderer/
│   ├── render.py
│   ├── camera.py
│   ├── platform.py
│   └── drone.py
│
├── asset/
│   ├── platform/
│   └── drone/
│
└── main.py
```

---

## 28. Ordre de développement

### Phase 1 — Fenêtre
- initialiser Pygame ;
- créer la fenêtre ;
- gérer QUIT.

### Phase 2 — Assets
- charger le tileset ;
- découper les plateformes ;
- découper le sprite restricted ;
- charger les sprites du drone.

### Phase 3 — Plateformes
- créer une plateforme par hub ;
- positionner les plateformes ;
- régler spacing_x ;
- régler spacing_y.

### Phase 4 — Labels
- afficher le nom des hubs ;
- positionner les noms sous les plateformes.

### Phase 5 — Connexions
- récupérer les connexions du parsing ;
- dessiner les lignes ;
- les centrer sur les plateformes.

### Phase 6 — Restricted
- afficher le petit sprite du tileset ;
- le placer au centre de la connexion.

### Phase 7 — Caméra
- déplacement horizontal ;
- déplacement vertical ;
- transformation monde → écran.

### Phase 8 — Zoom
- zoom avant ;
- zoom arrière ;
- redimensionnement des plateformes ;
- redimensionnement des connexions ;
- redimensionnement des éléments restricted.

### Phase 9 — Drone
- afficher le drone sur START ;
- charger Idle.png ;
- positionner le drone au-dessus de la plateforme.

### Phase 10 — Animation Idle
- découper les quatre frames ;
- créer le timer ;
- boucler l'animation.

### Phase 11 — Déplacement
- recevoir la position du drone depuis la simulation ;
- interpoler entre deux plateformes ;
- utiliser Forward.png.

### Phase 12 — Interface de debug

Afficher temporairement :

```
Tour : 10
Drone : D1
State : MOVING
Hub : A
Destination : B
Path : START -> A -> B -> GOAL
```

Ces informations pourront être désactivées ensuite.

---

## 29. Critères de validation

| # | Test | Critère |
|---|------|---------|
| 1 | Plateformes | Tous les hubs du parsing sont représentés. |
| 2 | Connexions | Toutes les connexions du graphe sont visibles. |
| 3 | Restricted | Les zones restricted utilisent le sprite prévu. |
| 4 | Caméra | Le réseau peut être parcouru dans les quatre directions. |
| 5 | Zoom | Le réseau peut être agrandi et réduit sans casser les positions. |
| 6 | Drone | Le drone apparaît sur START. |
| 7 | Idle | Le drone possède une animation fluide. |
| 8 | Déplacement | Le drone se déplace visuellement d'une plateforme à l'autre. |
| 9 | Simulation | Le renderer affiche exactement l'état produit par la simulation. |

---

## Principe final

Le projet doit respecter cette séparation :

```
PARSER
   |
   v
NETWORK
   |
   v
SIMULATION
   |
   v
DRONES / STATES
   |
   v
RENDERER
   |
   v
PYGAME
```

- Le **parser** comprend les données.
- La **simulation** décide ce que font les drones.
- Le **renderer** affiche ce qui se passe.
