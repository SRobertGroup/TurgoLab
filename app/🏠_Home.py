import streamlit as st

st.cache_data.clear()

st.set_page_config(page_title="TurgoLab Suite", layout="wide")
st.title("Welcome to the TurgoLab Suite")

st.markdown("""
This is a multi-functional toolkit for plant tissue simulation and analysis.

Choose a module from the sidebar:
- 🧬 **Anatomeshr**: Process anatomical images and generate `.geo` files for meshing.
- 🧪 **TurgoLab**: Run FEM simulations on anatomical structures.
""")

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (0.1, 2, 0.2, 1, 0.1)
)
with row0_1:
    st.link_button("🐙 View Anatomeshr source code", "https://github.com/SRobertGroup/Anatomeshr")
with row0_2:
    st.link_button("🐙 View TurgorLab source code", "https://github.com/SRobertGroup/TurgorLab")

st.markdown("""
### Acknowledgments 

Anatomeshr and TurgoLab were developed by members of the [**Stéphanie Robert Group**](https://srobertgroup.com/) and [**Stéphane Verger Group**](https://www.upsc.se/researchers/6177-verger-stephane-mechanics-and-dynamics-of-cell-to-cell-adhesion-in-plants.html), in collaboration with the Inria project team [*Mosaic*](https://team.inria.fr/mosaic/) developping the [BVPy](https://mosaic.gitlabpages.inria.fr/bvpy/) library.

**Developers**: Adrien Heymans \n
**Main contributor**: Gonzalo Revilla \n
**Other contributors**: Ioannis Theodorou, Grégoire Loupit, Vinod Kumar, Olivier Ali.\n
**Coordination**: Stéphanie Robert, Stéphane Verger

### 📝 License

This project is licensed under the [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html).\n
Copyright © 2025, Umeå Plant Science Center, Swedish University Of Agricultural Sciences, Umeå, Sweden

### Citation

> Please cite [**BVPy**](https://gitlab.inria.fr/mosaic/bvpy) and [**Anatomeshr**](https://github.com/SRobertGroup/Anatomeshr) repository if you are using **Anatomeshr** or **TurgoLab** in your work.  
> A manuscript describing the method is currently in preparation.

""")