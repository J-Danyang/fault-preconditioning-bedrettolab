# Export the model mesh to TOUGH3 (MESH + INCON) and FLAC3D (.f3grid) formats.
# Run inside FLAC3D with the toughflac package after restoring the mesh model:
#     model restore 'mesh2.sav'
#     program call 'export_mesh.py'
# The boundary conditions differ between outputs (see README); comment/uncomment the
# relevant block and run once per output file:
#   MESH_o   : all boundaries Dirichlet  (TOUGH steady state + coupled run;
#              archived as MESH_o_homog)
#   MESH_otb : only top/bottom Dirichlet (alternative TOUGH steady state)
#   OUTPUT1_mesh.f3grid : FLAC3D grid for the mechanical steady state

# import itasca as it
import toughflac as tf
# from itasca import zonearray as za

# Export to f3grid
# tf.zone.import_flac("OUTPUT1_mesh.f3grid", binary=True)
# tf.zone.export_flac("OUTPUT1_mesh.f3grid", binary=True)

# Define boundary conditions 
tf.zone.set_dirichlet_bc("RIGHB")
tf.zone.set_dirichlet_bc("LEFTB")
tf.zone.set_dirichlet_bc("FRONB")
tf.zone.set_dirichlet_bc("BACKB")
tf.zone.set_dirichlet_bc("TOPPB")
tf.zone.set_dirichlet_bc("BOTTB")

# Define initial conditions
tf.zone.initialize_pvariables(
    x1=lambda z: 6.8e6 - 9.81e3 * z,
    x2=lambda z: 0,
    x3=lambda z: 19.4 - 0.020855 * z,
)

# Export MESH and INCON
tf.zone.export_tough("MESH_o", incon=True, slot='Default')

# Define boundary conditions 
# tf.zone.set_dirichlet_bc("TOPPB")
# tf.zone.set_dirichlet_bc("BOTTB")
# Export MESH and INCON
# tf.zone.export_tough("MESH_otb", incon=False, slot='Default')