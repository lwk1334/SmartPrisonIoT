const int sampleWindow = 50;                              // Sample window width in mS (50 mS = 20Hz)
unsigned int sample;
 
#define SENSOR_PIN A0
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
 
LiquidCrystal_I2C lcd(0x27, 16, 2);
const int LED_GREEN = 12;
const int LED_RED =13;

int threshold = 50 ;

void setup ()  
{   
  pinMode (SENSOR_PIN, INPUT); // Set the signal pin as input  
  Serial.begin(9600);
  pinMode(LED_RED,OUTPUT);
  pinMode(LED_GREEN,OUTPUT);
  lcd.init();
  lcd.backlight();
}  
 
   
void loop ()  
{ 
  if (Serial.available() > 0) {
    threshold = Serial.parseInt();  // Read the threshold value from serial input
    Serial.println(threshold); // Echo the threshold value back to the Python script
  }
   unsigned long startMillis= millis();                   // Start of sample window
   float peakToPeak = 0;                                  // peak-to-peak level
 
   unsigned int signalMax = 0;                            //minimum value
   unsigned int signalMin = 1024;                         //maximum value
 
                                                          // collect data for 50 mS
   while (millis() - startMillis < sampleWindow)
   {
      sample = analogRead(SENSOR_PIN);                    //get reading from microphone
      if (sample < 1024)                                  // toss out spurious readings
      {
         if (sample > signalMax)
         {
            
            signalMax = sample;                           // save just the max levels
            
         }
         else if (sample < signalMin)
         {
            signalMin = sample; 
            // digitalWrite(LED_GREEN,HIGH);
           
                                     // save just the min levels
         }
      }
   }
 
   peakToPeak = signalMax - signalMin;                    // max - min = peak-peak amplitude
   int sound = map(peakToPeak,20,900,49.5,90);             //calibrate for deciBels
 
  lcd.setCursor(1, 0);
  lcd.print("Loudness: ");
  lcd.print(sound);
  lcd.setCursor(1,1);
  lcd.print("Sound DB: Good ");
  Serial.println(sound);

if(sound > threshold) 
{
digitalWrite(LED_GREEN,LOW);
digitalWrite(LED_RED,HIGH);
//delay(3000);
lcd.setCursor(1,0);
lcd.print("Loudness: ");
lcd.print(sound);
lcd.setCursor(1,1);
lcd.print("Sound DB: Bad ");

}
else if (sound <= threshold)
{
digitalWrite(LED_GREEN,HIGH);
digitalWrite(LED_RED,LOW);

}
   delay(2000); 
}