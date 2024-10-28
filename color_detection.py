import numpy as np
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import cv2

# Function to calculate the minimum distance from all colors and get the closest color name
def get_closest_color_name(R, G, B, color_data):
    min_distance = float("inf")
    closest_color = ""

    for i in range(len(color_data)):
        r_val, g_val, b_val = int(color_data.loc[i, "R"]), int(color_data.loc[i, "G"]), int(color_data.loc[i, "B"])
        distance = abs(R - r_val) + abs(G - g_val) + abs(B - b_val)

        if distance < min_distance:
            min_distance = distance
            closest_color = color_data.loc[i, "color_name"]
    
    return closest_color

# Function to detect the color name and RGB values based on image coordinates
def detect_color(image, color_data, x, y):
    img_array = np.array(image)

    if 0 <= y < img_array.shape[0] and 0 <= x < img_array.shape[1]:
        pixel_values = img_array[y, x]
        r, g, b = (pixel_values[:3] if len(pixel_values) == 4 else pixel_values)
        color_name = get_closest_color_name(r, g, b, color_data)
        return color_name, r, g, b
    return None, None, None, None

# Load the color data from CSV
csv_headers = ["color", "color_name", "hex", "R", "G", "B"]
color_data = pd.read_csv("colors.csv", names=csv_headers, header=None)

# Streamlit interface setup
st.title("ShadeSleuth")

# Image uploader
uploaded_file = st.file_uploader("Choose an image to continue with color detection...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Convert image to OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # K-means clustering for color detection
    def get_dominant_colors(image, k=5):
        pixels = np.float32(image.reshape(-1, 3))
        _, labels, palette = cv2.kmeans(pixels, k, None, 
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), 
                                        10, cv2.KMEANS_RANDOM_CENTERS)
        _, counts = np.unique(labels, return_counts=True)
        dominant_colors = palette[np.argsort(counts)[-5:]]
        return dominant_colors

    # Display dominant colors in a row (left to right)
    st.write("Top Colors in Image:")
    dominant_colors = get_dominant_colors(opencv_image, k=5)
    color_blocks = "".join(
        f"<div style='display:inline-block; background-color: rgb({int(color[2])},{int(color[1])},{int(color[0])}); width:100px; height:100px; margin-right:5px;'></div>"
        for color in dominant_colors
    )
    st.markdown(color_blocks, unsafe_allow_html=True)

    # Pan controls
    x_offset = y_offset = 0
    if image.width > 800:
        max_x_offset = image.width - 800
        x_offset = st.slider("Pan Horizontally:", 0, max_x_offset, 0)
    if image.height > 600:
        max_y_offset = image.height - 600
        y_offset = st.slider("Pan Vertically:", 0, max_y_offset, 0)

    # Cropped image based on pan
    cropped_image = image.crop((x_offset, y_offset, x_offset + 800, y_offset + 600))
    st.write("Click anywhere in the image to display its color.")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_color="rgba(255, 0, 0, 1)",
        stroke_width=5,
        background_image=cropped_image,
        update_streamlit=True,
        height=600,
        width=800,
        drawing_mode="point",
        point_display_radius=5,
        key="canvas",
    )

    # Detect color on clicked points
    last_color_info = None
    if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
        for obj in canvas_result.json_data["objects"]:
            x, y = int(obj["left"]) + x_offset, int(obj["top"]) + y_offset
            if 0 <= x < image.width and 0 <= y < image.height:
                color_name, r, g, b = detect_color(image, color_data, x, y)
                if color_name is not None:
                    last_color_info = (color_name, r, g, b)

    # Display the detected color info if available
    if last_color_info:
        color_name, r, g, b = last_color_info
        st.write(f"Detected Color: {color_name}")
        st.write(f"RGB Values: R={r}, G={g}, B={b}")
        st.markdown(f"<div style='background-color: rgb({r},{g},{b}); width:100px; height:100px;'></div>", unsafe_allow_html=True)
