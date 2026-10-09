# 00_mesh: shared mesh files

All models use the same FLAC3D grid and TOUGH initial conditions. They differ only in the TOUGH
mesh file (`MESH_o*`). The mesh files are stored zipped in the repository root as `model_inputs.zip` (44 MB); unzip it
there (`unzip model_inputs.zip`) and the files land in this folder.

| File | Size | Used by | Content |
|---|---|---|---|
| `OUTPUT1_mesh.f3grid` | 18 MB | all models, `1_FLAC_steady_state` | FLAC3D grid |
| `INCON` | 32 MB | all models, `2_TOUGH_steady_state` | TOUGH initial conditions (hydrostatic pressure, geothermal gradient) |
| `MESH_o` | 72 MB | 01, 01_np, 02, 02_np, 04 | TOUGH mesh, homogeneous fault zone, one injection element |
| `MESH_o_heterf` | 72 MB | 03, 03_np | as above, with the heterogeneous permeability multipliers (pmx) |
| `MESH_o_2i2o` | 72 MB | 05 | heterogeneous fault zone, with two injection and two production elements |
| `mesh.sav` | 100 MB | `export_mesh.py` only | FLAC3D model used to export the meshes |

Each model's `run.sh` copies the right `MESH_o*` file into its run folder as `MESH`.

## Regenerating the meshes (optional)

- `export_mesh.py`: run in FLAC3D with `toughflac` after `model restore 'mesh.sav'`. It writes the
  TOUGH mesh and `INCON` and the FLAC3D grid (see the comments in the script for the boundary settings).
- `heterogeneous_permeability/preproc.m` (MATLAB, uses `RMESH.m`): assigns lognormal permeability
  multipliers to the fault-zone elements of `MESH` and writes `MESH_MODIFIED`. It uses `rng('shuffle')`,
  so each run gives a new realization; the realization used in the paper is the archived `MESH_o_heterf`
  (and `MESH_o_2i2o` for model 05).
