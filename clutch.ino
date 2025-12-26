#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include <EEPROM.h>

#define ADC_PIN 26
#define OVERSAMPLES 16
#define FILTER_ALPHA 0.2f
#define SERIAL_INTERVAL 20

struct Calibration {
  uint32_t magic;
  uint32_t min;
  uint32_t max;
};

#define EEPROM_MAGIC 0xDEADBEEF
Calibration cal;

Adafruit_USBD_HID hid;
uint8_t hid_desc[] = {
  0x05,0x01,0x09,0x05,0xA1,0x01,0x85,0x01,
  0x09,0x30,0x16,0x00,0x80,0x26,0xFF,0x7F,
  0x75,0x10,0x95,0x01,0x81,0x02,0xC0
};

typedef struct { int16_t x; } report_t;
report_t rpt;

float adc_filtered = 0;
unsigned long last_serial_time = 0;

uint32_t readADC() {
  uint32_t sum = 0;
  for (int i = 0; i < OVERSAMPLES; i++) sum += analogRead(ADC_PIN);
  return sum;
}

void saveCalibration() {
  cal.magic = EEPROM_MAGIC;
  EEPROM.put(0, cal);
  EEPROM.commit();
  Serial.println("Calibration saved!");
}

void loadCalibration() {
  EEPROM.get(0, cal);
  if (cal.magic != EEPROM_MAGIC) {
    cal.min = 0;
    cal.max = 4095*OVERSAMPLES;
  }
}

void handleSerial() {
  if (!Serial.available()) return;
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  uint32_t raw = readADC();

  if (cmd == "min") { cal.min = raw; Serial.print("MIN:"); Serial.println(cal.min); }
  else if (cmd == "max") { cal.max = raw; Serial.print("MAX:"); Serial.println(cal.max); }
  else if (cmd == "save") saveCalibration();
  else if (cmd == "load") { loadCalibration(); Serial.println("Calibration loaded"); }
  else if (cmd == "show") {
    Serial.print("MIN:"); Serial.print(cal.min);
    Serial.print(" MAX:"); Serial.println(cal.max);
  }
  else if (cmd == "reset") { cal.min = 0; cal.max = 4095*OVERSAMPLES; Serial.println("Calibration reset"); }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  EEPROM.begin(sizeof(Calibration));
  loadCalibration();

  hid.setReportDescriptor(hid_desc, sizeof(hid_desc));
  hid.begin();
  delay(1000);
}

void loop() {
  handleSerial();

  uint32_t adc_raw = readADC();
  adc_filtered = FILTER_ALPHA*adc_raw + (1-FILTER_ALPHA)*adc_filtered;

  float norm = (float)(adc_filtered - cal.min) / (float)(cal.max - cal.min);
  if (norm < 0) norm = 0; if (norm > 1) norm = 1;
  int16_t mapped = (int16_t)((norm*2.0f - 1.0f) * 32767);

  rpt.x = mapped;
  hid.sendReport(1, &rpt, sizeof(rpt));

  if (millis() - last_serial_time >= SERIAL_INTERVAL) {
    Serial.print("ADC_CAL:"); Serial.println(mapped);
    last_serial_time = millis();
  }

  delay(1);
}
