#!/usr/bin/env python3
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

import inclusion_map.back
import inclusion_map.front


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    # autopep8: off
    # ---- options générales
    parser.add_argument('roots',
        nargs='+',
        type=Path,
        help="Répertoires racines du projet"
    )
    parser.add_argument('-I', '--include-dirs',
        nargs='*',
        type=Path,
        help=(
            "Répertoires dans lesquels commence la recherche des fichiers "
            "inclus. Par défaut, la recherche commence dans les répertoires "
            "racines."
        )
    )

    parser.add_argument('-l', '--language',
        required=True,
        choices=('c', 'c++', 'python'),
        help="Langage dans lequel sont écrits les fichiers du projet."
    )
    parser.add_argument('-e', '--extensions',
        nargs='*',
        type=str,
        help=(
            "Extensions des fichiers à afficher dans le graphe. Par défaut, "
            "détermine automatiquement les extensions selon le langage utilisé."
        )
    )
    parser.add_argument('-i', '--ignore-dirs',
        nargs='*',
        type=str,
        help=(
            "Répertoires à ignorer. Par défaut, détermine automatiquement les "
            "répertoires à ignorer selon le langage utilisé (par exemple "
            "`__pycache__` pour python)."
        )
    )

    parser.add_argument('-s', '--simplify',
        action='store_true',
        help=(
            "Simplifie le graphe en exploitant la transitivité de la relation "
            "d'inclusion. Si x inclut y, y inclut z, et x inclut z, alors "
            "le graphe n'affichera pas le fait que x inclu z."
        )
    )

    # ---- options graphiques
    parser.add_argument('--display-algorithm',
        choices=('patchwork', 'circo', 'osage', 'sfdp', 'dot', 'twopi', 'neato', 'fdp'),
        help=(
            "Nom de l'algorithme permettant de déterminer les positions des "
            "noeuds du graphe."
        )
    )

    parser.add_argument('--font-size',
        default=7.,
        type=float,
        help="Taille de la police utilisée pour écrire les noms des fichiers."
    )

    # autopep8: on
    return parser


def unsupported_language_error(language: str) -> ValueError:
    return ValueError(f'Unsupported language : {language}')

def path_does_not_exist_error(path: Path) -> ValueError:
    return ValueError(f'Path does not exist : {path}')


def create_project(language: str) -> inclusion_map.back.Project:
    if language in ('c', 'c++'):
        return inclusion_map.back.Project(
            inclusion_map.back.c_include_matcher,
            inclusion_map.back.CTargetParser
        )
    elif language == 'python':
        return inclusion_map.back.Project(
            inclusion_map.back.python_import_matcher,
            inclusion_map.back.PythonTargetParser
        )
    raise unsupported_language_error(language)


def default_extension_set(language: str) -> set[str]:
    if language in ('c', 'c++'):
        return {'.c', '.cpp', '.h', '.hpp'}
    elif language == 'python':
        return {'.py'}
    raise unsupported_language_error(language)


def default_ignore_dirs(language: str) -> set[str]:
    if language in ('c', 'c++'):
        return set()
    elif language == 'python':
        return {'__pycache__'}
    raise unsupported_language_error(language)


if __name__ == '__main__':
    # ---- argument parsing
    args = build_arg_parser().parse_args()

    # ---- argument processing
    if args.extensions:
        extensions = set()
        for ext in args.extensions:
            if ext.startswith('*.'):
                extensions.add(ext[1:])
            elif ext.startswith('.'):
                extensions.add(ext)
            else:
                extensions.add(f'.{ext}')
    else:
        extensions = default_extension_set(args.language)

    if args.ignore_dirs:
        ignore_dirs = set(args.ignore_dirs)
    else:
        ignore_dirs = default_ignore_dirs(args.language)

    if args.include_dirs:
        include_dirs = args.include_dirs
    else:
        include_dirs = args.roots

    # ---- project scan
    project = create_project(args.language)

    for rdir in args.roots:
        if not rdir.is_dir():
            raise path_does_not_exist_error(rdir)
        project.add_root_directory(rdir)

    for idir in include_dirs:
        project.add_include_directory(idir)

    project.find_source_files(extensions, ignore_dirs)
    project.find_dependencies()

    if args.simplify:
        project.remove_redundancies()

    print(project)

    # ---- interactive graph display
    if project.is_not_empty():
        plot_instance = inclusion_map.front.project_to_graph(project, args.font_size, args.display_algorithm)
        plt.show()
    else:
        print("No intern inclusion found")
