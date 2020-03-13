"""
spotify-runners python package configuration.
"""
from setuptools import setup

setup(
    name="spotifyrunners",
    version="0.1.0",
    packages=["spotifyrunners"],
    include_package_data=True,
    install_requires=[
        "Flask==1.1.1",
        "Flask-Testing==0.7.1",
        "html5validator==0.3.1",
        "nodeenv==1.3.3",
        "pycodestyle==2.5.0",
        "pydocstyle==4.0.1",
        "pylint==2.4.1",
        "pytest==5.2.0",
        "requests==2.22.0",
    ],
)
