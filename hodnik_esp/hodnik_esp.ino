#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
#include <ESP8266WiFi.h>

const int buttonPin = D8;     // the number of the pushbutton pin
const int ledPin =  D6;       // the number of the LED pin
const int pirPin =  D3;       // the number of the PIR sensor pin

#define WLAN_SSID       "KIKA"
#define WLAN_PASS       ""

#define MQTT_SERVER      "192.168.88.2"
#define MQTT_SERVERPORT  1883                   // use 8883 for SSL
#define MQTT_USERNAME    ""
#define MQTT_KEY         ""

WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, MQTT_SERVER, MQTT_SERVERPORT, MQTT_USERNAME, MQTT_USERNAME, MQTT_KEY);

Adafruit_MQTT_Subscribe feedLed = Adafruit_MQTT_Subscribe(&mqtt, "haklab/hodnik/led");
Adafruit_MQTT_Publish feedButton = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/button");
Adafruit_MQTT_Publish feedPir = Adafruit_MQTT_Publish(&mqtt, "haklab/hodnik/pirsensor");


// Bug workaround for Arduino 1.6.6, it seems to need a function declaration
// for some reason (only affects ESP8266, likely an arduino-builder bug).
void MQTT_connect();

int buttonState = 0;
int pirState = 0;
int prevButtonState = 0;
int prevPirState = 0;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT);
  pinMode(pirPin, INPUT);

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

  feedLed.setCallback(&ledCallback);
  mqtt.subscribe(&feedLed);

  buttonState = digitalRead(buttonPin);
  pirState = digitalRead(pirPin);
  feedButton.publish(buttonState == HIGH ? "ON" : "OFF");
  feedPir.publish(pirState == HIGH ? "ON" : "OFF");
  prevButtonState = buttonState;
  prevPirState = pirState;
}

void ledCallback(char *data, uint16_t len) {
  Serial.print(F("Got LED state: "));
  Serial.println(data);
  
  if (strcmp(data, "OFF") == 0) {
    digitalWrite(ledPin, LOW); 
  }
  if (strcmp(data, "ON") == 0) {
    digitalWrite(ledPin, HIGH); 
  }
}

void loop() {
  MQTT_connect();

  buttonState = digitalRead(buttonPin);
  pirState = digitalRead(pirPin);
  if (buttonState != prevButtonState) {
    feedButton.publish(buttonState == HIGH ? "ON" : "OFF");  
    Serial.print(F("Set BTN state: "));
    Serial.println(buttonState == HIGH ? "ON" : "OFF");
  }
  if (pirState != prevPirState) {
    feedPir.publish(pirState == HIGH ? "ON" : "OFF");
    Serial.print(F("Set PIR state: "));
    Serial.println(pirState == HIGH ? "ON" : "OFF");
  }
  prevButtonState = buttonState;
  prevPirState = pirState;

  mqtt.processPackets(500);

  // ping the server to keep the mqtt connection alive
  if(! mqtt.ping()) {
    mqtt.disconnect();
  }

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

  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
       Serial.println(mqtt.connectErrorString(ret));
       Serial.println("Retrying MQTT connection in 5 seconds...");
       mqtt.disconnect();
       delay(5000);  // wait 5 seconds
       retries--;
       if (retries == 0) {
         // basically die and wait for WDT to reset me
         while (1);
       }
  }
  Serial.println("MQTT Connected!");
}
