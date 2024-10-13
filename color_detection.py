import numpy as np
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# Function to calculate the minimum distance from all colors and get the most matching color
def getColorName(R, G, B, csv):
    minimum = 10000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# Function to get the RGB values from an image and detect the color name based on coordinates
def detect_color(image, csv, x, y):
    # Get RGB values from the clicked point
    img = np.array(image)
    
    # Ensure the coordinates are within the image dimensions
    if y < img.shape[0] and x < img.shape[1]:
        r, g, b = img[y, x]
        # Get the closest color name from the CSV
        color_name = getColorName(r, g, b, csv)  # Use RGB values
        return color_name, r, g, b
    return None, None, None, None  # Return None if out of bounds

# Load color data from CSV
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Streamlit interface
st.title("Color Detection App with Drawable Canvas")

# Uploading an image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_array = np.array(image)

    # Slider for adjusting image display size
    image_scale = st.slider("Adjust Image Display Size:", min_value=100, max_value=1000, value=800)

    # Display the image on a drawable canvas
    st.write("Draw on the canvas to select colors.")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill color
        stroke_color="rgba(255, 0, 0, 1)",  # Red stroke color for visibility
        stroke_width=5,
        background_image=image,
        update_streamlit=True,
        height=int(image.height * (image_scale / 800)),
        width=int(image.width * (image_scale / 800)),
        drawing_mode="point",
        point_display_radius=5,
        key="canvas",
    )

    # Variable to store last detected color information
    last_color_info = None

    if canvas_result.json_data is not None:
        # Extract coordinates of the clicked points
        if len(canvas_result.json_data["objects"]) > 0:
            for obj in canvas_result.json_data["objects"]:
                x, y = int(obj["left"]), int(obj["top"])

                # Get color information at the clicked coordinates
                color_name, r, g, b = detect_color(image, csv, x, y)
                
                if color_name is not None:
                    # Store the last detected color information
                    last_color_info = (color_name, r, g, b)

    # Display the last detected color information, if available
    if last_color_info:
        color_name, r, g, b = last_color_info
        st.write(f"Detected Color: {color_name}")
        st.write(f"RGB Values: R={r}, G={g}, B={b}")

        # Display a rectangle with the detected color
        st.markdown(f"<div style='background-color: rgb({r},{g},{b}); width:100px; height:100px;'></div>", unsafe_allow_html=True)
