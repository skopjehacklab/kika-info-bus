The code here runs on an Arduino (avr atmega328p) and collects info from:
 - 1wire sensors
 - a rotary encoder knob

Displays data on a:
 - small LiquidCrystal lcd
 - bigger DPD-201 LED display

Pushes out data to serial line, in the form of:

    Sensor_ID,Current_Temp,Readout_Time,Current_Time\n
    ...
    Status: Knob_State\n
    \n


