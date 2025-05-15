# -*- python -*-
# -*- coding: utf-8 -*-
#
#      turgor simulation with bvpy
#
#      File contributor(s)
#            Adrien Heymans <adrien.heymans@slu.se>
#            Gonzalo Revilla <gonzalo.revilla-mut@inria.fr>
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------

import os
os.environ["PYVISTA_OFF_SCREEN"] = "true"
os.environ["DISPLAY"] = ""

import pandas as pd
import fenics as fe
from bvpy.domains import FixedGMSH
from bvpy.vforms import HyperElasticForm
from bvpy.vforms.elasticity import StVenantKirchoffPotential
from bvpy import BVP

# ----- Read Parameters -----
params = pd.read_csv("params.csv").iloc[0]
young = float(params["young"])
poisson = float(params["poisson"])
bc_name = params["dirichlet"]
pressure = float(params["pressure"])

# ----- Utility Functions -----
def xdmf_save(path, solution, vform):
    solution.rename("Displacement Vector", "")
    strain = vform.get_strain(solution)
    strain.rename("Strain", "")
    stress = vform.get_stress(solution)
    stress.rename("Stress", "")
    xdmf_file = fe.XDMFFile(fe.MPI.comm_world, path)
    xdmf_file.parameters["flush_output"] = True
    xdmf_file.parameters["functions_share_mesh"] = True
    xdmf_file.parameters["rewrite_function_mesh"] = False    
    xdmf_file.write(solution, 1)
    xdmf_file.write(strain, 1)
    xdmf_file.write(stress, 1)



mesh_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'geometry.msh')  # os.getcwd() may work otherwise

# ----- FEM Setup -----
cd = FixedGMSH(fname=mesh_path, gdim=2)
elastic_potential = StVenantKirchoffPotential(young=young, poisson=poisson)
form = HyperElasticForm(potential_energy=elastic_potential, source=[0., 0.], plane_stress=True)
turgor = BVP(domain=cd, vform=form)

# ----- Dirichlet BC -----
turgor.add_zero_dirichlet_bc(boundary=bc_name)

# ----- Neumann BC -----
turgor.add_normal_neumann_bc(boundary="inner", norm=-pressure)

# ----- Solver -----
turgor.solve(
    linear_solver='mumps',
    krylov_solver={'absolute_tolerance': 1e-14},
    relative_tolerance=1e-6,
    absolute_tolerance=1e-8,
    preconditioner='none',
    maximum_iterations=500,
    line_search='bt'
)

# ----- Output -----
xdmf_save("./turgor.xdmf", turgor.solution, form)

# ----- Visualization -----

import pyvista as pv
from bvpy.utils.visu_pyvista import add_subplot

# pv.start_xvfb()  # Start virtual framebuffer if needed

# Define Plotter with subplots
off_screen = True  # If True, the GUI will not be displayed and the plot will be saved as a PNG
pl = pv.Plotter(shape=(2, 3), window_size=[1000, 800], off_screen=off_screen)

# -- Row 0 --
pl.subplot(0, 0)
add_subplot(pl, turgor.domain.mesh, title='Domain')

pl.subplot(0, 1)
add_subplot(pl, turgor.domain.fdata, mf_dict=turgor.domain.sub_facets_names, title="Boundaries")

pl.subplot(0, 2)
add_subplot(pl, turgor.dirichletCondition, title="Dirichlet BC", show_norm=True)

pl.subplot(1, 0)
add_subplot(pl, turgor.neumannCondition, neumann_mf=turgor.neu_fdata, title='Neumann BC')

pl.subplot(1, 1)
add_subplot(pl, turgor.solution, title='Displacement field', mesh_kwargs={"show_edges": False})

pl.subplot(1, 2)
applied_turgor = cd.move(turgor.solution, return_cdata=False)  # Apply the solution to the domain (deformed geometry)
add_subplot(pl, applied_turgor, title="Deformed domain", mesh_kwargs={"show_edges": False})

# Finalize and save
pl.link_views()
if not off_screen:
    pl.show()  # Show the plot in GUI
else:
    pl.screenshot("plot.png")  # <- Save figure as PNG
    pl.close()