#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

#include <DHT.h>
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

class DataProcessor {
public:
    DataProcessor(int bufferSize = 5) : size(bufferSize), index(0), count(0) {
        buffer = new float[size];
    }
    ~DataProcessor() {
        delete[] buffer;
    }
    void addReading(float value) {
        buffer[index] = value;
        index = (index + 1) % size;
        if (count < size) count++;
    }
    float getFilteredValue() const {
        if (count == 0) return 0.0f;
        float sum = 0;
        for (int i = 0; i < count; i++) sum += buffer[i];
        return sum / count;
    }
    bool isBufferFull() const {
        return count >= size;
    }
    void clear() {
        count = 0;
        index = 0;
    }
private:
    float* buffer;
    int size;
    int index;
    int count;
};

DataProcessor tempProcessor(5);
DataProcessor humProcessor(5);
DataProcessor co2Processor(5);
int sensorId = -1;

void connectWiFi() {
    Serial.print("Connecting to WiFi ");
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected!");
}

void registerSensor() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = String(API_BASE_URL) + "/sensors/";
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        JsonDocument doc;
        doc["serial_number"] = SENSOR_SERIAL;
        doc["location"] = "IoT Lab Desk";
        doc["type"] = "ESP32-STATION";
        doc["is_active"] = true;
        String json;
        serializeJson(doc, json);
        int httpResponseCode = http.POST(json);
        if (httpResponseCode > 0) {
            String response = http.getString();
            JsonDocument resDoc;
            deserializeJson(resDoc, response);
            sensorId = resDoc["id"];
            Serial.print("Registered Sensor ID: ");
            Serial.println(sensorId);
        }
        http.end();
    }
}

void fetchConfig() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(String(API_BASE_URL) + "/admin/settings/");
        int httpResponseCode = http.GET();
        if (httpResponseCode == 200) {
            JsonDocument doc;
            deserializeJson(doc, http.getString());
            for (JsonObject setting : doc.as<JsonArray>()) {
                if (setting["key"] == "REPORTING_INTERVAL") {
                    reportingInterval = setting["value"].as<unsigned long>();
                }
            }
        }
        http.end();
    }
}

void sendMeasurement(float temp, float hum, float co2) {
    if (WiFi.status() == WL_CONNECTED && sensorId != -1) {
        HTTPClient http;
        http.begin(String(API_BASE_URL) + "/sensors/" + String(sensorId) + "/measurements");
        http.addHeader("Content-Type", "application/json");
        JsonDocument doc;
        doc["temperature"] = temp;
        doc["humidity"] = hum;
        doc["co2_level"] = co2;
        String json;
        serializeJson(doc, json);
        http.POST(json);
        http.end();
    }
}

void setup() {
    Serial.begin(115200);
    dht.begin();
    connectWiFi();
    registerSensor();
    fetchConfig();
}

unsigned long lastReadTime = 0;
unsigned long samplingInterval = 2000;

void loop() {
    if (millis() - lastReadTime >= samplingInterval) {
        lastReadTime = millis();
        float h = dht.readHumidity();
        float t = dht.readTemperature();
        float c = random(400, 1200);
        if (!isnan(h) && !isnan(t)) {
            tempProcessor.addReading(t);
            humProcessor.addReading(h);
            co2Processor.addReading(c);
        }
        if (tempProcessor.isBufferFull()) {
            sendMeasurement(tempProcessor.getFilteredValue(), humProcessor.getFilteredValue(), co2Processor.getFilteredValue());
            tempProcessor.clear(); humProcessor.clear(); co2Processor.clear();
            fetchConfig();
        }
    }
}