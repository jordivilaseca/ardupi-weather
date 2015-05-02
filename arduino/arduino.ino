#include <Wire.h>
#include <SFE_BMP180.h>
#include "DHT.h"

#define count(x) sizeof(x)/sizeof(unsigned long)
#define groundPin A0


#define ALTITUDE 570 // We need it for the barometric pressure calculus

#define BMP180T 0   // Temperature
#define BMP180P 1   // Pressure
#define DHT22T  2   // Temperature
#define DHT22H  3   // Humidity
#define DHT22HI 4   // Heat Index

#define NOTUSED -1  // For BMP180/DHT22 sensor.

#define DHTTYPE DHT22
#define DHTPIN  4

SFE_BMP180 pressure;
DHT dht(DHTPIN, DHTTYPE);

int types[] = {BMP180T,BMP180P,DHT22T,DHT22H,DHT22HI};
unsigned long lastUpdate[] = {0,0,0,0,0};
unsigned long updateTimes[] = {30000,60000,30000,30000,60000};
int pins[] = {NOTUSED,NOTUSED,NOTUSED,NOTUSED,NOTUSED};

int secureAnalogRead(int pin) {
  //delay(0.01);
  //analogRead(groundPin);
  //delay(0.01);
  return analogRead(pin);
  
}

boolean bmp180Temperature(double &T) {
  char status;
  status = pressure.startTemperature();
  if (status != 0) {
    delay(status);
    status = pressure.getTemperature(T);
    if(status != 0) return true;
  }
  return false;
}

boolean bmp180Pressure(double &P) {
  double T, absP;
  char status;
  if(bmp180Temperature(T)) {
    status = pressure.startPressure(3);
    if (status != 0) {
        delay(status);
        status = pressure.getPressure(absP,T);
        if (status != 0) {
          P = pressure.sealevel(absP,ALTITUDE);
          return true;
        }
      }
  }
  return false;
}

float lm35(int pin) {
  return (5.0 * secureAnalogRead(pin) * 100.0) / 1024;
}

int ldr(int pin) {
  return map(secureAnalogRead(pin), 0, 1023, 0, 100);
}

void sendCommand(String c, String v) {
  Serial.println(c);
  Serial.println(v);
}

void update(int type, int pin) {
  String c, v;
  switch (type) {
    case BMP180T:
      {
      double t;
      c = "BMP180T";
      if (bmp180Temperature(t)) v = String(t);
      else v = c + " Error";
      break;
      }

    case BMP180P:
      {
      double p;
      c = "BMP180P";
      if (bmp180Pressure(p)) v = String(p);
      else v = c + " Error";
      break;
      }

    case DHT22T:
      {
      float t = dht.readTemperature();    // Default temperature unit is ºC.
      c = "DHT22T";
      v = String(t);
      break;
      }

    case DHT22H:
      {
      float h = dht.readHumidity();
      c = "DHT22H";
      v = String(h);
      break;
      }
    case DHT22HI:
      {
      float h, t, hi;
      h = dht.readHumidity();
      t = dht.readTemperature(true);    // We need value in farenheit.
      hi = dht.computeHeatIndex(t,h);
      c = "DHT22HI";
      v = String(dht.convertFtoC(hi));
      break;
      }
  }
  sendCommand(c, v);
}

void updateAll() {
  for (int i = 0; i < count(updateTimes); i++) {
    unsigned long actTime = millis();
    if (actTime - lastUpdate[i]  > updateTimes[i]) {
      update(types[i], pins[i]);
      lastUpdate[i] += updateTimes[i];
    }
  }
}

// DUMP FUNCTIONS

String inpBuffer = "";

String readCommand() {
  String ret = "";
  if (Serial.available()){
    char c;
    while(Serial.available() && (c = Serial.read()) != '\n') {
      inpBuffer += c;
    }
    if (c == '\n') {
      ret = inpBuffer;
      inpBuffer = "";
    }
  }
  return ret;
}

void dump() {
  String inp = readCommand();
  if (inp == "") {
  } else if (inp == "dump") {
    for (int i = 0; i < count(updateTimes); i++) {
      String com = String(i) + " " + String(types[i]) + " " + String(updateTimes[i]) + " " + String(pins[i]);
      sendCommand("dump_pin", com);
    }
  } else if (inp == "modify") {
    int sensor = Serial.parseInt();
    types[sensor] = Serial.parseInt();
    updateTimes[sensor] = Serial.parseInt(); 
    pins[sensor] = Serial.parseInt();   
  }
}

void setup() {
  Serial.begin(9600); // set the baud rate
  if (pressure.begin()) Serial.println("BMP180 init success");
  else Serial.println("BMP180 init fail\n\n");
  dht.begin();
  
  for (int i = 0; i < count(updateTimes); i++) {
    pinMode(pins[i], INPUT);
    update(types[i],pins[i]);
  }
}

void loop() {
  updateAll();
  dump();
}

