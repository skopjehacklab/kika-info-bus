#include <OneWire.h>
#include <LiquidCrystal.h>

#define INPUTPIN 5
OneWire  ds(12);  // on pin 12 (a 4.7K resistor is necessary)
LiquidCrystal lcd(6, 7, 8, 9, 10, 11);


// printf support
static int Serial_write(char c, FILE *) {
    return Serial.write(c);
}
static FILE mystdout;

void setup(void) {
  Serial.begin(9600);
  stdout = &mystdout;
  fdev_setup_stream(stdout, Serial_write, NULL, _FDEV_SETUP_WRITE);
  lcd.begin(20, 4);
}

void loop(void) {
  byte data[12];
  byte addr[8];

  if ( !ds.search(addr)) {
    if (digitalRead(INPUTPIN)) {
      Serial.println("status: OPEN");
    } else {
      Serial.println("status: CLOSED");
    }
    Serial.println();
    ds.reset_search();
    delay(1000);
    return;
  }

  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("<4>addr CRC is not valid!");
      return;
  }

  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x28: // only handle DS18B20 for now;
      break;
    default:
      //Serial.println("<4>Device is not a DS18x20 family device.");
      return;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end

  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.

  ds.reset();
  ds.select(addr);
  ds.write(0xBE);         // Read Scratchpad

  for (byte i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }
  if (OneWire::crc8(data, 8) != data[8]) {
    Serial.println("<4>data CRC is not valid!");
    return;
  }

  // OUTPUT
  float celsius = calculateTemperature(data);
  lcdPrint(addr, celsius);

  for(byte j = 0; j < 7; j++) {
    printf("%02X", addr[j]);
  }
  Serial.print(',');
  Serial.print(celsius);
  Serial.print(',');
  Serial.print(millis());
  Serial.println();
}

float calculateTemperature(byte data[8]) {
  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];

  byte cfg = (data[4] & 0x60);
  // at lower res, the low bits are undefined, so let's zero them
  if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
  else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
  else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
  //// default is 12 bit resolution, 750 ms conversion time
  return (float)raw / 16;
}

void lcdPrint(byte addr[7], float celsius) {
  byte line;
  String place;
  if (memcmp(addr, (const byte[]){0x28, 0x4C, 0x60, 0x63, 0x04, 0x00, 0x00}, 7) == 0) {
    place = "Lounge: ";
    line = 0;
  } else if (memcmp(addr, (const byte[]){0x28, 0x25, 0x76, 0xB0, 0x03, 0x00, 0x00}, 7) == 0) {
    place = "Outside: ";
    line = 1;
  } else if (memcmp(addr, (const byte[]){0x28, 0xB5, 0x03, 0x59, 0x03, 0x00, 0x00}, 7) == 0) {
    place = "HW room: ";
    line = 2;
  } else if (memcmp(addr, (const byte[]){0x28, 0x5B, 0xEF, 0x57, 0x03, 0x00, 0x00}, 7) == 0) {
    place = "Random: ";
    line = 3;
  } else {
    return;
  };
  lcd.setCursor(0, line);
  lcd.print(place);
  lcd.print(celsius);
}

