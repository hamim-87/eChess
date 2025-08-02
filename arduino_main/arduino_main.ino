#include <Wire.h>

#define ATMEGA32_ADDRESS 0x08
#define BUTTON_WHITE_SWITCH_MOTOR_WHITE 10
#define BUTTON_BLACK_SWITCH_MOTOR_BLACK 11
#define MOSFET_GATE 9

// Commands to send to ATmega32 (matching your direction definitions)
#define CMD_L_R 0
#define CMD_R_L 1
#define CMD_B_T 2
#define CMD_T_B 3
#define CMD_STOP 4
#define CMD_CALIBRATE_STEP 5


// for debugging 
const int ledPin = 13;  
const int limitSwitchPin = 11; 

//button
bool lastButtonState = HIGH;
bool currentButtonState = HIGH;
const int BUTTON_PIN = 2;

int moveCount = 0;

String storedMoves[100];



//
enum { start, player_white, player_black};
byte sequence = start;

void setup() {
  Wire.begin(); // Initialize I2C as master
  Wire.setClock(100000);

  pinMode(MOSFET_GATE, OUTPUT);
  digitalWrite(MOSFET_GATE, LOW);


  pinMode(limitSwitchPin, INPUT_PULLUP); // Use internal pull-up resistor
  pinMode(ledPin, OUTPUT); 

  pinMode(BUTTON_WHITE_SWITCH_MOTOR_WHITE, INPUT_PULLUP);
  pinMode(BUTTON_BLACK_SWITCH_MOTOR_BLACK, INPUT_PULLUP);

  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);

  // button
  pinMode(BUTTON_PIN, INPUT_PULLUP);



  Serial.begin(9600);


    //   delay(100);

    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_L_R);
    // Wire.write(4);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();

  // helper_cal_top();

  // calibrate();
  // zero_zero_pos();

   // make_move();

  // Electromagnet_on();



  // calibrate();


  // zero_zero_pos();

  // delay(5000);

  // Electromagnet_off();

  // make_move(0,1,2,2);

  

  
  // Wire.beginTransmission(ATMEGA32_ADDRESS);
  //     //Serial.println("after ....");
  //   Wire.write(CMD_STOP);
  //   Wire.write(1);
  //   //Serial.println("after2 ....");

  //   Wire.endTransmission();



    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_R_L);
    // Wire.write(28);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();

    // delay(3000);

    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_T_B);
    // Wire.write(28);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();

    // delay(14000);

    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_T_B);
    // Wire.write(14);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();


  

}

void calibrate() {
  Serial.println("Starting calibration...");
  Electromagnet_off();


    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_T_B);
    // Wire.write(5);
    // //Serial.println("after2 ....");

    // byte error = Wire.endTransmission();


     helper_cal_left();

    delay(100); // Wait for step completion
  
  // Step 1: Move to limit switches (homing)
  // Move B_T slowly until WHITE limit switch is pressed
  while (digitalRead(BUTTON_WHITE_SWITCH_MOTOR_WHITE) == HIGH) {
    Serial.println("white pin");
    Wire.beginTransmission(ATMEGA32_ADDRESS);
      //Serial.println("after ....");
    Wire.write(CMD_B_T);
    Wire.write(1);
    //Serial.println("after2 ....");

    byte error = Wire.endTransmission();
    //Serial.println("after3 ....");

    // if (error == 0) {
    //   Serial.println("✅ I2C OK");
    // } else {
    //   Serial.print("❌ I2C Error: ");
    //   Serial.println(error);
    // }
    delay(100); // Wait for step completion

    digitalWrite(ledPin, HIGH);
  }
  
  // Move L_R slowly until BLACK limit switch is pressed
  while (digitalRead(BUTTON_BLACK_SWITCH_MOTOR_BLACK) == HIGH) {
    Wire.beginTransmission(ATMEGA32_ADDRESS);

     Serial.println("in black pin");

    Wire.write(CMD_L_R);
    Wire.write(1);

    Wire.endTransmission();
    delay(100); // Wait for step completion

    digitalWrite(ledPin, LOW);
  }
  
  delay(500); // Mechanical settling




  digitalWrite(ledPin, HIGH); // Turn LED on
  delay(500);
  

  
  Serial.println("Calibration complete!");
}

void zero_zero_pos(){
    Electromagnet_off();
     Wire.beginTransmission(ATMEGA32_ADDRESS);

     Serial.println("0 , 0");

    Wire.write(CMD_T_B);
    Wire.write(2);

    Wire.endTransmission();
    delay(500);
}


void helper_cal_left(){
    Wire.beginTransmission(ATMEGA32_ADDRESS);
      //Serial.println("after ....");
    Wire.write(CMD_R_L);
    Wire.write(4);
    //Serial.println("after2 ....");

    Wire.endTransmission();
}

void helper_cal_top(){
    Wire.beginTransmission(ATMEGA32_ADDRESS);
      //Serial.println("after ....");
    Wire.write(CMD_T_B);
    Wire.write(1);
    //Serial.println("after2 ....");

    Wire.endTransmission();
}


void Electromagnet_on(){
    digitalWrite(MOSFET_GATE, HIGH);  // ON
    Serial.println("magnet on");
}

void Electromagnet_off() {
    digitalWrite(MOSFET_GATE, LOW);  // ON
    Serial.println("magnet off");
}


void make_move(int x1, int y1, int x2, int y2) {


    // //line y+2;
    //  Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_R_L);
    // Wire.write(2);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();

    // delay(1000);



    //x1 axis move

    Electromagnet_off();

    int pos_x1 = 4*x1;

    Serial.print("going x1: ");
    Serial.println(x1);

    Wire.beginTransmission(ATMEGA32_ADDRESS);
      //Serial.println("after ....");
    Wire.write(CMD_R_L);
    Wire.write(pos_x1);
    //Serial.println("after2 ....");

    Wire.endTransmission();

    Electromagnet_off();
    
    delay(x1*4000+100);



    // // y + 2-2
    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_L_R);
    // Wire.write(2);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();

    // delay(1000);

    // y1 axis move
    int pos_y2 = 4*y1;

    
    Serial.print("going y1: ");
    Serial.println(y1);

    Wire.beginTransmission(ATMEGA32_ADDRESS);
      //Serial.println("after ....");
    Wire.write(CMD_T_B);
    Wire.write(pos_y2);
    //Serial.println("after2 ....");

    Wire.endTransmission();

    // electro magnet on



    delay(y1*4000+100);

    Electromagnet_on();

    delay(3000);
      Serial.println("going in line: +2");

      //line x+2;
      Wire.beginTransmission(ATMEGA32_ADDRESS);
        //Serial.println("after ....");
      Wire.write(CMD_T_B);
      Wire.write(2);
      //Serial.println("after2 ....");

      Wire.endTransmission();

    delay(5000);

    Electromagnet_on();
    int direction_x;

    int distance_x;

    if(x2-x1 >= 0){
      direction_x = CMD_R_L;
      distance_x = (x2-x1) * 4;
      if(distance_x != 0)
      {
        distance_x = distance_x -2;
      }

    }else{
      direction_x = CMD_L_R;
      distance_x = (x1-x2)*4;

      if(distance_x != 0)
      {
        distance_x = distance_x - 2;
      }

    }

    Electromagnet_on();
    //x2 pos
    Serial.println("going up from ai");
    if(distance_x != 0){
       Wire.beginTransmission(ATMEGA32_ADDRESS);
        //Serial.println("after ....");
      Wire.write(direction_x);
      Wire.write(distance_x);
      //Serial.println("after2 ....");

      Wire.endTransmission();

      delay(distance_x*1500+100);
    }else{
       Wire.beginTransmission(ATMEGA32_ADDRESS);
        //Serial.println("after ....");
      Wire.write(CMD_R_L);
      Wire.write(2);
      //Serial.println("after2 ....");

      Wire.endTransmission();
      delay(5000);
    }


    Electromagnet_on();

    //y2 pos

    int direction_y;
    int distance_y;

    if((y2-y1)>= 0) {
      direction_y = CMD_T_B;
      distance_y = (y2-y1)*4;
      if(distance_y != 0){
        distance_y = distance_y-2 ;
      }


    }else{
      direction_y = CMD_B_T; 
      distance_y = (y1-y2) *4;

      Serial.println("y1>y2");

      if(distance_y != 0)
      {
        distance_y = distance_y-2;
      }

    }
    Electromagnet_on();
        //y2 pos - 2

      Serial.print("going left from ai ");
      Serial.println(y2);
      if( distance_y != 0)
      {
         Wire.beginTransmission(ATMEGA32_ADDRESS);
        Serial.println("after ....");
        Wire.write(direction_y);
        Wire.write(distance_y);
        //Serial.println("after2 ....");

        Wire.endTransmission();
        delay(distance_y*2500+100);
      }else{

        Serial.println("y same b to T");
         Wire.beginTransmission(ATMEGA32_ADDRESS);
          //Serial.println("after ....");
        Wire.write(CMD_B_T);
        Wire.write(2);
        //Serial.println("after2 ....");

        Wire.endTransmission();
        delay(distance_y*1500+1000);
      }

  






    Serial.print("going y2: ");
    Serial.println();

    //y2 pos-2+2
      Wire.beginTransmission(ATMEGA32_ADDRESS);
        //Serial.println("after ....");
      Wire.write(CMD_R_L);
      Wire.write(2);
      //Serial.println("after2 ....");

      Wire.endTransmission();

    delay(5000);

    Serial.print("move completed:  ");

  Electromagnet_off();



    Serial.println("MOTOR_DONE");
    Serial.flush();
}


void detect_human_movement() {

    int reading = digitalRead(BUTTON_PIN);

    if (reading != lastButtonState) {



        currentButtonState = reading;

        if(currentButtonState == LOW) {

            Serial.println("TRIGGER_PYTHON");
            Serial.flush();

            sequence=player_black;
            currentButtonState = HIGH;
        }
     }
}

void handleSerialData() {

  if(Serial.available() > 0) {
    String receivedData = Serial.readStringUntil('\n');
    receivedData.trim();
    
    if (receivedData.startsWith("MOVE:")) {
      String coordinates = receivedData.substring(5);
      

        
        Serial.println("\n🎉 NEW COORDINATE RECEIVED!");
        Serial.print("📝 Move: ");
        Serial.println(coordinates);

        
        // Send confirmation back to Python
        Serial.print("ARDUINO_ACK:Move_stored_");
        Serial.println(moveCount);




        int x1 = coordinates[0] - '0';  // 'h' -> 7
        int y1 = coordinates[1] - '0';  // '1' -> 0
        int x2 = coordinates[2] - '0';  // 'a' -> 0
        int y2 = coordinates[3] - '0';  // '7' -> 6
        


        calibrate();

        zero_zero_pos();

        delay(1000);

        make_move(x1,y1,x2,y2);



        sequence = player_white;

    }
  }

}

void loop() {
     //Electromagnet_on();
    // // Serial.print("on");
    // delay(100);
    //  helper_cal_top();
    // Electromagnet_off();
    // Serial.print("off");
    // delay(3000);

    // Wire.beginTransmission(ATMEGA32_ADDRESS);
    //   //Serial.println("after ....");
    // Wire.write(CMD_T_B);
    // Wire.write(1);
    // //Serial.println("after2 ....");

    // Wire.endTransmission();


    switch (sequence) {
      case start:
        sequence = player_white;
        break;
      case player_white:
         detect_human_movement();

        break;

      case player_black:
        handleSerialData();

        break;
    }


  }