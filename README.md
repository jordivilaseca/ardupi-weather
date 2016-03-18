# Weather-station
## Description
This is a weather station done using a Raspberry Pi and an Arduino. It includes a webserver to show the data that
contains the current values of the sensors, a chart with the history and a chart with the daily history (containing
minimum, maximum and the average values). The Arduino is in charge of collecting and sending the data and the 
Rasbperry Pi processes and stores the data (at this moment mongo and sqlite databases are supported).

The webserver can be executed in the Raspberry Pi itself, or wherever you want. In the first case a mongo or a sqlite databases can be used, but in the second one there is only support for mongo databases.

## Installation

### Arduino
The following packages are used in the Arduino script, if you need some of them for your own station, they need
to be manually installed. In most cases it can be done by copying the github repositories to the libraries folder
of the pc ("~/Arduino/libraries" in linux).

BH1750: BH1750 - https://github.com/claws/BH1750
DHT22: DHT-sensor-library - https://github.com/adafruit/DHT-sensor-library
NRF24L01+: RF24 - https://github.com/TMRh20/RF24
BMP180: BMP180_Breakout - https://github.com/sparkfun/BMP180_Breakout

### Raspberry Pi

## Configuration
