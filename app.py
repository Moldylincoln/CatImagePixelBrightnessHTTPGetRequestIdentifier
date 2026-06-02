import os
from io import BytesIO
from flask import Flask, request, render_template_string
# Added ImageEnhance to boost image visibility and contrast automatically
from PIL import Image, ImageEnhance 
import requests

app = Flask(__name__)

# IMPROVED PALETTE: Fewer gradients make the shapes pop instantly instead of looking muddy
ASCII_CHARS = "@M80GCit:,. "

def scale_image(image, new_width=40): # Increased resolution from 120 to 160 for more details
    original_width, original_height = image.size
    aspect_ratio = original_height / float(original_width)
    # Changed 0.55 to 0.45 to squash characters and prevent vertical image stretching
    new_height = int(aspect_ratio * new_width * 0.45) 
    return image.resize((new_width, new_height))

def optimize_contrast(image):
    # 1. Convert to grayscale
    grayscale_img = image.convert("L")
    # 2. Boost the contrast by 200% so dark details get darker and light details get lighter
    enhancer = ImageEnhance.Contrast(grayscale_img)
    return enhancer.enhance(2.0) 

@app.route("/")
def generate_ascii():
    default_url = "https://picsum.photos/200/300"
    url = request.args.get("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJ_iJ0hDHRx0YhaUqvcqC1cExS4SRCCgcP5g&s", default_url)

    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=browser_headers, timeout=10)
        if response.status_code != 200:
            return f"Website blocked us or image missing. Status code: {response.status_code}", 400

        img = Image.open(BytesIO(response.content))

        # Apply the new scaling and visibility enhancements
        img = scale_image(img, new_width=160)
        img = optimize_contrast(img)

        # Map pixels dynamically based on the length of our new clean palette
        pixels = img.getdata()
        palette_size = len(ASCII_CHARS)
        ascii_str = "".join([ASCII_CHARS[(pixel * palette_size) // 256] for pixel in pixels])

        # Slice string into rows
        img_width = img.width
        ascii_img = [
            ascii_str[index : index + img_width]
            for index in range(0, len(ascii_str), img_width)
        ]
        result = "\n".join(ascii_img)

        # CSS OPTIMIZATIONS:
        # 1. Increased font-weight to bold to fill out text spaces.
        # 2. Set line-height to 0.85 to squeeze lines together, removing background gap lines.
        # 3. Adjusted letter-spacing to prevent letters from drifting apart horizontally.
        html_template = """
        <html>
        <head>
            <title>High Contrast ASCII Art</title>
            <style>
                body { 
                    background-color: #050505; 
                    color: #00ff66; 
                    font-family: 'Courier New', Courier, monospace; 
                    padding: 20px; 
                    display: flex;
                    justify-content: center;
                }
                pre { 
                    font-size: 7px; 
                    line-height: 0.85; 
                    letter-spacing: -1px; 
                    font-weight: bold;
                    white-space: pre; 
                }
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
