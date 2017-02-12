#include <OneWire.h>
#include <avr/delay.h>

#define CHANGERATE 5 // in which limits will the temperature change since the last reading, in degrees

// uses OneWire library from http://playground.arduino.cc/Learning/OneWire
//
// For every sensor found it outputs to serial:
// SensorID,CurrentTemp,Readout time,Current time
// Info at: http://wiki.spodeli.org/Хаклаб/Температура

OneWire ds(12);                       // 1Wire network on pin 12
int FirstRun = 1;

struct SensorData {
    byte addr[8];
    float temp;
    unsigned long time;
    unsigned int raw;
    byte signBit;
};

SensorData Senzori[8]; // we define that we will have a maximum of 8 sensors attached to the network
byte currentSensor = 0;
byte attachedSensors = 0;

void setup(void) {
    Serial.begin(9600);
    lcd.begin(20, 4);

    _delay_ms(100);

    // search for sensors
    cli();
    while (ds.search(Senzori[attachedSensors].addr)) {
        attachedSensors++;
    }
    sei();
}

void loop(void) {
    byte i, signBit;
    byte data[12];
    float celsius;

    for (currentSensor=0; currentSensor<attachedSensors; currentSensor++) {
        //CRC is not valid, go to next address
        if (OneWire::crc8(Senzori[currentSensor].addr, 7) != Senzori[currentSensor].addr[7]) {
            continue;
        }

        ds.reset();
        ds.select(Senzori[currentSensor].addr);
        ds.write(0x44,1); // start conversion, with parasite power on at the end

        _delay_ms(1000); // maybe 750ms is enough, maybe not

        ds.reset();
        ds.select(Senzori[currentSensor].addr);
        ds.write(0xBE); // Read Scratchpad

        //Get the temperature
        for ( i = 0; i < 9; i++) { // we need 9 bytes
            data[i] = ds.read();
        }

        // convert the data to actual temperature
        unsigned int raw = (data[1] << 8) | data[0];
        signBit = (raw & 0x8000) >> 15; // Check if we have a negative temperature reading
        if (signBit) {
            raw = (raw ^ 0xFFFF) + 1; // If the reading is negative (signBit) - do a 2's compliment
        }
        byte cfg = (data[4] & 0x60);
        if (cfg == 0x00) raw = raw << 3; // 9 bit resolution, 93.75 ms
        else if (cfg == 0x20) raw = raw << 2; // 10 bit res, 187.5 ms
        else if (cfg == 0x40) raw = raw << 1; // 11 bit res, 375 ms
        celsius = (float)raw / 16.0;


        // Add current data to struct
        Senzori[currentSensor].time = millis();
        // put the new sensor data into the structure, only if the current sensor redout is in the limit +/- CHANGERATE
        if ((celsius <= Senzori[currentSensor].temp + CHANGERATE) && (celsius >= Senzori[currentSensor].temp - CHANGERATE) && !FirstRun ) {
            Senzori[currentSensor].temp = celsius;
        }
        else if(FirstRun) {
            Senzori[currentSensor].temp = celsius;
        }

        Senzori[currentSensor].raw = raw;
        Senzori[currentSensor].signBit = signBit;
    }

    FirstRun=0;
}
