import pandas as pd
import fenics as fe
from bvpy.domains import CustomDomainGmsh
from bvpy.vforms import HyperElasticForm
from bvpy.vforms.elasticity import StVenantKirchoffPotential
from bvpy import BVP
from bvpy.domains.geometry import boundary_normal

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


mesh_path = './geometry.msh'

# ----- FEM Setup -----
cd = CustomDomainGmsh(fname=mesh_path)
elastic_potential = StVenantKirchoffPotential(young=young, poisson=poisson)
form = HyperElasticForm(potential_energy=elastic_potential, source=[0., 0., 0.], plane_stress=True)
turgor = BVP(domain=cd, vform=form)

# ----- Dirichlet BC -----
boundary2tag = {name: tag for tag, name in cd.sub_boundary_names.items()}
tag = boundary2tag[bc_name]
bc = fe.DirichletBC(turgor.functionSpace, [0, 0, 0], cd.bdata, tag)
turgor.dirichletCondition.append(bc)

# ----- Neumann BC -----
tag = boundary2tag["inner"]
assert tag == 1, "Expected tag 1 for Neumann BC due to current BVPy limitations"
nf = boundary_normal(turgor.functionSpace.mesh(), scale=-pressure)
turgor.neumannCondition['variable'].append(nf)
turgor._neumann_domain_id['variable'].append(tag)

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

import pyvista as pv
from bvpy.utils.visu_pyvista import visualize

# pv.start_xvfb()  # Start virtual framebuffer if needed

# Apply the solution to the domain (deformed geometry)
applied_turgor = cd.move(turgor.solution, return_cdata=False)

# Define Plotter with subplots
pl = pv.Plotter(shape=(2, 3), window_size=[1000, 800], off_screen=True)  # <- off_screen disables GUI

# -- Row 0 --
pl.subplot(0, 0)
visualize(turgor, visu_type='dirichlet', val_range=[-0.5, 0.5], plotter=pl, show_plot=False)

pl.subplot(0, 1)
visualize(turgor, visu_type='domain', plotter=pl, show_plot=False)

pl.subplot(0, 2)
visualize(turgor, visu_type='young', cmap='Pastel2', plotter=pl, show_plot=False)

# -- Row 1 --
pl.subplot(1, 0)
visualize(turgor, visu_type='mesh', plotter=pl, show_plot=False)
pl.add_title('Mesh \n(undeformed config.)', font_size=12)

pl.subplot(1, 1)
visualize(turgor, visu_type='solution', title='Displacement field', plotter=pl, show_plot=False)

pl.subplot(1, 2)
visualize(applied_turgor, plotter=pl, show_plot=False)
pl.add_title('Mesh \n(deformed config.)', font_size=12)

# Finalize and save
pl.link_views()
pl.screenshot("plot.png")  # <- Save figure as PNG
pl.close()
