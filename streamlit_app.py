import streamlit as st
import cadquery as cq
from cube_gen import build_letter_cube, export_stl
from streamlit_stl import stl_from_file
import time

def main():
    st.set_page_config(page_title="Perforated Initials Cube", layout="centered")
    st.title("🧊 Perforated Initials Cube Generator")

    # Only two inputs
    initials = st.text_input("Enter initials (3 letters)", value="ABC")
    cube_size = st.number_input("Cube size (mm)", min_value=20, max_value=200, value=30, step=5)

    if st.button("Generate Cube"):
        with st.spinner("Building your cube..."):
            start = time.time()
            cube = build_letter_cube(initials, font_size=cube_size, target_size=cube_size)
            stl_name = f"cube_{initials}_{int(cube_size)}.stl"
            export_stl(cube, stl_name)
            end = time.time()

        st.success(f"Cube generated in {end - start:.2f} seconds ✅")

        # STL preview
        stl_from_file(stl_name)

        # Download button
        with open(stl_name, "rb") as f:
            st.download_button(
                label="Download STL",
                data=f,
                file_name=stl_name,
                mime="model/stl"
            )

if __name__ == "__main__":
    main()
