#!/usr/bin/env python3

from setuptools import setup

packages = [
        'ardupi_weather',
        'ardupi_weather.arduino',
        'ardupi_weather.database',
        'ardupi_weather.flaskfiles.app'
]

setup(
    name='ardupi_weather',
    url='https://github.com/jordivilaseca/Weather-station',
    license='Apache License, Version 2.0',
    author='Jordi Vilaseca',
    author_email='jordivilaseca@outlook.com',
    description='Weather station with Raspberry Pi and Arduino',
    long_description=open('../README.md').read(),
    packages=[str(l) for l in packages],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Flask>=0.10.1',
        'pymongo>=3.2.1',
        'PyYAML>=3.11',
        'bson>=0.4.2',
        'pyserial>=3.0.1' #,
        #'RPi.GPIO>=0.6.1'
    ],
    entry_points={
        'console_scripts': [
            'weather-station = ardupi_weather.station:main',
            'weather-server = ardupi_weather.flaskapp:main'
        ],
    },
)
