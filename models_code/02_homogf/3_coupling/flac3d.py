from toughflac.coupling import extra, run
import numpy as np
from toughflac.coupling.permeability import rinaldi2019,rutqvist2002
from flac_output_d import run_flac_output

# FLAC3D solver parameters
model_save = "tf_in.f3sav"
deterministic = False
damping = "combined"
mechanical_ratio = 1.0e-7
n_threads = 28
thermal = True

# Output parameters
savedir = "f3out"
save_python = False

# Extra variables to save
extra["porosity"] = True
extra["porosity_delta"] = True
extra["pp"] = True
extra["pp_equivalent"] = True
extra["pp_delta"] = True
extra["temperature"] = True
extra["temperature_delta"] = True
extra["stress_delta"] = True
extra["stress_delta_prin"] = True
extra["density"] = True
extra["biot"] = True
extra["therm_coeff"] = True
extra["saturation"] = True
extra["pcap"] = True
extra["permeability"] = True


# Extra Python functions as a list of callables
python_tough_func = ()  # Before mechanical analysis
python_func_flac = {run_flac_output}  # After mechanical analysis

# Extra FISH functions as a list of strings
fish_func_tough = ()  # Before mechanical analysis
fish_func_flac = ()  # After mechanical analysis

# Permeability functions as a dict of functions per group
permeability_func = {
     "CORER": lambda g: rinaldi2019(g, k0 = 7.0e-15, phi0 = 0.024, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
     "COREM": lambda g: rinaldi2019(g, k0 = 3.0e-15, phi0 = 0.02, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
     "COREL": lambda g: rinaldi2019(g, k0 = 3.0e-15, phi0 = 0.02, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
     "INTEL": lambda g: rinaldi2019(g, k0 = 1.0e-14, phi0 = 0.027, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
     "INTER": lambda g: rinaldi2019(g, k0 = 1.0e-14, phi0 = 0.027, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
     "INTEM": lambda g: rinaldi2019(g, k0 = 6.0e-14, phi0 = 0.03, n=5, w=1, br=1.0e-5, bmax=1.0e-4, alpha=0.05, n_vector=np.asarray([-0.95882, 0, 0.284015]), joint=True),
}

history_func = {}
history_attributes = [
#     "temp",
#     "pp",
#     "permeability",
#     "stress_xx",
#     "stress_yy",
#     "stress_zz",
#     "stress_xz",
#     "stress_yz",
#     "stress_xy",
#     "strain_xx",
#     "strain_yy",
#     "strain_zz",
#     "strain_xz",
#     "strain_yz",
#     "strain_xy",
#     "disp_x",
#     "disp_y",
#     "disp_z"
]

history = {
    #"hist1": {k: [[0.2049, 0.0, 0.6916]] for k in history_attributes},
    #"hist2": {k: [[0.0, 0.0, 0.0]] for k in history_attributes},
    #"hist3": {k: [[-0.5604, 1.536, -0.5834]] for k in history_attributes},
    #"hist4": {k: [[1.5820, -7.0981, 14.3437]] for k in history_attributes},
    #"top_1": {k: [[0.211428, -0.5, 1.06587]] for k in history_attributes},
    #"top_2": {k: [[0.211428, 0.5, 1.06587]] for k in history_attributes},
    #"top_3": {k: [[0.403198, -0.5, 1.00907]] for k in history_attributes},
    #"top_4": {k: [[0.403198, 0.5, 1.00907]] for k in history_attributes},
    #"bot_1": {k: [[-0.198323, -0.5, -0.317424]] for k in history_attributes},
    #"bot_2": {k: [[-0.198323, 0.5, -0.317424]] for k in history_attributes},
    #"bot_3": {k: [[-0.00655254, -0.5, -0.374224]] for k in history_attributes},
    #"bot_4": {k: [[-0.00655254, 0.5, -0.374224]] for k in history_attributes},
}

if __name__ == "__main__":
    run(
        model_save=model_save,
        deterministic=deterministic,
        damping=damping,
        mechanical_ratio=mechanical_ratio,
        n_threads=n_threads,
        thermal=thermal,
        permeability_func=permeability_func,
        callback_tough=python_tough_func,
        callback_flac=python_func_flac,
        history_func=history_func,
        history=history,
        savedir=savedir,
        save_python=save_python,
    )
