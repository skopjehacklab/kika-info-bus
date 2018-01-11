#include <ESP8266WiFi.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const int buttonPin = D7;     // the number of the pushbutton pin
const int ledPin =  D6;       // the number of the LED pin
const int pirPin =  D5;       // the number of the PIR sensor pin
const int onewirePin = D2;

#define WLAN_SSID       "KIKA"
#define WLAN_PASS       ""

#define MQTT_SERVER      "192.168.88.2"
#define MQTT_SERVERPORT  1883                   // use 8883 for SSL
#define MQTT_USERNAME    ""
#define MQTT_KEY         ""

WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_USERNAME, MQTT_KEY);

Adafruit_MQTT_Subscribe feedLed = Adafruit_MQTT_Subscribe(&mqtt, "haklab/status");
Adafruit_MQTT_Publish feedBoot = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/bootup");
Adafruit_MQTT_Publish feedButton = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/button");
Adafruit_MQTT_Publish feedPir = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/pirsensor");
Adafruit_MQTT_Publish feedTemp = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/temp");

OneWire oneWire(onewirePin);
DallasTemperature sensors(&oneWire);

// Bug workaround for Arduino 1.6.6, it seems to need a function declaration
// for some reason (only affects ESP8266, likely an arduino-builder bug).
void MQTT_connect();

int buttonState = 0;
int prevBtnPub = 0;
int pirState = 0;
int prevPirPub = 0;
bool pubButtonState = 0;
bool pubPirState = 0;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT);
  pinMode(pirPin, INPUT);
  sensors.begin();
  sensors.setResolution(12);
 
  Serial.begin(115200);
  delay(10);

  // Connect to WiFi access point.
  Serial.println(); Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.println("WiFi connected");
  Serial.println("IP address: "); Serial.println(WiFi.localIP());

  sensors.requestTemperatures(); // Send the command to get temperatures
  Serial.print("Temperature for the device 1 (index 0) is: ");
  Serial.println(sensors.getTempCByIndex(0)); 

  feedLed.setCallback(&ledCallback);
  mqtt.subscribe(&feedLed);

  buttonState = digitalRead(buttonPin);
  pirState = digitalRead(pirPin);
  feedButton.publish(buttonState == HIGH ? "ON" : "OFF");
  feedPir.publish(pirState == HIGH ? "ON" : "OFF");
  prevBtnPub = buttonState;
  prevPirPub = pirState;

  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonChanged, CHANGE);
  attachInterrupt(digitalPinToInterrupt(pirPin), pirChanged, CHANGE);

  feedBoot.publish("ON");
}

void buttonChanged() {
  buttonState = digitalRead(buttonPin);
  Serial.print(F("Set BTN state: "));
  Serial.println(buttonState == HIGH ? "ON" : "OFF");
  pubButtonState = true;
}

void pirChanged() {
  pirState = digitalRead(pirPin);
  Serial.print(F("Set PIR state: "));
  Serial.println(pirState == HIGH ? "ON" : "OFF");
  pubPirState = true;
}

void ledCallback(char *data, uint16_t len) {
  Serial.print(F("Got LED state: "));
  Serial.println(data);
  
  if (strcmp(data, "CLOSED") == 0) {
    digitalWrite(ledPin, LOW); 
  }
  if (strcmp(data, "OPEN") == 0) {
    digitalWrite(ledPin, HIGH); 
  }
}

int msecMqttProc = 100;
int loopsForPing = 0;

void loop() {
  MQTT_connect();

  if (pubButtonState) {
    if (prevBtnPub == LOW && buttonState == LOW) {
      Serial.println(F("Missed a button ON event, publishing it..."));
      feedButton.publish("ON");  
    }
    Serial.print(F("Publishing BTN state: "));
    Serial.println(buttonState == HIGH ? "ON" : "OFF");
    feedButton.publish(buttonState == HIGH ? "ON" : "OFF");  
    pubButtonState = false;
    prevBtnPub = buttonState;
  }
  if (pubPirState) {
    if (prevPirPub == LOW && pirState == LOW) {
      Serial.println(F("Missed a pir ON event, publishing it..."));
      feedPir.publish("ON");  
    }
    Serial.print(F("Publishing PIR state: "));
    Serial.println(pirState == HIGH ? "ON" : "OFF");
    feedPir.publish(pirState == HIGH ? "ON" : "OFF");
    pubPirState = false;
    prevPirPub = pirState;
  }
  
  mqtt.processPackets(msecMqttProc);

  // ping the server to keep the mqtt connection alive
  int secsSinceLastPing = loopsForPing / (1000 / msecMqttProc);
  if (secsSinceLastPing > 30) {
    
    if(!mqtt.ping())
      mqtt.disconnect();

    sensors.setResolution(12);
    sensors.requestTemperatures(); // Send the command to get temperatures
    float temp = sensors.getTempCByIndex(0);
    Serial.print("Temperature for the device 1 (index 0) is: ");
    Serial.println(temp); 
    feedTemp.publish(temp);

    loopsForPing = 0;
  }
  loopsForPing++;

}


// Function to connect and reconnect as necessary to the MQTT server.
// Should be called in the loop function and it will take care if connecting.
void MQTT_connect() {
  int8_t ret;

  // Stop if already connected.
  if (mqtt.connected()) {
    return;
  }

  Serial.print("Connecting to MQTT... ");

  uint8_t retries = 12; // retry for one minute
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    
    delay(5000);  // wait 5 seconds
    retries--;
    if (retries == 0) {
      // reset ourselves
      ESP.restart();
    }
  }
  Serial.println("MQTT Connected!");
  
  // tell the world we reconnected, send us updates
  feedBoot.publish("ON");
}
