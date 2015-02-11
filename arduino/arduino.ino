// temps entre actualitzacions de els elements
// [lm35_1, lm35_2, ldr_1]
const int numSen = 3;
const int groundPin = A0;
int types[] = {0,0,1};
unsigned long lastUpdate[] = {0,0,0};
unsigned long updateTimes[] = {60000,60000,30000};
int pins[] = {A1,A5,A3};

int secureAnalogRead(int pin) {
  delay(0.01);
  analogRead(groundPin);
  delay(0.01);
  return analogRead(pin);
  
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
    case 0:
        c = "lm35_" + String(pin);
        v = String(lm35(pin));
        break;
    case 1:
        c = "ldr_" + String(pin);
        v = String(ldr(pin));
        break;
  }
  sendCommand(c, v);
}

void updateAll() {
  for (int i = 0; i < numSen; i++) {
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
    for (int i = 0; i < numSen; i++) {
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
  Serial.begin(57600); // set the baud rate
  for (int i = 0; i < numSen; i++) {
    pinMode(pins[i], INPUT);
    update(types[i],pins[i]);
  }  
}

void loop() {
  updateAll();
  dump();
}

