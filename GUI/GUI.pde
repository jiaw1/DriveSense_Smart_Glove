import processing.net.*;

Server arduinoServer;
Client arduinoClient;

Client pythonClient;

PImage bg;
PImage emerg;
PImage call;
PImage play;
PImage repeat;
PImage[] songs = new PImage[3];

boolean showEmerg = false;
boolean inEmergencyMode = false;

boolean showPlay = false;
boolean showRepeat = false;

boolean showCall = false;
boolean forceShowCall = false;

int currentSongIndex = 0;

int callStartTime = 0;
int lastCallCycleStart = 0;
int callInterval = 10000;  // Show call every 10 seconds
int callDuration = 5000;   // For 5 seconds

String dataString = "";

void setup() {
  size(1200, 800);
  
  // Load and resize background
  bg = loadImage("bg.png");
  bg.resize(width, height);
  
  // Load and resize function images
  emerg = loadImage("emergency.png");
  emerg.resize(400, 115);
  call = loadImage("call.png");
  call.resize(320, 230);
  play = loadImage("play.png");
  play.resize(80, 80);
  repeat = loadImage("repeat.png");
  repeat.resize(55, 50);

  songs[0] = loadImage("song1.png");
  songs[1] = loadImage("song2.png");
  songs[2] = loadImage("song3.png");

  for (int i = 0; i < songs.length; i++) {
    songs[i].resize(280, 50);
  }
  
  // Set up server and client
  arduinoServer = new Server(this, 5000);  // From Arduino
  println("Waiting for Arduino on port 5000...");

  pythonClient = new Client(this, "127.0.0.1", 6000);  // To Python
  println("Connecting to Python on port 6000...");
}

void draw() {
  image(bg, 0, 0);

  int currentTime = millis();

  // Only run call timer logic if NOT in emergency
  if (!inEmergencyMode) {
    if (!forceShowCall && currentTime - lastCallCycleStart > callInterval) {
      showCall = true;
      callStartTime = currentTime;
      lastCallCycleStart = currentTime;
    }

    if (!forceShowCall && showCall && (currentTime - callStartTime > callDuration)) {
      showCall = false;
    }
  }

  // Reconnect to Python if lost
  if (pythonClient == null || !pythonClient.active()) {
    println("Trying to reconnect to Python...");
    pythonClient = new Client(this, "127.0.0.1", 6000);
    delay(1000);
    return;
  }

  // Read data from Arduino
  arduinoClient = arduinoServer.available();
  if (arduinoClient != null) {
    String received = arduinoClient.readStringUntil('\n');
    if (received != null) {
      received = trim(received);
      dataString = received;
      println("From Arduino: " + received);
      pythonClient.write(received + "\n");
    }
  }

  // Read prediction from Python
  if (pythonClient.available() > 0) {
    String response = pythonClient.readStringUntil('\n');
    if (response != null) {
      response = trim(response);
      println("Prediction from Python: " + response);

      if (response.equals("1")) {
        showPlay = !showPlay;
      }

      if (response.equals("7")) {
        showRepeat = !showRepeat;
      }

      if (response.equals("2")) {
        currentSongIndex = (currentSongIndex + 1) % songs.length;
      }

      if (response.equals("3")) {
        currentSongIndex = (currentSongIndex - 1 + songs.length) % songs.length;
      }

      if (response.equals("6")) {
        inEmergencyMode = true;
        showEmerg = true;
        showCall = false;
        forceShowCall = false;
      }

      if (response.equals("4")) {
        if (inEmergencyMode) {
          inEmergencyMode = false;
          showEmerg = false;
          lastCallCycleStart = millis();  // resume call cycle
        } else {
          showCall = false;
          forceShowCall = false;
        }
      }

      if (!inEmergencyMode && response.equals("5")) {
        forceShowCall = !forceShowCall;
        showCall = forceShowCall;
      }
    }
  }

  // Show emergency
  if (showEmerg) {
    image(emerg, 510, 115);
  }

  // Show play
  if (showPlay) {
    image(play, 270, 470);
  }

  // Show repeat
  if (showRepeat) {
    image(repeat, 360, 480);
  }

  // Show call
  if (showCall) {
    image(call, 500, 380);
  }

  // Show current song
  image(songs[currentSongIndex], 170, 550);
}
