import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Function to calculate minimum distance from all colors and get the most matching color
def getColorName(R, G, B, csv):
    minimum = 10000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

# Load the CSV file with colors
def load_colors():
    index = ["color", "color_name", "hex", "R", "G", "B"]
    return pd.read_csv('colors.csv', names=index, header=None)

# Function to crop image based on slider values (simulate scrolling)
def crop_image(img, start_x, start_y, display_width, display_height):
    cropped_img = img[start_y:start_y + display_height, start_x:start_x + display_width]
    return cropped_img

# Streamlit App
def main():
    st.title("Color Detector")
    st.write("Upload an image and click on it to detect the color. Use the sliders to pan over the image.")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img = np.array(img)

        img_height, img_width, _ = img.shape
        display_height = 400  # Fixed display window height
        display_width = 600   # Fixed display window width

        # Create a layout with the image on the left and details on the right
        col1, col2 = st.columns([2, 2])  # 3:1 ratio for larger image area

        with col1:
            st.write("### Image:")

            # Add sliders for panning through the image (scrolling simulation)
            # Horizontal slider at the bottom
            st.write("### Horizontal Scroll")
            start_x = st.slider("Horizontal Scroll", min_value=0, max_value=img_height - display_height, value=0, format="%d", step=1, key="horizontal_scroll", help="Scroll left/right", label_visibility="hidden")

            # Vertical slider on the left
            st.write("### Vertical Scroll")
            start_y = st.slider("Vertical Scroll", min_value=0, max_value=img_height - display_height, value=0, format="%d", step=1, key="vertical_scroll", help="Scroll up/down", label_visibility="hidden")

            # Crop image based on slider values
            cropped_img = crop_image(img, start_x, start_y, display_width, display_height)
            clicked = st.checkbox("Enable Color Detection", label_visibility="visible")  # Visible label example


            # Display the cropped image
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",  # transparent fill
                stroke_width=0,
                stroke_color="#000",
                background_image=Image.fromarray(cropped_img),
                update_streamlit=True,
                height=cropped_img.shape[0],  # Set height to the cropped image's height
                width=cropped_img.shape[1],   # Set width to the cropped image's width
                drawing_mode="point",
                key="canvas",
            )

        # Load the colors CSV file
        csv = load_colors()

        # If a point is clicked, show the color information in the second column
        if canvas_result.json_data is not None:
            if len(canvas_result.json_data["objects"]) > 0:
                last_obj = canvas_result.json_data["objects"][-1]  # Get the last clicked point
                x = int(last_obj["left"]) + start_x  # Adjust for panning offset
                y = int(last_obj["top"]) + start_y   # Adjust for panning offset

                if 0 <= x < img_width and 0 <= y < img_height:
                    # Get the RGB values at the clicked point
                    b, g, r = img[y, x]
                    color_name = getColorName(r, g, b, csv)

                    with col2:
                        st.subheader("Color Details")
                        st.write(f"**Detected Color**: {color_name}")
                        st.write(f"**RGB**: ({r}, {g}, {b})")
                        st.write(f"**Coordinates**: (X: {x}, Y: {y})")

                        # Show the detected color as a rectangle
                        color_display = np.zeros((100, 100, 3), dtype=np.uint8)
                        color_display[:] = [b, g, r]
                        st.image(color_display, caption=f"Color: {color_name}", use_column_width=False)

if __name__ == "__main__":
    main()
