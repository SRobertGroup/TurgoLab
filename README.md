# TurgoLab

> _A Finite Element Modeling app to inflate 2D cell networks from .geo file_

**Lead Development:**   Adrien Heymans

**Contributors:** 
Ioannis Theodorou, Grégoire Loupit, Vinod Kumar, Gonzalo Revilla, Olivier Ali, Stéphanie Robert, Stéphane Verger

---

## 1. About

This application is built using **[Streamlit](https://streamlit.io/)** and containerized with **Docker**.  
It uses **Mamba** for robust dependency management and reproducible environments.

It provides:

- Mesh generation from .geo file made through [Anatomeshr](https://anatomeshr.serve.scilifelab.se/)
- Solve the boundary value problem through [BVPy](https://gitlab.inria.fr/mosaic/bvpy):
  - Define the biomechanical properties of the cell walls (Young's Modulus and Poisson coef.)
  - Select the turgor pressure [MPa].
  - Select the cell that will be fix (so the mesh don't fly away)
  - Download results

### [Run the app](https://turgolab.serve.scilifelab.se/) 

## 2. Installation

### Clone the Repository

```bash
git clone https://github.com/SRobertGroup/TurgoLab/
cd TurgoLab
```

### Run via Docker

To run with Docker (recommended):

```bash
docker pull heymansadrien/turgolab:0.0.1
```

Then launch it:

```bash
docker run -p 8501:8501 heymansadrien/turgolab:0.0.1
```

App will be available at: [http://localhost:8501](http://localhost:8501)

---

## 3. Usage

### Step 1: Upload Geo file and generate the mesh

Choose the geometry file that was made through [Anatomeshr](https://anatomeshr.serve.scilifelab.se/)

- 📂 **Anatomeshr GEO:** `.geo` or an equivalent `.geo` that has `Physical curve` with the specific label "inner" for all inner edge that will be under pressure, and "fix" for all edges that will be used to anchor the mesh.

### Step 2: Assign mechanical properties and boundary conditions

Customize the stiffness of the cell wall (`Young`) or the Turgor pressure value [MPa]

### Step 3: Solve the non-linear elastic problem (Saint Venant-Kirchoff)

Export your results 

---

> ⚠️ **Tips & Warnings**
>
> - Concave cells in `.xml` input can cause meshing errors
> - When using `.roi` input, consider increasing wall thickness to improve polygon closure
> - Use higher smoothing values to improve mesh quality in large or irregular cells

---

## 4. Citation

> Please cite [**Anatomeshr**](https://github.com/SRobertGroup/Anatomeshr) repository if you are using **Anatomeshr** or **TurgoLab** in your work.  
> A manuscript describing the method is currently in preparation.

---

## Acknowledgments

Anatomeshr and TurgoLab were developed by members of the [**Stéphanie Robert Group**](https://srobertgroup.com/) and [**Stéphane Verger Group**](https://www.upsc.se/researchers/6177-verger-stephane-mechanics-and-dynamics-of-cell-to-cell-adhesion-in-plants.html), in collaboration with the Inria project team *Mosaic* developping the BVPy library.
