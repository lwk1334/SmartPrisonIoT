#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);

#define LED 2
#define Buzzer 3
#define Sensor A0
#define PumpPin 7

int threshold = 600;
bool alertTriggered = false;

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  pinMode(LED, OUTPUT);
  pinMode(Buzzer, OUTPUT);
  pinMode(PumpPin, OUTPUT);
}

void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("threshold:")) {
      threshold = command.substring(10).toInt();
      Serial.println(threshold); // Echo the threshold value back to the Python script
    } else if (command == "stop") {
      digitalWrite(PumpPin, LOW); // Turn off the water pump
    }
  }

  int value = analogRead(Sensor);
  lcd.setCursor(0, 0);
  lcd.print("Value: ");
  lcd.print(value);
  lcd.print("   ");
  Serial.println(value);

  if (value > threshold && !alertTriggered) {
    alertTriggered = true;
    digitalWrite(LED, HIGH);
    tone(Buzzer, 1000);
    lcd.setCursor(0, 1);
    lcd.print("GAS Detected!");
    digitalWrite(PumpPin, HIGH);
    Serial.println(value);
    //delay(500); // Delay for the alert
    //noTone(Buzzer);
    //delay(500); // Delay for the alert
  } else if (value <= threshold && alertTriggered) {
    alertTriggered = false;
    digitalWrite(LED, LOW);
    noTone(Buzzer);
    lcd.setCursor(0, 1);
    lcd.print("              ");
    digitalWrite(PumpPin, LOW);
    Serial.println(value);
  }
  delay(2000);
}
