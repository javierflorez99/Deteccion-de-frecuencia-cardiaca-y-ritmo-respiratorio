#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

/* Puede ser ejecutado con un servidor emulador on host
        cd esp8266-core-root-dir
        cd tests/host
        make ../../libraries/ESP8266WebServer/examples/PostServer/PostServer
        bin/PostServer/PostServer
    Después poner la dirección IP del PC en SERVER_IP debajo, port 9080 (en lugar de default 80):
*/

/* !!! Cambiar los valores por los propios (local server address, essid and bssid(password) por) */
#define SERVER_IP "http://192.168.2.100:5000/" // por ejemplo

#ifndef STASSID
#define STASSID "name_of_your_wifi_or_ap"
#define STAPSK  "password"
#endif
/* también, puede intentar cambiar el retardo entre las peticiones POST 
(en caso de que el trabajo sea inexacto, establezca un valor mayor) */

unsigned long lastTime = 0;
unsigned long timerDelay = 8000;

#define USE_ARDUINO_INTERRUPTS false // no funciona con interrupciones, nodemcu vuela al infinito -2 segfault
#include <PulseSensorPlayground.h>

const int PULSE_INPUT = A0;
const int PULSE_BLINK = 2;    // Pin 13 es el on-board LED
const int PULSE_FADE = 5;
const int THRESHOLD = 550;   //  Ajustar el número para evitar ruido con el IDLE
PulseSensorPlayground pulseSensor;
const int OUTPUT_TYPE = SERIAL_PLOTTER; // Con el propósito de debuggear

byte samplesUntilReport;
const byte SAMPLES_PER_SERIAL_SAMPLE = 10;

void setup() {

  Serial.begin(115200);

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  pulseSensor.analogInput(PULSE_INPUT);
  pulseSensor.blinkOnPulse(PULSE_BLINK);
  pulseSensor.fadeOnPulse(PULSE_FADE);

  pulseSensor.setSerial(Serial);
  pulseSensor.setOutputType(OUTPUT_TYPE);
  pulseSensor.setThreshold(THRESHOLD);

  // Ignorar los primeros SAMPLES_PER_SERIAL_SAMPLE en el loop().
  samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE;

  if (!pulseSensor.begin()) {
    for(;;) {
      // Luz led para mostrar lo que no está funcionando
      digitalWrite(PULSE_BLINK, LOW);
      delay(50);
      digitalWrite(PULSE_BLINK, HIGH);
      delay(50);
    }
  }
}

void loop() {
  int myBPM = pulseSensor.getBeatsPerMinute();
  Serial.println(myBPM);
  Serial.println(millis() - lastTime);
  
  if (pulseSensor.sawNewSample()) {
    if (--samplesUntilReport == (byte) 0) {
      samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE;

      pulseSensor.outputSample();
      if (pulseSensor.sawStartOfBeat()) {
        pulseSensor.outputBeat();
      }
    }

    if ((WiFi.status() == WL_CONNECTED) && ((millis() - lastTime) > timerDelay)) {

      WiFiClient client;
      HTTPClient http;

      Serial.print("[HTTP] begin...\n");
      // Configurar el servidor traged y la url
      http.begin(client, SERVER_IP); //HTTP
      http.addHeader("Content-Type", "application/json");

      Serial.print("[HTTP] POST...\n");
      // Iniciar connection y enviar el header y body HTTP
      String s1 = String("{\"pulse\":") + String(myBPM) + String("}");
      int httpCode = http.POST(s1);

      // httpCode va a ser negativo en errores
      if (httpCode > 0) {
        // HTTP header ha sido enviador y la respuesta del Server header ya fue lidiada
        Serial.printf("[HTTP] POST... code: %d\n", httpCode);

        // archivo encontrado en el servidor
        if (httpCode == HTTP_CODE_OK) {
          const String& payload = http.getString();
          Serial.println("received payload:\n<<");
          Serial.println(payload);
          Serial.println(">>");
        }
      } 
      else {
        Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
      lastTime = millis();
    }
  }
}
