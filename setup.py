from distutils.core import setup
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIREMENTS_FILE = HERE.joinpath(Path('inclusion_map', 'requirements.txt'))

with REQUIREMENTS_FILE.open(mode='r') as requirements:
    install_requires = requirements.read().splitlines()

setup(
    name="InclusionMap",
    version="1.1",
    description=(
        "A tool for generating the inclusion map of a programming project. "
        "Several programming languages are supported."
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.11'
    ],
    keywords='dependency graph map programming project tool',

    author="Victor Laügt",
    url="https://github.com/VictorLaugt/InclusionMap",
    license='GPLv3',

    packages=['inclusion_map', 'inclusion_map.back'],
    install_requires=install_requires,

    entry_points={
        "console_scripts": ["inclusionmap = inclusion_map.__main__:main"],
    },

    include_package_data=True,
)
