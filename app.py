import os
from io import BytesIO
from flask import Flask, request, render_template_string
from PIL import Image
import requests

app = Flask(__name__)

# ASCII palette ordered from darkest (dense) to lightest (empty)
ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def scale_image(image, new_width=100):
    original_width, original_height = image.size
    aspect_ratio = original_height / float(original_width)
    # 0.55 adjusts for monospace fonts being taller than they are wide
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height))


def convert_to_grayscale(image):
    return image.convert("L")


@app.route("/")
def generate_ascii():
    # Dynamic URL fallback to a sample image if none is provided in the query string
    url = request.args.get(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ_iJ0hDHRx0YhaUqvcqC1cExS4SRCCgcP5g&s", "https://picsum.photos"
    )  # Generates a random image

    try:
        # 1. Fetch image
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))

        # 2. Process image
        img = scale_image(img, new_width=120)
        img = convert_to_grayscale(img)

        # 3. Map pixels to characters
        pixels = img.getdata()
        ascii_str = "".join([ASCII_CHARS[pixel // 4] for pixel in pixels])

        # 4. Split into lines based on image width
        img_width = img.width
        ascii_img = [
            ascii_str[index : index + img_width]
            for index in range(0, len(ascii_str), img_width)
        ]
        result = "\n".join(ascii_img)

        # 5. Render inside HTML pre tags with a clean dark theme for presentation
        html_template = """
        <html>
        <head>
            <title>ASCII Art Generator</title>
            <style>
                body { background-color: #121212; color: #00ff00; font-family: monospace; padding: 20px; }
                pre { font-size: 8px; line-height: 1.1; letter-spacing: 1px; white-space: pre; }
            </style>
        </head>
        <body>
            <pre>{{ art }}</pre>
        </body>
        </html>
        """
        return render_template_string(html_template, art=result)

    except Exception as e:
        return f"Error processing image: {str(e)}", 400


if __name__ == "__code__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
