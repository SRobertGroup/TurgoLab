import os
os.environ["PYVISTA_OFF_SCREEN"] = "true"
os.environ["DISPLAY"] = ""
import pyvista as pv

mesh = pv.read("geometry.msh")
pl = pv.Plotter(window_size=[1000, 800], off_screen=True, image_scale = 5)
pl.add_mesh(mesh, show_edges=True, color="lightblue")
pl.camera_position = 'xy'
pl.show(screenshot="mesh_preview.png")
pl.close() 