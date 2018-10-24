#include <SFE_BMP180.h>
#include <BH1750.h>
#include <DHT.h>

#define count(x) sizeof(x)/sizeof(unsigned long)

#define BMP180T 0   // Temperature
#define BMP180P 1   // Pressure
#define DHT22T  2   // Temperature
#define DHT22H  3   // Humidity
#define DHT22HI 4   // Heat Index
#define BH1750L 5   // Light sensor
#define LM35    6   // Temperature (analogical)
#define LDR     7   // Light sensor (analogical)

#define NOTUSED -1  // For BMP180/DHT22/BH1750 sensor.

/*
 * CONNEXION CONFIGURATION
 */
#define CONNECTION_TYPE 2 // 0 -> USB, 1 -> 433mhz, 2 -> nrf24l01+

#if CONNECTION_TYPE == 1
  #include <VirtualWire.h>
  #define TRANSMIT_PIN 10
  #define REPETITIONS 5   // Number of times that a message will be sent. Minimum is 1
#elif CONNECTION_TYPE == 2
  #include <SPI.h>
  #include "RF24.h"
  RF24 radio(9,10);       // CE and CSN of nrf24l01+
  const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };
#endif

/*
 * BMP180 CONFIGURATION
 */
#define BMP180_ENABLE true
#define ALTITUDE 570 // We need it for the barometric pressure calculus

/*
 * DHTXX CONFIGURATION
 */
#define DHT_ENABLE true
#define DHTTYPE DHT22
#define DHTPIN  6

/*
 * BH1750 CONFIGURATION
 */
 #define BH1750_ENABLE true

/*
 * ANALOG SENSOR CONFIGURATION
 */
#define groundPin A0  // In case of not having any analog it doesn't matter its value.

/*
 * GENERAL CONFIGURATION
 */
int types[] = {BMP180T,BMP180P,DHT22T,DHT22H,DHT22HI,BH1750L};
unsigned long lastUpdate[] = {0,0,0,0,0,0};
unsigned long updateTimes[] = {60000,60000,30000,30000,60000,60000};
int pins[] = {NOTUSED,NOTUSED,NOTUSED,NOTUSED,NOTUSED,NOTUSED};

/*
 * DECLARE VARIABLES
 */
#if BMP180_ENABLE
  SFE_BMP180 pressure;
#endif
#if DHT_ENABLE
  DHT dht(DHTPIN, DHTTYPE);
#endif
#if BH1750_ENABLE
  BH1750 light;
#endif

int secureAnalogRead(int pin) {
  delay(0.01);
  analogRead(groundPin);
  delay(0.01);
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

uint16_t BH1750Light() {
  return light.readLightLevel();
}

#if CONNECTION_TYPE == 0

void sendCommand(String c, String v) {
  Serial.println(c + "_" + v);
}

#elif CONNECTION_TYPE == 1

void sendData(String s) {
  const char* cchar = s.c_str();
  vw_send((uint8_t *)cchar, strlen(cchar));
  vw_wait_tx(); // Wait until the whole message is gone
}

void sendCommand(String c, String v) {
  for(int i = 0; i < REPETITIONS; i++) {
    sendData(c + "_" + v);
  }
}

#elif CONNECTION_TYPE == 2

void sendCommand(String c, String v) {
  String data = c + "_" + v;
  const char* datachar = data.c_str();

  radio.powerUp();
  radio.write(datachar, strlen(datachar));
  radio.powerDown();
}
#endif

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
    case BH1750L:
      {
        c = "BH1750";
        v = String(BH1750Light());
        break;
      }
    case LM35:
      {
        c = "LM35";
        v = secureAnalogRead(pin);
        break;
      }
    case LDR:
      {
        c = "LDR";
        v = secureAnalogRead(pin);
      }
  }
  sendCommand(c, v);
}

void updateAll() {
  for (int i = 0; i < count(updateTimes); i++) {
    unsigned long currentTime = millis();
    if (currentTime < lastUpdate[i]) {
      lastUpdate[i] = 0;
    }
    else if (currentTime - lastUpdate[i]  > updateTimes[i]) {
      update(types[i], pins[i]);
      lastUpdate[i] += updateTimes[i];
    }
  }
}

void setup() {

  #if CONNECTION_TYPE == 0
    Serial.begin(57600,SERIAL_8E1); // set the baud rate
  #elif CONNECTION_TYPE == 1
    vw_set_tx_pin(TRANSMIT_PIN);
    vw_setup(2000);       // Bits per sec
  #elif CONNECTION_TYPE == 2
    radio.begin();
    radio.setPALevel(RF24_PA_MAX);
    radio.setDataRate( RF24_250KBPS ) ;
    radio.enableDynamicPayloads();
    radio.setRetries(5,15);
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
    radio.stopListening();
  #endif

  #if BMP180_ENABLE
    pressure.begin();
  #endif

  #if DHT_ENABLE
    dht.begin();
  #endif

  #if BH1750_ENABLE
    light.begin();
  #endif

  for (int i = 0; i < count(updateTimes); i++) {
    update(types[i],pins[i]);
  }
}

void loop() {
  updateAll();
}

