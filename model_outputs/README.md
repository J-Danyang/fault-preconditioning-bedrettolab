# Model outputs

This folder holds the post-processed output of each model, which the figure notebook reads:

```
model_outputs/
├── 01_base/F_clean.parquet
├── 01_base_np/F_clean.parquet
├── ...
└── 05_heterf_multi2i2o/F_clean.parquet
```

The files are too large for git. For peer review, download `model_outputs.zip` (9.7 GB) from
https://polybox.ethz.ch/index.php/s/4f3JGJp8ZZQHgEz (it will later be archived in the ETH Research
Collection) and unzip it in the repository root.

Each `F_clean.parquet` contains the fault-zone state at every coupling step, written by
`models_code/<model>/3_coupling/flac_output_d.py` and converted with `postprocessing/reformat_output.py`.

Columns: `ELEM` (TOUGH element id), `X`, `Y`, `Z` (m), `Slip_X/Y/Z` (relative displacement across the
fault layer, m), `Strain_P` (plastic joint shear strain), `Normal_Stress(Pa)`, `Shear_Stress(Pa)`
(effective normal and shear stress on the fault plane), `Vol_zone` (m³), `Pressure(Pa)`, `K_x/K_y/K_z`
(permeability, m²), `Time` (s), `ROCK` (TOUGH material index; 5/6/7 = left/right/middle permeable layer).
`05_heterf_multi2i2o` adds the total and effective stress tensor components and the principal stresses.

`TF_full.parquet` (also written by `reformat_output.py`) is not needed for the figures and is not
archived. The full raw simulation output (~200 GB, including FLAC3D save files) is not archived either;
it can be regenerated with the code and inputs in this repository.
