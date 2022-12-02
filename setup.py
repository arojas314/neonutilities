from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf8")

setup(
    name="neonutilities",
    version="0.0.1",
    author="Alex Rojas",
    author_email="a.rojas8907@gmail.com",
    description="Retreive data from the NEON api. Also provides some functionality to analyze and visualize eddy covariance data.",
    long_description=README,
    long_description_content_type="text/markdown",
    project_urls={
        "Source Code": "https://github.com/arojas314/neonutilities",
        # "Documentation": "https://arojas314.github.io/neonutilities/_build/html/",
    },
    license="MIT",
    packages=find_packages(),
    package_data={
        "": ["*.cfg", "*.txt"],
    },
    # python_requires='>3.7',
    install_requires=["numpy", "pandas", "geopandas", "urllib", "re", "shapely"],
    keywords=["NEON", "ecology", "lidar", "hyperspectral"],
    classifiers=[
        "Development Status :: 1 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Ecological Science",
    ],
    zip_safe=False,
)

###############################################################################
## Note: How to upload a new version to PyPI
## -------------------------------------------------
# Update version in
#  - setup.py
#  - CITATION.cff
#  - Create a tag and release in GitHub
# Created a new conda environment with twine
# conda create -n pypi python=3 twine pip -c conda-forge
"""
cd neonutilities
python setup.py sdist bdist_wheel
twine check dist/*
# Test PyPI
twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*
# PyPI
twine upload --skip-existing dist/*
"""


#######################################################
## If you need to change the default branch (to main in this case)
"""
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
"""
#######################################################
## {push updates to github}
"""
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
"""