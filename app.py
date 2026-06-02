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
    # 1. Fallback url if none is provided in the query string
    default_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ_iJ0hDHRx0YhaUqvcqC1cExS4SRCCgcP5g&s"
    url = request.args.get("url", default_url)

    # 2. Add a User-Agent header so Google knows we are trying to view the image
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # 3. Fetch image using the fake browser headers
        response = requests.get(url, headers=browser_headers, timeout=10)

        # Check if the website actually returned a valid successful request
        if response.status_code != 200:
            return (
                f"Website blocked us or image missing. Status code: {response.status_code}",
                400,
            )

        img = Image.open(BytesIO(response.content))

        # 4. Process image
        img = scale_image(img, new_width=120)
        img = convert_to_grayscale(img)

        # 5. Map pixels to characters
        pixels = img.getdata()
        ascii_str = "".join([ASCII_CHARS[pixel // 4] for pixel in pixels])

        # 6. Split into lines
        img_width = img.width
        ascii_img = [
            ascii_str[index : index + img_width]
            for index in range(0, len(ascii_str), img_width)
        ]
        result = "\n".join(ascii_img)

        # 7. Render inside HTML pre tags
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
