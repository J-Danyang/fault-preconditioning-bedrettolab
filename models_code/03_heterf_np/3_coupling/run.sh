#!/bin/bash
./clean.sh
cp ../../00_mesh/MESH_o_heterf MESH
sed "/+++/Q" < ../2_TOUGH_steady_state/SAVE > INCON
echo "" >> INCON
#cp ../flac3d.py .
cp ../1_FLAC_steady_state/tf_in.f3sav tf_in.f3sav
#time mpiexec -n 6 toughflac-eco2n 2dldV6.dat
tough3-flac-eos3 INFILE
