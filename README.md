# Reactivating Targeted Fault Interfaces Using Pre-conditioning in Complex Fault Zones

Code and model input files for:

> Jiang, D., Rinaldi, A. P., Ceccato, A., & Wiemer, S. *Reactivating Targeted Fault Interfaces Using Pre-conditioning in Complex Fault Zones*.

The repository has the coupled hydro-mechanical models (TOUGH3–FLAC3D) of fluid injection
into the MC fault at the BedrettoLab (inspired by the FEAR-1 stimulation, winter 2024). It also has
the pre- and post-processing scripts and the notebook that produces the figures in the paper.

- **Code (this repository):** https://github.com/J-Danyang/fault-preconditioning-bedrettolab
- **Model inputs (mesh files):** included in this repository as `model_inputs.zip`
- **Post-processed model outputs:** for peer review: https://polybox.ethz.ch/index.php/s/4f3JGJp8ZZQHgEz (to be archived in the ETH Research Collection)

## Model overview

The models are run with TOUGH3 (Jung et al., 2017) for fluid flow and FLAC3D (Itasca Consulting Group,
Inc., 2019) for geomechanics. The coupling methodology is described in Rutqvist et al. (2002) and
Rinaldi et al. (2022).

A 300 m × 500 m × 500 m domain (x: ±150 m, y: ±250 m, z: ±250 m; 231,960 elements) contains a fault
zone that dips 73.5°, as observed in geological mapping of the MC fault (Achtziger-Zupančič et al., 2024).
The injection point is at the origin point (0, 0, 0) located in the middle fault interface. The fault zone
has three permeable fault layers, each next to a core layer:

| TOUGH/FLAC3D group | Meaning | `ROCK` id in outputs |
|---|---|---|
| `INTEM` | middle permeable layer (contains the injection point) | 7 |
| `INTER` / `INTEL` | right / left permeable layer | 6 / 5 |
| `COREM`, `CORER`, `COREL` | fault core layers | – |
| `ROCKS` | host rock | – |
| `FRONB`, `BACKB`, `LEFTB`, `RIGHB`, `TOPPB`, `BOTTB` | boundary elements | – |
| `INJEC` | injection element (TOUGH only) | – |

Fault-zone permeability evolves with deformation following Rinaldi and Rutqvist (2019) (`rinaldi2019` in
`flac3d.py`). The permeable layers use a strain-softening ubiquitous-joint model (joint friction
21° → 16.5°, cohesion 2 MPa). The initial stress state comes from mini-frac measurements
(see `preprocessing/initial_stress_calculation.ipynb`).

## Models

| Folder | Fault permeability | Injection schedule (kg/s) | Simulated time | Used in |
|---|---|---|---|---|
| `01_base` | only `INTEM` permeable (and the only layer that can slip; the rest is elastic) | 0.40 for 24 h (pre-conditioning), then 1.20 | 50 h | Fig. 3 |
| `01_base_np` | as `01_base` | 1.20 from t = 400 s (no pre-conditioning) | 25 h | Fig. 3 |
| `02_homogf` | all layers, homogeneous | 0.83 for 24 h, then 2.50 | 50 h | Figs. 2, 4, 6–8, S2 (Scenario 3) |
| `02_homogf_np` | as `02_homogf` | 2.50 from t = 400 s | 25 h | Figs. 2, 4, 5, 8 (Scenario 1) |
| `03_heterf` | all layers, heterogeneous (lognormal) | 0.83 for 24 h, then 2.50 | 30 h | Figs. 2, 4, 6–8 (Scenario 4) |
| `03_heterf_np` | as `03_heterf` | 2.50 from t = 400 s | 5.1 h | Figs. 4, 5, 8, S1 (Scenario 2) |
| `04_homogf_biot0_hf` | as `02_homogf`, Biot coefficient ≈ 0, joint friction 24° | 0.83 for 24 h, then 2.50 | 50 h | Fig. 8 |
| `05_heterf_multi2i2o` | as `03_heterf` | 2 injectors (0.60 → 2.50) + 2 producers (0 → −1.0) | 30 h | Fig. 9 (mitigation) |

The mesh files are shared by all models and stored once in `models_code/00_mesh/`
(see [`models_code/00_mesh/README.md`](models_code/00_mesh/README.md)). Every model folder has the same three steps,
run in order:

```
models_code/
├── 00_mesh/                 # shared meshes (from model_inputs.zip) + mesh scripts
└── <model>/
    ├── 1_FLAC_steady_state/     # initialize_model.f3dat -> tf_in.f3sav (mechanical equilibrium)
    ├── 2_TOUGH_steady_state/    # INFILE, run.sh -> SAVE (hydraulic steady state)
    └── 3_coupling/              # INFILE (injection schedule), flac3d.py (permeability law),
                                 # flac_output_d.py (custom output), run.sh
```

## Requirements

**To run the models** (licensed software, not included):

- FLAC3D 7.0 (Itasca Consulting Group, Inc., 2019), https://www.itascacg.com/software/flac3d
- TOUGH3 with EOS3 (Jung et al., 2017; LBNL), https://tough.lbl.gov, coupled to FLAC3D through
  TOUGH3-FLAC3D (Rinaldi et al., 2022) and its `toughflac` Python package (the executable is called as
  `tough3-flac-eos3`)
- `toughio` (used by `flac_output_d.py`)
- MATLAB, only to generate a new heterogeneous permeability field (`models_code/00_mesh/heterogeneous_permeability/`)

**To post-process outputs and make the figures** (Python ≥ 3.10 with numpy, pandas, pyarrow, scipy,
matplotlib). With conda:

```bash
conda env create -f environment.yml
conda activate tf-fault
```

or with pip: `pip install -r requirements.txt`. Reading the `.parquet` files needs `pyarrow`, so run
the scripts and the notebook inside this environment (in VS Code, select it as the Python interpreter /
notebook kernel).

## Reproducing the results

### Option A: figures from the archived outputs (no licensed software needed)

1. Download `model_outputs.zip` (link above) and unzip it in the repository root; the files go to
   `model_outputs/<model>/` (see [`model_outputs/README.md`](model_outputs/README.md)). For Fig. 1, put the
   FEAR-1 field data in `field_data/` (see [`field_data/README.md`](field_data/README.md)).
2. Unzip `model_inputs.zip` in the repository root (`unzip model_inputs.zip`). Fig. 2 also reads the heterogeneous
   mesh `models_code/00_mesh/MESH_o_heterf`.
3. Run `figures/paper_figures.ipynb` from top to bottom (see [Figures](#figures)); PDFs are written
   to `figures/output/`.

### Option B: rerun the simulations

> **Note:** the coupled runs use the permeability function `rinaldi2019` from `toughflac.coupling.permeability`
> (imported in `3_coupling/flac3d.py`), which implements the permeability model of Rinaldi and Rutqvist (2019).
> Your TOUGH3-FLAC3D installation (`toughflac` package) must include this function.

1. Unzip `model_inputs.zip` in the repository root. This places the mesh files in `models_code/00_mesh/`.
2. **Mechanical steady state:** in `1_FLAC_steady_state/`, run `initialize_model.f3dat` in FLAC3D.
   Output: `tf_in.f3sav`. (The heterogeneous permeability is applied in TOUGH through the mesh file;
   fluid flow is computed by TOUGH.)
3. **Hydraulic steady state:** in `2_TOUGH_steady_state/`, run `./run.sh`. Check that the final
   state is steady before continuing.
4. **Coupled injection:** in `3_coupling/`, run `./run.sh`. It takes the TOUGH `SAVE` file as `INCON`
   and the FLAC3D `tf_in.f3sav`. The injection schedule is in the `GENER` block of `INFILE`, the
   permeability law in `flac3d.py`, and the fault-slip/stress output in `flac_output_d.py`
   (written to `OUTPUT_Flac.csv`).
5. **Post-process:** `python postprocessing/reformat_output.py models_code/<model>/3_coupling`, or open
   `reformat_output.py` in VS Code, set `MODEL_RUN_DIR` at the top and run the cells. It writes
   `F_clean.parquet` and `TF_full.parquet` in that folder.

- `clean.sh` in each step folder removes everything except the input files.
- `flac3d.sh` launches the FLAC3D console under WSL/Linux/Cygwin (edit the install paths for your system).

> Runtime: a coupled run takes several hours and varies with the model and the hardware. For example,
> the coupling step took about 5.1 h for `02_homogf` (50 h of simulated time) and about 3.7 h for
> `02_homogf_np` (25 h of simulated time), with 28 threads (`n_threads` in `flac3d.py`) on a Linux
> workstation with an Intel Xeon Platinum 8180 CPU (28 cores). The archived outputs let you reproduce all figures without rerunning.

### Regenerating the mesh (optional)

See [`models_code/00_mesh/README.md`](models_code/00_mesh/README.md). Note that the heterogeneous permeability
field is random (`rng('shuffle')`), so the realization used in the paper is the archived `MESH_o_heterf`.

## Figures

All figures are made by `figures/paper_figures.ipynb`. Each section of the notebook is one figure and
writes its panels as PDFs to `figures/output/`.

| Figure | Content | Input data |
|---|---|---|
| Fig. 1 | FEAR-1 Test 14 injection and seismicity | FEAR-1 field data |
| Fig. 2 | Data-constrained permeability evolution, permeability scaling and structure | `02_homogf`, `02_homogf_np`, `03_heterf`, `00_mesh/MESH_o_heterf` |
| Fig. 3 | Pre-conditioning on a single permeable fault | `01_base`, `01_base_np` |
| Fig. 4 | Slipping-area radius for the four scenarios | `02_*`, `03_*` |
| Fig. 5 | Results without pre-conditioning | `02_homogf_np`, `03_heterf_np` |
| Fig. 6 | Results with pre-conditioning | `02_homogf`, `03_heterf` |
| Fig. 7 | Reactivation comparison | `02_homogf`, `03_heterf` |
| Fig. 8 | Pre-conditioning: homogeneous vs heterogeneous, and the Biot ≈ 0 case | `02_*`, `03_*`, `04_homogf_biot0_hf` |
| Fig. 9 | Mitigation with two injectors and two producers | `05_heterf_multi2i2o` |
| Fig. S1 | Shear stress on the heterogeneous faults | `03_heterf_np` |
| Fig. S2 | Slip tendency of the three faults (homogeneous case) | `02_homogf` |

Run the setup cells at the top first. Each figure section can then be run on its own. The model results
are read from `model_outputs/<model>/F_clean.parquet`.

## Repository structure

```
├── models_code/
│   ├── 00_mesh/                # shared mesh files + export_mesh.py, preproc.m, RMESH.m
│   └── 01_base ... 05_...      # 8 model setups (see table above)
├── preprocessing/
│   └── initial_stress_calculation.ipynb   # rotation of the measured stress tensor into model coordinates
├── postprocessing/
│   └── reformat_output.py      # OUTPUT_ELEME.csv + OUTPUT_Flac.csv -> parquet
├── figures/
│   └── paper_figures.ipynb     # all paper figures
├── model_outputs/              # post-processed model outputs (download, see model_outputs/README.md)
├── field_data/                 # FEAR-1 field data for Fig. 1 (download, see field_data/README.md)
├── model_inputs.zip            # mesh files for models_code/00_mesh/ (44 MB)
├── environment.yml / requirements.txt
└── LICENSE
```

## Contact

Danyang Jiang, Swiss Seismological Service (SED), ETH Zurich, danyang.jiang@sed.ethz.ch

## Citation

Citation details will be added once the paper is published.

## License

The code in this repository is released under the MIT License (see [LICENSE](LICENSE)), except
`models_code/00_mesh/heterogeneous_permeability/RMESH.m`, which was written by A. P. Rinaldi (TOUGH2Matlab)
and keeps its original terms.

## Acknowledgements

The Bedretto Underground Laboratory for Geosciences and Geoenergies (BedrettoLab) is financed by the
Werner Siemens Foundation, ETH Zürich, and the Swiss National Science Foundation (grants 10.003.096 and
200021_192151). We thank Matterhorn Gotthard Infrastructure for providing access to the tunnel. This work
received funding from the European Research Council (ERC) through the FEAR project (grant agreement
No. 856559) under the European Union’s Horizon 2020 research and innovation program.

## References

- Itasca Consulting Group, Inc. (2019). *FLAC3D V7.0 – Fast Lagrangian Analysis of Continua in 3 Dimensions* (Version 7.0). Minneapolis, MN, USA.
- Jung, Y., Pau, G. S. H., Finsterle, S., & Pollyea, R. M. (2017). TOUGH3: A new efficient version of the TOUGH suite of multiphase flow and transport simulators. *Computers & Geosciences*, 108, 2–7. https://doi.org/10.1016/j.cageo.2016.09.009
- Rinaldi, A. P., & Rutqvist, J. (2019). Joint opening or hydroshearing? Analyzing a fracture zone stimulation at Fenton Hill. *Geothermics*, 77, 83–98. https://doi.org/10.1016/j.geothermics.2018.08.006
- Rinaldi, A. P., Rutqvist, J., Luu, K., Blanco-Martín, L., Hu, M., Sentís, M. L., Eberle, L., & Kaestli, P. (2022). TOUGH3-FLAC3D: a modeling approach for parallel computing of fluid flow and geomechanics. *Computational Geosciences*, 26(6), 1563–1580. https://doi.org/10.1007/s10596-022-10176-0
- Rutqvist, J., Wu, Y.-S., Tsang, C.-F., & Bodvarsson, G. (2002). A modeling approach for analysis of coupled multiphase fluid flow, heat transfer, and deformation in fractured porous rock. *International Journal of Rock Mechanics and Mining Sciences*, 39(4), 429–442. https://doi.org/10.1016/S1365-1609(02)00022-9
