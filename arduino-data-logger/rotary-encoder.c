enum PinAssignments {
  encoderPinA = 2,  // INT0 (PD2)  External Interrupt Request 0
  encoderPinB = 3,  // INT1 (PD3)  External Interrupt Request 1
  clearButton = 8
};

#define CHANGETIMEOUT 2000
#define CHANGETHRESHOLD 10

volatile unsigned int encoderPos = 0;

void rotary_encoder_init () {
  pinMode(encoderPinA, INPUT);
  pinMode(encoderPinB, INPUT);
  pinMode(clearButton, INPUT);
  digitalWrite(encoderPinA, HIGH);  // turn on pullup resistor
  digitalWrite(encoderPinB, HIGH);  // turn on pullup resistor
  digitalWrite(clearButton, HIGH);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoderA, CHANGE);
  // encoder pin on interrupt 1 (pin 3)
  attachInterrupt(1, doEncoderB, CHANGE);
}

// loop variables
unsigned int  lastReportedPos = 1;
signed   int  relativePosChange = 0;
unsigned long lastPosChangeTime = 0;

void rotary_encoder_loop (){
  unsigned long time;
  if (lastReportedPos != encoderPos) {
    time = millis();
    if ( time - lastPosChangeTime < CHANGETIMEOUT) {
      relativePosChange += encoderPos - lastReportedPos;
      if (abs(relativePosChange) > CHANGETHRESHOLD) {
        relativePosChange = 0;
      }
    } else {
      relativePosChange = 0;
    }
    lastPosChangeTime = time;
    lastReportedPos = encoderPos;
  }
  if (digitalRead(clearButton) == LOW)  {
    encoderPos = 0;
    relativePosChange = 0;
  }
}

// Interrupt on A changing state
void doEncoderA(){
  byte port = PIND & 0b00001100;                // interested only in pins 2 and 3
  if ((port == 0b00001100) or (port == 0)) {
    encoderPos++;
  } else {
    encoderPos--;
  }
}

// Interrupt on B changing state
void doEncoderB(){
  byte port = PIND & 0b00001100;                // interested only in pins 2 and 3
  if ((port == 0b00001100) or (port == 0)) {
    encoderPos--;
  } else {
    encoderPos++;
  }
}
