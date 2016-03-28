# Weather-station
## Description
This is a weather station done using a Raspberry Pi and an Arduino. It includes a webserver to show the data that
contains the current values of the sensors, a chart with the history and a chart with the daily history (containing
minimum, maximum and the average values). The Arduino is in charge of collecting and sending the data and the 
Rasbperry Pi processes and stores the data (at this moment mongo and sqlite databases are supported).

The webserver can be executed in the Raspberry Pi itself, or wherever you want. In the first case a mongo or a sqlite databases can be used, but in the second one there is only support for mongo databases.

## Hardware tested
This package has been tested using an Arduino Nano v3 and Raspberry Pi 2. In case of using a different Raspberry Pi model there must not be differences in the connexions, but in the arduino case in most cases there will be.

## Installation

### Arduino
The following packages are used in the Arduino script, if you need some of them for your own station, they need
to be manually installed. In most cases it can be done by copying the github repositories to the libraries folder
of the pc ("~/Arduino/libraries" in linux).

 * BH1750: BH1750 - https://github.com/claws/BH1750
 * DHT22: DHT-sensor-library - https://github.com/adafruit/DHT-sensor-library
 * NRF24L01+: RF24 - https://github.com/TMRh20/RF24
 * BMP180: BMP180_Breakout - https://github.com/sparkfun/BMP180_Breakout

Once you have all the necessary packages downloaded you must be able to compile the .ino file from inside the arduino folder.

### Raspberry Pi
To install the package on a Raspberry Pi you can follow the next steps.
```bash
git clone https://github.com/jordivilaseca/ardupi-weather.git
cd ardupi-weather/RaspberryPi
chmod +x setup.py
./setup.py build
sudo ./setup.py install
```

At this point you must be able to start the station using the default configuration (the data will be radomly generated). Check out the additional requirements for some specific configurations.

to run the station you need write this command into the terminal `weather-station`, or for the server case `weather-server`.

#### Additional packages
##### NRF24L01+
[This](https://github.com/TMRh20/RF24) library has been used to add NRF24L01+ connexion between the Arduino and the Raspberry Pi. The package configuration steps are [here](http://tmrh20.github.io/RF24/RPi.html). Keep in mind that for using this hardware the SPI kernel module of the Raspberry Pi must be enabled.

## Connexions schematic
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/sensorsSketch_bb.png)
