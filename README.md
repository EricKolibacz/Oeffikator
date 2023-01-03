# Oeffikator

![Code Checks](https://github.com/EricKolibacz/Oeffikator/actions/workflows/code_checks.yml/badge.svg)
![Python Tests](https://github.com/EricKolibacz/Oeffikator/actions/workflows/python_tests.yml/badge.svg)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com/)
[![Coverage Status](https://coveralls.io/repos/github/EricKolibacz/Oeffikator/badge.svg?branch=main&kill_cache=1&service=github&sanitize=true)](https://coveralls.io/github/EricKolibacz/Oeffikator?branch=main)

The Oeffikator App enables you to receive an visual overview of commuting times via public transport in Berlin. Oeffikator uses BVG and VBB APIs to get information on commuting times between an origin and possible destinations and plots the result through an overlaying head map on a central Berlin map. You can see an example map with the Brandenburger Gate as origin below:

![map_Berlin_BranderburgerTor](https://user-images.githubusercontent.com/26793186/155340615-c61b984c-9019-4f6d-bf61-5c50f88547ec.png)


## Logic

The underlying idea of the Oeffikator app is to compute the travel time between a given origin to possible different destinations in central Berlin. The following GIF shall provide some idea on how this is achieved. The origin here is Brandeburger Tor. First, we create a 3x3 grid on the bounding box of the area we want to evaluate (here raughly public transportation area A). Then, we compute the travel times to all of these destinations. Following, we determin the area with the least points through a Triangulisation and compute its travel time. On the fly, we collect the travelling times for all the stops we take on our trip to this destination. And this is what we repeat over and over again until we have a fine net of points all over Berlin. 


![example_gif](https://user-images.githubusercontent.com/26793186/210392418-28f91afc-c348-4b23-9b19-ddeeae014f35.gif)
