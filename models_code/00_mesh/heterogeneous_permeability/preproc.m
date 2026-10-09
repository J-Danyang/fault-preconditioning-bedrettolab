% preproc.m - assign a heterogeneous permeability field to the fault zone.
%
% Draws a permeability multiplier (pmx) for every fault-zone element
% (groups COREM/CORER/COREL/INTEM/INTER/INTEL) from a mixture of three
% lognormal distributions centred at 0.1, 1 and 10, clipped to [1e-3, 1e3].
% Elements within R = 1.5 m of the injection point keep pmx = 1.
% The multiplier is written into columns 41-50 of the ELEME block of the
% TOUGH mesh files.
%
% Inputs  (in this folder): MESH (= MESH_otb renamed), MESH_o
% Outputs: MESH_MODIFIED, MESH_o_MOD, figure_hist.pdf
%
% NOTE: rng('shuffle') makes every run a new random realization. The
% realization used in the paper is the archived models/00_mesh/MESH_o_heter.
% Requires RMESH.m (A. P. Rinaldi, see header of that file).

%function preproc()
clear
rng('shuffle')
if exist('mesh_data.mat','file')
    load mesh_data
    disp('----------------------------------------------------------')
    disp('')
    disp('MESH file opened from existing file...')
    disp('')
    disp('----------------------------------------------------------')
else
    [group ID coor_mesh V]=RMESH();
    save mesh_data
end

%% writing CONNE with awk
!rm CONNE.txt
system(['awk ''FNR > ' num2str(length(ID)+2) ''' MESH > CONNE.txt']);

%%
disp('')
disp('Assigning permeable patches...')
tic
PMX=ones(length(ID),1);

group_cell=mat2cell(group(:,11:15),ones(length(ID),1),5);
ind_ele_FAUCA1 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'COREM'), 'UniformOutput', 1));
ind_ele_FAUCA2 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'CORER'), 'UniformOutput', 1));
ind_ele_FAUCA3 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'COREL'), 'UniformOutput', 1));
ind_ele_FAUCA4 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'INTEM'), 'UniformOutput', 1));
ind_ele_FAUCA5 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'INTER'), 'UniformOutput', 1));
ind_ele_FAUCA6 = find(cellfun(@(x) ~isempty(x), strfind(group_cell,'INTEL'), 'UniformOutput', 1));

ind_ele_FAUCA = [ind_ele_FAUCA1; ind_ele_FAUCA2; ind_ele_FAUCA3; ind_ele_FAUCA4; ind_ele_FAUCA5; ind_ele_FAUCA6];

x=ones(length(ind_ele_FAUCA),1);

%% Patches
% r = randi(5, length(ind_ele_FAUCA), 1);
% x(r == 2) = 1e1;
% x(r == 3) = 1e2;
% x(r == 4) = 1e-1;
% x(r == 5) = 1e-2;

%% lognormal with two peaks
pd1 = makedist('Lognormal','mu',0,'sigma',0.5);
pd2 = makedist('Lognormal','mu',0,'sigma',0.5);
pd3 = makedist('Lognormal','mu',0,'sigma',0.5);

den1 = floor(length(ind_ele_FAUCA)/3);
den2 = floor(length(ind_ele_FAUCA)/3);
den3 = length(ind_ele_FAUCA) - den1 - den2;

x1=random(pd1,den1,1)*1e1;
x2=random(pd2,den2,1)*1e-1;
x0=random(pd3,den3,1)*1;
x3=[x0;x1;x2];
x3=x3(randperm(length(x3)));

if length(x3)<=length(ind_ele_FAUCA)
    x(1:length(x3))=x3;
else
    x=x3(1:length(ind_ele_FAUCA));
end

x(x<1.e-3)=1.e-3;
x(x>1.e3)=1.e3;

hist(log10(x),100)  % distribution of log10(pmx)
h=gcf;
set(h,'PaperOrientation','landscape');
print(['figure_hist.pdf'],'-dpdf','-r600','-fillpage')

%%
PMX(ind_ele_FAUCA)=x;

% coor_mesh is 1x3 cell: {X, Y, Z}
mesh_X = coor_mesh{1};
mesh_Y = coor_mesh{2};
mesh_Z = coor_mesh{3};
% Sphere definition
center = [0, 0, 0];   % sphere center
R = 1.5;            % radius
% Logical mask for points inside (or on) the sphere
mask = (mesh_X-center(1)).^2 + (mesh_Y-center(2)).^2 + (mesh_Z-center(3)).^2 <= R^2;
% Example: assign into an existing field/array the same size as X/Y/Z
PMX(mask) = 1;
%%
tic
disp('Writing MESH with permeability modifiers...')

fid=fopen('MESH');

if(fid<0)
    error('The file: "MESH" does not exist')
end

if exist('MESH_new','file')
    !rm MESH_new
end
line=fgets(fid);
dlmwrite('MESH_new',line(1:end-1),'-append', 'delimiter','');


for i=1:length(ID)
    row{1,i}=fgets(fid);
    row{1,i}(41:50)=num2str(PMX(i),'%.4E');
end


clear temp
temp=cell2mat(row);
dlmwrite('MESH_new',[temp '     '],'-append','delimiter','');
system('cat MESH_new CONNE.txt > MESH_MODIFIED');
fclose('all')
toc

