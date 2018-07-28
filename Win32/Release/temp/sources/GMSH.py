# -*- coding: utf-8 -*-
'''
Created on 07/10/2016

@author: adrien.gros
'''
import subprocess

class GMSH_GEO:
    """ Classe python to create an GMSH_GEO object"""

    def __init__(self):
        self.list_point = []
        self.list_line = []
        self.list_loop = []
        self.list_surface = []
        self.list_surface_loop = []
        self.list_volume = []
        self.dico_surf_gr_phy = {}
        self.list_surface_crak = []
        self.cl1 = 2.5#0.01
        self.cl2 = self.cl1*5
        self.cl3 = 5*self.cl2
        self.option_mesh_size = False
        
    def write_open_geo_file(self,nomfichier):
        ''' function to write a geo file in the floder named 'nomfichier'
        the parameter self.option_mesh_size is a bollean:
        if it is thrue: 
        the mesh size of the 4 last points are assigned to 10 
        and the 4 previuos point are assugnet to 15 
        '''
        self.f = open(nomfichier,'w')
        self.f.write('//parametre de maillage:\n')
        self.f.write('cl1 = %f;\n'% (self.cl1))#parametre qui permet  de regler le maillage....
        self.write_point()
        self.write_line()
        self.write_lineloop_and_surface()
        self.write_surfaceloop_and_volume()
#         self.write_physical_group()
        self.write_physical_group_number()
        if self.option_mesh_size:
            id_last_point = len(self.list_point)
            liste_point = [id_last_point,id_last_point-1,id_last_point-2,id_last_point-3]
            mesh_size = self.cl3
            self.write_mesh_size_point(liste_point,mesh_size)
            liste_point = [id_last_point-4,id_last_point-5,id_last_point-6,id_last_point-7]
            mesh_size = self.cl2
            self.write_mesh_size_point(liste_point,mesh_size)
        self.f.close()

        
        
    def write_point(self):
        self.f.write('//write of the points\n')

        for i in xrange(len(self.list_point)):

            self.f.write('Point(%d) = {%s, %s, %s, cl1};\n'% (i+1,self.list_point[i][0],self.list_point[i][1],self.list_point[i][2]))
            
    def write_line(self):
        self.f.write('//write of the lines\n')

        for i in xrange(len(self.list_line)):

            self.f.write('Line(%d) = { %d, %d};\n'% (i+1,self.list_line[i][0],self.list_line[i][1]))
            
    def write_lineloop_and_surface(self):
        self.f.write('//write of the linesloops and surface\n')

        for i in xrange(len(self.list_loop)):
            print' lineloop n°',i
            self.f.write('Line Loop(%d) = { %d'% (i+1,self.list_loop[i][0]))
            for j in xrange(1,len(self.list_loop[i])):
                self.f.write(',%d'% (self.list_loop[i][j]))
            self.f.write('};\n')
        for i in xrange(len(self.list_surface)):
            self.f.write('Plane Surface(%d) = { %d'% (i+1,self.list_surface[i][0]))
            for j in xrange(1,len(self.list_surface[i])):
                self.f.write(',%d'% (self.list_surface[i][j]))
            self.f.write('};\n')
    def write_surfaceloop_and_volume(self):
        self.f.write('//write of the surfacelinesloops and volume\n')

        for i in xrange(len(self.list_surface_loop)):
            self.f.write('Surface Loop(%d) = { %d'% (i+1,self.list_surface_loop[i][0]))
            for j in xrange(1,len(self.list_surface_loop[i])):
                self.f.write(',%d'% (self.list_surface_loop[i][j]))
            self.f.write('};\n')
            
        for i in xrange(len(self.list_volume)):
            self.f.write('Volume(%d) = { %d'% (i+1,self.list_volume[i][0]))
            for j in xrange(1,len(self.list_volume[i])):
                self.f.write(',%d'% (self.list_volume[i][j]))
            self.f.write('};\n')
#             self.f.write('Plane Surface(%d) = {%d};\n'% (i+1,i+1))

    def write_physical_group(self):
        self.f.write('//write of the physical group\n')

        for key in self.dico_surf_gr_phy.keys():
            self.f.write('Physical Surface("%s") = { %d'% (key,self.dico_surf_gr_phy[key]['id_surface'][0]))
            for j in xrange(1,len(self.dico_surf_gr_phy[key]['id_surface'])):
                self.f.write(',%d'% (self.dico_surf_gr_phy[key]['id_surface'][j]))
            self.f.write('};\n')
            
        for key in self.dico_vol_gr_phy.keys():
            self.f.write('Physical Volume("%s") = { %d'% (key,self.dico_vol_gr_phy[key][0]))
            for j in xrange(1,len(self.dico_vol_gr_phy[key]['id_surface'])):
                self.f.write(',%d'% (self.dico_vol_gr_phy[key]['id_surface'][j]))
            self.f.write('};\n')

    def write_physical_group_number(self):
        self.f.write('//write of the physical group\n')
        number = 1
        for key in self.dico_surf_gr_phy.keys():
#             print'keys = ', key
            self.dico_surf_gr_phy[key]['number'] = number
            self.f.write('Physical Surface("%s") = { %d'% (key,self.dico_surf_gr_phy[key]['id_surface'][0]))
            for j in xrange(1,len(self.dico_surf_gr_phy[key]['id_surface'])):
                self.f.write(',%d'% (self.dico_surf_gr_phy[key]['id_surface'][j]))
            self.f.write('};\n')
            number+=1
            
#         for key in self.dico_surf_gr_phy.keys():
# #             print'keys = ', key
#             self.dico_surf_gr_phy[key]['number'] = number
#             self.f.write('Physical Surface(%s) = { %d'% (self.dico_surf_gr_phy[key]['number'],self.dico_surf_gr_phy[key]['id_surface'][0]))
#             for j in xrange(1,len(self.dico_surf_gr_phy[key]['id_surface'])):
#                 self.f.write(',%d'% (self.dico_surf_gr_phy[key]['id_surface'][j]))
#             self.f.write('};\n')
#             number+=1
            
            
        for key in self.dico_vol_gr_phy.keys():
            self.f.write('Physical Volume("%s") = { %d'% (key,self.dico_vol_gr_phy[key][0]))
            for j in xrange(1,len(self.dico_vol_gr_phy[key])):
                self.f.write(',%d'% (self.dico_vol_gr_phy[key][j]))
            self.f.write('};\n')       
    def write_mesh_size_point(self,liste_point,mesh_size):
        ''' function to write the attribution of size of mesh to a list a point contained in liste_point:
        liste_point: index of the point concerned
        mesh_size =  size of the mesh attributed
        ex : liste_point = [34,98,56], mesh_size = 15  will give in the geo:
        Characteristic Length {34,98,56} = 15;
        '''
        self.f.write('Characteristic Length { %d'% (liste_point[0]))

        for id_point in xrange(1,len(liste_point)):
            self.f.write(',%d'% (liste_point[id_point]))
        self.f.write('} = %f;\n'% (mesh_size))

    def write_plugin_crack(self,nomfichier):
        
        self.fbis = open(nomfichier,'w')
        self.fbis.write('//write of the physical group that crack\n')
        list_id_surface = []
        for gr_phy in self.list_surface_crak:

            self.fbis.write('Plugin(Crack).Dimension=2;\n')
            self.fbis.write('Plugin(Crack).PhysicalGroup=%s;\n'% (self.dico_surf_gr_phy[gr_phy]['number']))
            self.fbis.write('Plugin(Crack).OpenBoundaryPhysicalGroup=0;\n')
            self.fbis.write('Plugin(Crack).NormalX=0;\nPlugin(Crack).NormalY=0;\nPlugin(Crack).NormalZ=1;\n')
            self.fbis.write('Plugin(Crack).Run;\n')
        self.fbis.close()
        

class GMSH_command():
    def __init__(self):
        self.gmsh_directory = "C:\Program Files\GMSH\gmsh.exe"
        self.geo_directory = ''
        self.geo_crack_directory = ''
        self.msh_directory = ''
        
    def open_geo_in_gmsh(self):
        subprocess.Popen("%s %s " % (self.gmsh_directory, self.geo_directory)).wait()
        
    def triD_mesh_of_geo(self):
        ''' function to create a 3D mesh of the geometry in the directory self.geo_directory'''
        
        subprocess.Popen("%s %s -3" % (self.gmsh_directory, self.geo_directory))
    
    def triD_mesh_apply_plugin_crack(self):
        
        subprocess.Popen("%s %s %s -3" % (self.gmsh_directory, self.msh_directory, self.geo_crack_directory)).wait()
        
    def save_bdf(self):
        
        self.bdf_directory = self.msh_directory[:-3]+'bdf'       
#         subprocess.Popen("%s %s -0 -o %s " % (self.gmsh_directory, self.msh_directory, self.bdf_directory))
        subprocess.Popen("%s %s -format bdf -o %s -3" % (self.gmsh_directory, self.msh_directory, self.bdf_directory)).wait()


     
        

        
