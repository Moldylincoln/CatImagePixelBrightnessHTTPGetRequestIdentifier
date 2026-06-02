import requests
from io import BytesIO
from PIL import Image

ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def scale_image(image, new_width=100):
    (original_width, original_height) = image.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height))

def convert_to_grayscale(image):
    return image.convert("L")

def map_pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // 4] for pixel in pixels])
    return characters

url = "https://example.com"
response = requests.get(url)
img = Image.open(BytesIO(response.content))

# img = scale_image(img)
img = convert_to_grayscale(img)
ascii_str = map_pixels_to_ascii(img)

img_width = img.width
ascii_str_len = len(ascii_str)
ascii_img = [ascii_str[index:index + img_width] for index in range(0, ascii_str_len, img_width)]

print("\n".join(ascii_img))
