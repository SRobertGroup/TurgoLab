#
# This is a Streamlit web application. You can run the application with the following command
# 'streamlit run main.py'
#
# Copyright © 2025, Umeå Plant Science Center, Swedish University Of Agricultural Sciences, Umeå, Sweden
# All rights reserved.
# 
# Developers: Adrien Heymans
# 
# Redistribution and use in source and binary forms, with or witvim hout modification, are permitted under the GNU General Public License v3 and provided that the following conditions are met:
#   
#   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# 
# Disclaimer
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# You should have received the GNU GENERAL PUBLIC LICENSE v3 with this file in license.txt but can also be found at http://www.gnu.org/licenses/gpl-3.0.en.html
# 
# NOTE: The GPL.v3 license requires that all derivative work is distributed under the same license. That means that if you use this source code in any other program, you can only distribute that program with the full source code included and licensed under a GPL license.

import streamlit as st
import pandas as pd
import subprocess
import zipfile
import os
from subprocess import call, DEVNULL

st.set_page_config(page_title="TurgoLab App", layout="wide")

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)

row0_1.title("Turgor Simulation")

row0_2.subheader(
    "A Finite Element Modeling app to inflate 2D cell networks from .geo file"
)

row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.columns(
    (0.1, 1.5, 0.2, 1.5, 0.1)
)

with row1_1:
    st.markdown(
        'This application provides: \n - Mesh generation from .geo file made through [Anatomeshr](https://anatomeshr.serve.scilifelab.se/) \n - Solve the boundary value problem through [BVPy](https://gitlab.inria.fr/mosaic/bvpy): \n  - Define the biomechanical properties of the cell walls (Young s Modulus and Poisson coef.)\n  - Select the turgor pressure [MPa].\n - Select the cell that will be fix \n - Download results'
    )

    # --- Inputs ---
    geo_file = st.file_uploader("Upload .geo file", type=["geo"])
    scale = st.number_input("Mesh scale", min_value=0.1, max_value=10.0, value=1.5)
    mesh_done = False

# --- Save uploaded geometry ---
    if geo_file:
        geo_path = f"./uploaded_{geo_file.name}"
        with open(geo_path, "wb") as f:
            f.write(geo_file.read())
    else:
        geo_path = './geometry.geo'



with row1_2:
    # ----- Mesh Generation -----
    if st.button("Generate Mesh"):
        with st.spinner("Generating mesh with Gmsh..."):
            result = subprocess.run(
                ["gmsh", geo_path, "-2", "-format", "msh2", "-clscale", str(scale), "-o", "geometry.msh"],
                capture_output=False, text=False
            )
            if result.returncode != 0:
                st.error("Mesh generation failed:\n" + result.stderr)
            else:
                st.success("Mesh generated successfully!")
                mesh_done = True
    # ----- Mesh Generation -----
    if st.button("Plot Mesh"):
        with st.spinner("Reading Mesh..."):
            result = subprocess.run(["python3", "plot_mesh.py"], capture_output=False, text=False)
            if result.returncode != 0:
                st.error("Mesh visualization failed:\n" + result.stderr)
            else:
                st.session_state.plot_displayed = True
                st.image("mesh_preview.png", caption="mesh preview", use_container_width=True)

# --- FEM Input Parameters ---
st.subheader("FEM Simulation Parameters")

young = st.slider("Young's Modulus (MPa)", min_value=0.1, max_value=1e4, value=200.0)
poisson = st.number_input("Poisson's Ratio", 0.0, 0.5, 0.4)
selected_bc = st.selectbox("Dirichlet BC", options=["fix", "outer"])
pressure = st.number_input("Pressure (MPa)", 0.0, 10.0, 0.3)

# --- Write parameters to CSV ---
params = pd.DataFrame([{
    "young": young,
    "poisson": poisson,
    "dirichlet": selected_bc,
    "pressure": pressure
}])
params.to_csv("params.csv", index=False)

# Session state
if "plot_displayed" not in st.session_state:
    st.session_state.plot_displayed = False

output_sim = False
# --- Launch solver script ---
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        log_placeholder = st.empty()
        process = subprocess.Popen(
            ["python3", "turgor.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        log_lines = []
        for line in iter(process.stdout.readline, ''):
            log_lines.append(line)
            log_placeholder.code(''.join(log_lines), language='bash')

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            st.error("Simulation failed with errors. See output above.")
        else:
            st.success("Simulation completed.")

            if os.path.exists("plot.png"):
                st.session_state.plot_displayed = True
                st.image("plot.png", caption="Simulation Output", use_container_width=True)
            # Zip xdmf + h5
            zip_path = "turgor_output.zip"
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.write("turgor.xdmf")
                if os.path.exists("turgor.h5"):
                    zf.write("turgor.h5")
        
            with open(zip_path, "rb") as f:
                st.download_button("Download Results (XDMF + H5)", f, file_name="turgor_output.zip")


st.markdown(
        '### Acknowledgments \n \n Anatomeshr and TurgoLab were developed by members of the [**Stéphanie Robert Group**](https://srobertgroup.com/) and [**Stéphane Verger Group**](https://www.upsc.se/researchers/6177-verger-stephane-mechanics-and-dynamics-of-cell-to-cell-adhesion-in-plants.html), in collaboration with the Inria project team [*Mosaic*](https://team.inria.fr/mosaic/) developping the [BVPy](https://mosaic.gitlabpages.inria.fr/bvpy/) library.'
    )