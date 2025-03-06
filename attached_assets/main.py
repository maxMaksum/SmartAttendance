from flask import Flask, request, jsonify
import cv2
import os
import csv
import numpy as np
from PIL import Image
import datetime
import hashlib

app = Flask(__name__)

# ============================== CONSTANTS ==============================
HAARCASCADE_PATH = "haarcascade_frontalface_default.xml"
DATA_DIR = "attendance_data"
STUDENT_DB = os.path.join(DATA_DIR, "students.csv")
ATTENDANCE_DIR = os.path.join(DATA_DIR, "attendance_records")
TRAINING_DATA_DIR = os.path.join(DATA_DIR, "training_images")
MODEL_FILE = os.path.join(DATA_DIR, "attendance_model.yml")
PASSWORD_FILE = os.path.join(DATA_DIR, ".admin_password")
DESIRED_SAMPLE_COUNT = 30

# ============================== HELPER FUNCTIONS ==============================
def initialize_system():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    os.makedirs(TRAINING_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(STUDENT_DB):
        with open(STUDENT_DB, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Registration Date"])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



def load_training_data():
    """
    Loads training images and corresponding IDs from the training images directory.
    Assumes images are stored in subdirectories named after the user_id.
    """
    faces = []
    ids = []
    # Iterate over each user folder in the training images directory
    for user_folder in os.listdir(TRAINING_DATA_DIR):
        folder_path = os.path.join(TRAINING_DATA_DIR, user_folder)
        if os.path.isdir(folder_path):
            try:
                user_id = int(user_folder)
            except ValueError:
                continue
            # For each image file in the user folder
            for file in os.listdir(folder_path):
                if file.endswith(".jpg"):
                    img_path = os.path.join(folder_path, file)
                    try:
                        img = Image.open(img_path).convert('L')  # Convert to grayscale
                        faces.append(np.array(img, 'uint8'))
                        ids.append(user_id)
                    except Exception as e:
                        print(f"Error processing file {img_path}: {e}")
    if not faces:
        raise ValueError("No training data found")
    return faces, ids
# ============================== API ENDPOINTS ==============================
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    
    if not user_id or not user_name:
        return jsonify({"error": "Missing user_id or user_name"}), 400
    
    with open(STUDENT_DB, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, user_name, datetime.datetime.now().strftime("%Y-%m-%d")])
    
    return jsonify({"message": "User registered successfully"})

@app.route("/register_photo", methods=["POST"])
def register_photo():
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    user_dir = os.path.join(TRAINING_DATA_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(HAARCASCADE_PATH)

    count = 0
    while count < DESIRED_SAMPLE_COUNT:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y + h, x:x + w]
            img_path = os.path.join(user_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face)
            count += 1
            if count >= DESIRED_SAMPLE_COUNT:
                break

        cv2.imshow("Capturing Faces", frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if count >= DESIRED_SAMPLE_COUNT:
        return jsonify({"message": "Face registered successfully"})
    else:
        return jsonify({"error": "Face registration failed"}), 500


@app.route("/train", methods=["POST"])
def train_model():
    try:
        faces, ids = load_training_data()
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))
        recognizer.save(MODEL_FILE)
        return jsonify({"message": "Model trained successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_file = os.path.join(ATTENDANCE_DIR, f"{datetime.date.today()}.csv")
    
    with open(today_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, timestamp])
    
    return jsonify({"message": "Attendance marked"})

# ============================== MAIN ==============================
if __name__ == "__main__":
    initialize_system()
    app.run(debug=True)
