#include <Arduino.h>

// put function declarations here:
#define TEMP_PIN       26
#define LED_PIN        32
#define RUNNING_LED_PIN  14

#define R_BIAS        14870 // ohm 
#define VCC           5.13 //V_in value
#define V_READ        3.3 //Maximum value of reading == 4095
#define RES           4095 
#define TIME_RES      500 //Time between each read

bool STATE_LED = 0; 
bool DO_READ = 0;
bool STATE_RUNNING_LED = 0;

int _READ ;

void setup() {

  Serial.begin(115200);

  pinMode(LED_PIN,OUTPUT);
  pinMode(TEMP_PIN,INPUT);
  pinMode(RUNNING_LED_PIN,OUTPUT);

  Serial.println("Initializing OK");
}

void loop() {
  // Read if there is instruction from the computer

  if(Serial.available()){
    _READ =  Serial.read();
    Serial.print("Recieved : "); Serial.println(_READ);
    if(_READ == 78){ //N in ascii for ON
      DO_READ = 1;
    }
    else if(_READ == 70){ //F in ascii for OFF
      DO_READ = 0;
    }

  }

  // Turning HIGH the LED if it is LOW and we are reading the values
  if(DO_READ){
    if(!STATE_LED){
      digitalWrite(LED_PIN,HIGH);
      STATE_LED = !STATE_LED;
    }
  }

  // Turning LOW the LED if it is HIGH and we are NOT reading the values
  else if(!DO_READ){
    if(STATE_LED){
      digitalWrite(LED_PIN,LOW);
      STATE_LED = !STATE_LED;
    }
  }

  int bit_read = analogRead(TEMP_PIN);        // Read
  float volt = (V_READ/RES)*bit_read;         //Convert to volts = V_out 
  float res = (R_BIAS*volt)/(VCC - volt) ;    // Voltage divider formula for resistance : Thermistor -> R2

//The line the computer is going to receive
// If you want to change this line, you need to change the python GUI reading function
  Serial.print("R = "); Serial.println(res); 


  delay(TIME_RES);

  // Blinking the LED showing that the program is running
  STATE_RUNNING_LED = !STATE_RUNNING_LED;
  digitalWrite(RUNNING_LED_PIN,STATE_RUNNING_LED);

}