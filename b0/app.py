import PIL.Image
from flask import Flask, render_template, redirect, request
import subprocess
import PIL
import numpy as np
import io
import face_recognition

app = Flask(__name__)

reference_pic = face_recognition.load_image_file("fabian.jpg")
ref_face_encoding = face_recognition.face_encodings(np.array(reference_pic))[0]

def liveliness_check(ref: np.array, test_pic: PIL.Image):
    # Rescale for comparision if needed
    test_pic_resized = test_pic.resize(ref.shape[:2])

    # Calc Mean Square Error as measurement to check if the webcam
    # image is *too* similar to our reference image
    mse = ((ref - np.array(test_pic_resized))**2).mean()
    print(f"Got an image with MSE of {mse}")

    # Let's take a good old educated guess as rejection threshold
    THRESHOLD = 100
    return not mse < THRESHOLD

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    # Get Image data
    try:
        test_img = PIL.Image.open(io.BytesIO(request.data))
    except PIL.UnidentifiedImageError:
        return {"error": "Login failed - The uploaded image doesn't look like an image!"}
    
    test_img = test_img.convert("RGB")

    test_face_encodings = face_recognition.face_encodings(np.array(test_img))
    if len(test_face_encodings) < 1:
        return {"error": "Login failed - Our AI wasn't able to recognize your face on the image!"}
    elif len(test_face_encodings) > 1:
        return {"error": "Login failed - There are multiple persons on the picture?!"}

    if not liveliness_check(reference_pic, test_img):
        return {"error": "Login failed - This wasn't made with your webcam! Try to hack another website!"}
    
    results = face_recognition.compare_faces([ref_face_encoding], test_face_encodings[0])
    if results[0] == True:
        return {"flag": subprocess.check_output("/bin/flag").decode().strip()}
    else:
        return {"error": "Login failed - You do not like an authorized person!"}