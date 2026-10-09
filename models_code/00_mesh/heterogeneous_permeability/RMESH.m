function [group,ID,coor_mesh,V,conne,e]=RMESH(varargin)
% File MESH reader
% [group,ID,coor_mesh,V]=RMESH()-------------------------------------------
%              
% INPUT Variables
% Name-Value arguments:
% 'connection'-> true to analyze connection (default is false)
% 
% OUTPUT Variables
% coor -------> provides the meshgrid coordinates. It is a 2 cell array for
%               2D mesh, and a 3 cell array for 3D mesh. A cell array 
%               provides a storage mechanism for dissimilar kinds of data.
% ID ---------> Array of the elements name (5 char), with a length equal to
%               the mesh length.
% coor_mesh --> It is a 3 cell array, providing the coordinate X, Y, Z for
%               each meshgrid element. Each matrix of the cell array is
%               1xlength(ID).
% conne ------> Array containing the connection areas. It is useful to
%               compute the fluxes.
% e ----------> indexing connection
%
% 
% Versions:
% 1.0 RMESH.m for TOUGH2Matlab (July 2014)
% (https://tough.lbl.gov/licensing-download/free-software-download/)
% 2.0 Modified for reading larger meshes (TOUGH3) (October 2019)
%
% Author:
% A. P. Rinaldi (antoniopio.rinaldi@sed.ethz.ch)
%
% Acknowledgements:
% function "PADCAT" version 1.4 (dec 2018) (c) Jos van der Geest
% -------------------------------------------------------------------------


p = inputParser;
paramName1 = 'connection';
defaultVal1 = false;
% 
errorMsg = 'Value must be boolean.'; 
validationFcn = @(x) assert(islogical(x),errorMsg);
addParameter(p,paramName1,defaultVal1,validationFcn)
parse(p,varargin{:});
% 
connection=p.Results.connection;

%% Analysis of the grid mesh
tic
disp('-------------------------------------------------------')
disp('Reading file MESH.....')
disp('')

fid=fopen('MESH');
if(fid<0)
    error('The file MESH does not exist')
end

C = textscan(fid,'%s','delimiter','\n','whitespace', '','headerline',1);
C = vertcat( C{:} );
ind=find(strcmp('     ',C));
if isempty(ind)
    error('Not able to read number of elements')
else
    lmesh=ind(1)-1;
end
fclose(fid);

disp(['MESH has ' num2str(lmesh) ' elements'])

%%

C2 = textscan(fopen('MESH'),'%s',lmesh,'delimiter','\n','whitespace', '','headerline',1);
C2 = cell2mat(vertcat(C2{:}));

%%

ID=C2(:,1:5);
group(:,1:15)=C2(:,6:20);
V=str2num(C2(:,21:30));

coor_mesh{1,1}=str2num(C2(:,51:60));
coor_mesh{1,2}=str2num(C2(:,61:70));
coor_mesh{1,3}=str2num(C2(:,71:80));


%% Analysis of the connections

if nargout>4 && ~connection
    warning('You need to run the function with option (''connection'',true) to have connections parameters. Dumped dummy values for ''conne'' and ''e''');
    conne = NaN;
    e = NaN;
end

if connection

    ind2=find(strcmp('+++  ',C));
    if ~isempty(ind2)
        lconne=ind2-ind(1)-2;
    elseif length(ind)==2
        lconne=ind(2)-ind(1)-2;
    else
        error('Not able to read number of connection')
    end
    
    disp(['MESH has ' num2str(lconne) ' connections'])
    
    C3 = textscan(fopen('MESH'),'%s',lconne,'delimiter','\n','whitespace', '','headerline',lmesh+3);
    C3 = vertcat( C3{:} );
    CC = cell2mat(cellfun(@(x) x(:,1:60),C3,'UniformOutput',false));
    
    conne = str2num(CC(:,51:60)); %Connection Area
        
    nu1=mat2cell(CC(:,1:5),ones(lconne,1),5);
    nu2=mat2cell(CC(:,6:10),ones(lconne,1),5);
    ID_cell=mat2cell(ID,ones(lmesh,1),5);

    
    [~,e1] = ismember(nu1,ID_cell);
    [~,e2] = ismember(nu2,ID_cell);

    e=[e1 e2];

end

fclose(fid);

disp('')
toc
disp('-------------------------------------------------------')

end

