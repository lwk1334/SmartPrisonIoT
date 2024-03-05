#include <Servo.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN 10
#define RST_PIN 9
#define redpin 7
#define greenpin 6


char command;
Servo servo;
LiquidCrystal_I2C lcd(0x27, 16, 2);
MFRC522 rfid(SS_PIN, RST_PIN);


void setup() {
  pinMode(redpin, OUTPUT);
  pinMode(greenpin, OUTPUT);
  digitalWrite(redpin, LOW);
  digitalWrite(greenpin, LOW);
  Serial.begin(9600);
  servo.attach(3);
  servo.write(70);
  lcd.init();
  lcd.clear();
  lcd.backlight();
  SPI.begin();
  rfid.PCD_Init();
  
}

void loop() {
  lcd.clear();
  lcd.setCursor(4, 0);
  lcd.print("Welcome!");
  lcd.setCursor(1, 1);
  lcd.print("Scan Your Card");

  if ( ! rfid.PICC_IsNewCardPresent())
    return;
     delay(100);

  if ( ! rfid.PICC_ReadCardSerial())
    return;
     delay(100);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Scanning");
  Serial.println("");

    // Clear the serial buffer
  while (Serial.available()) {
    Serial.read();
  }

  String ID = "";
  
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
    ID.concat(String(rfid.uid.uidByte[i] < 0x10 ? " 0" : " "));
    ID.concat(String(rfid.uid.uidByte[i], HEX));
    delay(300);
  }

  ID.toUpperCase();

 if (Serial.available() > 0) {
    command = Serial.read(); // Read the incoming command

      if (command == 'o') {
      servo.write(160); // Open the door
    
      lcd.clear();
    
      digitalWrite(greenpin, HIGH);
      lcd.setCursor(1, 1);
      lcd.print("Accesss Granted");
      delay(3000);
      digitalWrite(greenpin, LOW);
      servo.write(70);
    }
    
    if (command == 'c') {
    servo.write(70);
    lcd.clear();
    
    digitalWrite(redpin, HIGH);
    lcd.setCursor(0, 0);
    lcd.print("Accesss Denied");
    delay(3000);
    digitalWrite(redpin, LOW);
    }

    command = ' ';
 }

}
   
