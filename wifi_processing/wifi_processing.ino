#include <WiFiNINA.h>
#include "credentials.h"

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;
char server[] = SECRET_IP;

WiFiClient client;
int port = 5000;

// Initialize sensor pins
int sensorpin0 = A0;
int sensorpin1 = A1;
int sensorpin2 = A2;
int sensorpin3 = A3;
int sensorpin4 = A4;
int sensorpin5 = A5;
int sensorpin6 = A6;

void setup() {
  Serial.begin(9600);
  delay(1000);  // Ensure Serial starts properly

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);  // Start with LED off
  
  Serial.println("Connecting to Wi-Fi...");
  connectToWiFi();  // Call function to connect to Wi-Fi
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi Disconnected. Reconnecting...");
    digitalWrite(LED_BUILTIN, LOW);
    connectToWiFi();
  }

  sendDataToProcessing();   // Function to send sensor data
  delay(100);  // 10Hz sampling rate
}

void connectToWiFi() {
  WiFi.begin(ssid, pass);
  unsigned long startAttemptTime = millis();
  const unsigned long timeout = 10000;  // 10 seconds timeout

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (millis() - startAttemptTime >= timeout) {
      Serial.println("\nWi-Fi connection failed!");
      return;
    }
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(LED_BUILTIN, HIGH);  // Indicate connection success
}

void sendDataToProcessing() {
  if (!client.connected()) {
    if (client.connect(server, port)) {
      Serial.println("Connected to Processing!");
    } else {
      Serial.println("Connection to Processing failed.");
      return;
    }
  }

  // Read sensor values
  float sensorvalue0 = analogRead(sensorpin0);
  float sensorvalue1 = analogRead(sensorpin1);
  float sensorvalue2 = analogRead(sensorpin2);
  float sensorvalue3 = analogRead(sensorpin3);
  float sensorvalue4 = analogRead(sensorpin4);
  float sensorvalue5 = analogRead(sensorpin5);
  float sensorvalue6 = analogRead(sensorpin6);
    
  // Inverted voltage calculation
  float voltage0 = 3.3 - ((sensorvalue0 / 1023.0) * 3.3);
  float voltage1 = 3.3 - ((sensorvalue1 / 1023.0) * 3.3);
  float voltage2 = 3.3 - ((sensorvalue2 / 1023.0) * 3.3);
  float voltage3 = 3.3 - ((sensorvalue3 / 1023.0) * 3.3);
  float voltage4 = 3.3 - ((sensorvalue4 / 1023.0) * 3.3);
  float voltage5 = 3.3 - ((sensorvalue5 / 1023.0) * 3.3);
  float voltage6 = 3.3 - ((sensorvalue6 / 1023.0) * 3.3); 
  
  // Get current timestamp
  String timestamp = getFormattedTime();
  
  // Create CSV data
  String csvData = timestamp + "," + String(sensorvalue0) + "," + String(sensorvalue1) + "," +
           String(sensorvalue2) + "," + String(sensorvalue3) + "," +
           String(sensorvalue4) + "," + String(sensorvalue5) + "," +
           String(sensorvalue6) + "," + String(voltage0) + "," + 
           String(voltage1) + "," + String(voltage2) + "," + 
           String(voltage3) + "," + String(voltage4) + "," + 
           String(voltage5) + "," + String(voltage6) + "," + "NA";
  
  // Send data to Processing
  client.println(csvData);  
}

// Function to format the timestamp
String getFormattedTime() {
  unsigned long currentMillis = millis();
  
  // Convert millis to hours, minutes, seconds, and milliseconds
  int ms = currentMillis % 1000;            // Get milliseconds part
  int sec = (currentMillis / 1000) % 60;    // Get seconds part
  int min = (currentMillis / 60000) % 60;   // Get minutes part
  int hr = (currentMillis / 3600000) % 24;  // Get hours part

  // Format with leading zeros
  String timestamp = String(hr) + ":" + String(min) + ":" + String(sec) + ":" + String(ms);
  return timestamp;
}
