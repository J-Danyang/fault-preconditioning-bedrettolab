import itasca as it
from itasca import zonearray as za
from itasca import gridpointarray as gpa
from toughio._mesh._common import labeler
import numpy as np
import csv
from scipy.sparse import csr_matrix

def get_gpaID(group_name):
    group_flag = za.in_group(group_name)
    idx_fault = za.ids()[group_flag]
    top = np.full(len(idx_fault), -1, dtype =int)
    bot = np.full(len(idx_fault), -1, dtype =int)

    for i in range(0, len(idx_fault)):
        # face_find_normal returns 0~5
        zone_i = it.zone.find(idx_fault[i])
        top[i] = zone_i.face_find_normal([-0.95882, 0, 0.284015]) # top
        bot[i] = zone_i.face_find_normal([0.95882, 0, -0.284015]) # bottom

    f_info_0 = za.faces()[group_flag, :, :]
    t_bool = np.eye(6, dtype=bool)[top]
    t_info = f_info_0[t_bool, :]
    top_idx = np.unique(t_info.flatten())

    b_bool = np.eye(6, dtype=bool)[bot]
    b_info = f_info_0[b_bool, :]
    bot_idx = np.unique(b_info.flatten())
    
    return top_idx, bot_idx, t_info, b_info # t_info and b_info give the mapping info for composing the sparse matrix
    
def get_faultSlip_surface(top_id, t_map):
    N_z = t_map.shape[0]
    N_p = len(top_id)

    zone_points = np.searchsorted(top_id, t_map)
    row_idx = np.repeat(np.arange(N_z), 4)
    col_idx = zone_points.reshape(-1)
    data    = np.full(N_z * 4, 0.25)     # average weight
    # compose the sparse matrix
    A = csr_matrix((data, (row_idx, col_idx)), shape=(N_z, N_p))
    
    # cauculate the x,y,z components of displacement
    disp_x = gpa.disp()[top_id, 0]
    avg_x = A @ disp_x
    disp_y = gpa.disp()[top_id, 1]
    avg_y = A @ disp_y
    disp_z = gpa.disp()[top_id, 2]
    avg_z = A @ disp_z
    
    return avg_x, avg_y, avg_z
    
def form_export_data(labels, disp_x, disp_y, disp_z, plastic_disp, sn, ss, volume, pp, perm_k):
    labels_e = labels.reshape(len(labels), 1)
    disp_x_e = disp_x.reshape(len(disp_x), 1)
    disp_y_e = disp_y.reshape(len(disp_y), 1)
    disp_z_e = disp_z.reshape(len(disp_z), 1)
    plastic_disp_e = plastic_disp.reshape(len(plastic_disp), 1)
    sn_e = sn.reshape(len(sn), 1)
    ss_e = ss.reshape(len(ss), 1)
    vol_e = volume.reshape(len(volume), 1)
    pp_e = pp.reshape(len(pp), 1)

    k_x = perm_k[:,0]
    permk_x = k_x.reshape(len(k_x), 1)
    k_y = perm_k[:,1]
    permk_y = k_y.reshape(len(k_y), 1)
    k_z = perm_k[:,2]
    permk_z = k_z.reshape(len(k_z), 1)
    
    x = za.pos()[:,0]
    x_e = x.reshape(len(x), 1)
    y = za.pos()[:,1]
    y_e = y.reshape(len(y), 1)
    z = za.pos()[:,2]
    z_e = z.reshape(len(z), 1)
    return np.concatenate((labels_e, x_e, y_e, z_e, disp_x_e, disp_y_e, disp_z_e, plastic_disp_e, sn_e, ss_e, vol_e, pp_e, permk_x, permk_y, permk_z), axis=1)

def write_Flac_output(output_file, t, matrix):
    with open(output_file, 'a') as f:
        f.write(f'TIME [sec]  {t:.8E}\n')
        matrix_lines = [','.join(map(str, row)) for row in matrix]
        f.write('\n'.join(matrix_lines) + '\n')

def run_flac_output(tough_time):
    print("writing_OutputFlac")
    tought, tstep = tough_time
    
    global INTEM_top_id, INTEM_bot_id, INTER_top_id, INTER_bot_id
    global INTEM_t_map, INTEM_b_map, INTER_t_map, INTER_b_map

    output_file = "OUTPUT_Flac.csv"
    if tstep == 1:
        # get the index for different interface for calculate the fault slip ## example for the function - top_id, bot_id, t_map, b_map = get_gpaID('Test1')
        INTEM_top_id, INTEM_bot_id, INTEM_t_map, INTEM_b_map = get_gpaID('INTEM')
        INTER_top_id, INTER_bot_id, INTER_t_map, INTER_b_map = get_gpaID('INTER')
        
        # Write header only for the first time step
        header = ['ELEM', 'X', 'Y', 'Z', 'Slip_X', 'Slip_Y', 'Slip_Z', 'Strain_P', 'Normal_Stress(Pa)', 'Shear_Stress(Pa)', 'Vol_zone', 'Pressure(Pa)', 'K_x', 'K_y', 'K_z']
        with open(output_file, 'w', newline='') as csvfile:
            csvfile.write(','.join(header) + '\n')
    
    num_cells = it.zone.count()
    labels = labeler(num_cells, label_length=None)  # Get the ID in TOUGH

    plastic_disp = za.prop_scalar('strain-shear-plastic-joint')
    volume = np.array([z.vol() for z in it.zone.list()]) # checked by za.ids() and z.id(), the order is the same
    pp = np.asarray(za.extra(15)) # Pore pressure
    perm_k = np.asarray(za.extra(11)) # permeability
    
    disp_x = np.zeros_like(plastic_disp)
    disp_y = np.zeros_like(plastic_disp)
    disp_z = np.zeros_like(plastic_disp)
    group_flag = za.in_group('INTEM')
    tx, ty, tz = get_faultSlip_surface(INTEM_top_id, INTEM_t_map)
    bx, by, bz = get_faultSlip_surface(INTEM_bot_id, INTEM_b_map)
    disp_x[group_flag] = tx - bx
    disp_y[group_flag] = ty - by
    disp_z[group_flag] = tz - bz
    group_flag = za.in_group('INTER')
    tx, ty, tz = get_faultSlip_surface(INTER_top_id, INTER_t_map)
    bx, by, bz = get_faultSlip_surface(INTER_bot_id, INTER_b_map)
    disp_x[group_flag] = tx - bx
    disp_y[group_flag] = ty - by
    disp_z[group_flag] = tz - bz
    # fault_slip = np.sqrt(np.clip((tz-bz)**2 + (ty-by)**2 + (tx-bx)**2, 0, None)) # since the displacements have the different directions
    
    n = np.asarray([-0.95882, 0, 0.284015]) # Normal vector to the plane
    eff_stress = np.array([-z.stress_effective() for z in it.zone.list()]) 
    # Compute traction vectors, normal stresses (sn), and shear stresses (ss)
    T = np.einsum('ijk,k->ij', eff_stress, n)
    sn = np.einsum('ij,j->i', T, n)
    ss = np.sqrt(np.einsum('ij,ij->i', T, T) - sn**2)

    data_to_export = form_export_data(labels, disp_x, disp_y, disp_z, plastic_disp, sn, ss, volume, pp, perm_k)
    write_Flac_output(output_file, tought, data_to_export)

    return
