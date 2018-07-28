# -*- coding: utf-8 -*-
'''
Created on 03/10/2016

@author: adrien gros
'''

import GMSH
import cPickle
import struct
from geometrie import *
#import numpy 

class IDF:
    """ Classe python to create an IDF object"""
    def __init__(self):
        self.id_zones = []
        self.id_hole_wall = []
        self.dico_surface = []
        self.dico_fenes_surface = []
        self.zones = {}
        self.dico_ptf = {}
        self.parametre_first_id = 1
#         self.H,self.D = 150,50
        self.option_outdoor = True
        self.file_name_idf = r"D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela.idf"#_nrj.idf"
        self.file_name_gmsh = r"D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela2.geo"
        self.domus_estadoSim_directory = ''
        self.domus_estadoSim_directory_init = ''
        self.list_surface_loop = []
        self.list_volume = []
        self.dico_vol_gr_phy = {}
        self.zone1_name = 'Zona 1'
        self.list_intersurface = []
        self.idf = 'domus'
        self.meshsize = 0.5
        self.domus_version = '2.5.28.0'
        ''' if self.idf = 'nrjplus' the idf file read to make geometry is from nrjplus
        if self.idf = 'domus' the idf file read to make geometry is from domus '''
        
    def parsing(self,file_name):
        """ function to read an energyplus idf file:
        arguments:
        * file_name : the name of the path where is the file
        """
        idf_file = open(file_name,'r')
        self.liste_idf_file = idf_file.readlines()
        self.table_idf = []
        for i in xrange(len(self.liste_idf_file)):
#             print(self.liste_idf_file[i])
             
            # vérification lignes vides
            if self.liste_idf_file[i] != '\r\n' and self.liste_idf_file[i] != '\n':
                self.table_idf.append(self.liste_idf_file[i].split())
#                 print(self.table_idf[-1])

        self.domus_version = self.table_idf[2][0][:-1]
    def record_name(self,name):
        newname = name[0]
        for j in xrange(1,len(name)):
            if name[j]!='-':
                newname+=name[j]
        return newname
    
    def dictionnary_boundary_condition(self):
        ''' function to build a dictionnary with all boundary conditon for domus, this dictionnary will be used later to build text file to domus to have result from CFX'''
        self.dico_BC = {}
#         for i in xrange(len(self.dico_surface)):
#             key = self.dico_surface[i]['domus_name']
#             self.dico_BC[key] = {'temperature_int':',','temperature_ext':',','velocity_int':',','velocity_ext':',','hc_int':',','hc_ext':',','Cp_int':',','Cp_ext':','}
#         for i in xrange(len(self.dico_fenes_surface)):
#             key = self.dico_surface[i]['domus_name']
#             self.dico_BC[key] = {'temperature_int':',','temperature_ext':',','velocity_int':',','velocity_ext':',','hc_int':',','hc_ext':',','Cp_int':',','Cp_ext':','}
        for i in xrange(len(self.dico_surface)):
            key = self.dico_surface[i]['domus_name']
            self.dico_BC[key] = {'temperature_int':20.00,'temperature_ext':20.00,'velocity_int':3.00,'velocity_ext':3.00,'hc_int':3.00,'hc_ext':12.00,'Cp_int': 0.0,'Cp_ext': 0.0}
          #  self.dico_BC[key]['Cond_ext'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_int'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_extB'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_intB'] = numpy.zeros(8)
            
        for i in xrange(len(self.dico_fenes_surface)):
            key = self.dico_fenes_surface[i]['domus_name']
            self.dico_BC[key] = {'temperature_int':20.00,'temperature_ext':20.00,'velocity_int':3.00,'velocity_ext':3.00,'hc_int':3.00,'hc_ext':12.00,'Cp_int': 0.0,'Cp_ext': 0.0}
          #  self.dico_BC[key]['Cond_ext'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_int'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_extB'] = numpy.ones(8)
          #  self.dico_BC[key]['Cond_intB'] = numpy.ones(8)
            
    def complete_ts_BC_with_bin_estadosim(self,estadosim_file_name):
        ''' function to read value in binaries files and put them in self.dico_BC'''
        print ' dans complete_ts_BC_with_bin_estadosim, self.domus_estadoSim_directory = ',self.domus_estadoSim_directory
        for i in xrange(len(self.dico_surface)):
            key = self.dico_surface[i]['domus_name']
            zone_name = self.dico_surface[i]['Zone Name']
            ptf_name = self.dico_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45 
            wallname = key.replace("-"+zone_name, "")
            name_file = estadosim_file_name+zone_name+' - '+key# wallname# = '''D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1'
#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
            self.estadosim = Estadosim(node_number,tdma_number)

#                 print 'pause pour',key
            self.estadosim.read_file(name_file)
#             self.estadosim.print_values()
            val_oct = self.estadosim.dic['Tm'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['temperature_ext'] = val_float
            val_oct = self.estadosim.dic['Tm'][-1-self.estadosim.tdma_number]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['temperature_int'] = val_float           
#             val_oct = self.estadosim.dic['Te'][0]
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['Ta_ext'] = val_float
#             val_oct = self.estadosim.dic['Ti'][0]
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['Ta_int'] = val_float
            val_oct = self.estadosim.dic['hce'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['hc_ext'] = val_float
            val_oct = self.estadosim.dic['hci'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['hc_int'] = val_float
            
         #   self.dico_BC[key]['Cond_ext'] = numpy.zeros(8)
         #   self.dico_BC[key]['Cond_int'] = numpy.zeros(8)
         #   self.dico_BC[key]['Cond_extB'] = numpy.ones(8)
         #   self.dico_BC[key]['Cond_intB'] = numpy.ones(8)

#             if 'Zona 2' in key[-6:]:
#                 print' avant CFX pour', key,' Tint :',self.dico_BC[key]['Ta_int'], ' et Text:',self.dico_BC[key]['Ta_ext'], 'et  hcint :',self.dico_BC[key]['hc_int'], ' et hcext:',self.dico_BC[key]['hc_ext']

            #             print ' nom_fichier :',name_file
            self.estadosim.binfile.close()

        for i in xrange(len(self.dico_fenes_surface)):
            key = self.dico_fenes_surface[i]['domus_name']
            zone_name = self.dico_fenes_surface[i]['Zone Name']
            wall_name = self.dico_fenes_surface[i]['Building Surface Name']
            ptf_name = self.dico_fenes_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45             
            name_file = estadosim_file_name+zone_name+' - '+wall_name+key# wallname# = '''D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1'
#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
            self.estadosim = Estadosim(node_number,tdma_number)
            self.estadosim.node_number = node_number
            self.estadosim.read_file(name_file)
            val_oct = self.estadosim.dic['Tm'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['temperature_ext'] = val_float
            val_oct = self.estadosim.dic['Tm'][-1-self.estadosim.tdma_number]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['temperature_int'] = val_float
#             val_oct = self.estadosim.dic['Te'][0]
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['Ta_ext'] = val_float
#             val_oct = self.estadosim.dic['Ti'][0]
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['Ta_int'] = val_float
            
            val_oct = self.estadosim.dic['hce'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['hc_ext'] = val_float
            val_oct = self.estadosim.dic['hci'][0]
            val_float = struct.unpack('f', val_oct)[0]
            self.dico_BC[key]['hc_int'] = val_float
            
          #  self.dico_BC[key]['Cond_ext'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_int'] = numpy.zeros(8)
          #  self.dico_BC[key]['Cond_extB'] = numpy.ones(8)
          #  self.dico_BC[key]['Cond_intB'] = numpy.ones(8)
            

            
#             if 'Zona 2' in key:
#                 print' avant CFX pour', key,' Tint :',self.dico_BC[key]['Ta_int'], ' et Text:',self.dico_BC[key]['Ta_ext'], 'et  hcint :',self.dico_BC[key]['hc_int'], ' et hcext:',self.dico_BC[key]['hc_ext']

            self.estadosim.binfile.close()
        del self.estadosim
#             binfile = open(name_file, "rb")
#             a = len(binfile.read())
# #             print"a:",a
#             binfile.close()
#             binfile = open(name_file, "rb")
#         
#         
#         
# 
#             i=0
#             value = []
#             ''' lecture of the 4*2*(node_number+ 3*0 values) value corresponding to the temperature of the last past time and last iteration'''
#             val_oct = binfile.read((node_number+3)*2*4)
#             val_oct = binfile.read(4)
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['temperature_ext'] = val_float
# #             print 'pour ',key,'temperature_ext',self.dico_BC[key]['temperature_ext']
#             ''' lecture of the next node_number-1 value corresponding to the temperature in the wall( -1 because the last node havs not to be read because we need after''' 
#             val_oct = binfile.read((node_number-2)*4)
#             val_oct = binfile.read(4)
#             val_float = struct.unpack('f', val_oct)[0]
#             self.dico_BC[key]['temperature_int'] = val_float
# #             print 'pour ',key,'temperature_int',self.dico_BC[key]['temperature_int']
# #             while i<a/4:
# # 
# #                 val_oct = binfile.read(node_number*4)
# #                 
# #                 val_float = struct.unpack('f', val_oct)[0]
# #         #         lst_facform[i] = float32(val_float)
# #                 print 'i=',i+1,val_float
# #                 i+=1
# #                 value.append(val_float)
# #             self.dico_BC[key]= {'temperature_int':',','temperature_ext':',','velocity_int':',','velocity_ext':',','hc_int':',','hc_ext':',','Cp_int':',','Cp_ext':','} 
            
    def complete_hc_in_bin_estadosim(self):
        ''' function to complete the hc coeficient in the binary file'''
        ''' first step : read the original bin file'''
        for i in xrange(len(self.dico_surface)):
            key = self.dico_surface[i]['domus_name']
            zone_name = self.dico_surface[i]['Zone Name']
            ptf_name = self.dico_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45 
            line_number = 9
            wallname = key.replace("-"+zone_name, "")
            name_file = self.domus_estadoSim_directory_init+zone_name+' - '+key#wallname# = '''D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1'
#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
#             self.open_and_write_estadosimfile(name_file,key,node_number,line_number)
            self.change_estadosim(name_file,node_number,tdma_number,['hce','hci'],[self.dico_BC[key]['hc_ext'],self.dico_BC[key]['hc_int']])
            
        for i in xrange(len(self.dico_fenes_surface)):
            key = self.dico_fenes_surface[i]['domus_name']
            zone_name = self.dico_fenes_surface[i]['Zone Name']
            ptf_name = self.dico_fenes_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
            zone_name = self.dico_fenes_surface[i]['Zone Name']
            wall_name = self.dico_fenes_surface[i]['Building Surface Name']
            self.estadosim.tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45             
            name_file = self.domus_estadoSim_directory+zone_name+' - '+wall_name+key#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
#             self.open_and_write_estadosimfile(name_file,key,node_number,line_number)
            self.change_estadosim(name_file,node_number,tdma_number,['hce','hci'],[self.dico_BC[key]['hc_ext'],self.dico_BC[key]['hc_int']])
            
    def complete_flux_in_bin_estadosim(self,name_file_estadosim , hc = True, Ta = False, Cht = False ):
        ''' function to complete the convectif fluxes (hc, ta, cht, Cp,.....)  in the binary file'''
        ''' first step : read the original bin file'''
        clef_flux_list = []
        type = []
        "condition pour modifier les valeurs de coefficient de convection"    
        clef_flux_list.append('hce')
        clef_flux_list.append('hci')
        type.append('f')
        type.append('f')

        "condition pour ajouter des valeurs de temperature d'air en contacte avec le mur"    
        
        clef_flux_list.append('Te')
        clef_flux_list.append('Ti')
        type.append('f')
        type.append('f')
        clef_flux_list.append('Teb')
        clef_flux_list.append('Tib')
        type.append('B')
        type.append('B')
            

        'condition pour ajouter des valeurs de flux sensible'
       
        clef_flux_list.append('Fcse')
        clef_flux_list.append('Fcsi')
        type.append('f')
        type.append('f')
        clef_flux_list.append('Fcseb')
        clef_flux_list.append('Fcsib')
        type.append('B')
        type.append('B')

            
        print ' dans complete_flux_in_bin_estadosim, self.domus_estadoSim_directory =  ',name_file_estadosim
        for i in xrange(len(self.dico_surface)):
            key = self.dico_surface[i]['domus_name']
            zone_name = self.dico_surface[i]['Zone Name']
            ptf_name = self.dico_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45 
            line_number = 9
            wallname = key.replace("-"+zone_name, "")
            name_file = name_file_estadosim+zone_name+' - '+key#wallname# = '''D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1'
#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
#             self.open_and_write_estadosimfile(name_file,key,node_number,line_number)
            valeurs_flux_list = [] 
            
#             valeurs_flux_list.append(Teb)
#             valeurs_flux_list.append(Tib)
            
            valeurs_flux_list.append(self.dico_BC[key]['hc_ext'])            
            valeurs_flux_list.append(self.dico_BC[key]['hc_int'])

                

            valeurs_flux_list.append(self.dico_BC[key]['Cond_ext'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_int'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_extB'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_intB'][0])
                
            #if Fcse:
            valeurs_flux_list.append(self.dico_BC[key]['Cond_ext'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_int'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_extB'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_intB'][4])
                
            #print' apres CFX pour', key,' Tint :',self.dico_BC[key]['Ta_int'], ' et Text:',self.dico_BC[key]['Ta_ext'],' et hc_int:',self.dico_BC[key]['hc_int'],' et hc_ext:',self.dico_BC[key]['hc_ext']

            self.change_estadosim(name_file,node_number,tdma_number,clef_flux_list,valeurs_flux_list,type)
            
        for i in xrange(len(self.dico_fenes_surface)):
            key = self.dico_fenes_surface[i]['domus_name']
            zone_name = self.dico_fenes_surface[i]['Zone Name']
            ptf_name = self.dico_fenes_surface[i]['PTF']
            node_number = self.dico_ptf[ptf_name]['Numero de nos tot']
            tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
            zone_name = self.dico_fenes_surface[i]['Zone Name']
            wall_name = self.dico_fenes_surface[i]['Building Surface Name']
            self.estadosim.tdma_number = len(self.dico_ptf[ptf_name]['camadas'])-1
#             node_number = 45             
            name_file = name_file_estadosim+zone_name+' - '+wall_name+key#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
#             self.open_and_write_estadosimfile(name_file,key,node_number,line_number)
            valeurs_flux_list = [] 
            
#             valeurs_flux_list.append(Teb)
#             valeurs_flux_list.append(Tib)
            valeurs_flux_list.append(self.dico_BC[key]['hc_ext'])            
            valeurs_flux_list.append(self.dico_BC[key]['hc_int'])

                

            valeurs_flux_list.append(self.dico_BC[key]['Cond_ext'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_int'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_extB'][0])            
            valeurs_flux_list.append(self.dico_BC[key]['Cond_intB'][0])
                
            #if Fcse:
            valeurs_flux_list.append(self.dico_BC[key]['Cond_ext'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_int'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_extB'][4])
            valeurs_flux_list.append(self.dico_BC[key]['Cond_intB'][4])
                
            
            self.change_estadosim(name_file,node_number,tdma_number,clef_flux_list,valeurs_flux_list,type) 
        print ' fichier estasim qui a ete change:',name_file_estadosim  
            
    def open_and_write_estadosimfile(self,name_file,key,node_number,line_number):
            binfile = open(name_file, "rb")
            a = binfile.read((node_number+3)*4*line_number)
#             ''' temperature of the anterior time step:'''
#             temp_ant = binfile.read((node_number+3)*4)
#             ''' temperature of the anterior iteration:'''
#             temp_itant =  binfile.read((node_number+3)*4)
#             ''' actual temperature '''
#             temp_actualt =  binfile.read((node_number+3)*4)
#             ''' humidity of the anterior time step:'''
#             temp_ant =  binfile.read((node_number+3)*4)
#             ''' humidity of the anterior iteration:'''
#             temp_itant =  binfile.read((node_number+3)*4)
#             ''' actual humidity '''
#             temp_actualt =  binfile.read((node_number+3)*4)
#             ''' PPV of the anterior time step:'''
#             temp_ant =  binfile.read((node_number+3)*4)
#             ''' PPV of the anterior iteration:'''
#             temp_itant =  binfile.read((node_number+3)*4)
#             ''' actual PPV '''
#             temp_actualt =  binfile.read((node_number+3)*4)
            hint = binfile.read(4)
            hint = struct.pack('f',self.dico_BC[key]['hc_int'])
            hext = binfile.read(4)
            hext = struct.pack('f',self.dico_BC[key]['hc_ext'])
            hhumint = binfile.read(4)

            hhumext = binfile.read(4)

            hum_rel = binfile.read(4*(node_number+3))
            flux = binfile.read(4*3)
            binfile.close()
            binfiledst = open(name_file, "wb")#+"bis", "wb")
            binfiledst.write(a)
            binfiledst.write(hint)
            binfiledst.write(hext)
            binfiledst.write(hhumint)
            binfiledst.write(hhumext)
            binfiledst.write(hum_rel)
            binfiledst.write(flux)
            binfiledst.close()
    def change_estadosim(self,name_file,node_number, tdma_number ,key = ['hce'],valu = [3.0],type = ['f']):
        
        self.estadosim = Estadosim(node_number,tdma_number)

        self.estadosim.read_file(name_file)
        for i in xrange(len(key)):
            self.estadosim.replace_valu(key[i], valu[i], type[i])
        self.estadosim.binfile.close()
        self.estadosim.write_file()
        
    def upload_ptf_dic_surface_domus(self): 
        ''' function to read the ptf of the dictionnary of the different surface'''
#         self.dico_surface = []
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'Domus:FaceIDF,'in self.liste_idf_file[i]: 
                self.dico_surface[-1]['PTF'] = self.save_util_value(self.liste_idf_file[i+10],6)
                
            if 'Domus:FenestraIDF,'in self.liste_idf_file[i]:#:'ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED' in self.liste_idf_file[i]:#=='!-   ===========  ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED ===========':
                self.dico_fenes_surface[-1]['PTF'] = self.save_util_value(self.liste_idf_file[i+10],6)
                 
             
    def dictionnary_surface_domus(self):
        ''' function to build a dictionnary with all proporties of the differents surfaces in the IDF from domus'''
#         self.dico_surface = []
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'Domus:FaceIDF,'in self.liste_idf_file[i]:#:'ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED' in self.liste_idf_file[i]:#=='!-   ===========  ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED ===========':
#                 print(self.liste_idf_file[i])
                self.dico_surface.append({}) 
                ''' the domus_face_index represent the indexation of the face used in the domus idf file in the class DOMUS:FACE
                this indexation of the face  start at 1 but 1,2,3,4,5,6,7 correspond to the soil object, then it is start at 8'''
                self.dico_surface[-1]['domus_face_index'] = len(self.dico_surface)+7
                self.dico_surface[-1]['name'] = self.save_util_value(self.liste_idf_file[i+1],4)
                name = self.save_util_value(self.liste_idf_file[i+1],4)
                name = name.split('-')
                cfxname = ''
                for n in xrange(len(name)):
                    cfxname+=name[n]
                self.dico_surface[-1]['name'] = cfxname#self.record_name(name)
                self.dico_surface[-1]['domus_name'] = self.save_domus_name(self.liste_idf_file[i+1], 4)#name#self.record_name(name)
                self.dico_surface[-1]['Surface Type'] = self.save_util_value(self.liste_idf_file[i+2],4)
                self.dico_surface[-1]['Construction Name'] = self.save_util_value(self.liste_idf_file[i+3],3)                
                self.dico_surface[-1]['Zone Name'] = self.save_util_value(self.liste_idf_file[i+4],4,False)
                self.dico_surface[-1]['Outside Boundary Condition'] = self.save_util_value(self.liste_idf_file[i+5],5)
                self.dico_surface[-1]['Outside Boundary Condition Object'] = self.save_util_value(self.liste_idf_file[i+6],7,False)
                if self.dico_surface[-1]['Outside Boundary Condition']== 'Surface':
                    name = self.dico_surface[-1]['Outside Boundary Condition Object']
                    self.dico_surface[-1]['Outside Boundary Condition Object'] = name# self.record_name(name)
                self.dico_surface[-1]['Sun Exposure'] = self.save_util_value(self.liste_idf_file[i+7],4)
                self.dico_surface[-1]['Wind Exposure'] = self.save_util_value(self.liste_idf_file[i+8],4)
                self.dico_surface[-1]['View Factor to Ground'] = self.save_util_value(self.liste_idf_file[i+9],7)
                self.dico_surface[-1]['PTF'] = self.save_util_value(self.liste_idf_file[i+10],6)
                vertex_number = int(self.save_util_value(self.liste_idf_file[i+14],4))
                self.dico_surface[-1]['vertex'] = []
                j = 0
                while j <vertex_number*3:
                    x = self.save_util_value(self.liste_idf_file[i+15+j+2],3)
                    y = self.save_util_value(self.liste_idf_file[i+15+j],3)
                    z = self.save_util_value(self.liste_idf_file[i+15+j+1],3)
                    j = j+3
#                     print([x,y,z])
                    self.dico_surface[-1]['vertex'].append([x,y,z])
                    
    def build_reflectance_array(self,dict_FF):
        ''' function to build
        array of ext_reflectance
        '''
       # reflectance_array = numpy.zeros(len(dict_FF.keys()))
         
         
 
        for i in xrange(len(self.dico_fenes_surface)):
            name = self.dico_fenes_surface[i]['domus_name']
#             if 'Zona 1' not in name:
#                 name = name + '-ext'
#             else:
#                 name = name
            if name in dict_FF.keys():
                ptf_name = self.dico_fenes_surface[i]['PTF']
                glazing_ptf_name = self.dico_ptf[ptf_name]['Glazing prop']
                 
                indice = dict_FF[name]['indice']
                reflectance_array[indice] = self.dico_ptf[glazing_ptf_name]['refl_ext']
                
             
        for i in xrange(len(self.dico_surface)):
            name = self.dico_surface[i]['domus_name']
#             if 'Zona 1' not in name:
#                 name = name + '-ext'
#             else:
#                 name = name
            if name in dict_FF.keys():
                ptf_name = self.dico_surface[i]['PTF']
                 
     
                indice = dict_FF[name]['indice']
                reflectance_array[indice] = 1-self.dico_ptf[ptf_name]['abs_ext']
                
                 
        return reflectance_array
                    
    def build_area_array(self,dict_FF):
        ''' function to build
        array of ext_reflectance
        '''
      #  area_array = numpy.zeros(len(dict_FF.keys()))


        for i in xrange(len(self.dico_fenes_surface)):
            name = self.dico_fenes_surface[i]['domus_name']
            if name in dict_FF.keys():
                area = self.dico_fenes_surface[i]['area']
                indice = dict_FF[name]['indice']
                area_array[indice] = area

            
        for i in xrange(len(self.dico_surface)):
            name = self.dico_surface[i]['domus_name']
            if name in dict_FF.keys():
                area = self.dico_surface[i]['area']
                indice = dict_FF[name]['indice']
                area_array[indice] = area
            
        return area_array
              
    def build_ptf_array(self,dict_FF):
        ''' function to build
        array of ext_reflectance
        '''
      #  reflectance_array = numpy.zeros(len(dict_FF.keys()))
      #  emissivity_array = 0.9999999999999999999*numpy.ones(len(dict_FF.keys()))

        for i in xrange(len(self.dico_fenes_surface)):
            name = self.dico_fenes_surface[i]['domus_name']
#             if 'Zona 1' not in name:
#                 name = name + '-ext'
#             else:
#                 name = name
            if name in dict_FF.keys():
                ptf_name = self.dico_fenes_surface[i]['PTF']
                glazing_ptf_name = self.dico_ptf[ptf_name]['Glazing prop']
                
                indice = dict_FF[name]['indice']
                reflectance_array[indice] = self.dico_ptf[glazing_ptf_name]['refl_ext']
                emissivity_array[indice] = self.dico_ptf[glazing_ptf_name]['emissivity']
            else:
                print 'il y a un probleme ',name,"n'est pas dans la matrice des facteur de forme"
            
        for i in xrange(len(self.dico_surface)):
            name = self.dico_surface[i]['domus_name']
#             if 'Zona 1' not in name:
#                 name = name + '-ext'
#             else:
#                 name = name
            if name in dict_FF.keys():
                ptf_name = self.dico_surface[i]['PTF']
                
    
                indice = dict_FF[name]['indice']
                reflectance_array[indice] = 1-self.dico_ptf[ptf_name]['abs_ext']
                emissivity_array[indice] = self.dico_ptf[ptf_name]['emissivity_ext']
            else:
                print 'il y a un probleme ',name,"n'est pas dans la matrice des facteur de forme"
                
        return reflectance_array, emissivity_array 
     
    def dictionnary_PTF(self):
        if (self.domus_version=='2.5.28.0')or(self.domus_version=='2.5.29.0'):
            indice = 1
        else:
            indice = 0
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'Domus:Face:PTF,'in self.liste_idf_file[i]:#
#                 self.dico_ptf.append({})
                name = self.save_util_value(self.liste_idf_file[i+1],4)
                self.dico_ptf[name] = {}
                self.dico_ptf[name]['camadas'] = []
                self.dico_ptf[name]['Numero de nos tot'] = 0
                layers_number = int(self.save_util_value(self.liste_idf_file[i+11],4))
                for j in xrange(layers_number):
                    self.dico_ptf[name]['camadas'].append({})
                    self.dico_ptf[name]['camadas'][-1]['Material'] = self.save_util_value(self.liste_idf_file[i+11+j*3+1],4+indice)
                    self.dico_ptf[name]['camadas'][-1]['Numero de nos'] = self.save_util_value(self.liste_idf_file[i+11+j*3+2],6+indice)
                    self.dico_ptf[name]['Numero de nos tot']+= int(self.dico_ptf[name]['camadas'][-1]['Numero de nos'])
                    self.dico_ptf[name]['camadas'][-1]['Espessura'] = self.save_util_value(self.liste_idf_file[i+11+j*3+3],4+indice)
                ''' dans domus en realite il faut rajouter un noeuds au nombre de noeuds indiqués dans l'idf'''
                self.dico_ptf[name]['Numero de nos tot']+=1
                self.dico_ptf[name]['abs_int'] = float(self.save_util_value(self.liste_idf_file[i+4],3))
                self.dico_ptf[name]['abs_ext'] = float(self.save_util_value(self.liste_idf_file[i+5],3))
                self.dico_ptf[name]['emissivity_int'] = float(self.save_util_value(self.liste_idf_file[i+6],3))
                self.dico_ptf[name]['emissivity_ext'] = float(self.save_util_value(self.liste_idf_file[i+7],3))
       
    def dictionnary_PTF_glass(self):   
        if (self.domus_version=='2.5.28.0')or(self.domus_version=='2.5.29.0'):
            indice = 1
        else:
            indice = 0
        
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'Domus:Face:PTF:Vidro:R,'in self.liste_idf_file[i]:#
#                 self.dico_ptf.append({})
                name = self.save_util_value(self.liste_idf_file[i+1],4)
                self.dico_ptf[name] = {}
                self.dico_ptf[name]['camadas'] = []
                self.dico_ptf[name]['Numero de nos tot'] = 0
                layers_number = int(self.save_util_value(self.liste_idf_file[i+11],4))
                for j in xrange(layers_number):
                    self.dico_ptf[name]['camadas'].append({})
                    self.dico_ptf[name]['camadas'][-1]['Material'] = self.save_util_value(self.liste_idf_file[i+11+j*3+1],4+indice)
                    self.dico_ptf[name]['camadas'][-1]['Numero de nos'] = self.save_util_value(self.liste_idf_file[i+11+j*3+2],6+indice)
                    self.dico_ptf[name]['Numero de nos tot']+= int(self.dico_ptf[name]['camadas'][-1]['Numero de nos'])
                    self.dico_ptf[name]['camadas'][-1]['Espessura'] = self.save_util_value(self.liste_idf_file[i+11+j*3+3],4+indice) 
                ''' dans domus en realite il faut rajouter un noeuds au nombre de noeuds indiqués dans l'idf'''
                self.dico_ptf[name]['Numero de nos tot']+=1 
                self.dico_ptf[name]['Glazing prop'] =  self.save_util_value(self.liste_idf_file[i+10],4)
#                 self.dico_ptf[name]['emissivity_int'] = float(self.save_util_value(self.liste_idf_file[i+4],2))
#                 self.dico_ptf[name]['emissivity_ext'] = float(self.save_util_value(self.liste_idf_file[i+4],2))
                
            if 'Domus:Face:PTF:Vidro:R:Glazing,'in self.liste_idf_file[i]:
                name = self.save_util_value(self.liste_idf_file[i+1],4)
                self.dico_ptf[name] = {}
                self.dico_ptf[name]['emissivity'] = float(self.save_util_value(self.liste_idf_file[i+8],8))
                self.dico_ptf[name]['refl_int'] = float(self.save_util_value(self.liste_idf_file[i+3],8))
                self.dico_ptf[name]['refl_ext'] = float(self.save_util_value(self.liste_idf_file[i+4],8))
                self.dico_ptf[name]['trans'] = float(self.save_util_value(self.liste_idf_file[i+2],6))

              
    def dictionnary_surface(self):
        ''' function to build a dictionnary with all proporties of the differents surfaces in the IDF'''
#         self.dico_surface = []
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'BuildingSurface:Detailed,'in self.liste_idf_file[i]:#:'ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED' in self.liste_idf_file[i]:#=='!-   ===========  ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED ===========':
#                 print(self.liste_idf_file[i])
                self.dico_surface.append({}) 
                ''' the domus_face_index represent the indexation of the face used in the domus idf file in the class DOMUS:FACE
                this indexation of the face  start at 1 but 1,2,3,4,5,6,7 correspond to the soil object, then it is start at 8'''
                self.dico_surface[-1]['domus_face_index'] = len(self.dico_surface)+7
                self.dico_surface[-1]['name'] = self.save_util_value(self.liste_idf_file[i+1],2)
                name = self.save_util_value(self.liste_idf_file[i+1],2)
                self.dico_surface[-1]['name'] = name#self.record_name(name)
                self.dico_surface[-1]['domus_name'] = self.save_domus_name(self.liste_idf_file[i+1], 2)#name#self.record_name(name)
                self.dico_surface[-1]['Surface Type'] = self.save_util_value(self.liste_idf_file[i+2],3)
                self.dico_surface[-1]['Construction Name'] = self.save_util_value(self.liste_idf_file[i+3],3)
                self.dico_surface[-1]['Zone Name'] = self.save_util_value(self.liste_idf_file[i+4],3,False)#self.dico_surface[-1]['Zone Name'] = self.save_util_value(self.liste_idf_file[i+4],3,False)
                self.dico_surface[-1]['Outside Boundary Condition'] = self.save_util_value(self.liste_idf_file[i+5],4)
                self.dico_surface[-1]['Outside Boundary Condition Object'] = self.save_util_value(self.liste_idf_file[i+6],5,False)
                if self.dico_surface[-1]['Outside Boundary Condition']== 'Surface':
                    name = self.dico_surface[-1]['Outside Boundary Condition Object']
                    self.dico_surface[-1]['Outside Boundary Condition Object'] = name# self.record_name(name)
                self.dico_surface[-1]['Sun Exposure'] = self.save_util_value(self.liste_idf_file[i+7],3)
                self.dico_surface[-1]['Wind Exposure'] = self.save_util_value(self.liste_idf_file[i+8],3)
                self.dico_surface[-1]['View Factor to Ground'] = self.save_util_value(self.liste_idf_file[i+9],5)
                vertex_number = int(self.save_util_value(self.liste_idf_file[i+10],4))
                self.dico_surface[-1]['vertex'] = []
                j = 0
                while j <vertex_number*3:
                    x = self.save_util_value(self.liste_idf_file[i+11+j],5)
                    y = self.save_util_value(self.liste_idf_file[i+11+j+1],5)
                    z = self.save_util_value(self.liste_idf_file[i+11+j+2],5)
                    j = j+3
#                     print([x,y,z])
                    self.dico_surface[-1]['vertex'].append([x,y,z])
#                 print('the dictionnary of surface is',self.dico_surface[-1])




#                 print(dico[-1]['name'])
#                 dico[-1]['name']=self.liste_idf_file[i+1][:-16]
#                 print(dico[-1]['name'])
#                 for j in range(10):
#                     
#                     dico[-1]['name']=self.liste_idf_file[i+1].split()[:-2]
#                     print(dico[-1]['name'])

    def dictionnary_fenestration_surface(self):
        ''' function to build a dictionnary with all proporties of the differents fenestration surfaces in the IDF'''
#         self.dico_fenes_surface = []
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'FenestrationSurface:Detailed,'in self.liste_idf_file[i]:#:'ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED' in self.liste_idf_file[i]:#=='!-   ===========  ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED ===========':
#                 print(self.liste_idf_file[i])
                self.dico_fenes_surface.append({}) 
                self.dico_fenes_surface[-1]['name'] = self.save_util_value(self.liste_idf_file[i+1],2)
                self.dico_fenes_surface[-1]['domus_name'] = self.save_domus_name(self.liste_idf_file[i+1], 2)#self.save_util_value(self.liste_idf_file[i+1],2)
                ''' to know the zone , we search the information in the surface corresponding to the fenestration'''
#                 self.dico_fenes_surface[-1]['Zone Name'] = self.dico_fenes_surface[-1]['name'].split('-')[-1]
                name = self.save_util_value(self.liste_idf_file[i+1],2)
                ''' the '-' caracteres have to be deleted'''
                self.dico_fenes_surface[-1]['name'] = name#self.record_name(name)
                
                ''' when in windows is a contact between two zones, Outside Boundary Condition Object give the name of the windows
                but the probleme is that it not the same name as indicated in Name, to know what surface is in contact with other the name indicated in 'Name' use the same format than in
                'Outside Boundary Condition Object'
                '''
#                 newname = 'janela'+self.liste_idf_file[i+1].split('-')[0][11:]+'Zone'+self.liste_idf_file[i+1].split('-')[2][5:-3]
#                 self.dico_fenes_surface[-1]['name'] = newname
                self.dico_fenes_surface[-1]['Surface Type'] = self.save_util_value(self.liste_idf_file[i+2],3)
                self.dico_fenes_surface[-1]['Construction Name'] = self.save_util_value(self.liste_idf_file[i+3],3)

                self.dico_fenes_surface[-1]['Building Surface Name'] = self.save_util_value(self.liste_idf_file[i+4],4)
                name = self.save_util_value(self.liste_idf_file[i+4],4)
                self.dico_fenes_surface[-1]['Building Surface Name'] = name#self.record_name(name)
                for surface in self.dico_surface:# xrange(len(self.dico_surface)):
                    if surface['name']==name:
                        self.dico_fenes_surface[-1]['Zone Name'] = surface['Zone Name']
                        break
                self.dico_fenes_surface[-1]['Outside Boundary Condition Object'] = self.save_util_value(self.liste_idf_file[i+5],4,False)
                if self.dico_fenes_surface[-1]['Outside Boundary Condition Object']!=', !':
                    new_name = self.save_util_value(self.liste_idf_file[i+5],5)
                    ''' the '-' caracteres have to be deleted'''
                    
                else: 
                    new_name = ''
                self.dico_fenes_surface[-1]['Outside Boundary Condition Object'] = new_name #self.record_name(new_name)
                self.dico_fenes_surface[-1]['View Factor to Ground'] = self.save_util_value(self.liste_idf_file[i+6],5)
                self.dico_fenes_surface[-1]['Shading Control Name'] = self.save_util_value(self.liste_idf_file[i+7],4)
                self.dico_fenes_surface[-1]['Frame and Divider Name'] = self.save_util_value(self.liste_idf_file[i+8],5)
                self.dico_fenes_surface[-1]['Multiplier'] = self.save_util_value(self.liste_idf_file[i+9],2)
                vertex_number = int(self.save_util_value(self.liste_idf_file[i+10],4))
                self.dico_fenes_surface[-1]['vertex'] = []
                j = 0
                while j <vertex_number*3:
                    x = self.save_util_value(self.liste_idf_file[i+11+j],5)
                    y = self.save_util_value(self.liste_idf_file[i+11+j+1],5)
                    z = self.save_util_value(self.liste_idf_file[i+11+j+2],5)
                    j = j+3
#                     print([x,y,z])
                    self.dico_fenes_surface[-1]['vertex'].append([x,y,z])
                ''' the opening level is a number between 0 and 1:
                1: the windows is fully opened, it si represented as hole in CFD simulation
                0: the windows is fully closed, it is represented as a completely opaque wall in CFD simulation
                <1&>0 : the windows is partially opened, physical laws have to be applied to determine the debit throw the windows
                '''
                self.dico_fenes_surface[-1]['opening_level'] = 0
#                 print('the dictionnary of the fenestre is',self.dico_fenes_surface[-1])
    
    def dictionnary_fenestration_surface_domus(self):
        ''' function to build a dictionnary with all proporties of the differents fenestration surfaces in the IDF'''
#         self.dico_fenes_surface = []
        for i in xrange(len(self.liste_idf_file)):
            # print(self.liste_idf_file[i])
            if 'Domus:FenestraIDF,'in self.liste_idf_file[i]:#:'ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED' in self.liste_idf_file[i]:#=='!-   ===========  ALL OBJECTS IN CLASS: BUILDINGSURFACE:DETAILED ===========':
#                 print(self.liste_idf_file[i])
                self.dico_fenes_surface.append({}) 
                self.dico_fenes_surface[-1]['name'] = self.save_util_value(self.liste_idf_file[i+1],4)
                self.dico_fenes_surface[-1]['domus_name'] = self.save_domus_name(self.liste_idf_file[i+1], 4)#self.save_util_value(self.liste_idf_file[i+1],2)

                self.dico_fenes_surface[-1]['Zone Name'] = self.dico_fenes_surface[-1]['domus_name'].split('-')[-1]
                name = self.save_util_value(self.liste_idf_file[i+1],4)
                ''' the '-' caracteres have to be deleted'''
                self.dico_fenes_surface[-1]['name'] = name#self.record_name(name)
                name = name.split('-')
                cfxname = ''
                for n in xrange(len(name)):
                    cfxname+=name[n]
                self.dico_fenes_surface[-1]['name'] = cfxname
                ''' when in windows is a contact between two zones, Outside Boundary Condition Object give the name of the windows
                but the probleme is that it not the same name as indicated in Name, to know what surface is in contact with other the name indicated in 'Name' use the same format than in
                'Outside Boundary Condition Object'
                '''
#                 newname = 'janela'+self.liste_idf_file[i+1].split('-')[0][11:]+'Zone'+self.liste_idf_file[i+1].split('-')[2][5:-3]
#                 self.dico_fenes_surface[-1]['name'] = newname
                self.dico_fenes_surface[-1]['PTF'] = self.save_util_value(self.liste_idf_file[i+10],6)
                self.dico_fenes_surface[-1]['Surface Type'] = self.save_util_value(self.liste_idf_file[i+2],4)
                self.dico_fenes_surface[-1]['Construction Name'] = self.save_util_value(self.liste_idf_file[i+3],5)

                self.dico_fenes_surface[-1]['Building Surface Name'] = self.save_util_value(self.liste_idf_file[i+4],5,False)
                name = self.save_util_value(self.liste_idf_file[i+4],5)
#                 for surface in self.dico_surface:# xrange(len(self.dico_surface)):
#                     if surface['name']==name:
#                         self.dico_fenes_surface[-1]['Zone Name'] = surface['Zone Name']
#                         break
                
                self.dico_fenes_surface[-1]['Building Surface Name'] = name#self.record_name(name)
                self.dico_fenes_surface[-1]['Building Surface Name'] = self.save_util_value(self.liste_idf_file[i+4],5,False)
                self.dico_fenes_surface[-1]['Outside Boundary Condition Object'] = self.save_util_value(self.liste_idf_file[i+5],7,False)
                if self.dico_fenes_surface[-1]['Outside Boundary Condition Object']!=', !':
                    
                    new_name = self.save_util_value(self.liste_idf_file[i+5],7)
                    ''' the '-' caracteres have to be deleted'''
                else: 
                    new_name = ''
#                 self.dico_fenes_surface[-1]['Outside Boundary Condition Object'] = new_name #self.record_name(new_name)
                self.dico_fenes_surface[-1]['View Factor to Ground'] = self.save_util_value(self.liste_idf_file[i+6],7)
                self.dico_fenes_surface[-1]['Shading Control Name'] = self.save_util_value(self.liste_idf_file[i+7],6)
                self.dico_fenes_surface[-1]['Frame and Divider Name'] = self.save_util_value(self.liste_idf_file[i+8],6)
                self.dico_fenes_surface[-1]['Multiplier'] = self.save_util_value(self.liste_idf_file[i+9],2)
                vertex_number = int(self.save_util_value(self.liste_idf_file[i+23],4))
                self.dico_fenes_surface[-1]['vertex'] = []
                j = 0
                while j <vertex_number*3:
                    x = self.save_util_value(self.liste_idf_file[i+24+j+2],3)
                    y = self.save_util_value(self.liste_idf_file[i+24+j],3)
                    z = self.save_util_value(self.liste_idf_file[i+24+j+1],3)
                    j = j+3
#                     print([x,y,z])
                    self.dico_fenes_surface[-1]['vertex'].append([x,y,z])
                ''' the opening level is a number between 0 and 1:
                1: the windows is fully opened, it si represented as hole in CFD simulation
                0: the windows is fully closed, it is represented as a completely opaque wall in CFD simulation
                <1&>0 : the windows is partially opened, physical laws have to be applied to determine the debit throw the windows
                '''
                self.dico_fenes_surface[-1]['opening_level'] = 1
#                 print('the dictionnary of the fenestre is',self.dico_fenes_surface[-1])

    def dictionnary_form__and_sky_view_factors(self,file_name,sky_option = True):
        ''' function to build a view fator matrice from idf file
        only the view facor between outside wall and outsidewindows are taking acount'''
        ''' funcion to read the idf in file_init and wrtie a new file 
        if sky_option== True, the form factor with the sky are in the matrice'''
        self.dict_FF = {}
        idf_init = IDF()
    
        idf_init.parsing(file_name)
        newliste_idf_file = []
        i = 0
        car = idf_init.liste_idf_file[i]
        specific_caractere = '!-   ===========  ALL OBJECTS IN CLASS: DOMUS:FACE:FATORFORMA ===========\n'
        while car!=specific_caractere:        
            #print car
            i+=1
            car = idf_init.liste_idf_file[i]
            
        specific_caractere = '!-   ===========  ALL OBJECTS IN CLASS: DOMUS:FACE:PTF:MODELOSIMULACAO ===========\n'
        indice_face = 0
        while car!=specific_caractere:        
            #print car
            i+=1
            car = idf_init.liste_idf_file[i]
            
            if car=='  Domus:Face:FatorForma,\n':
                
                i+=1
                name = idf_init.liste_idf_file[i][18:-20]
                sum_ff = 0
                if 'sky' not in name:
                    #if ('Zona 1' in name) or ('ext' in name):
                    self.dict_FF[name] = {}
                    self.dict_FF[name]['indice'] = indice_face
                    indice_face+=1
                    self.dict_FF[name]['FF'] = {}
                    ''' SVF, le sky view factor ici represente la part de l'energie sortant de la parois name et qui va dans le ciel'''
                    self.dict_FF[name]['SVF'] = 0
                    
                    i+=1
                    face_number = int(idf_init.liste_idf_file[i].split()[0][:-1])
                    for j in xrange(face_number):
                        i+=1
                        face_name = idf_init.liste_idf_file[i].split(',')[0][4:]
                        i+=1
                        
                        if j== face_number-1:
                            FF = float(idf_init.liste_idf_file[i].split(';')[0][4:])                            
                                
                        else:
                            FF = float(idf_init.liste_idf_file[i].split(',')[0][4:])
                        sum_ff+=FF    
                        if 'sky' not in face_name:
                            self.dict_FF[name]['FF'][face_name] = FF
                                
                        else:
                            self.dict_FF[name]['SVF']+= FF
                    ''' verication of the  form factor sum for each surface'''
                    print'For ',name,' the form factor sum is  : ',sum_ff,' and the SVF is',self.dict_FF[name]['SVF']
            
                    

    def dictionnary_form_factor(self,file_name,sky_option = True):
        ''' function to build a view fator matrice from idf file
        only the view facor between outside wall and outsidewindows are taking acount'''
        ''' funcion to read the idf in file_init and wrtie a new file 
        if sky_option== True, the form factor with the sky are in the matrice'''
        self.dict_FF = {}
        idf_init = IDF()
    
        idf_init.parsing(file_name)
        newliste_idf_file = []
        i = 0
        car = idf_init.liste_idf_file[i]
        specific_caractere = '!-   ===========  ALL OBJECTS IN CLASS: DOMUS:FACE:FATORFORMA ===========\n'
        while car!=specific_caractere:        
            print car
            i+=1
            car = idf_init.liste_idf_file[i]
            
        specific_caractere = '!-   ===========  ALL OBJECTS IN CLASS: DOMUS:FACE:PTF:MODELOSIMULACAO ===========\n'
        indice_face = 0
        while car!=specific_caractere:        
            print car
            i+=1
            car = idf_init.liste_idf_file[i]
            
            if car=='  Domus:Face:FatorForma,\n':
                
                i+=1
                name = idf_init.liste_idf_file[i][18:-20]
                if 'sky' not in name:
                    #if ('Zona 1' in name) or ('ext' in name):
                    self.dict_FF[name] = {}
                    self.dict_FF[name]['indice'] = indice_face
                    indice_face+=1
                    self.dict_FF[name]['FF'] = {}
                    i+=1
                    face_number = int(idf_init.liste_idf_file[i].split()[0][:-1])
                    for j in xrange(face_number):
                        i+=1
                        face_name = idf_init.liste_idf_file[i].split(',')[0][4:]
                        i+=1
                        if 'sky' not in face_name:
                            if j== face_number-1:
                                FF = float(idf_init.liste_idf_file[i].split(';')[0][4:])                            
                                self.dict_FF[name]['FF'][face_name] = FF
                            else:
                                FF = float(idf_init.liste_idf_file[i].split(',')[0][4:])
                                self.dict_FF[name]['FF'][face_name] = FF
                    
                    
    def build_view_factor_matrice_from_dic_domus(self,dict_FF):
            matrice_size = len(dict_FF.keys())
         #   matrice_ff = numpy.zeros((matrice_size,matrice_size))
            print'build_view_factor_matrice_from_dic_domus'
            for surface_name in dict_FF.keys():
                id_surface_name = dict_FF[surface_name]['indice']
                for surface_namebis in dict_FF[surface_name]['FF'].keys():
                    id_surface_namebis = dict_FF[surface_namebis]['indice']
                    matrice_ff[id_surface_name][id_surface_namebis] = dict_FF[surface_name]['FF'][surface_namebis]
                print surface_name
                print matrice_ff[id_surface_name]
                    
            return matrice_ff  
               
    def build_SVF_array(self,dict_FF):   
      #  svf = numpy.zeros(len(dict_FF.keys())) 
        for surface_name in dict_FF.keys():
            id_surface_name = dict_FF[surface_name]['indice']
            svf[id_surface_name] = dict_FF[surface_name]['SVF']
        return svf
        
    def compute_area_surface(self):
        
        for i in xrange(len(self.dico_surface)):
            coord = []
            for j in xrange(len(self.dico_surface[i]['vertex'])):
                coord.append([])

                x = float(self.dico_surface[i]['vertex'][j][0])
                y = float(self.dico_surface[i]['vertex'][j][1])
                z = float(self.dico_surface[i]['vertex'][j][2])
                coord[-1] = [x,y,z]
            polygone = Polygone(coord)
            self.dico_surface[i]['area'] = polygone.S
        
        for i in xrange(len(self.dico_fenes_surface)):
            coord = []
            for j in xrange(len(self.dico_fenes_surface[i]['vertex'])):
                coord.append([])
                
                x = float(self.dico_fenes_surface[i]['vertex'][j][0])
                y = float(self.dico_fenes_surface[i]['vertex'][j][1])
                z = float(self.dico_fenes_surface[i]['vertex'][j][2])
                coord[-1] = [x,y,z]
            polygone = Polygone(coord)
            self.dico_fenes_surface[i]['area'] = polygone.S
            ''' la surface de la fenetre doit etre soustraite de la surface du mur la portant'''
            wall_name = self.dico_fenes_surface[i]['Building Surface Name']
            for j in xrange(len(self.dico_surface)):
                if wall_name==self.dico_surface[j]['domus_name']:
                    self.dico_surface[j]['area'] = self.dico_surface[j]['area'] - self.dico_fenes_surface[i]['area']
                    break
            

        
    def correction_dictionnarry_name(self):
        ''' function to delete the '-' in 'name' '''
        for i in xrange(len(self.dico_surface)):
            self.dico_surface[i]['name'] = self.record_name(self.dico_surface[i]['name'])
        
        for i in xrange(len(self.dico_fenes_surface)):
            self.dico_fenes_surface[i]['name'] = self.record_name(self.dico_fenes_surface[i]['name'])
        
    def dictionnary_zone(self):
        ''' function to build a dictionnary with all proporties of the differents zones in the IDF''' 
        self.zones = {}
        for i in xrange(len(self.dico_surface)):
            zone_name = self.dico_surface[i]['Zone Name']
            
            if zone_name not in self.zones.keys():
                
                self.zones[zone_name] = {}
                ''' creation of a list with id of fenestre for all the zone even if there is no fenestre
                thus it will be more easy for the next of the script
                '''
                self.zones[zone_name]['id_fenestre'] = []
                self.zones[zone_name]['id_wall']=[i]
            else:
                self.zones[zone_name]['id_wall'].append(i)
                
        for i in xrange(len(self.dico_fenes_surface)):
            name_surface_in_contact = self.dico_fenes_surface[i]['Building Surface Name']

            id_surface_in_contact = self.list_id_surfacename.index(name_surface_in_contact)
            self.dico_fenes_surface[i]['Zone Name'] = self.dico_surface[id_surface_in_contact]['Zone Name']
            zone_name = self.dico_fenes_surface[i]['Zone Name']
#             if 'id_fenestre' not in self.zones[zone_name]:
#                 self.zones[zone_name]['id_fenestre']=[i]
#             else:
#             print 'zone name = ',zone_name
            self.zones[zone_name]['id_fenestre'].append(i)
            ''' if it is a fenestration that is a contact between 2 zone we have to looking for the name of this second zone'''
            if self.dico_fenes_surface[i]['Outside Boundary Condition Object']!='':
                zone_name2 = self.dico_fenes_surface[i]['Outside Boundary Condition Object'].split('-')[-1]
                self.zones[zone_name2]['id_fenestre'].append(i)
                


    def select_zones_and_surface_depanding_coupling_method(self,option_outdoor = True):
        ''' function to create liste 
        self.id_surface
        self.if_fenestre
        '''
        
        self.id_walls_int = []
        self.id_walls_ext = []
        self.id_fenestres_int = []
        self.id_fenestres_ext = []
        
        self.id_walls = []
        self.id_fenestres = []
        
        ''' for all wall and fenestre we check if we need inside surface temperature and the outside surface temperature for the CFD simulation'''
        
        for id_wall in xrange(len(self.dico_surface)):
#             if self.dico_surface[id_wall]['domus_name'] not in self.id_hole_wall:
            ''' 1st check : the inside surface temperature is needed?
            we have to check that the zone  of this wall is taking into acount in CFD simulation'''
            name_zone = self.dico_surface[id_wall]['Zone Name']
#             id_zone = int(name_zone[4:])
            if name_zone in self.id_zones:
                self.id_walls_int.append(id_wall)           
                ''' 2nd check : the otherside surface temperature is needed?'''
                if self.dico_surface[id_wall]['Outside Boundary Condition']=='Surface':    
                    ''' we have to check that the zone at the other side of this wall is taking into acount in CFD simulation'''
                    name_surface_in_contact = self.dico_surface[id_wall]['Outside Boundary Condition Object']
                    id_zone_in_contact = name_surface_in_contact.split('-')[-1]
#                     newname = ''
#                     for word in name_surface_in_contact.split():
#                         newname+=word
#                     name_surface_in_contact = newname
#                     id_zone_in_contact = name_surface_in_contact.split('-')[-1]#int(name_surface_in_contact.split('-')[-1][4:])
                    if id_zone_in_contact in self.id_zones:
                        self.id_walls_ext.append(id_wall)
    #                     if name_surface_in_contact in self.list_id_surfacename:
    #                         id_surface_in_contact = self.list_id_surfacename.index(name_surface_in_contact)
    #                         name_zone_in_contact = self.dico_surface[id_surface_in_contact]['Zone Name']
    #                         id_zone_in_contact = int(name_zone_in_contact[4:])
    #                         if id_zone_in_contact in self.id_zones:
    #                             self.id_walls_ext.append(id_wall)
    # 
    #                     else:
    #                         print 'il y a un probleme avec ',self.dico_surface[id_wall]
                        
                    ''' 3rd check : the outside surface temperature is needed?'''
            if self.dico_surface[id_wall]['Outside Boundary Condition']=='Outdoors':
                if self.option_outdoor:
                    self.id_walls_ext.append(id_wall)
                    
            
        self.id_walls = self.id_walls_int[:]
        for i in (self.id_walls_ext):
            if i not in self.id_walls:
                self.id_walls.append(i)
                
        for id_fen in xrange(len(self.dico_fenes_surface)):
            # if self.dico_fenes_surface[id_fen]['Building Surface Name'] not in self.id_hole_wall:
            ''' 1st check : the inside surface temperature is needed?
            we have to check that the zone  of this fenestre is taking into acount in CFD simulation'''
            name_zone = self.dico_fenes_surface[id_fen]['Zone Name']
#             id_zone = int(name_zone[4:])
            if name_zone in self.id_zones:
                self.id_fenestres_int.append(id_fen)           
                ''' 2nd check : the otherside surface temperature is needed?'''
            if self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object']!='':#!=',!':    
                ''' we have to check that the zone at the other side of this wall is taking into acount in CFD simulation'''
                name_surface_in_contact = self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object']
    #                     num_fen_contact = self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object'].split('-')[0][6:]
                id_zone_in_contact = self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object'].split('-')[-1]#int(self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object'].split('-')[-1][4:])
                if id_zone_in_contact in self.id_zones:
                    self.id_fenestres_ext.append(id_fen)
    #                     if name_surface_in_contact in self.list_id_fenestrename:
    #                         id_surface_in_contact = self.list_id_fenestrename.index(name_surface_in_contact)
    #                         name_zone_in_contact = self.dico_fenes_surface[id_surface_in_contact]['Zone Name']
    #                         id_zone_in_contact = int(name_zone_in_contact[4:])
    #                         if id_zone_in_contact in self.id_zones:
    #                             self.id_fenestres_ext.append(id_fen)
# 
#                     else:
#                         print 'il y a un probleme avec ',self.dico_fenes_surface[id_fen]
                        
                    ''' 3rd check : the outside surface temperature is needed?'''
            if self.dico_fenes_surface[id_fen]['Outside Boundary Condition Object']=='':#!=',!':',!':
                if self.option_outdoor:
                    self.id_fenestres_ext.append(id_fen)
                       
            
        self.id_fenestres = self.id_fenestres_int[:]
        for i in (self.id_fenestres_ext):
            if i not in self.id_fenestres:
                self.id_fenestres.append(i)
                
        ''' the lists are sorted by croissant order so that surface would be defined in gmsh in the same order than in IDF'''
        
        self.id_walls.sort()
        self.id_fenestres.sort()
        
#         for zone_name in self.zones.keys(): #xrange(len(self.zones)):
#             id_zone = int(zone_name[4:])
#             if id_zone in self.id_zones:
#                 for id_wall in self.zones[zone_name]['id_wall']:
#                     self.id_walls_int.append(id_wall)
#                     self.id_walls_ext.append(id_wall)
#                     self.id_walls.append(id_wall)
#                 
#                 for id_fenestre in self.zones[zone_name]['id_fenestre']:
#                     self.id_fenestres_int.append(id_fenestre)
#                     self.id_fenestres_ext.append(id_fenestre)
#                     self.id_fenestres.append(id_fenestre)
#             elif self.option_outdoor:
#                 for id_wall in self.zones[zone_name]['id_wall']:
#                     if self.dico_surface[id_wall]['Outside Boundary Condition']=='Outdoors':
#                         self.id_walls_ext.append(id_wall)
#                         self.id_walls.append(id_wall)
#                 for id_fenestre in self.zones[zone_name]['id_fenestre']:
#                     if self.dico_fenes_surface[id_fenestre]['Outside Boundary Condition Object']==',!':
#                         self.id_fenestres_ext.append(id_fenestre)
#                         self.id_fenestres.append(id_fenestre)
#         ''' the lists are sorted by croissant order so that surface would be defined in gmsh in the same order than in IDF'''
#         self.id_walls_int.sort()
#         self.id_walls_ext.sort()
#         self.id_fenestres_int.sort()
#         self.id_fenestres_ext.sort()
#         
#         self.id_walls.sort()
#         self.id_fenestres.sort()
#                                     
#         if option_outdoor:
#             ''' if it is a simulation indoor/outdoor the zone numver 1 is not taking acount'''
#             if self.zone1_name in  self.zones:
#                 del self.zones[self.zone1_name]
        
            
    def save_util_value(self,value,n_delet,glue = True):
        '''
        function to read value contained in list by deleting some element,
        ex: value = ['piso', '(solo)', '5-Zona', '1,', '!-', 'Name']
        '!-'&'Name' have to be deleted with n_delet = 1 we obtain
        'piso', '(solo)', '5-Zona'& '1,' have to be unified and the last ',' have to be deleted
        if glue is true the different element are glued else there space between different element
        
        In the idf file
        n_delet is an integer
        '''
        ''' list of values is splited'''
        valuesplited = value.split()
#         print(valuesplited)
        ''' n_delet last elements are deleted of this list'''
        valuesplited = valuesplited[:-n_delet]
#         print(valuesplited)
        ''' all the other element are glued together'''
        sumelement=valuesplited[0]
#         print(sumelement)
        for i in range(1,len(valuesplited)):
            if glue:
                sumelement+=valuesplited[i]
            else:
                sumelement+=' '+valuesplited[i]
#             print(sumelement)
        ''' the comma: the lqst string of this new element is not taking account'''
        element_final = sumelement[:-1]
#         print(element_final)
        return element_final

    def save_domus_name(self,value,n_delet = 2):
        '''
        function to read surface name and write it as in domus,
        ex: value = ['piso', '(solo)', '5-Zona', '1,', '!-', 'Name']
        '!-'&'Name' have to be deleted with n_delet = 1 we obtain
        'piso', '(solo)', '5-Zona'& '1,' have to be unified and the last ',' have to be deleted
        somes spaces are added to give at the final 
        'piso (solo) 5-Zona 1'
        
        In the idf file
        n_delet is an integer
        '''
        ''' list of values is splited'''
        valuesplited = value.split()
#         print(valuesplited)
        ''' n_delet last elements are deleted of this list'''
        valuesplited = valuesplited[:-n_delet]
#         print(valuesplited)
        ''' all the other element are glued together'''
        sumelement=valuesplited[0]
#         print(sumelement)
        for i in xrange(1,len(valuesplited)):
            sumelement+=' '+valuesplited[i]
#             print(sumelement)
        ''' the comma: the lqst string of this new element is not taking account'''
        element_final = sumelement[:-1]
#         print(element_final)
        return element_final  
    def listing_point(self):
        ''' function to list all the point existing in the project
        a point is a list with the different coordinate: point[0] = x, point[1] = y,point[2] = z
        the function:
        1. create a liste: self.list_point with all the point of the project 
        2.add in self.dico_surface['id_point'] and self.dico_fenes_surface['id_point'] the indice of the point
        NB: when a same point exist in two different surface ( intersection), it is the same indice in self.dico_surface['id_point'] or self.dico_fenes_surface['id_point']
        
        when a point already it'''
        self.list_point = []
        self.listing_point_dico(self.dico_surface,self.id_walls)
        self.listing_point_dico(self.dico_fenes_surface,self.id_fenestres)
                    
    def listing_point_dico(self,dico_surface, id_surface):
        ''' subfunction of listing_point to realise this on any type of dictionnary dico_surface'''
        for i in id_surface:# xrange(len(dico_surface)):
#             if i==35:
#                 print'oups'
            dico_surface[i]['id_point'] = []
            for point in dico_surface[i]['vertex']:
                if point not in self.list_point:
                    self.list_point.append(point)
                    id_point=len(self.list_point)-1

                else:
                    id_point=self.list_point.index(point)
                dico_surface[i]['id_point'].append(id_point+self.parametre_first_id)
                

                
            
    def listing_line(self):
        ''''a line is composed of two points line[0] = indice of the point n°1, liste[1] = indice of the point n°2,'''
        self.list_line = []
        ''' self.list_line_limit will contain the indices of lines at the limit of the domaine of the domus geometry
        this id_line are need to build the line_loop of the sol_atmosphere'''
        self.list_line_limit = []
        
        self.listing_line_dico(self.dico_surface,self.id_walls,option_line_limite = True)
        self.listing_line_dico(self.dico_fenes_surface,self.id_fenestres,option_line_limite = False)
#         print('les lignes formant la limite sont',self.list_line_limit)
        ''' good order of the point are checked'''
#         list_limite_bis = [self.list_line_limit[0]]
#         while len(list_limite_bis)<len(self.list_line_limit):
#             idline1 = list_limite_bis[-1]-self.parametre_first_id
#             idpoint2line1 = self.list_line[idline1][1]
#             
#             
#         for i in xrange(len(self.list_line_limit)-1):
#             idline1 = self.list_line_limit[i]-self.parametre_first_id
#             
#             idpoint2line1 = self.list_line[idline1][1]
#             for j in xrange(len(i+1,self.list_line_limit)):
#                 idline2 = self.list_line_limit[i+j]-self.parametre_first_id            
#                 idpoint1line2 = self.list_line[idline1][0]
#                 idpoint2line2 = self.list_line[idline1][1]
#                 if idpoint2line1==idpoint1line2:
#                     list_limite_bis.append(self.list_line_limit[i+j])
#                     break
#                 elif idpoint2line1==idpoint2line2:
#                     list_limite_bis.append(-self.list_line_limit[i+j])
#                     break
#                 
                    
    def listing_line_dico(self,dico_surface,id_surface,option_line_limite = True):
        ''' subfunction of listing_point to realise this on any type of dictionnary dico_surface'''
        
        for i in id_surface:# xrange(len(dico_surface)):
#             print' dico ',dico_surface[i]
            
            dico_surface[i]['id_line'] = []
            for j in xrange(len(dico_surface[i]['id_point'])-1):
                self.define_indice_line(dico_surface[i],j,j+1,option_line_limite )
            self.define_indice_line(dico_surface[i],len(dico_surface[i]['id_point'])-1,0,option_line_limite)
            
    def define_indice_line(self,dico_surface,n,m,option_line_limite = True):
        line = [dico_surface['id_point'][n],dico_surface['id_point'][m]]
        linebis = [dico_surface['id_point'][m],dico_surface['id_point'][n]]
#         print 'line: ',line,'linebis:',linebis
        if (line not in self.list_line)&(linebis not in self.list_line):
            self.list_line.append(line)
            id_line = len(self.list_line)-1+self.parametre_first_id
            if option_line_limite:
                ''' all the id_line are added in self.list_line_limit if they are used an other time that is mean they are not line that define limit of the domus geometry
                and they will be deleted in *1 or *2'''
                self.list_line_limit.append(id_line)
                
        elif line in self.list_line:
            id_line = self.list_line.index(line)+self.parametre_first_id
            '''*1 : if this line already exist in self.list_line_limit that is mean it is not a line that define limit of the domus geometry, 
            thus it is delet of self.list_line_limit'''
            if id_line in self.list_line_limit:
                id = self.list_line_limit.index(id_line)
                if option_line_limite:
                    del self.list_line_limit[id]
        elif linebis in self.list_line:
            id_line = -(self.list_line.index(linebis)+self.parametre_first_id)
            '''*2 : if this line already exist in self.list_line_limit that is mean it is not a line that define limit of the domus geometry, 
            thus it is delet of self.list_line_limit'''
            if -id_line in self.list_line_limit:
                id = self.list_line_limit.index(-id_line)
                if option_line_limite:
                    del self.list_line_limit[id]
        dico_surface['id_line'].append(id_line)

    def listing_line_loop(self):  
        self.list_loop = []
        self.list_surface = []
        self.listing_line_loop_dico(self.dico_surface,self.id_walls)
        self.listing_line_loop_dico(self.dico_fenes_surface,self.id_fenestres)
        
    def listing_line_loop_dico(self, dico,id_surface):
        for i in id_surface:#xrange(len(dico)):
            if dico[i]['id_line'] not in self.list_loop:
                self.list_loop.append(dico[i]['id_line'])
                self.list_surface.append([len(self.list_loop)-1+self.parametre_first_id])
                dico[i]['id_line_loop'] = [len(self.list_loop)-1+self.parametre_first_id]
            else:
                id_line_loop = self.list_loop.index(dico[i]['id_line'])+self.parametre_first_id 
                dico[i]['id_line_loop'] = [id_line_loop]
                
    def listing_surface(self):  

        self.list_surface = []
        self.listing_surface_dico(self.dico_surface,self.id_walls)
        self.listing_surface_dico(self.dico_fenes_surface,self.id_fenestres)
        
    def listing_surface_dico(self, dico,id_surface):
        
        for i in id_surface:#xrange(len(dico)):
            if dico[i]['id_line_loop'] not in  self.list_surface:
                self.list_surface.append(dico[i]['id_line_loop'])
                dico[i]['id_surface'] = len(self.list_surface)-1+self.parametre_first_id
            else:
                id_surface = self.list_surface.index(dico[i]['id_line_loop'])+self.parametre_first_id 
                dico[i]['id_surface'] = id_surface            
        

                

        

    def listing_surface_name(self):   
        ''' function to create a list that contain the name of each surface
        and a list with the correspondance between domus name and ansys name
        thus self.list_id_surfacename '''
        self.list_id_surfacename = []

        for i in xrange(len(self.dico_surface)):
            self.list_id_surfacename.append(self.dico_surface[i]['domus_name'])

        ''' function to create a list that contain the name of each fenestre surface
        thus self.list_id_fenestrename '''
        self.list_id_fenestrename = []
        for i in xrange(len(self.dico_fenes_surface)):
            self.list_id_fenestrename.append(self.dico_fenes_surface[i]['domus_name'])

            
    def listing_correspondance_name(self):   
        ''' function to create a list 
         with the correspondance between domus name and ansys name
        '''

        self.name_connection = {}
        for i in xrange(len(self.dico_surface)):
            self.list_id_surfacename.append(self.dico_surface[i]['domus_name'])
            self.name_connection[self.dico_surface[i]['name']] = self.dico_surface[i]['domus_name']
            self.name_connection[self.dico_surface[i]['name']+'ext'] = self.dico_surface[i]['domus_name']
        ''' function to create a list that contain the name of each fenestre surface
        thus self.list_id_fenestrename '''
        self.list_id_fenestrename = []
        for i in xrange(len(self.dico_fenes_surface)):
            self.list_id_fenestrename.append(self.dico_fenes_surface[i]['domus_name'])
            self.name_connection[self.dico_fenes_surface[i]['name']] = self.dico_fenes_surface[i]['domus_name']
            self.name_connection[self.dico_fenes_surface[i]['name']+'ext'] = self.dico_fenes_surface[i]['domus_name']
            
    def checking_surface_contact(self):
        ''' function to check surfaces in contact with an other one
        if it is the case,  the same dico_surface['id_line'] is attributed for the two surface
        '''
        
        list_id_surface = self.id_walls[:]#range(len(self.dico_surface))

        for i in list_id_surface:
#             print 'surface name = ',self.dico_surface[i]['name']
            if self.dico_surface[i]['Outside Boundary Condition']=='Surface':
                name_surface_in_contact = self.dico_surface[i]['Outside Boundary Condition Object']

                if name_surface_in_contact in self.list_id_surfacename:
                    id_surface_in_contact = self.list_id_surfacename.index(name_surface_in_contact)
#                     print'surface in contacte',self.dico_surface[id_surface_in_contact]['name']
                    self.dico_surface[id_surface_in_contact]['vertex'] = self.dico_surface[i]['vertex']
#                     self.dico_surface[id_surface_in_contact]['id_line'] = self.dico_surface[i]['id_line']
#                     self.dico_surface[id_surface_in_contact]['id_point'] = self.dico_surface[i]['id_point']
                    ''' this id_surface is remove from the list to not to be treated again'''
                    if id_surface_in_contact in list_id_surface:
                        list_id_surface.remove(id_surface_in_contact)
                        
#                     del list_id_surface[id_surface_in_contact]

        list_id_surface = self.id_fenestres[:]#range(len(self.dico_surface))

        for i in list_id_surface:
#             print 'surface name = ',self.dico_fenes_surface[i]['name']
            if self.dico_fenes_surface[i]['Outside Boundary Condition Object']!='':#,!':
                name_surface_in_contact = self.dico_fenes_surface[i]['Outside Boundary Condition Object']

                if name_surface_in_contact in self.list_id_fenestrename:
                    id_surface_in_contact = self.list_id_fenestrename.index(name_surface_in_contact)
#                     print'surface in contacte',self.dico_fenes_surface[id_surface_in_contact]['name']
                    self.dico_fenes_surface[id_surface_in_contact]['vertex'] = self.dico_fenes_surface[i]['vertex']
#                     self.dico_fenes_surface[id_surface_in_contact]['id_line'] = self.dico_fenes_surface[i]['id_line']
#                     self.dico_fenes_surface[id_surface_in_contact]['id_point'] = self.dico_fenes_surface[i]['id_point']
                    ''' this id_surface is remove from the list to not to be treated again'''
                    if id_surface_in_contact in list_id_surface:
                        list_id_surface.remove(id_surface_in_contact)
                        
    def checking_surface_contact_new(self):
        ''' function to check surfaces in contact with an other one
        if it is the case,  the same dico_surface['id_line'] is attributed for the two surface
        '''
        
        list_id_surface = range(len(self.dico_surface))

        new_dico = []
        for i in list_id_surface:
            new_dico.append(self.dico_surface[i])
#             print 'surface name = ',self.dico_surface[i]['name']
            if self.dico_surface[i]['Outside Boundary Condition']=='Surface':
                name_surface_in_contact = self.dico_surface[i]['Outside Boundary Condition Object']
                
                if name_surface_in_contact in self.list_id_surfacename:
                    id_surface_in_contact = self.list_id_surfacename.index(name_surface_in_contact)
                    
                    if id_surface_in_contact in list_id_surface:
                        list_id_surface.remove(id_surface_in_contact)
    
        self.dico_surface = new_dico
            
            
        list_id_surface = range(len(self.dico_fenes_surface))
        new_dico = []
        for i in list_id_surface:
            new_dico.append(self.dico_fenes_surface[i])
#             print 'surface name = ',self.dico_fenes_surface[i]['name']
            if self.dico_fenes_surface[i]['Outside Boundary Condition Object']!=',!':
                name_surface_in_contact = self.dico_fenes_surface[i]['Outside Boundary Condition Object']
                
                if name_surface_in_contact in self.list_id_fenestrename:
                    id_surface_in_contact = self.list_id_fenestrename.index(name_surface_in_contact)
                    

                    ''' this id_surface is remove from the list to not to be treated again'''
                    if id_surface_in_contact in list_id_surface:
                        list_id_surface.remove(id_surface_in_contact)
                        
        self.dico_fenes_surface = new_dico
                        


                

            
    def listing_surface_groupe_physic(self):
        ''' function to create physical groupe of surfaces'''
        self.dico_surf_gr_phy = {}
        self.listing_surface_groupe_physic_dico(self.dico_surface,self.id_walls)
#             if self.windowsoption:
        self.listing_surface_groupe_physic_fenestre(self.dico_fenes_surface,self.id_fenestres)
        
    def listing_surface_groupe_physic_dico(self, dico,id_dico):
        list_id_surface = []
        for i in id_dico :#xrange(len(dico)):
            gr_phys_name = dico[i]['name']
            if dico[i]['id_surface'] not in list_id_surface:
                if dico[i]['domus_name'] not in self.id_hole_wall:
                    self.dico_surf_gr_phy[gr_phys_name] = {}
                    self.dico_surf_gr_phy[gr_phys_name]['id_surface'] = [dico[i]['id_surface']]
                    self.dico_surf_gr_phy[gr_phys_name]['number'] = i+self.parametre_first_id
                    list_id_surface.append(dico[i]['id_surface'])
                    self.dico_surf_gr_phy[gr_phys_name]['type'] = 'BC'
    #                 if dico[i]['domus_name'] in self.id_hole_wall:
    #                     self.dico_surf_gr_phy[gr_phys_name]['type'] = 'INTERFACE'
                    if i not in self.id_walls_int:
                        self.dico_surf_gr_phy[gr_phys_name]['side'] = 'out'
                    else:
                        self.dico_surf_gr_phy[gr_phys_name]['side'] = 'in'
    def listing_surface_groupe_physic_fenestre(self, dico,id_dico):
        list_id_surface = []
        for i in id_dico :#xrange(len(dico)):
            ''' the opened windows are not taking acount to simulate a hole'''
#             if dico[i]['opening_level']!=1:
            gr_phys_name = dico[i]['name']
            if dico[i]['id_surface'] not in list_id_surface:
                self.dico_surf_gr_phy[gr_phys_name] = {}
                self.dico_surf_gr_phy[gr_phys_name]['id_surface'] = [dico[i]['id_surface']]
                self.dico_surf_gr_phy[gr_phys_name]['number'] = i+self.parametre_first_id
                if dico[i]['opening_level']!=1:
                    self.dico_surf_gr_phy[gr_phys_name]['type'] = 'BC'
                else:
                    self.dico_surf_gr_phy[gr_phys_name]['type'] = 'INTERFACE'
                list_id_surface.append(dico[i]['id_surface'])
            if gr_phys_name in self.dico_surf_gr_phy.keys():
                if i not in self.id_fenestres_int:
                    self.dico_surf_gr_phy[gr_phys_name]['side'] = 'out'
                else:
                    self.dico_surf_gr_phy[gr_phys_name]['side'] = 'in'
            
            
    def listing_volume_zone_indoor(self):
        for zone in self.zones.keys():
#             id_zone = int(zone[4:])
            if zone in self.id_zones:#if id_zone in self.id_zones:
                self.zones[zone]['id_surface_loop'] = []
            
                for id_wall in self.zones[zone]['id_wall']:
                    id_surface = self.dico_surface[id_wall]['id_surface']
                    self.zones[zone]['id_surface_loop'].append(id_surface)
                 
                if 'id_fenestre' in  self.zones[zone].keys():
                    for id_fenestre in self.zones[zone]['id_fenestre']:
                        id_surface = self.dico_fenes_surface[id_fenestre]['id_surface']
                        self.zones[zone]['id_surface_loop'].append(id_surface)
                    
                    
                self.list_surface_loop.append(self.zones[zone]['id_surface_loop'])
                self.list_volume.append([len(self.list_surface_loop)-1+self.parametre_first_id])
                self.dico_vol_gr_phy[zone] = [len(self.list_surface_loop)-1+self.parametre_first_id]
            
        

            

    def define_surface_contact(self):
        ''' function to put the same point to the surface in contacte'''
        for i in xrange(len(self.dico_surface)):
            ''' we check the surface is in contact with other surface'''
            if self.dico_surface[id_surface_in_contact]['Outside Boundary Condition']=='Surface':
                name_surface_in_contact = self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object']
                new_name = ''
                for word in name_surface_in_contact.split():
                    new_name+=word
                name = ''
                for word in new_name.split('-'):
                    name+=word
                id_surface_in_contact = self.list_id_surfacename.index(name)
                self.dico_surface[id_surface_in_contact]['id_line_loop']
        for i in self.id_fenestres:# xrange(len(self.dico_fenes_surface)):
#             print 'ok'
            name_surface_in_contact = self.dico_fenes_surface[i]['Building Surface Name']
            new_name = ''
            for word in name_surface_in_contact.split():
                new_name+=word
            name = ''
            for word in new_name.split('-'):
                name+=word
            id_surface_in_contact = self.list_id_surfacename.index(name)
            ''' the loop of the windows is added in the loop list of the wall'''
            if 'id_line_loop' in self.dico_surface[id_surface_in_contact].keys():
                if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contact]['id_line_loop']:
                    self.dico_surface[id_surface_in_contact]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])
                    ''' In the case of it is a windows in contact with 2 zones,'''
                    if self.dico_surface[id_surface_in_contact]['Outside Boundary Condition']=='Surface':
                        '''the same thing have to be done with the surface in contact: the wall,indexe in self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object']'''
                        name_surface_in_contact = self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object']
                        new_name = ''
                        for word in name_surface_in_contact.split():
                            new_name+=word
                        name = ''
                        for word in new_name.split('-'):
                            name+=word
                        id_surface_in_contact2 = self.list_id_surfacename.index(name)
                        if 'id_line_loop' in self.dico_surface[id_surface_in_contact2].keys():
                            if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contact2]['id_line_loop']:
                                self.dico_surface[id_surface_in_contact2]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])
                        
            ''' In the case of it is a windows in contact with 2 zones,
            the same thing have to be done with the surface in contact'''
            if self.dico_surface[id_surface_in_contact]['Outside Boundary Condition']=='Surface':
                name = ''
                for word in self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object'].split():
                    name+=word
                name_surface_in_contactbis = name
                name = ''
                for word in new_name.split('-'):
                    name+=word
                name_surface_in_contactbis = name
                if name_surface_in_contactbis in self.list_id_surfacename:
                    id_surface_in_contactbis = self.list_id_surfacename.index(name_surface_in_contactbis)
#                     print'surface in contacte',self.dico_surface[id_surface_in_contact]['name']
                    if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contactbis]['id_line_loop']:
                        self.dico_surface[id_surface_in_contactbis]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])
                  
    def define_lineloop_windows_in_wall(self):
        ''' function to define the geometry of the window'''
        for i in self.id_fenestres:# xrange(len(self.dico_fenes_surface)):
            #print 'self.id_fenestres',i
            name_surface_in_contact = self.dico_fenes_surface[i]['Building Surface Name']

            id_surface_in_contact = self.list_id_surfacename.index(name_surface_in_contact)
            ''' the loop of the windows is added in the loop list of the wall'''
            if 'id_line_loop' in self.dico_surface[id_surface_in_contact].keys():
                if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contact]['id_line_loop']:
                    self.dico_surface[id_surface_in_contact]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])
                    ''' In the case of it is a windows in contact with 2 zones,'''
                    if self.dico_surface[id_surface_in_contact]['Outside Boundary Condition']=='Surface':
                        '''the same thing have to be done with the surface in contact: the wall,indexe in self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object']'''
                        name_surface_in_contact = self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object']
                        new_name = ''
                        for word in name_surface_in_contact.split():
                            new_name+=word
                        name = ''
                        for word in new_name.split('-'):
                            name+=word
                        id_surface_in_contact2 = self.list_id_surfacename.index(name)
                        if 'id_line_loop' in self.dico_surface[id_surface_in_contact2].keys():
                            if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contact2]['id_line_loop']:
                                self.dico_surface[id_surface_in_contact2]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])
                        
            ''' In the case of it is a windows in contact with 2 zones,
            the same thing have to be done with the surface in contact'''
            '''            if self.dico_surface[id_surface_in_contact]['Outside Boundary Condition']=='Surface':
                name = ''
                for word in self.dico_surface[id_surface_in_contact]['Outside Boundary Condition Object'].split():
                    name+=word
                name_surface_in_contactbis = name
                name = ''
                for word in new_name.split('-'):
                    name+=word
                name_surface_in_contactbis = name
                if name_surface_in_contactbis in self.list_id_surfacename:
                    id_surface_in_contactbis = self.list_id_surfacename.index(name_surface_in_contactbis)
                    print'surface in contacte',self.dico_surface[id_surface_in_contact]['name']
                    if self.dico_fenes_surface[i]['id_line_loop'][0] not in self.dico_surface[id_surface_in_contactbis]['id_line_loop']:
                        self.dico_surface[id_surface_in_contactbis]['id_line_loop'].append(self.dico_fenes_surface[i]['id_line_loop'][0])'''
                
    
    def apply_ground_condition(self):
        ''' function to apply ground condition for floor and wall of the zone1 '''
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['Zone Name']=='Zona 1':
                if (self.dico_surface[i]['Surface Type']=='WALL')or  (self.dico_surface[i]['Surface Type']=='FLOOR') :
                    self.dico_surface[i]['Outside Boundary Condition']='Ground'
            
    def select_surface_contact_outdoor(self):
        ''' function to del all the surface that are not in contact with the outdoor'''
        new_list = []
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['Outside Boundary Condition']=='Outdoors':
                new_list.append(self.dico_surface[i]) 
        self.dico_surface = new_list
        
    def select_surface_contact_outdoor_zone1(self):
        ''' function to del all the surface that are not in contact with the outdoor in the zone1'''
        new_list = []
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['Zone Name']==self.zone1_name:
                if self.dico_surface[i]['Outside Boundary Condition']=='Outdoors':
                    new_list.append(self.dico_surface[i]) 
            else:
                new_list.append(self.dico_surface[i]) 
        self.dico_surface = new_list
        
    def close_windows_from_coupling_method(self):
        ''' function to :
        #close all the windows when the zone is not simulated in the CFD and the outdoor too
        #fully open windows when the zone is simulated in the CFD and the outdoor too
        '''
        for zone in self.zones.keys():
#             id_zone = int(zone[4:])
            if zone in self.id_zones:#if id_zone in self.id_zones:
                for id_f in self.zones[zone]['id_fenestre']:
                    self.dico_fenes_surface[id_f]['opening_level']=1
            else:
                for id_f in self.zones[zone]['id_fenestre']:
                    self.dico_fenes_surface[id_f]['opening_level']=0
#             for id_f in self.zones[zone]['id_fenestre']:
#                 self.dico_fenes_surface[id_f]['opening_level']=0
            
                
                
        
        
    def select_surface_contact_outdoor(self):
        ''' function to del all the surface that are not in contact with the outdoor '''
        new_list = []
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['Zone Name']==self.zone1_name:
                if self.dico_surface[i]['Outside Boundary Condition']=='Outdoors':
                    new_list.append(self.dico_surface[i]) 
            else:
                new_list.append(self.dico_surface[i]) 
        self.dico_surface = new_list
        
    def create_list_surface_interface_init(self):
        ''' function to create a list with the name of the physical surface that correspond to surface with two boundary each side: outdoor and indoor condition
        this list will be use to write the plugin crack for gmsh'''
        self.list_intersurface = []
        list_id_surface = []
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['id_surface'] not in list_id_surface:
                list_id_surface.append(self.dico_surface[i]['id_surface'])
                ''' all the walls in contact with zone1 are no selected'''
                if self.dico_surface[i]['Zone Name']!=self.zone1_name:
                    if self.dico_surface[i]['Outside Boundary Condition Object'][-5:]!=self.zone1_name:
                        self.list_intersurface.append(self.dico_surface[i]['name'])
        if self.windowsoption:
            for i in xrange(len(self.dico_fenes_surface)):
                if self.dico_surface[i]['id_surface'] not in list_id_surface:
                    list_id_surface.append(self.dico_surface[i]['id_surface'])
                    ''' all the walls in contact with zone1 are no selected'''
                    if self.dico_fenes_surface[i]['Zone Name']!=self.zone1_name:
    
                        self.list_intersurface.append(self.dico_fenes_surface[i]['name'])
#             print'okbaba'

    def create_list_surface_interface(self):
        ''' function to create a list with the name of the physical surface that correspond to surface with two boundary each side: outdoor and indoor condition
        this list will be use to write the plugin crack for gmsh'''
        self.list_intersurface = []
        list_id_surface = []
        for i in xrange(len(self.dico_surface)):
#             print 'i=',i,self.dico_surface[i]
            if self.dico_surface[i]['domus_name'] not in self.id_hole_wall: 
                if (i in self.id_walls_ext) & (i in self.id_walls_int):
                    if self.dico_surface[i]['id_surface'] not in list_id_surface:
                        list_id_surface.append(self.dico_surface[i]['id_surface'])
                        ''' all the walls in contact with zone1 are no selected'''
                        if self.dico_surface[i]['Zone Name']!=self.zone1_name:
                            if self.dico_surface[i]['Outside Boundary Condition Object'][-6:]!=self.zone1_name:
                                self.list_intersurface.append(self.dico_surface[i]['name'])
        
        for i in xrange(len(self.dico_fenes_surface)):
            if (i in self.id_fenestres_ext) & (i in self.id_fenestres_int):
#                 print self.dico_fenes_surface[i]

                if self.dico_fenes_surface[i]['id_surface'] not in list_id_surface:
                    list_id_surface.append(self.dico_fenes_surface[i]['id_surface'])
                    ''' all the fenestres in contact with zone1 are no selected'''
                    if self.dico_fenes_surface[i]['Zone Name']!=self.zone1_name:
#                         if self.dico_fenes_surface[i]['opening_level']!=1:
    
                        self.list_intersurface.append(self.dico_fenes_surface[i]['name'])
#         print'okbaba'   
        

        
    def create_canope(self):#,self.H=150,D=50):#self.H=1,D=0.1):#:
        ''' surface corresponding to walls and fenestration are added to the list_surface_loop corresponding to the canopy'''
        
        self.list_surface_loop_canopy = []
        for i in xrange(len(self.dico_surface)):
            if self.dico_surface[i]['Outside Boundary Condition']=='Outdoors':
                self.list_surface_loop_canopy.append(self.dico_surface[i]['id_surface'])
        for i in xrange(len(self.dico_fenes_surface)):
            if self.dico_fenes_surface[i]['Outside Boundary Condition Object']=='':#',!':
                self.list_surface_loop_canopy.append(self.dico_fenes_surface[i]['id_surface'])
        
        self.canopy = Canopy()
        self.canopy.cl = self.meshsize
        self.canopy.define_limite(self.list_point)
        self.canopy.compute_mesh_size()

        number_of_point = len(self.list_point)
        for i in xrange(len(self.canopy.points_limit)):
            for j in xrange(len(self.canopy.points_limit[i])):
                self.canopy.points_limit[i][j]=str(self.canopy.points_limit[i][j])
            self.list_point.append(self.canopy.points_limit[i])
        
        
        for j in xrange(0,2):
            for i in xrange(3):
                self.list_line.append([number_of_point+self.parametre_first_id+i+j*4,number_of_point+self.parametre_first_id+i+1+j*4])
            self.list_line.append([number_of_point+self.parametre_first_id+i+1+j*4,number_of_point+self.parametre_first_id+j*4])
        for i in xrange(4):  
            self.list_line.append([number_of_point+self.parametre_first_id+i,number_of_point+self.parametre_first_id+4+i])

        ''' lineloop for the top atmosphere'''
        lineloop_topatmosphere = [len(self.list_line)-7,len(self.list_line)-6,len(self.list_line)-5,len(self.list_line)-4]

        self.list_loop.append(lineloop_topatmosphere)
        self.list_surface.append([len(self.list_loop)-1+self.parametre_first_id])
        self.list_surface_loop_canopy.append(self.list_surface[-1][0])
        phy_gr_name = 'topatmosphere'
        self.dico_surf_gr_phy[phy_gr_name] = {}
        self.dico_surf_gr_phy[phy_gr_name]['id_surface'] = [len(self.list_surface)-1+self.parametre_first_id]#self.list_surface[-1] 
        self.dico_surf_gr_phy[phy_gr_name]['side'] = 'in'
        self.dico_surf_gr_phy[phy_gr_name]['type'] = 'BC'
        ''' lineloop for the sideatmosphere'''
        for i in xrange(3):
            lineloop_sideatmosphere = [len(self.list_line)-11+i,len(self.list_line)-2+i,-(len(self.list_line)-7+i),-(len(self.list_line)-3+i)]
            self.list_loop.append(lineloop_sideatmosphere)
            self.list_surface.append([len(self.list_loop)-1+self.parametre_first_id])
            self.list_surface_loop_canopy.append(self.list_surface[-1][0])
            phy_gr_name = 'sideatmosphere'+str(i+1)
            self.dico_surf_gr_phy[phy_gr_name] = {}
            self.dico_surf_gr_phy[phy_gr_name]['id_surface'] =  [len(self.list_surface)-1+self.parametre_first_id]#self.list_surface[-1] 
            self.dico_surf_gr_phy[phy_gr_name]['side'] = 'in'
            self.dico_surf_gr_phy[phy_gr_name]['type'] = 'BC'
        lineloop_sideatmosphere = [len(self.list_line)-8,len(self.list_line)-3,-(len(self.list_line)-4),-(len(self.list_line))]
        self.list_loop.append(lineloop_sideatmosphere)
        self.list_surface.append([len(self.list_loop)-1+self.parametre_first_id])
        self.list_surface_loop_canopy.append(self.list_surface[-1][0])
        phy_gr_name = 'sideatmosphere'+str(4)
        self.dico_surf_gr_phy[phy_gr_name] = {}
        self.dico_surf_gr_phy[phy_gr_name]['id_surface'] = [len(self.list_surface)-1+self.parametre_first_id]#self.list_surface[-1] 
        self.dico_surf_gr_phy[phy_gr_name]['side'] = 'in'
        self.dico_surf_gr_phy[phy_gr_name]['type'] = 'BC'
                
        ''' lineloop for the sol atmosphere'''
        lineloop_solatmosphere = [len(self.list_line)-11,len(self.list_line)-10,len(self.list_line)-9,len(self.list_line)-8]
        self.list_loop.append(lineloop_solatmosphere)
        self.list_loop.append(self.list_line_limit)
        self.list_surface.append([len(self.list_loop)-2+self.parametre_first_id,len(self.list_loop)-1+self.parametre_first_id])
        self.list_surface_loop_canopy.append(self.list_surface[-1][0])
        
        phy_gr_name = 'solatmosphere'
        self.dico_surf_gr_phy[phy_gr_name] = {}
        self.dico_surf_gr_phy[phy_gr_name]['id_surface'] =  [len(self.list_surface)-1+self.parametre_first_id]#self.list_surface[-1] 
        self.dico_surf_gr_phy[phy_gr_name]['side'] = 'in'
        self.dico_surf_gr_phy[phy_gr_name]['type'] = 'BC'
        

#         for i in xrange(len(self.list_surface)):
#             self.list_surface_loop[-1].append(i+self.parametre_first_id)
        self.list_surface_loop.append(self.list_surface_loop_canopy)

        self.list_volume = [[self.parametre_first_id]]
        
        self.dico_vol_gr_phy['canopy'] = [self.parametre_first_id]
        
        
    def write_viewfactor_lst_geom(self):
        

        ''' function to write a poly file in the floder named 'nomfichier'
        to be used next to comput form factor
        '''
        file_name_poly = self.file_name_gmsh[:-4]+'.poly'
        f = open(file_name_poly,'w')
        f.write('[Analitico Abertura 0,1]\n')
        f.write('[faces = %i, vertices = %i]\n'% (len(self.list_surface),len(self.list_point)))#parametre qui permet  de regler le maillage....
        f.write('\n')
        f.write('[vertices = {')
        for i in xrange(len(self.list_point)):
            f.write('(%s,%s,%s),'% (self.list_point[i][0],self.list_point[i][1],self.list_point[i][2]))
        f.write('}]')
        f.write('\n')
        id_face = 0
        for i in xrange(len(self.dico_surface)):
            if 'id_line_loop' in self.dico_surface[i].keys():
                id_face+=1
            
                f.write('[face %i, holes =  %i]\n'% (id_face,len(self.dico_surface[i]['id_line_loop'])-1))
                f.write('\n')
                f.write('[vertices(%i) = {'% (len(self.dico_surface[i]['id_point'])))
                for j in self.dico_surface[i]['id_point']:
                    f.write('%i,'% (j))
                f.write('}]\n')
                f.write('\n')
                points_holes = []
                for j in xrange(1,len(self.dico_surface[i]['id_line_loop'])):
                    id_line = self.dico_surface[i]['id_line_loop'][j]
                    id_point1 = self.list_line[id_line[0]]
                    id_point2 = self.list_line[id_line[1]]
                f.write('\n')
        f.close()

#          
        
    def built_gmsh(self,nomfichier,):
        self.gmsh = GMSH.GMSH_GEO()
        if 'canopy' in self.__dict__.keys():
            self.gmsh.cl1,self.gmsh.cl2,self.gmsh.cl3 = self.canopy.cl,self.canopy.clbot,self.canopy.cltop
        else:
            self.gmsh.cl1,self.gmsh.cl2,self.gmsh.cl3 = 0.5,0.5,0.5
        self.gmsh.option_mesh_size = self.option_mesh_size 
        self.gmsh.list_point = self.list_point
        self.gmsh.list_line = self.list_line
        self.gmsh.list_loop = self.list_loop
        self.gmsh.list_surface = self.list_surface
        self.gmsh.list_surface_loop = self.list_surface_loop
        self.gmsh.list_volume = self.list_volume
        self.gmsh.dico_surf_gr_phy = self.dico_surf_gr_phy
        self.gmsh.dico_vol_gr_phy = self.dico_vol_gr_phy
        self.gmsh.write_open_geo_file(nomfichier,)
        self.gmsh.list_surface_crak = self.list_intersurface
        
    def listing_element(self):
        self.listing_point()
        self.listing_line()
        self.listing_surface_name()
        self.checking_surface_contact()
        self.listing_line_loop()
        self.define_lineloop_windows_in_wall()
        self.listing_surface()
        
        
    def from_idf_to_geo_outdoor(self):
        self.windowsoption = True
        self.parsing(self.file_name_idf)
        self.dictionnary_surface()
        self.dictionnary_surface_domus()
        self.dictionnary_fenestration_surface()
        self.apply_ground_condition()
        self.select_surface_contact_outdoor()
         
        self.listing_point()
        self.listing_line()
        self.listing_surface_name()
        self.checking_surface_contact()
        self.listing_line_loop()
        self.define_lineloop_windows_in_wall()
        self.listing_surface()
        self.listing_surface_groupe_physic()
#         H,D = self.H,self.D
        self.create_canope()
#         self.build_mockup()  
             
        self.built_gmsh(self.file_name_gmsh)
        
    def from_idf_to_geo_indoor(self):
        self.parsing(self.file_name_idf)
        self.dictionnary_surface()
        self.dictionnary_fenestration_surface()
        self.dictionnary_zone() 

        self.listing_point()
        self.listing_line()
        self.listing_surface_name()
        self.checking_surface_contact()
        self.listing_line_loop()
        self.define_lineloop_windows_in_wall()
        self.listing_surface()
        self.listing_surface_groupe_physic()
        self.listing_volume_zone_indoor()      
        self.built_gmsh(self.file_name_gmsh)       

    def from_idf_to_geo_outdoor_and_indoor(self,windowsoption = False,file_name_idf_class = ""):
        self.windowsoption = windowsoption
        self.build_mockup()
        self.picklesaving(file_name_idf_class)
        
#         self.write_viewfactor_lst_geom()
       
        self.built_gmsh(self.file_name_gmsh)
        
        self.file_name_gmsh_crack = self.file_name_gmsh[:-4]+'_crack.geo'
        
        self.gmsh.write_plugin_crack(self.file_name_gmsh_crack)
    
    def update_idf(self):
        ''' parsing of the idf nrj plus idf file'''
        if self.idf=='domus':
            self.parsing(self.file_name_idf_domus)#self.file_name_idf)
    
            #self.dictionnary_surface_domus()
     
            #self.dictionnary_fenestration_surface_domus()
            self.dictionnary_PTF()
            self.dictionnary_PTF_glass()
    
    def build_mockup(self):
        ''' parsing of the idf nrj plus idf file'''
        if self.idf=='domus':
            self.parsing(self.file_name_idf_domus)#self.file_name_idf)
    
            self.dictionnary_surface_domus()
     
            self.dictionnary_fenestration_surface_domus()
            self.dictionnary_PTF()
            self.dictionnary_PTF_glass()
            
        elif self.idf=='nrjplus':        
            ''' parsing of the idf nrj plus idf file'''
            self.parsing(self.file_name_idf)
            self.dictionnary_surface()
            self.dictionnary_fenestration_surface()
        

        
        self.dictionnary_boundary_condition()
        self.listing_surface_name()
        
        
#         ''' as the surface and fenstes dictionnary was modified a new listing is needed'''
#         self.listing_surface_name()
        
        
        
        if self.option_outdoor:
            ''' in the case of outdoor simulation, the zone number one is used to represent the ground'''
            self.apply_ground_condition()
#             self.select_surface_contact_outdoor_zone1()

        self.dictionnary_zone() 
        self.select_zones_and_surface_depanding_coupling_method()
        self.checking_surface_contact()

        
        if self.option_outdoor:
            ''' all the windows are opened to be treated as hole in CFD simulation'''
            self.close_windows_from_coupling_method()
        else:
            ''' all the windows are closed'''
            for i in xrange(len(self.dico_fenes_surface)):
                self.dico_fenes_surface[i]['opening_level'] = 0
            
#         self.create_list_surface_interface()
        
        self.listing_point()
        self.listing_line()
        
        
        
        
        self.listing_line_loop()
        self.define_lineloop_windows_in_wall()
        self.listing_surface()
        self.create_list_surface_interface()
        self.listing_surface_groupe_physic()

#         self.write_viewfactor_lst_geom()
        
        if self.option_outdoor:
            self.create_canope() 
            self.option_mesh_size = True
        else:
            self.option_mesh_size = False
        
        self.listing_volume_zone_indoor()
        
    
                
                

        
        
    def picklesaving(self,foldername):
        ''' function to save all the attribut except the attribut gmsh ( this is an other object, it can be save with a pickle)
        '''
#         print ' on va sauver'

        for keys in self.__dict__.keys():
#             print 'cle = ',keys
            if keys!='gmsh':
                cPickle.dump(self.__dict__[keys],open(foldername+keys,'wb'))
        
                
    def pickleloading_keys(self,foldername,keys):
        
        self.__dict__[keys] = cPickle.load(open(foldername+keys))
        
    def write_IDF(self,filename):
        self.new_file = open(filename,'w')
        for string in self.liste_idf_file:
            self.new_file.write(string)
        self.new_file.close()
#     def write_IDF_intro(self):
#         self.idf_file.write("
#         ")

class Estadosim :
    ''' class pour manipuler des fichier estadosim'''
    def __init__(self,node_number,tdma_number,type = 'wall'):
        if type== 'wall':
            self.dic = {}
            self.clefvecteur1 = ['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']
    #         self.clef = ['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm',
            self.clefvecteur2 = ['hci','hce','hmi','hme']
            self.clefvecteur3 = ['umiRel']
            self.clefvecteur4 = ['fluxo']
            self.clefvecteur5 = ['Ti','Pvi','Fvi','Fli','Fcsi','cui','cdi','cti','Fclwi','Cpi','Fairi',
                                 'Te','Pve','Fve','Fle','Fcse','cue','cde','cte','Fclwe','Cpe','Faire']
            self.clefvecteur6 = ['Tib','Pvib','Fvib','Flib','Fcsib','cuib','cdib','ctib','Fclwib','Cpib','Fairib',
                                 'Teb','Pveb','Fveb','Fleb','Fcseb','cueb','cdeb','cteb','Fclweb','Cpeb','Faireb']
            self.node_number = node_number
            self.tdma_number = tdma_number
            self.name_file = ''
            self.dico_clef = []
            self.dico_clef.append({'cle':self.clefvecteur1,'nbre_value':node_number+tdma_number, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur2,'nbre_value':1, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur3,'nbre_value':node_number+tdma_number, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur4,'nbre_value':3, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur5,'nbre_value':1, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur6,'nbre_value':1, 'type':'B','size':1})
        elif type=='zone':
            self.dic = {}
            self.clefvecteur1 = ['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']
    #         self.clef = ['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm',
            self.clefvecteur2 = ['hci','hce','hmi','hme']
            self.clefvecteur3 = ['umiRel']
            self.clefvecteur4 = ['fluxo']
            self.clefvecteur5 = ['Ti','Pvi','Fvi','Fli','Fcsi','cui','cdi','cti','Fclwi','Cpi','Fairi',
                                 'Te','Pve','Fve','Fle','Fcse','cue','cde','cte','Fclwe','Cpe','Faire']
            self.clefvecteur6 = ['Tib','Pvib','Fvib','Flib','Fcsib','cuib','cdib','ctib','Fclwib','Cpib','Fairib',
                                 'Teb','Pveb','Fveb','Fleb','Fcseb','cueb','cdeb','cteb','Fclweb','Cpeb','Faireb']
            self.node_number = node_number
            self.tdma_number = tdma_number
            self.name_file = ''
            self.dico_clef = []
            self.dico_clef.append({'cle':self.clefvecteur1,'nbre_value':node_number+tdma_number, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur2,'nbre_value':1, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur3,'nbre_value':node_number+tdma_number, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur4,'nbre_value':3, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur5,'nbre_value':1, 'type':'f','size':4})
            self.dico_clef.append({'cle':self.clefvecteur6,'nbre_value':1, 'type':'B','size':1})
    def print_values(self):    
        for i in xrange(len(self.dico_clef)):
            for cle in self.dico_clef[i]['cle']:
                print cle,':',
                for j in xrange(self.dico_clef[i]['nbre_value']):
                    
                    valeurs = struct.unpack(self.dico_clef[i]['type'], self.dic[cle][j])[0] 
                    print valeurs,
                print '/n'
    def read_file(self,name_file):
        self.name_file = name_file
        self.binfile = open(name_file, "rb")
        num_valeurs = 0
        for i in xrange(len(self.dico_clef)):
            for cle in self.dico_clef[i]['cle']:
                self.dic[cle] = []
                for j in xrange(self.dico_clef[i]['nbre_value']):
                    self.dic[cle].append(self.binfile.read(self.dico_clef[i]['size']))
#                     num_valeurs+=1
#                     print 'num_valeurs:',num_valeurs
                
#         '''temperature pour les node_number noeuds du mur au pas de temps anterieur'''
#         self.dic['Tmpa'] = []
#         '''temperature pour les node_number noeuds du mur au pas de l'iteration anterieur'''
#         self.dic['Tmia'] = []
#         '''temperature pour les node_number noeuds du mur au pas de temps actuel'''
#         self.dic['Tm'] = []
#         '''humidite pour les node_number noeuds du mur au pas de temps anterieur'''
#         self.dic['Umpa'] = []
#         '''humidite pour les node_number noeuds du mur au pas de l'iteration anterieur'''
#         self.dic['Umia'] = []
#         '''humidite pour les node_number noeuds du mur au pas de temps actuel'''
#         self.dic['Um'] = []
#         '''PPV pour les node_number noeuds du mur au pas de temps anterieur'''
#         self.dic['PPVmpa'] = []
#         '''PPV pour les node_number noeuds du mur au pas de l'iteration anterieur'''
#         self.dic['PPVmia'] = []
#         '''PPV pour les node_number noeuds du mur au pas de temps actuel'''
#         self.dic['PPVm'] = []
#         for cle in self.clefvecteur1:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle] = []
#             for i in xrange(self.node_number+self.tdma_number):
#                 self.dic[cle].append(self.binfile.read(4))
#                 num_valeurs+=1
#         for cle in self.clefvecteur2:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle]=[self.binfile.read(4)]
#             num_valeurs+=1
#         for cle in self.clefvecteur3:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle] = []
#             for i in xrange(self.node_number+self.tdma_number):
#                 self.dic[cle].append(self.binfile.read(4))
#                 num_valeurs+=1
#         for cle in self.clefvecteur4:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle] = []
#             for i in xrange(3):
#                 self.dic[cle].append(self.binfile.read(4))
#                 num_valeurs+=1
#         for cle in self.clefvecteur5:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle]=[self.binfile.read(4)]
#             num_valeurs+=1
#         for cle in self.clefvecteur6:#['Tmpa','Tmia','Tm','Umpa','Umia','Um','PPVmpa','PPVmia','PPVm']:
#             self.dic[cle]=[self.binfile.read(1)]
#             num_valeurs+=1
# #         '''temperature interior:'''
# #         self.dic['Ti'] = [self.binfile.read(4)]
# #         '''pression de vapeur interior'''
# #         self.dic['Pvi'] = [self.binfile.read(4)]
# #         '''Flux de vapeur interior'''
# #         self.dic['Fvi'] = [self.binfile.read(4)]
# #         '''Flux de liquide interior'''
# #         self.dic['Fli'] = [self.binfile.read(4)]
# #         '''Flux de chaleur sensible interior'''
# #         self.dic['Fcsi'] = [self.binfile.read(4)]
# #         '''concentration polluant1 interior'''
# #         self.dic['cui'] = [self.binfile.read(4)]
# #         '''concentration polluant2 interior'''
# #         self.dic['cdi'] = [self.binfile.read(4)]
# #         '''concentration polluant3 interior'''
# #         self.dic['cti'] = [self.binfile.read(4)]
# #         '''temperature exterior:'''
# #         self.dic['Te'] = [self.binfile.read(4)]
# #         '''pression de vapeur exterior'''
# #         self.dic['Pve'] = [self.binfile.read(4)]
# #         '''Flux de vapeur exterior'''
# #         self.dic['Fve'] = [self.binfile.read(4)]
# #         '''Flux de liquide exterior'''
# #         self.dic['Fle'] = [self.binfile.read(4)]
# #         '''Flux de chaleur sensible exterior'''
# #         self.dic['Fcse'] = [self.binfile.read(4)]
# #         '''concentration polluant1 exterior'''
# #         self.dic['cue'] = [self.binfile.read(4)]
# #         '''concentration polluant2 exterior'''
# #         self.dic['cde'] = [self.binfile.read(4)]
# #         '''concentration polluant3 exterior'''
# #         self.dic['cte'] = [self.binfile.read(4)]
# #         '''temperature interior boolean:'''
# #         self.dic['Tib'] = [self.binfile.read(4)]
# #         '''pression de vapeur interior  boolean'''
# #         self.dic['Pvib'] = [self.binfile.read(4)]
# #         '''Flux de vapeur interior  boolean'''
# #         self.dic['Fvib'] = [self.binfile.read(4)]
# #         '''Flux de liquide interior boolean '''
# #         self.dic['Flib'] = [self.binfile.read(4)]
# #         '''Flux de chaleur sensible interior boolean ''' 
# #         self.dic['Fcsib'] = [self.binfile.read(4)]
# #         '''concentration polluant1 interior boolean ''' 
# #         self.dic['cuib'] = [self.binfile.read(4)]
# #         '''concentration polluant2 interior boolean ''' 
# #         self.dic['cdib'] = [self.binfile.read(4)]
# #         '''concentration polluant3 interior boolean ''' 
# #         self.dic['ctib'] = [self.binfile.read(4)]
# #         '''temperature exterior boolean:'''
# #         self.dic['Teb'] = [self.binfile.read(4)]
# #         '''pression de vapeur exterior boolean ''' 
# #         self.dic['Pveb'] = [self.binfile.read(4)]
# #         '''Flux de vapeur exterior boolean ''' 
# #         self.dic['Fveb'] = [self.binfile.read(4)]
# #         '''Flux de liquide exterior boolean ''' 
# #         self.dic['Fleb'] = [self.binfile.read(4)]
# #         '''Flux de chaleur sensible exter ior boolean ''' 
# #         self.dic['Fcseb'] = [self.binfile.read(4)]
# #         '''concentration polluant1 exter ior boolean ''' 
# #         self.dic['cueb'] = [self.binfile.read(4)]
# #         '''concentration polluant2 exter ior boolean ''' 
# #         self.dic['cdeb'] = [self.binfile.read(4)]
# #         '''concentration polluant3 exter ior boolean ''' 
# #         self.dic['cteb'] = [self.binfile.read(4)]
      
      
    def write_file(self):

        binfile = open(self.name_file, "wb")
        for i in xrange(len(self.dico_clef)):
            for cle in self.dico_clef[i]['cle']:
                for j in xrange(len(self.dic[cle])):
                    binfile.write(self.dic[cle][j])
        binfile.close()
        
    def replace_valu(self,cle, newvalu,type = 'f'):
        ''' function to replace the valu in self.dic[cle] by newvalu
        the newvalu is binarised:'''
        binnewvalu = struct.pack(type,newvalu)
        self.dic[cle][0] = binnewvalu
        
class Canopy:
    ''' class python to build a canopy''' 
    def __init__(self):

        self.H = 0.855#150#0.875#150
        self.Dx = 0.5#50#1.25#1.50#  
        self.Dy =  0.5#50#0.325#1.50#50  
        self.option_calcul_limit = True
        self.cl = 2.5#0.01
        ''' parameter to determine the mesh size at the bottom of the canopy'''
        self.clbot = 2*self.cl
        ''' parameter to determine the mesh size at the top of the canopy'''
        self.cltop = 2*self.clbot


    def define_limite(self,list_point):
        ''' function to looking for the limit of the domaine'''
        xmin,xmax,ymin,ymax = 100000,0,10000000,0
        self.zmin,self.zmax = 1000000,0
        id_xmin,id_xmax,id_ymin,id_ymax = 0,0,0,0
        list_point_zero = []
        for point in list_point:
            if float(point[2])<self.zmin:
                self.zmin = float(point[2])
            if float(point[2])>self.zmax:
                self.zmax = float(point[2])
            
#             if point[2]=='0':
#                 list_point_zero.append(self.list_point.index(point))
            if float(point[0])>xmax:
                xmax = float(point[0])
                id_xmax = list_point.index(point)
            if float(point[1])>ymax:
                ymax = float(point[1])
                id_ymax = list_point.index(point)
            if float(point[0])<xmin:
                xmin = float(point[0])
                id_xmin = list_point.index(point)
            if float(point[1])<ymin:
                ymin = float(point[1])
                id_ymin = list_point.index(point)
                    
        self.xmin,self.xmax,self.ymin,self.ymax = xmin,xmax,ymin,ymax
        
        #         id_point1,id_point2,id_point3,id_point4 = 0,0,0,0
#         for i in list_point_zero:
#                 if (float(self.list_point[i][0])==xmin)&(float(self.list_point[i][1])==ymin):
#                     id_point1 = 
#                     xmax = float(point[0])
#                     id_xmax = self.list_point.index(point)
#                 if float(point[1])>ymax:
#                     ymax = float(point[1])
#                     id_ymax = self.list_point.index(point)
#                 if float(point[0])<xmin:
#                     xmin = float(point[0])
#                     id_xmin = self.list_point.index(point)
#                 if float(point[1])<ymin:
#                     ymin = float(point[1])
#                     id_ymin = self.list_point.index(point)
        

        if (self.zmax-self.zmin!=0) & (self.option_calcul_limit):
            self.deltax = 15*abs(self.zmax-self.zmin)
            self.deltay = 15*abs(self.zmax-self.zmin)
            self.deltaz = 5*abs(self.zmax-self.zmin)
        else:
            self.deltax = self.Dx
            self.deltay = self.Dy
            self.deltaz = self.H   
        self.points_limit = []
        self.point1,self.point2,self.point3,self.point4 = [self.xmin-self.deltax,self.ymin-self.deltay,self.zmin],[self.xmax+self.deltax,self.ymin-self.deltay,self.zmin],[self.xmax+self.deltax,self.ymax+self.deltay,self.zmin],[self.xmin-self.deltax,self.ymax+self.deltay,self.zmin]
        self.points_limit.append(self.point1)
        self.points_limit.append(self.point2)
        self.points_limit.append(self.point3)
        self.points_limit.append(self.point4)
        self.point5,self.point6,self.point7,self.point8 = [self.xmin-self.deltax,self.ymin-self.deltay,self.zmax+self.deltaz],[self.xmax+self.deltax,self.ymin-self.deltay,self.zmax+self.deltaz],[self.xmax+self.deltax,self.ymax+self.deltay,self.zmax+self.deltaz],[self.xmin-self.deltax,self.ymax+self.deltay,self.zmax+self.deltaz]
        self.points_limit.append(self.point5)
        self.points_limit.append(self.point6)
        self.points_limit.append(self.point7)
        self.points_limit.append(self.point8)
        ''' 4 points with'''
    def compute_mesh_size(self):
        ''' function to comput self.clbot'''
        '''1° to compute the diagonals'''
        D1 = self.compute_diagonal(self.point1,[self.xmin,self.ymin,self.zmin])
        D2 = self.compute_diagonal(self.point2,[self.xmax,self.ymin,self.zmin])
        D3 = self.compute_diagonal(self.point3,[self.xmax,self.ymax,self.zmin])
        D4 = self.compute_diagonal(self.point4,[self.xmin,self.ymax,self.zmin])
        Dmin = min([D1,D2,D3,D4])
        distance = 0
        distance+= self.cl
        clnew = self.cl
        while distance<Dmin:
            clnew = 1.15*clnew
            distance+=clnew
        self.clbot = round(clnew,5)
        self.cltop = self.clbot
#         distance = 0 + self.clbot
#         while distance< self.deltaz:
#             clnew = 1.15*clnew
#             distance+=clnew
#         self.cltop = round(clnew,5)
#         self.clbot = 10*self.cl
#         self.cltop = 10*self.cl
            
            
            
    def compute_diagonal(self, point1,point2):
        diagonal = ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5
        return diagonal
if __name__ == "__main__":
    name_file =  r"D:\Users\adrien.gros\Documents\domus_project\BESTEST_dense\#BESTEST_dense\saidas\estadoSim\batiment.idf"
    read_file(self,name_file) 
    name_file =  r"D:\Users\user.mecanica\Documents\domus_project\batiment.idf"
#     file_name = r"D:\Users\adrien.gros\Documents\domus_project\#maison_sol.idf\saidas\sim001\Zon2TUP.sda"
#     idf_file = open(file_name,'r')
#     liste_idf_file = idf_file.readlines()
    file_name = r"D:\Users\user.mecanica\Documents\domus_project\batiment.idf"
    #file_name = r"D:\Users\adrien.gros\Documents\domus_project\bat_double_avec_porte_et_fenetre.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\batiment.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\maison_et_sol.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\bat_simple_fenetre.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\maison_sol_fenetrebis.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\maison_sol_fenetreter.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\casa_sol_janela.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\rua_canyon\\rua_canyon.idf"
    file_name = r"D:\Users\\adrien.gros\\Documents\\domus_project\\rua_canyon\\super_rua_canyon_essai.idf"
    file_name = r"D:\Users\adrien.gros\Documents\domus_project\eddificio_com_janela\edificio_com_janela_nrj.idf"
    file_name = r"D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela_nrj.idf"
    batidf = IDF()
    batidf.parsing(file_name)
    batidf.dictionnary_surface()
    batidf.dictionnary_fenestration_surface()
    batidf.apply_ground_condition()
    batidf.select_surface_contact_outdoor()
    batidf.listing_point()
    batidf.listing_line()
    batidf.listing_surface_name()
    batidf.checking_surface_contact()
    batidf.listing_line_loop()
    batidf.define_lineloop_windows_in_wall()
    batidf.listing_surface()
    batidf.listing_surface_groupe_physic()
    for i in xrange(len(batidf.dico_surface)):
        print(' indice of lines are ',batidf.dico_surface[i]['id_line'],' indice of points are ',batidf.dico_surface[i]['id_point'],'and vertex are',batidf.dico_surface[i]['vertex'])
    for i in xrange(len(batidf.dico_fenes_surface)):
        print(' indice of points are ',batidf.dico_fenes_surface[i]['id_point'],'and vertex are',batidf.dico_fenes_surface[i]['vertex'])
#     batidf.built_gmsh("D:\Users\\adrien.gros\\Documents\\domus_project\\batiment.geo")
    batidf.create_canope(H=150,D=50)
#     batidf.built_gmsh("D:\Users\\adrien.gros\\Documents\\domus_project\\batiment_et_sol.geo")
    file_name_gmsh = "D:\Users\\adrien.gros\\Documents\\domus_project\\maison_sol_fenetrebis.geo"
    file_name_gmsh = "D:\Users\\adrien.gros\\Documents\\domus_project\\maison_sol_fenetreter.geo"
    file_name_gmsh = "D:\Users\\adrien.gros\\Documents\\domus_project\\casa_sol_janela.geo"
    file_name_gmsh = "D:\Users\\adrien.gros\\Documents\\domus_project\\rua_canyon\\rua_canyon.geo"
    file_name_gmsh = "D:\Users\\adrien.gros\\Documents\\domus_project\\rua_canyon\\super_rua_canyon_essai.geo"
    file_name_gmsh = r"D:\Users\adrien.gros\Documents\domus_project\eddificio_com_janela\edificio_com_janela.geo"
    file_name_gmsh = r"D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela.geo"
    
    batidf.built_gmsh(file_name_gmsh)
    for i in xrange(len(batidf.dico_surface)):
        print(batidf.dico_surface[i])
    for i in xrange(len(batidf.dico_fenes_surface)):
        print(batidf.dico_fenes_surface[i])
    
    print (" c'est fini")