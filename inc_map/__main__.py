from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Optional
    from inc_map.back.common_features.abstract_inclusion_inspector import AbstractInclusionInspector

import argparse
from pathlib import Path
import re

import importlib
import sys

from inc_map.back.project import ProjectBuilder
from inc_map.back.support_python.import_inspector import ImportInspector
from inc_map.back.support_c.include_inspector import IncludeInspector

from inc_map.front import show_project_graph


def check_dependency(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def arg_checker_group_regex(arg: str) -> re.Pattern:
    try:
        return re.compile(arg)
    except re.error as err:
        raise argparse.ArgumentTypeError(err.args[0])


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
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
    parser.add_argument('--display-algorithm',
        choices=('default', 'patchwork', 'circo', 'osage', 'sfdp', 'dot', 'twopi', 'neato', 'fdp'),
        default='dot',
        help=(
            "Nom de l'algorithme permettant de déterminer les positions des "
            "noeuds du graphe."
        )
    )
    parser.add_argument('--font-size',
        default=7.,
        type=float,
        help=(
            "Taille de la police utilisée pour écrire les noms des fichiers "
            "(7 par défaut)."
        )
    )
    parser.add_argument('--groups', '-g',
        nargs='*',
        type=arg_checker_group_regex,
        help=(
            "Regex des noms de fichiers pour chaque groupe de couleur (par défaut, "
            "groupe par extensions)"
        )
    )

    return parser


def unsupported_language_error(language: str) -> ValueError:
    return ValueError(f'Unsupported language : {language}')


def path_does_not_exist_error(path: Path) -> ValueError:
    return ValueError(f'Path does not exist : {path}')


def default_extension_set(language: str) -> set[str]:
    if language in ('c', 'c++'):
        return {'.c', '.cpp', '.h', '.hpp'}
    elif language == 'python':
        return {'.py', '.ipynb'}
    raise unsupported_language_error(language)


def default_ignore_dirs(language: str) -> set[str]:
    if language in ('c', 'c++'):
        return set()
    elif language == 'python':
        return {'__pycache__'}
    raise unsupported_language_error(language)


def get_inspector_type(language: str) -> Type[AbstractInclusionInspector]:
    if language in ('c', 'c++'):
        return IncludeInspector
    elif language == 'python':
        return ImportInspector
    raise unsupported_language_error(language)


def get_display_algorithm_name(name: str) -> Optional[str]:
    if name != "default":
        if check_dependency("pygraphviz"):
            return name
        else:
            print((
                    "pygraphviz is not installed, switching to the default display "
                    "algorithm. (install pygraphviz: "
                    "https://pygraphviz.github.io/documentation/stable/install.html)"
                ),
                file=sys.stderr
            )


def main():
    # ---- parse arguments
    args = build_arg_parser().parse_args()

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
        ignored_dir_names = set(args.ignore_dirs)
    else:
        ignored_dir_names = default_ignore_dirs(args.language)

    if args.include_dirs:
        include_dirs = args.include_dirs
    else:
        include_dirs = args.roots

    # ---- scan the project
    project_builder = ProjectBuilder()
    for rdir in args.roots:
        if not rdir.is_dir():
            raise path_does_not_exist_error(rdir)
        project_builder.add_root_directory(rdir)

    for idir in include_dirs:
        if not idir.is_dir():
            raise path_does_not_exist_error(idir)
        project_builder.add_include_directory(idir)

    project = project_builder.build(
        extensions,
        ignored_dir_names,
        get_inspector_type(args.language)
    )

    if args.simplify:
        project.remove_redundancies()

    print(project)

    # ---- display the inclusion map
    if project.is_not_empty():
        layout_algorithm = get_display_algorithm_name(args.display_algorithm)
        show_project_graph(project, args.font_size, args.groups, layout_algorithm)
    else:
        print("No internal inclusion found")


if __name__ == '__main__':
    main()
