from distutils.core import setup
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parent
REQUIREMENTS_FILE = REPOSITORY.joinpath('requirements.txt')
README_FILE = REPOSITORY.joinpath("README.md")

with REQUIREMENTS_FILE.open(mode='r') as requirements:
    install_requires = requirements.read().splitlines()

with README_FILE.open(mode='r') as readme:
    long_description = readme.read()


setup(
    name="InclusionMap",
    version="1.5.1",

    description=(
        "A tool for generating the inclusion map of a programming project. "
        "Several programming languages are supported."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13'
    ],
    keywords='dependency graph map programming project tool',

    author="Victor Laügt",
    author_email='victorlaugtdev@gmail.com',
    url="https://github.com/VictorLaugt/InclusionMap",
    license='GPLv3',

    packages=[
        'inc_map',
        'inc_map.back',
        'inc_map.back.support_c',
        'inc_map.back.support_python'
    ],
    install_requires=install_requires,
    python_requires=">=3.9",

    entry_points={
        "console_scripts": ["inclusionmap = inc_map.__main__:main"],
    },

    include_package_data=True,
)
