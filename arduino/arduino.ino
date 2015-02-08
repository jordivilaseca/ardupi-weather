// temps entre actualitzacions de els elements
// [lm35_1, lm35_2, ldr_1]
const int numSen = 3;
const int groundPin = A0;
int types[] = {0,0,1};
unsigned long lastUpdate[] = {0,0,0};
unsigned long updateTimes[] = {60000,60000,30000};
int pins[] = {A1,A5,A3};

int secureAnalogRead(int pin) {
  delay(0.1);
  analogRead(groundPin);
  delay(0.1);
  return analogRead(pin);
  
}

float lm35(int pin) {
  return (5.0 * secureAnalogRead(pin) * 100.0) / 1024;
  //return analogRead(pin);
}

float ldr(int pin) {
  return secureAnalogRead(pin);
}

void sendCommand(String c, float v) {
  Serial.println(c);
  Serial.println(v);
}

void update(int type, int pin) {
  switch (type) {
    case 0:
      {
        float temp = lm35(pin);
        sendCommand("lm35_" + String(pin), temp);
        break;
      }
    case 1:
      {
        int val = ldr(pin);
        sendCommand("ldr_" + String(pin), val);
        break;
      }
  }
}

void updateAll() {
  for (int i = 0; i < numSen; i++) {
    unsigned long actTime = millis();
    if (actTime - lastUpdate[i]  > updateTimes[i]) {
      update(types[i], pins[i]);
      lastUpdate[i] = actTime;
    }
  }
}

void setup() {
  Serial.begin(9600); // set the baud rate
  for (int i = 0; i < numSen; i++) {
    pinMode(pins[i], INPUT);
    update(types[i],pins[i]);
  }  
}

void loop() {
  updateAll();
}

