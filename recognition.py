import os
import cv2
import numpy as np
from PIL import Image

class FaceRecognition:
    def __init__(self):
        print("Initializing FaceRecognition...")
        self.cascade_path = os.path.join("attached_assets", "haarcascade_frontalface_default.xml")
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.face_cascade.empty():
            print("Error: Haar cascade file not loaded! Check the path:", self.cascade_path)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_data_dir = "training_data"
        self.model_file = os.path.join("attached_assets", "attendance_model.yml")
        os.makedirs(self.training_data_dir, exist_ok=True)
        print("Training directory ensured.")
        if os.path.exists(self.model_file):
            self.recognizer.read(self.model_file)
            print("Model loaded from file.")
        else:
            print("No existing model found.")

    def detect_face(self, frame):
        """Detect face in frame and return the face region."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Adjusted parameters: scaleFactor=1.1, minNeighbors=5 often help.
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        print(f"Detected {len(faces)} faces.")
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            print(f"Face found at x:{x}, y:{y}, w:{w}, h:{h}")
            return gray[y:y+h, x:x+w], faces[0]
        print("No faces detected.")
        return None, None

    def recognize_face(self, frame):
        """Recognize face in frame and return user_id and confidence."""
        face, rect = self.detect_face(frame)
        if face is not None:
            user_id, confidence = self.recognizer.predict(face)
            print(f"Recognized user {user_id} with confidence {confidence}.")
            return user_id, confidence, rect
        return None, None, None

    def train_model(self):
        # (Unchanged training code)
        faces = []
        ids = []
        print("Collecting training data...")
        for user_folder in os.listdir(self.training_data_dir):
            folder_path = os.path.join(self.training_data_dir, user_folder)
            if os.path.isdir(folder_path):
                try:
                    user_id = int(user_folder)
                    for img_file in os.listdir(folder_path):
                        if img_file.endswith('.jpg'):
                            img_path = os.path.join(folder_path, img_file)
                            face_img = Image.open(img_path).convert('L')
                            face_np = np.array(face_img, 'uint8')
                            faces.append(face_np)
                            ids.append(user_id)
                except ValueError:
                    continue
        if not faces:
            raise ValueError("No training data found")
        print("Training the model with collected data...")
        self.recognizer.train(faces, np.array(ids))
        self.recognizer.save(self.model_file)
        print("Model trained and saved.")
        return len(faces)
