//pin definitions
#define BALLS1 8
#define BALLS2 9
#define BALLC1 10
#define BALLC2 11
#define SEL0 12
#define SEL1 13

//definitions of ballast states
#define IDLED (!digitalRead(BALLC1)&&!digitalRead(BALLC2))
#define ARMED (digitalRead(BALLC1)&&!digitalRead(BALLC2))
#define FIRED (!digitalRead(BALLC1)&&digitalRead(BALLC2))

void setup() {
  //set appropriate inputs and outputs
  pinMode(BALLS1, OUTPUT);
  pinMode(BALLS2, OUTPUT);
  pinMode(BALLC1, INPUT);
  pinMode(BALLC2, INPUT);
  pinMode(SEL0, INPUT_PULLUP);
  pinMode(SEL1, INPUT_PULLUP);
}

void loop() {
  digitalWrite(BALLS1, HIGH);    //default signal state, (ballast fails at addressing step) EC: 2
  digitalWrite(BALLS2, LOW);
  if(digitalRead(SEL0) && !digitalRead(SEL1)) //if selection pins are set to '01'
  {
    digitalWrite(BALLS1, LOW);               //fails at arming step EC: 4
  }
  else if(!digitalRead(SEL0) && digitalRead(SEL1)) //if selection pins are set to '10'
  {
    digitalWrite(BALLS1, LOW);                    //succeeds addressing/arming step
    while(!ARMED){}
    digitalWrite(BALLS2, HIGH);                     //fails at firing step EC: 8
  }
  else if(digitalRead(SEL0) && digitalRead(SEL1)) //if selection pins are set to '11'
  {
    digitalWrite(BALLS1, LOW);                   //succeeds all steps EC: 1
    while(!ARMED){}
    digitalWrite(BALLS2, HIGH);
    while(!FIRED){}
    digitalWrite(BALLS2, LOW);
  }
  while(!IDLED){} //wait for ballast to be idle before switching inputs
}
