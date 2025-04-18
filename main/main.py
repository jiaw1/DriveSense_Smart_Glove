import socket
import joblib
import numpy as np
from collections import deque

# Load your trained model
model = joblib.load("svm_model.pkl")
print("Loaded model: svm_model.pkl")

# Socket settings
HOST = '0.0.0.0'
PORT = 6000

# Sliding window parameters
WINDOW_SIZE = 25
FEATURES_PER_ROW = 14
BUFFER = deque(maxlen=WINDOW_SIZE)

# Start socket server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Waiting for Processing to connect on port {PORT}...")
client, addr = server.accept()
print(f"Connected from {addr}")

try:
    while True:
        data = client.recv(1024).decode().strip()
        if data:
            print("\nRaw data:", data)

            try:
                parts = data.split(',')

                if len(parts) == 16:  # ts + 14 features + label
                    features = [float(p) for p in parts[1:15]]
                    BUFFER.append(features)

                    # Only predict if buffer is full
                    if len(BUFFER) == WINDOW_SIZE:
                        flat_features = np.array(BUFFER).flatten().reshape(1, -1)
                        prediction = model.predict(flat_features)[0]
                        print(f"Prediction: {prediction}")

                        # Send prediction back to Processing
                        client.sendall(f"{prediction}\n".encode())

                    else:
                        print(f"Waiting to fill window... ({len(BUFFER)}/{WINDOW_SIZE})")
                else:
                    print(f"Invalid row: expected 16 columns (got {len(parts)})")

            except Exception as e:
                print(f"Error during parsing/prediction: {e}")

except KeyboardInterrupt:
    print("Server stopped.")
finally:
    client.close()
    server.close()
