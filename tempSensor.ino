#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>
#include <Adafruit_Si7021.h>
#include <ArduinoBLE.h>


#define BLE_UUID_ENVIRONMENTAL_SERVICE "181A"
#define BLE_UUID_TEMPERATURE "2A1F"   
#define BLE_UUID_HUMIDITY "2A6F"

#define BLE_DEVICE_NAME "Temerature sensor"
#define BLE_LOCAL_NAME "Temerature sensor"

BLEService environmentalService(BLE_UUID_ENVIRONMENTAL_SERVICE);
BLEFloatCharacteristic temperatureCharacteristic(BLE_UUID_TEMPERATURE, BLERead | BLENotify);
BLEFloatCharacteristic humidityCharacteristic(BLE_UUID_HUMIDITY, BLERead | BLENotify);

Adafruit_Si7021 sensor;     //1 
float temperature;
float humidity;

void setup() {    
    // put your setup code here, to run once:
  Serial.begin(9600);
  if (!sensor.begin()) //4
  {
    Serial.print("Sensor failed\n\n");
  }
  if (!BLE.begin()) {
    Serial.println("Starting BluetoothÂ® Low Energy module failed!");
  }
  
  BLE.setLocalName(BLE_LOCAL_NAME);
  BLE.setDeviceName(BLE_DEVICE_NAME);
  BLE.setAdvertisedService(environmentalService);
  
  environmentalService.addCharacteristic(temperatureCharacteristic);
  environmentalService.addCharacteristic(humidityCharacteristic);

  BLE.addService(environmentalService);
  BLE.advertise();
  Serial.println("BLE Envinronmental Peripheral");
}

void loop() {
  BLEDevice central = BLE.central(); 
  if (central)
  {
    while (central.connected())
    {
      temperature = sensor.readTemperature(); //2
      humidity = sensor.readHumidity(); //3
      
      temperatureCharacteristic.writeValue(temperature);
      humidityCharacteristic.writeValue(humidity);
    }
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
} 
