# InclusionMap

## Installation
`pip install InclusionMap`
Pour utiliser l'option `--display-algorithm` du programme, il est nécessaire d'installer le paquet `pygraphviz`.

## Utilisation
`inclusionmap LIST_OF_DIRECTORIES ... -l PROGRAMMING_LANGUAGE [OPTIONS]`
ou
`python3 -m inclusion_map LIST_OF_DIRECTORIES ... -l PROGRAMMING_LANGUAGE [OPTIONS]`

### Options générales
`LIST_OF_DIRECTORIES ...`
Répertoires racines du projet.

`[{-I|--include-dirs}]`
Répertoires dans lesquels commence la recherche des fichiers inclus.
Par défaut, cherche dans tous les répertoires racines.


`{-l|--language} {c|c++|python}`
Langage dans lequel sont écrits les fichiers du projet.

`[{-e|--extensions} LIST_OF_EXTENSIONS ...]`
Extensions des fichiers à afficher dans le graphe.
Par défaut, détermine automatiquement les extensions selon le langage utilisé.

`[{-i|--ignore-dirs} LIST_OF_STRINGS ...]`
Répertoires à ignorer.
Par défaut, détermine automatiquement les répertoires à ignorer selon le langage
utilisé (par exemple `__pycache__` pour python).


`[{-s|--simplify}]`
Simplifie le graphe en exploitant la transitivité de la relation d'inclusion.
Si x inclut y, y inclut z et x inclut z, alors n'affiche pas le fait que x inclut z.


### Options graphiques
`[--display-algorithm {patchwork|circo|osage|sfdp|dot|twopi|neato|fdp}]`
Nom d'un algorithme d'affichage de graphe.

`[--font-size INTEGER]`
Taille de la police utilisée pour écrire les noms des nœuds.


### TODO: Commande `inverted`
Construit le graphe des dépendances inverses d'un ensemble donné de fichiers.
I.e part d'un ensemble donné de fichiers et affiche sur le graphe les fichiers
qui incluent au moins l'un d'eux.

`LIST_OF_FILES ...`
Fichiers de départ à partir desquels on parcourt les dépendances inverses.

`[--max-depth INTEGER]`
Profondeur maximale des nœuds apparaissant sur le graphe (Infinie par défaut).
