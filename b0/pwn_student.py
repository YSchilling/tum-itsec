import requests
import io
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import numpy as np

def main():
    URL = "https://b0-ca3cf5aeca0e42d2.itsec.sec.in.tum.de/"
    IMG_URL = "./ref.jpg"

    img = Image.open(IMG_URL, "r")
    reference_image = Image.open(IMG_URL, "r")
    reference_array = np.array(reference_image)

    modified_img = img.convert("L").convert("RGB")
    modified_img = ImageChops.offset(modified_img, -64, 128)
    modified_img = ImageEnhance.Contrast(modified_img).enhance(1.5)

    with requests.Session() as sess:
        buffer = io.BytesIO()
        modified_img.save(buffer, format="JPEG")
        img_bytes = buffer.getvalue()
        response = sess.post(URL + "login", data=img_bytes)

        print(response.text)

if __name__ == "__main__":
    main()