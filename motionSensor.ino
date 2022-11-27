#include <ArduinoBLE.h>


// ultrasonic
#define ULTRASONIC_TRIG_PIN 2
#define ULTRASONIC_ECHO_PIN 3

#define BLE_UUID_ENVIRONMENTAL_SERVICE "181A"
#define BLE_UUID_DISTANCE "2A57"

#define BLE_DEVICE_NAME "Motion sensor"
#define BLE_LOCAL_NAME "Motion sensor"

BLEService environmentalService(BLE_UUID_ENVIRONMENTAL_SERVICE);
BLEFloatCharacteristic distanceCharacteristic(BLE_UUID_DISTANCE, BLERead | BLENotify);

long duration;
float distance;

void setup() {    
  Serial.begin(9600);
  if (!BLE.begin()) {
    Serial.println("Starting BluetoothÂ® Low Energy module failed!");
  }

  // ultrasonic sensor
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);

  BLE.setLocalName(BLE_LOCAL_NAME);
  BLE.setDeviceName(BLE_DEVICE_NAME);
  BLE.setAdvertisedService(environmentalService);
  
  environmentalService.addCharacteristic(distanceCharacteristic);

  BLE.addService(environmentalService);
  BLE.advertise();
  Serial.println("BLE Envinronmental Peripheral");

  delay(1500);
}

void loop() {
  BLEDevice central = BLE.central(); 
  if (central)
  {
    while (central.connected())
    {
      get_distance();
      distanceCharacteristic.writeValue(distance);
      
      // delay(500);
    }
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
} 

void get_distance(){
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;
  delay(100);
}