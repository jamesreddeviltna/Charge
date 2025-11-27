from streamlit_drawable_canvas import st_canvas
import streamlit as st

st.title("Drag the mass to change the gravitational field")

canvas_result = st_canvas(
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=400,
    width=400,
    drawing_mode="transform",  # use transform/drag mode
    key="canvas",
)

if canvas_result.json_data is not None:
    # Find your mass object and read its x,y
    # Then compute gravity field and display it
    st.write(canvas_result.json_data)
