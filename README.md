# ardupi-weather
## Description
This is a weather station done using a Raspberry Pi and an Arduino. It includes a webserver to show the data that
contains the current values of the sensors, a chart with the history and a chart with the daily history (containing
minimum, maximum and the average values). The Arduino is in charge of collecting and sending the data and the
Rasbperry Pi processes and stores the data (at this moment mongo and sqlite databases are supported).

The webserver can be executed in the Raspberry Pi itself, or wherever you want. In the first case a mongo or a sqlite databases can be used, but in the second one there is only support for mongo databases.

The currently compatible sensors are the following:

 * BMP180: Barometric pressure.
 * DHTXX: Humidity and temperature.
 * BH1750: Luminance.
 * LDR: Luminance (analogical).
 * LM35: Temperature (analogical).

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
To install the package on a Raspberry Pi you can do the following.

```bash
sudo pip install "git+https://github.com/jordivilaseca/ardupi-weather.git#egg=ardupi-weather[rpi]&subdirectory=RaspberryPi"
```

The only difference between this and the PC installer is that in the case of the Raspberry Pi it also installs the GPIO package used in the NRF24 connexion, package not supported in a PC.

Check out the additional packages for some specific configurations.

### PC
Use the following command.

```bash
sudo pip install "git+https://github.com/jordivilaseca/ardupi-weather.git#egg=ardupi-weather&subdirectory=RaspberryPi"
```

#### Additional packages
##### NRF24L01+
[This](https://github.com/TMRh20/RF24) library has been used to add NRF24L01+ connexion between the Arduino and the Raspberry Pi. The package configuration steps are [here](http://tmrh20.github.io/RF24/RPi.html). Keep in mind that for using this hardware the SPI kernel module of the Raspberry Pi must be enabled.

## Connexions schematic
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/sensorsSketch_bb.png)

## Configuration

### Arduino
The script can be found inside the Arduino folder. To configure the arduino you must do the following.
 * Configure the connexion. Set the CONNECTION_TYPE and related variables.
 * Configure specific sensors. BMP180/DHTXX/BHT1750 have specific configuration.
 * Analogical sensor configuration (if some analogical sensor is used). Set a pin to groundPin and a pull-down circuit to it.
 * General sensor configuration. You must add a value to each one of the following variables:
  - type: Type of sensor.
  - lastUpdate: 0 as a default value.
  - updateTimes: The Arduino will send a result each updateTime milliseconds.
  - pins: The read pin for a analogical sensor, NOTUSED otherwise.

### Raspberry Pi
All the configuration of the Raspberry Pi is inside a config.yml file. This file is placed inside the folder ~/.config/ardupi_weather. The folder and the configuration file are created the first time the server or the station are launched, but you can manually create with the command `weather-station --init` or restore the default configuration with `weather-station --restore-config`.


- **arduino**: This contains all the configuration related with the Arduino.
  - **sensors**: {sensorID:valueType}. sensorID is an identifier of sensor, valueType is the type of data that the sensors sends. In case of existing more than one sensor sending the same valueType, a mean between the two sensors is computed.
  - **usedConnection**:
    - **usb**: it must be configured a port and a baud rate (the same baud rate must be configured to the Arduino)
    - **nrf24l01p**: it must be configured a repetition value, thats it the number of times the Arduino will try to send data.
    - **test**: it generates random data.

- **data**: It contains all the related information about data and databases.
  - **name**: Name of the database.
  - **values**: {valueType:dataType}. For each valueType in the Arduino sensors, you must set its dataType (FLOAT/INTEGER).
  - **usedDB**: Name of the database used (mongo/sqlite).
  - **sqlite**: Information about sqlite database (if it is not used, there is no need to configure it).
    - **path**: Path of the database. The database will be searched to path with the name described in the name field. If the path is "default" the path will be inside de configuration folder of the station.
  - **mongo**: Information about mongo database (if it is not used, there is no need to configure it).
    - **uri**: Mongo database connection uri.
  - **currentData**: Record current data into the database, the old values are updated when new ones arrive.
    - **enable**: yes/no.
    - **name**: A name for the database.
    - **updateEvery**: A dictionary. The currentData will be updated every *d* days, *h* hours, *m* minutes and *s* seconds. The value of the sensor is the last one that has arrived.
  - **history**: Record of data, it stores all the data from the first moment it was initialized. The records are made every *updateEvery* time, it calculates the average for each type of data.
    - **enable**: yes/no.
    - **name**: A name for the database.
    - **updateEvery**: A dictionary. The currentData will be updated every *d* days, *h* hours, *m* minutes and *s* seconds. The value of the sensor is the last one that has arrived.
  - **dailyHistory**: Record of daily data, it stores the daily minimum, maximum and the average for each type of data.
    - **enable**: yes/no.
    - **name**: A name for the database.

## Running

When you have the package installed you must be able to start the station using the default configuration (the data will be randomly generated).

to run the station you need write this command into the terminal `weather-station`, or for the server case `weather-server`. In case of using NRF24L01+ as a connexion, it could be you need to run the weather-station as super user `sudo weather-station`.

## Screenshots
### Webpage
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/screenshots/webpage1.png)
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/screenshots/webpage2.png)
### History chart
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/screenshots/historyChart.png)
![Image Alt](https://github.com/jordivilaseca/ardupi-weather/blob/master/screenshots/DailyChart.png)

