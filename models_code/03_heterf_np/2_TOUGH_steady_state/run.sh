./clean.sh
cp ../../00_mesh/MESH_o_heterf MESH
cp ../../00_mesh/INCON .
# mpirun -np 28 toughflac-eos3 INFILE
tough3-flac-eos3 INFILE
