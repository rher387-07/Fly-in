# Compte rendu du projet Fly-in

## 1. Presentation du projet

Fly-in est une application Python qui dirige plusieurs drones dans un reseau de hubs connectes. Le projet propose deux sorties :

- une simulation terminale qui affiche les mouvements tour par tour ;
- un rendu Pygame optionnel qui affiche les hubs, les connexions, les drones, les zones restreintes, le zoom et le deplacement de camera.

L'application lit un fichier de carte, le valide, construit un graphe pondere, recherche plusieurs itineraires, planifie les drones en respectant les capacites, puis peut afficher le resultat graphiquement.

Le projet utilise Python 3.10 ou une version plus recente. Aucune bibliotheque specialisee de graphes n'est utilisee : les algorithmes sont implementes dans le depot.

## 2. Deroulement general

Le fonctionnement normal est le suivant :

```text
Fichier de carte
   |
   v
FlyInParser.parse()
   |
   v
Network, Hub, Connection
   |
   v
main.build_graph()
   |
   v
Graph.dijkstra() et Graph.yen()
   |
   v
Simulation.run_from_all_path()
   |
   +--> mouvements dans le terminal et Max turn
   |
   +--> Lancer.run() avec l'option --render
```

Le point d'entree en ligne de commande est `main.py`.

```bash
python3 main.py maps/easy/01_linear_path.txt
python3 main.py maps/challenger/01_the_impossible_dream.txt --render
```

La carte peut aussi etre fournie avec la variable d'environnement `MAP`.

```bash
MAP=maps/easy/01_linear_path.txt make run
```

## 3. Modele de donnees

### `Hub`

Defini dans `parser/models.py`.

Champs :

- `name` : nom unique du hub ;
- `x`, `y` : coordonnees entieres ;
- `zone_type` : `normal`, `blocked`, `restricted` ou `priority` ;
- `color` : couleur optionnelle pour l'affichage ;
- `max_drones` : occupation maximale simultanee, `1` par defaut.

### `Connection`

Represente une connexion bidirectionnelle entre deux hubs.

Champs :

- `hub1` et `hub2` : noms des extremites ;
- `max_capacity` : nombre maximal de drones utilisant la connexion simultanement.

### `Network`

Contient toute la carte analysee :

- nombre de drones ;
- hub de depart et hub d'arrivee uniques ;
- hubs indexes par nom ;
- connexions.

### `DroneState`

Defini dans `simulation/simulation.py`. Il contient l'identifiant d'un drone et le chemin qui lui est attribue.

## 4. Analyseur de carte

L'analyseur est implemente par `FlyInParser` dans `parser/parser.py`.

### `FlyInParser.__init__`

Stocke le nom du fichier et cree un `Network` vide.

### `FlyInParser.parse`

Execute tout le processus d'analyse :

1. lecture du fichier ;
2. analyse de la declaration `nb_drones` ;
3. analyse des hubs et des connexions ;
4. verification du hub de depart et du hub d'arrivee ;
5. verification de l'unicite des coordonnees ;
6. retour d'un `Network` valide.

### `_read_file`

Lit la carte avec un context manager. Les lignes vides et les commentaires sont ignores. Les commentaires en fin de ligne sont retires avant l'analyse.

### `_parse_nb_drones`

Verifie la premiere ligne et exige un entier positif.

### `_parse_line`

Dirige chaque ligne vers le parseur specialise correspondant :

- `_parse_special_hub` ;
- `_parse_regular_hub` ;
- `_parse_connection`.

Une instruction inconnue leve une `ParseError` avec le numero de ligne.

### `_parse_special_hub`

Cree et enregistre le `start_hub` ou le `end_hub` unique. Les noms dupliques et les definitions multiples sont refuses.

### `_parse_regular_hub`

Cree un hub classique et refuse les noms deja utilises.

### `_create_hub`

Analyse le nom, les coordonnees entieres, les metadonnees, le type de zone, la couleur et la capacite. Les tirets dans les noms, les types inconnus, les coordonnees invalides et les capacites invalides sont refuses.

### `_parse_connection`

Analyse une connexion bidirectionnelle. La fonction verifie que les deux hubs existent deja, refuse les boucles sur un meme hub et les connexions dupliquees, puis valide `max_link_capacity`.

### `_extract_metadata`

Analyse les blocs de metadonnees comme :

```text
[zone=restricted color=blue max_drones=2]
```

Les cles inconnues, les doublons, les valeurs vides et les blocs mal formes sont refuses.

### `_positive_int`

Convertit une capacite en entier positif et leve une erreur precise si la valeur est invalide.

### `_connection_exists`

Verifie les deux directions d'une connexion. `a-b` et `b-a` sont donc considerees comme des doublons.

### `_validate_network`

Exige exactement un hub de depart et un hub d'arrivee.

### `_validate_cordo`

Refuse les coordonnees dupliquees afin que les hubs puissent etre affiches separement.

## 5. Graphe et recherche de chemins

Le graphe est implemente dans `graph/graph.py` par la classe `Graph`.

### `Graph.__init__`

Cree le dictionnaire d'adjacence. Chaque entree contient une destination et son cout de mouvement.

### `Graph.add_summit`

Ajoute une arete orientee. Les connexions sont ajoutees dans les deux directions par `main.build_graph` et par le constructeur de la simulation.

Le cout depend du hub de destination :

- normal : `1` ;
- priority : `1` ;
- restricted : `2` ;
- blocked : exclu avant la construction du graphe.

Le cout est associe a la destination, car entrer dans une zone `restricted` prend deux tours.

### `Graph.dijkstra`

Recherche le chemin de cout minimal entre deux hubs avec une file de priorite basee sur un tas. La fonction accepte des hubs et des sequences temporairement ignores pour produire des chemins alternatifs.

Elle retourne :

```python
(distance, path)
```

### `Graph.sum_distance_path`

Additionne les couts des aretes d'un chemin.

### `Graph.yen`

Genere jusqu'a `k` chemins simples alternatifs. Le premier chemin est obtenu avec Dijkstra, puis certaines aretes et prefixes deja utilises sont temporairement retires pour rechercher d'autres solutions.

Le resultat est une liste de chemins ponderes utilisee par le planificateur.

## 6. Simulation et planification

La simulation est implemente par `Simulation` dans `simulation/simulation.py`.

### `Simulation.__init__`

Accepte un `Graph` existant ou une liste de chemins candidats. Il cree les tables de reservation des hubs et des connexions.

Etat principal :

- `node_reservations` : occupation des hubs par tour ;
- `edge_reservations` : occupation des connexions par tour ;
- `scheduled_routes` : chemins et intervalles utilises par le rendu ;
- `route_order` : chemin candidat choisi pour chaque drone.

### `_edge_capacity`

Recherche la capacite d'une connexion bidirectionnelle.

### `_travel_time`

Retourne `2` si la destination est `restricted`, sinon `1`.

### `_can_schedule`

Verifie qu'un drone peut utiliser une connexion pendant un intervalle donne et arriver dans le hub sans depasser sa capacite.

### `_reserve`

Reserve chaque tour pendant lequel un drone traverse une connexion.

### `_reserve_node_occupancy`

Reserve l'occupation d'un hub entre l'arrivee du drone et son prochain depart. Cette fonction est essentielle pour une regle comme :

```text
max_drones=1
```

Un second drone ne peut pas entrer pendant que le premier attend. Si un drone sort du hub au meme tour qu'un autre y entre, le depart libere la place pour ce tour.

### `_schedule_path`

Recherche le premier horaire possible pour un chemin complet. Un depart peut etre retarde si une connexion ou un hub est plein. Un mouvement vers une zone `restricted` occupe la connexion pendant deux tours et ne peut pas etre interrompu pendant le trajet.

Les mouvements sont stockes sous la forme :

```python
(first_hub, second_hub, departure_turn, arrival_turn)
```

### `run_from_all_path`

Planifie tous les drones, imprime leurs mouvements et conserve les horaires exacts pour le renderer. La fonction imprime aussi le tour maximal.

La methode de compatibilite `run` utilise ce format :

```text
Turn 1: D1-waypoint1
Turn 2: D1-waypoint2 D2-waypoint1
Turn 3: D1-goal D2-waypoint2
Turn 4: D2-goal
Max turn: 4
```

Le flux principal `run_from_all_path` affiche actuellement les lignes de mouvements puis le resume `Max turn`. Cette difference devra etre uniformisee si un format terminal identique est exige pour tous les points d'entree.

### `_find_best_route_order`

Teste des paires de chemins candidats repetes et choisit la combinaison dont la fin est la plus rapide. Cette strategie a ete ajoutee pour ameliorer les performances de la carte challenger.

La carte challenger se termine actuellement en environ 43 tours avec l'implementation fournie.

### `plan_drone`

Ajoute un drone avec un chemin explicite. Cette fonction est conservee pour compatibilite.

### `run`

Planifie les drones ajoutes explicitement et affiche leurs mouvements.

## 7. Rendu graphique

Le rendu est implemente dans `renderer/render.py` par la classe `Lancer`.

### Assets

Le renderer conserve les assets d'origine :

- `asset/platform/1_Industrial_Tileset_1B.png` pour les hubs et les marqueurs restricted ;
- `asset/drone/Idle.png` pour la base du sprite drone ;
- `asset/drone/Forward.png` pour les images d'animation ;
- `asset/cloud/1.png` pour le fond.

### `Lancer.__init__`

Initialise Pygame, charge les assets, cree les plateformes et un sprite par chemin planifie, puis calcule la disposition de la carte.

### `load_tile`

Extrait une tuile de plateforme ou de zone restricted depuis le tileset.

### `_layout`

Utilise les espacements et l'etendue des coordonnees pour calculer :

- l'espacement horizontal ;
- l'espacement vertical ;
- le zoom automatique ;
- les offsets d'ecran.

Les espacements minimaux actuels sont :

```python
MIN_SPACING_X = 200
MIN_SPACING_Y = 200
```

### `create_platform`

Cree un objet `Platform` pour chaque hub.

### `_screen_position`

Convertit les coordonnees de la carte en coordonnees d'ecran. Les dimensions du sprite mis a l'echelle sont utilisees pour calculer le centre. Les lignes et les marqueurs restent ainsi alignes pendant les changements de zoom.

### `_drone_position`

Interpole la position d'un drone entre deux hubs selon son intervalle de mouvement planifie.

### `_drone_speed`

Retourne une vitesse d'animation reduite de moitie quand un drone entre dans une zone restricted. Les autres mouvements utilisent la vitesse normale.

### `draw_background`

Redimensionne et affiche l'asset de fond cloud existant.

### `draw_connections`

Dessine toutes les connexions et place le marqueur restricted au milieu exact des deux centres de hubs mis a l'echelle.

### `draw`

Affiche le fond, les connexions, les plateformes et tous les drones pour une frame.

### `run`

Execute la boucle d'evenements Pygame. Elle gere :

- `ESC` : fermer le renderer ;
- `SPACE` : mettre en pause ou reprendre ;
- touches `+` et `-` du pave numerique : zoom ;
- fleches et pave numerique : deplacement de camera via `Camera`.

Le HUD textuel a ete retire de la fenetre Pygame. Les informations de tour sont affichees dans le terminal.

## 8. Sprite Drone

La classe `Drone` est implementee dans `renderer/drone.py`.

### `Drone.__init__`

Charge quatre images depuis le spritesheet forward. La classe conserve l'image courante, la vitesse d'animation et le rectangle Pygame.

### `Drone.update`

Avance l'image du sprite selon un multiplicateur de vitesse. Un mouvement restricted utilise `0.5`, donc son animation est deux fois plus lente qu'un mouvement normal.

### `Drone.draw`

Ancienne methode de dessin d'un drone attache a une plateforme.

### `Drone.draw_at`

Dessine le sprite anime a la position interpolee du trajet. L'implementation actuelle affiche le drone 30 pixels au-dessus du point du trajet afin de donner un effet de drone en vol au-dessus du hub.

## 9. Sprite Platform

La classe `Platform` est implementee dans `renderer/platform.py`.

### `Platform.__init__`

Stocke le hub, la tuile de plateforme, les coordonnees, la couleur, la capacite et les informations d'affichage.

### `check_capacity`

Met a jour l'ancienne barre de capacite lorsqu'un drone entre ou sort.

### `update_bar_max_drone`

Dessine l'ancienne barre de capacite. Le renderer principal actuel n'utilise plus cette methode depuis le retrait des barres d'occupation.

### `_get_color_rnadom`

Genere une couleur RGB changeante pour les hubs utilisant `color=rainbow`.

### `draw_platform`

Dessine l'asset de plateforme, affiche le nom du hub avec sa couleur et affiche un voile translucide lorsque la plateforme est en pause.

## 10. Camera

La classe `Camera` dans `renderer/camera.py` gere :

- les mouvements horizontaux et verticaux ;
- le niveau de zoom ;
- les limites du zoom ;
- la conversion des coordonnees monde vers l'ecran.

## 11. Modifications realisees

Les corrections et evolutions principales sont les suivantes :

1. Remplacement des deux simulations concurrentes du point d'entree par un flux unique.
2. Ajout de l'acceptation directe d'un chemin de carte et de l'option `--render`.
3. Correction de la gestion des commentaires et conservation des coordonnees de carte.
4. Correction des poids du graphe selon la zone de destination.
5. Exclusion des zones blocked de la construction du graphe.
6. Implementation de Dijkstra pondere et des chemins alternatifs avec Yen.
7. Ajout des reservations de capacite des hubs et des connexions.
8. Ajout des reservations d'occupation pendant l'attente dans les hubs.
9. Ajout de la recherche de paires de chemins pour ameliorer la carte challenger.
10. Ajout du resume `Max turn` dans la sortie terminale.
11. Utilisation des assets Pygame d'origine pour les plateformes, drones et nuages.
12. Synchronisation du rendu avec les intervalles de mouvement de la simulation.
13. Reduction de moitie de la vitesse visuelle dans les zones restricted.
14. Correction de l'alignement du zoom entre plateformes, lignes et marqueurs.
15. Ajout d'un espacement automatique et d'un zoom adapte aux grandes cartes.
16. Placement des drones au-dessus des hubs pour donner un effet de vol.
17. Retrait du stationnement visuel ajoute entre les hubs.
18. Retrait des compteurs et des barres d'occupation du renderer.
19. Retrait du HUD Pygame ; les tours restent affiches dans le terminal.
20. Correction du Makefile et des controles flake8/mypy.

## 12. Validation

Le projet a ete verifie avec :

```bash
make lint
```

Les cartes fournies ont ete executees, y compris la carte challenger. Des frames Pygame ont aussi ete rendues en mode headless avec l'environnement virtuel du projet et les assets d'origine.

Commandes utiles :

```bash
make lint
python3 main.py maps/easy/01_linear_path.txt
python3 main.py maps/challenger/01_the_impossible_dream.txt
./venv/bin/python main.py maps/easy/01_linear_path.txt --render
```

## 13. Notes de conception

- La sortie terminale contient un resume `Max turn` en plus des mouvements.
- Le renderer graphique est optionnel et necessite Pygame.
- Les hubs start et goal sont illimites selon le sujet.
- Les hubs blocked ne sont jamais traverses.
- Les hubs priority ont un cout de mouvement de `1`. Ils ne recoivent pas de cout artificiellement inferieur.
- Les decisions officielles de capacite sont prises par `Simulation`. Le renderer affiche les horaires fournis par cette simulation.
