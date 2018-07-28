# -*- coding: utf-8 -*-
'''
Created on 01/11/2016

@author: adrien.gros
'''
#from essai_canopy_gmsh_to_idf import *
from IDF_script import IDF
from simulation_ansys import Model_CFX,Script_Ansys,Fluid
from GMSH import GMSH_command
from simulation_domus import Domus_results, Domus_comand
from xml.dom import minidom
import subprocess
import os
import cPickle
import time
import shutil
from utilitaire_python import *
import pandas as pd
import numpy as np
import datetime, calendar

class Coupled_simulation():
    
    def __init__(self):
        self.xml_data = Xml_data()
        self.domus_comand = Domus_comand()
        self.result = Domus_results()
        ''' define the type of coupling:
        if self.coupling_method = 'indoor' : only the indoor of building is computed with cfx and Domus
        if self.coupling_method = 'outdoor' : only the outdoor is computed with CFX
        if self.coupling_method = 'out_int_door' : the indoor and the outdoor is computed with CFX and Domus
        '''
        self.coupling_method = 'out_int_door'
        '''
        define if the windows is considered
        when self.option_windows = False the geometry of windows is not describe in CFX,
        then they are reprensented as hole
        when self.option_windows = True the geometry of windows is  describe in CFX
        '''
        self.option_windows = False
        self.option_outdoor = True
        
        self.monthi,self.daysi,self.hoursi = '1','2','0' 
        self.monthf,self.daysf,self.hoursf = '1','2','1' 
        self.month,self.days,self.hours = '1','2','1'#07:00:00' 
        self.timestep = 3600 #unity in secondes
        self.id_zones = []
        ''' a liste of missing wall: wall represented by a hole'''
        self.id_hole_wall = []
        self.list_id_face = []
        self.liste_AC_wall_temp_ref = []
        self.cfx_model = Model_CFX()
        self.cfx_model.script = Script_Ansys()
        self.idf = 'domus'
        
        '''
        a dictionnary will contain for each direction, and velocity simulated with CFD the name of the folder corresponding to this parameters,
        exemple: 
        the results of  simulation realised in CFX with a   wind  orientation equal to 180°, a velocity equal to 1.5m/s and a temperature equal to 25°C
        will be record in folder_name
        self.meteo_par_simu_cfd[180][1.5][25] = folder_name'''
        self.meteo_par_simu_cfd = {}
        self.meshsize = 0.5
        self.liste_id_AC_wall = []
        ''' a model of artificial neural network'''
        self.arn_model = ''
        self.radiative_model = ''
        

        
    def read_times(self,month,days,hours):
        self.month,self.days,self.hours = month,days,hours
        
    def create_mockups(self,domus_project_directory,project_name = 'model',result_option = False, idf_file_name = ''):
        ''' if the result_option is activated, a small simulation  and results are created in CFX'''
        self.xml_file = self.xml_data.create_new_project(domus_project_directory,project_name)
        if idf_file_name!= '':
            self.xml_data.file_name_idf_domus = idf_file_name
        self.from_idf_to_ansys(result_option)
#         self.select_var_to_export()
        
    def load_project(self,filename):
        self.xml_file = filename
        self.xml_data.read_data(self.xml_file)
        self.xml_data.file_name_solar_results = self.xml_data.domus_project_directory+'/solar_result/'
        self.load_idf_mockup()
        self.batidf.dictionnary_boundary_condition()
        self.batidf.compute_area_surface()
        self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
        self.cfx_model.pickleloading_keys(self.xml_data.file_name_cfx_class,'list_boundary')
        self.cfx_model.pickleloading_keys(self.xml_data.file_name_cfx_class,'list_interfaces')
        
#         self.cfx_model.create_dico_boundary_from_interface()
        self.cfx_model.script.def_file = self.xml_data.file_name_ansys_files+r'dp0\CFX\CFX\Fluid Flow CFX.def'
        self.cfx_model.script.ANSYS_path = self.xml_data.ANSYS_path
        self.cfx_model.script.interactive_mode = self.xml_data.ansysinteractive_mode
        canopy = Fluid()
        canopy.name = self.cfx_model.script.name_domaine        
        self.cfx_model.list_fluid.append(canopy) 
        self.domus_comand.modificationtxtpath = self.xml_data.domus_project_directory+'\\modification_domus.txt'
        self.domus_comand.file_name_idf_domus = self.xml_data.file_name_idf_domus
        self.charge_meteo_par_simu_cfd()
        self.result.dico_surface = self.batidf.dico_surface
        self.result.zone_and_wall_numbering()
        
    def create_liste_date(self, mi = 1,mf = 1,di = 1 ,df = 28, hi = 0, hf = 23):
        self.year = 2003
        liste_date = []
        for num_month in xrange(mi,mf+1):
            if num_month==mi:
                dayfirst = di
            else:
                dayfirst = 1
            num_days = calendar.monthrange(self.year, num_month)[1]
            if num_month!=mf:
                daylast = calendar.monthrange(self.year, num_month)[1]
            else:
                daylast = df
            for day in xrange(dayfirst,daylast+1):#num_days+1,pasdetempsjours):
                self.daysi,self.daysf = str(day),str(day)
                if (num_month==mi)& (day ==di):
                    Hfirst = hi
                else:
                    Hfirst = 0
                if (num_month==mf)& (day ==df):
                    Hlast = hf+1
                else:
                    Hlast = 24
                for h in xrange(Hfirst,Hlast):
                    liste_date.append([h,day,num_month])
        return liste_date

    def date_attribution(self,liste_date,i):   
        self.monthi = str(liste_date[i][2])
        self.monthf = str(liste_date[i][2])
        self.daysi,self.daysf = str(liste_date[i][1]),str(liste_date[i][1])
        self.hoursi,self.hoursf =str(liste_date[i][0]),str(liste_date[i][0])     
        
        
    def periode_simulation(self,hi = 1,di = 1 ,mi = 1,hf = 23,df = 2,mf = 1,iteration_number = 3,couplage_mode = 'CFX'):
        ''' creation des dates initial et final qui serviront pour domus'''
        liste_date = self.create_liste_date( mi,mf,di ,df, hi, hf )
        if couplage_mode=='keras':
            liste_parois_ref_kera = []
            for key in self.batidf.dico_BC.keys():
                if key[-6:]=='Zona 2':
                    liste_parois_ref_kera.append(key)
        self.complet_batidfBC_from_meteo_data(mi,di,hi)
        
        self.batidf.complete_flux_in_bin_estadosim(self.xml_data.domus_estadoSim_directory_init) 
        self.copy_estadosim_init()
        
        
        for i in xrange(len(liste_date)):
            
            self.date_attribution(liste_date,i)

            print ('date simulation '+str(self.monthi)+'M'+str(self.daysi)+'D'+str(self.hoursi)+'H')            
            if couplage_mode== 'CFX':
                self.simple_coupling_method(iteration_number)
            elif couplage_mode== 'keras':
                self.kera_coupling_method(iteration_number)
    
    def read_solar_radiation(self,dict_FF):
        
        
        liste_name_surface_exter = []
        for name in dict_FF.keys():
            if name in self.batidf.dico_BC.keys():
                liste_name_surface_exter.append(name)
        
        save_name_file = self.xml_data.domus_project_directory+'/solar_result/'
        creer_nouveau_dossier(save_name_file,delete_option = False)
        liste_name = []
        liste_ray_direct = []
        liste_ray_diffus = []
        liste_ray_ref = []
        liste_month,liste_days,liste_hours = [],[],[]
        ''' le nom du fichier ou se trouve les resultas d'ensoleillement est'''
        
        name_file = liste_name_surface_exter[0]+'_Radiation.txt'
        name_file = self.xml_data.domus_results_directory+name_file
        table_idf = lire_fichier_txt(name_file)
        
        for ligne in xrange(5,len(table_idf)):
            print'ligne = ', ligne
            liste_name = []
            liste_name.append(self.batidf.dico_BC.keys()[0])
            liste_month.append(table_idf[ligne][0])
            liste_days.append(table_idf[ligne][1])
            liste_hours.append(table_idf[ligne][2])
            liste_ray_direct = [float(table_idf[ligne][3])]
            liste_ray_diffus = [float(table_idf[ligne][4])]
            liste_ray_ref = [float(table_idf[ligne][5])]
            
            objheure = datetime.datetime.strptime(table_idf[ligne][2], '%X')
            heure = datetime.datetime.strftime(objheure,'%H')
    
    
            
            hourly_results_folder = save_name_file+table_idf[ligne][0]+'_'+table_idf[ligne][1]+'_'+heure+'/'
            creer_nouveau_dossier(hourly_results_folder)
            
            for i in xrange(1,len(liste_name_surface_exter)):
                
                
                name_filebis = liste_name_surface_exter[i]+'_Radiation.txt'
                name_filebis = self.xml_data.domus_results_directory+name_filebis
                table_idfbis = lire_fichier_txt(name_filebis)
    
                liste_ray_direct.append(float(table_idfbis[ligne][3]))
                liste_ray_diffus.append(float(table_idfbis[ligne][4]))
                liste_ray_ref.append(float(table_idfbis[ligne][5]))
                
            liste_ray_direct = np.array(liste_ray_direct)
            liste_ray_diffus = np.array(liste_ray_diffus)
            liste_ray_ref = np.array(liste_ray_ref)
            
            np.save(hourly_results_folder+'direct',liste_ray_direct)
            np.save(hourly_results_folder+'diffus',liste_ray_diffus)
            np.save(hourly_results_folder+'reflect',liste_ray_ref)
            
        liste_name = np.array(liste_name_surface_exter)
        np.save(save_name_file+'name',liste_name)
       
    def read_meteo_data_from_domus(self):
        month,days,hours = [],[],[]
        temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel = [],[],[],[],[],[]
        
        f = open(self.xml_data.meteo_directory, "r")
        liste_file = f.readlines()
        for i in xrange(2,len(liste_file)):
            value = liste_file[i].split()
            month.append(value[0])
            days.append(value[1])
            hours.append(value[2])
            temperature.append(float(value[3]))
            wet.append(float(value[4]))
            direct_rad.append(float(value[5]))
            diffus_rad.append(float(value[6]))
            wind_dir.append(float(value[7]))
            wind_vel.append(float(value[8]))
        ''' all these data are multiindexed with the multiindex function from pandas'''        
        date = [month,days,hours]
        date_name = ['month', 'days','hours']
        index = pd.MultiIndex.from_arrays(date, names = date_name)
        data = np.array([temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel])
        data_name = ['temperature','wet','direct_rad','diffus_rad','wind_dir','wind_vel']
        self.meteo_data = pd.DataFrame(data, index = data_name, columns = index)
        
    def read_meteo_data_from_domus_bis(self):
        month,days,hours = [],[],[]
        temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel,sky_temp = [],[],[],[],[],[],[]
        
        f = open(self.xml_data.meteo_directory, "r")
        liste_file = f.readlines()
        for i in xrange(2,len(liste_file)):
            value = liste_file[i].split()
            month.append(str(int(value[0][4:6])))
            days.append(str(int(value[0][1:3])))
            hours.append(str(int(value[2][:2])))
            temperature.append(float(value[3].replace(',','.')))
            wet.append(float(value[4].replace(',','.')))
            direct_rad.append(float(value[5].replace(',','.')))
            diffus_rad.append(float(value[6].replace(',','.')))
            wind_dir.append(float(value[7].replace(',','.')))
            wind_vel.append(float(value[8].replace(',','.')))
            sky_temp.append(float(value[9].replace(',','.')))
        ''' all these data are multiindexed with the multiindex function from pandas'''        
        date = [month,days,hours]
        date_name = ['month', 'days','hours']
        index = pd.MultiIndex.from_arrays(date, names = date_name)
        data = np.array([temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel,sky_temp])
        data_name = ['temperature','wet','direct_rad','diffus_rad','wind_dir','wind_vel','sky_temp']
        self.meteo_data = pd.DataFrame(data, index = data_name, columns = index)
    
    def analyse_meteo_to_CFD(self,mi = 1,di = 1, mf = 12, df = 31, round_direction = True):
        ''' fonction pour analyser le fichier meteo et donner le nombre total  de vitesse et d'orientation differentes a simuler
        les données à analyser peuvent être reduite entre la periode du jours di dou mois mi et le jours df du mois mf'''
        liste_date = self.create_liste_date(mi,mf,di ,df)
        self.wind_dir_class = {}
        compteur = 1
        for date in liste_date:
            h,d,m = date
            wind_dir = self.meteo_data[str(m)][str(d)][str(h)]['wind_dir']
            valeur = round(float(wind_dir)/10)*10
            if valeur==360:
                valeur = 0
            wind_dir = valeur
            wind_vel = self.meteo_data[str(m)][str(d)][str(h)]['wind_vel']
            temperature = self.meteo_data[str(m)][str(d)][str(h)]['temperature']
            if wind_dir not in self.wind_dir_class.keys():
                self.wind_dir_class[wind_dir]={}                
                self.wind_dir_class[wind_dir][wind_vel] = [temperature]

            else:
                if wind_vel not in self.wind_dir_class[wind_dir].keys():
                    self.wind_dir_class[wind_dir][wind_vel] = [temperature]
                else:
                    if temperature not in self.wind_dir_class[wind_dir][wind_vel]:
                        self.wind_dir_class[wind_dir][wind_vel].append(temperature)
                    else:
                        print ('Nunero',compteur,'la temperature',temperature,'existe deja pour la vitesse',wind_vel," et l'orientation ",wind_dir)
                        compteur+=1

        total = 0
        print 'les differente orientation sont:',sorted(self.wind_dir_class.keys())
        for direction in self.wind_dir_class.keys():
            print ('pour direction: ',direction, 'il y a ',len(self.wind_dir_class[direction].keys()),'vitesses differentes:',self.wind_dir_class[direction].keys() )
            print ('le max des vitesse est ',max(self.wind_dir_class[direction].keys()))
#             for vel in 
#             print len(self.wind_dir_class[direction].keys()),' velocities: ' 
            total+= len(self.wind_dir_class[direction].keys())
#             for vel in self.wind_dir_class[direction].keys():
# #                 print vel,
#                 total+= len(self.wind_dir_class[direction][vel])
        print ('au total il y a ', total,' vitesses a simuler au lieu de 8760')
        print ('au total il y a ', len(self.wind_dir_class.keys()),' orientation a simuler a')
        
#         month,days,hours = [],[],[]
#         temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel = [],[],[],[],[],[]
#         
#         f = open(self.xml_data.meteo_directory, "r")
#         liste_file = f.readlines()
#         test = False
#         for i in xrange(2,len(liste_file)):
#             test = False
#             value = liste_file[i].split()
#             num_mois = int(value[0]) 
#             num_jours = int(value[1]) 
#             if (num_mois>mi) and (num_mois<mf):
#                 test = True
#             elif num_mois==mi:
#                 if num_jours>=di:
#                     test = True
#                     if mi==mf:
#                         if num_jours>df:
#                             test = False
#             elif num_mois==mf:
#                 
#                 if num_jours<=df:
#                     test = True
#             if test:
#                 month.append(value[0])
#                 days.append(value[1])
#                 hours.append(value[2])
#                 temperature.append(float(value[3]))
#                 wet.append(float(value[4]))
#                 direct_rad.append(float(value[5]))
#                 diffus_rad.append(float(value[6]))
#                 ''' les directions sont arrondie a la dizaine'''
#                 if round_direction:
#                     valeur = round(float(value[7])/10)*10
#                     if valeur==360:
#                         valeur = 0
#                     wind_dir.append(valeur)
# 
#                 else:
#                     wind_dir.append(float(value[7]))
#                 vel = float(value[8])
#     #             vel = round(vel,-1)
#     #             vel = vel/10
#                 wind_vel.append(vel)
# #         ''' all these data are multiindexed with the multiindex function from pandas'''        
# #         date = [month,days,hours]
# #         date_name = ['month', 'days','hours']
# #         index = pd.MultiIndex.from_arrays(date, names = date_name)
# #         data = np.array([temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel])
# #         data_name = ['temperature','wet','direct_rad','diffus_rad','wind_dir','wind_vel']
# #         self.meteo_data = pd.DataFrame(data, index = data_name, columns = index)
# #        
#         pickle_out = open(r'ventspeed',"wb")
#         cPickle.dump(wind_vel, pickle_out)
#         pickle_out.close() 
#         pickle_out = open(r'ventorientation',"wb")
#         cPickle.dump(wind_dir, pickle_out)
#         pickle_out.close()
#         
        
        
    def write_meteo_data_with_specific_wind(self,new_file,nbre_vitesse = 3):
        month,days,hours = [],[],[]
        temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel,sky_temp = [],[],[],[],[],[],[]
        
        f = open(self.xml_data.meteo_directory, "r")
        liste_file = f.readlines()

            
        for i in xrange(2,len(liste_file)):
            if i==8760:
                print 'i =',i
            value = liste_file[i].split()
            month.append(str(int(value[0][4:6])))
            days.append(str(int(value[0][1:3])))
            hours.append(str(int(value[2][:2])))
            temperature.append(float(value[3].replace(',','.')))
            wet.append(float(value[4].replace(',','.')))
            direct_rad.append(float(value[5].replace(',','.')))
            diffus_rad.append(float(value[6].replace(',','.')))
            wind_dir.append(float(value[7].replace(',','.')))
            wind_vel.append(float(value[8].replace(',','.')))
            sky_temp.append(float(value[9].replace(',','.')))
            
        i = 0
        
        for winddir in self.wind_dir_class.keys():


            sorted_vitesse = sorted(self.wind_dir_class[winddir])

            if min(sorted_vitesse)==0.0:
                sorted_vitesse.remove(0.0)
            vitesse = sorted_vitesse
            wind_vel[i+0] = min(vitesse)
            wind_vel[i+1] = max(vitesse)
            wind_dir[i+0] = winddir
            wind_dir[i+1] = winddir
            for k in xrange(nbre_vitesse-2):
                wind_vel[i+2+k] = min(vitesse)+(k+1)*(max(vitesse)-min(vitesse))/(nbre_vitesse-1)
                wind_dir[i+2+k] = winddir
            i = i+2+k+1
        nombre_total_de_vitesse = i
        

        j = nombre_total_de_vitesse   
        while j<(len(liste_file)-2):
            wind_vel[j] = wind_vel[j-nombre_total_de_vitesse]
            wind_dir[j] = wind_dir[j-nombre_total_de_vitesse]
            j+=1
            
            
        for i in xrange(0,len(liste_file)-2):


            value = liste_file[i].split()
            strDate = str(month[i])+'/'+str(days[i])
            objDate = datetime.datetime.strptime(strDate, '%m/%d')
            date = '('+datetime.datetime.strftime(objDate,'%d/%m')+')'
            strheure = str(hours[i])
            objheure = datetime.datetime.strptime(strheure, '%H')
            heure = datetime.datetime.strftime(objheure,'%X')
            ligne = date+' - '+heure+'\t '
            ligne+=str(temperature[i])+'\t '
            ligne+=str(wet[i])+'\t '
            ligne+=str(direct_rad[i])+'\t '
            ligne+=str(diffus_rad[i])+'\t '
            ligne+=str(wind_dir[i])+'\t '
            ligne+=str(wind_vel[i])+'\t '
            ligne+=str(sky_temp[i])+'\n'
            liste_file[i+2] = ligne
            
            
        f = open(new_file, "w")
        for car in liste_file:
            f.write(car)
        f.close()
        
    def charge_meteo_par_simu_cfd(self):
        ''' function to read in the folder self.xml_data.file_name_cfd_data_base_results the differents existing folder
        each sub-folder name represent a simulation parameter (direction and velocity)
        a dictionnary is created to record for each simulation type the folder where is the results
        '''
    
        self.meteo_par_simu_cfd = {}
        
        liste = os.listdir(self.xml_data.file_name_cfd_data_base_results)
        for wind_parameter in liste:
            wp = wind_parameter.replace("-", ".")
            wp = wp.split("_")
            orientation = float(wp[0])
            vel = float(wp[1])
            if orientation in self.meteo_par_simu_cfd.keys():
                self.meteo_par_simu_cfd[orientation][vel] = self.xml_data.file_name_cfd_data_base_results+wind_parameter+'/Fluid Flow CFX.res'
            else:
                self.meteo_par_simu_cfd[orientation] = {}
                self.meteo_par_simu_cfd[orientation][vel] = self.xml_data.file_name_cfd_data_base_results+wind_parameter+'/Fluid Flow CFX.res'
                
            
        

        
    def build_gmsh_command(self):
        
        self.command_gmsh = GMSH_command()
        self.command_gmsh.gmsh_directory = self.xml_data.gmsh_directory
        self.command_gmsh.geo_directory = self.batidf.file_name_gmsh
        self.command_gmsh.geo_crack_directory = self.batidf.file_name_gmsh_crack
        self.command_gmsh.msh_directory = self.command_gmsh.geo_directory[:-3]+'msh'
        self.xml_data.file_name_msh = self.command_gmsh.msh_directory
        
        
    def from_idf_to_ansys(self,result_option = False):
        

        self.build_idf()
        self.batidf.id_zones = self.id_zones
        self.batidf.option_outdoor = self.option_outdoor
        self.batidf.idf = self.idf
        # self.batidf.from_idf_to_geo_indoor()
#         if self.coupling_method== 'out_int_door':
        self.batidf.from_idf_to_geo_outdoor_and_indoor(file_name_idf_class = self.xml_data.file_name_idf_class)
#         else:
#             self.batidf.from_idf_to_geo_outdoor()
#             self.batidf.file_name_gmsh_crack = ''
        
        ''' idf class saving'''
        self.batidf.picklesaving(self.xml_data.file_name_idf_class)
        ''' reading .geo to built .msh and .bdf'''
        self.build_gmsh_command()
        self.command_gmsh.open_geo_in_gmsh()
        if self.coupling_method== 'out_int_door':
            self.command_gmsh.triD_mesh_apply_plugin_crack()
        self.command_gmsh.save_bdf()
        self.xml_data.file_name_bdf = self.command_gmsh.bdf_directory
        
        
        ''' writting the ansys project '''
#         self.cfx_model = Model_CFX()
        self.cfx_model.coupling_method = self.coupling_method
        # ansys_model.create_dico_surface_from_idf(batidf.dico_surf_gr_phy)
#         self.cfx_model.create_dico_boundary_from_idf(self.batidf.dico_surf_gr_phy)
        if self.coupling_method== 'out_int_door':
            self.cfx_model.create_dico_boundary_from_idf_outdoor_indoor(self.batidf)#.dico_surf_gr_phy,self.batidf.list_intersurface)
#         elif self.coupling_method== 'outdoor':
#             self.cfx_model.create_dico_boundary_from_idf(self.batidf.dico_surf_gr_phy,'ext')
        
        self.cfx_model.create_script()

        self.cfx_model.script.ANSYS_path = self.xml_data.ANSYS_path
        self.cfx_model.script.interactive_mode = self.xml_data.ansysinteractive_mode
        
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        self.cfx_model.script.bdf_geom_path = self.xml_data.file_name_bdf
        self.cfx_model.ansys_directory = self.xml_data.ansys_project_directory
        

        self.cfx_model.script.file_name_script = self.cfx_model.ansys_directory+r'/create_projet_cfx.wbjn'#create_projetrua_canyon_multiple.wbjn'#creer_projet.wbjn'#+r'\sim_janela_files\creer_projetbis2.wbjn'
        self.cfx_model.script.def_file = self.xml_data.file_name_ansys_files+r'dp0\CFX\CFX\Fluid Flow CFX.def'
        self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
        canopy = Fluid()
        canopy.name = self.cfx_model.script.name_domaine        
        self.cfx_model.list_fluid.append(canopy) 
        ''' the geometry of project is created'''        
        self.cfx_model.script.write_project_creation()
        if result_option:
        
            ''' a small simulation of 2 iteration is created to be able next creat result and user surface'''
            self.cfx_model.script.max_iteration_number = 2
            self.cfx_model.script.write_run_solution()
            ''' results and user surfaces are created'''
            self.cfx_model.script.create_results()
            self.cfx_model.create_user_surface_and_table()
            self.cfx_model.create_average_value_for_table()
            self.cfx_model.save_table_value()
        
#         self.cfx_model.script.f.close()
        
        
#         self.cfx_model.script.max_iteration_number = 100
        self.cfx_model.create_dico_boundary_from_interface()
        
        ''' idf class saving'''
        ''' the '-' caractere are deleted from the 'name' because this caractere '-' can be used in CFX
        this operation is not done before because '-' is used to split 'name' and read the indice of the zone
        '''
        self.batidf.correction_dictionnarry_name()
        self.batidf.listing_correspondance_name()
        self.batidf.picklesaving(self.xml_data.file_name_idf_class)
        self.cfx_model.picklesaving_key(self.xml_data.file_name_cfx_class,'list_boundary')
        self.cfx_model.picklesaving_key(self.xml_data.file_name_cfx_class,'list_interfaces')
        self.cfx_model.script.run_script()


        
    def create_domus_results(self):
        self.domus_results = Domus_results()
        self.domus_results.list_id_face = self.list_id_face
        self.domus_results.directory_name = self.xml_data.domus_results_directory
        self.domus_results.estadoSim_directory = self.xml_data.domus_estadoSim_directory
        self.domus_results.dico_surface = self.batidf.dico_surface
        self.domus_results.zone_and_wall_numbering()
        
    def allocate_ts_result(self):
        self.domus_results.multi_extract_surface_temperature_ext()
        self.domus_results.multi_extract_surface_temperature_int()
        
    def define_boundary_CFX(self):
#         self.cfx_model.create_dico_boundary_from_idf_outdoor_indoor(self.batidf.dico_surf_gr_phy,self.batidf.list_intersurface)
        self.cfx_model.assign_meteo_data_boundary()
        self.cfx_model.comput_U_V_ref()
        if self.option_outdoor:
            self.cfx_model.define_boundary_from_meteo()
#         self.cfx_model.assign_ts_from_domus_results_outdoor_indoor(self.domus_results)
        
    def build_idf(self):
        ''' creation of the idf object by parsing the idf file to write .geo'''
        self.batidf = IDF()
        self.batidf.file_name_idf = self.xml_data.file_name_idf
        self.batidf.file_name_idf_domus = self.xml_data.file_name_idf_domus
        self.batidf.file_name_gmsh = self.xml_data.file_name_geo   
        self.batidf.id_hole_wall = self.id_hole_wall
        self.batidf.meshsize = self.meshsize 
        
    def load_idf_mockup(self):
        self.batidf = IDF()
        self.batidf.file_name_idf_domus = self.xml_data.file_name_idf_domus
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'dico_surface')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'dico_fenes_surface')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'dico_surf_gr_phy')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'dico_ptf')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'list_intersurface')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'id_walls_int')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'id_walls_ext')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'dico_BC')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'name_connection')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'id_zones')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'zones')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'list_id_surfacename')
        self.batidf.pickleloading_keys(self.xml_data.file_name_idf_class,'list_id_fenestrename')
        self.batidf.listing_surface_name()
        self.batidf.id_hole_wall = self.id_hole_wall
        self.batidf.parsing(self.batidf.file_name_idf_domus)#self.file_name_idf)
        self.batidf.upload_ptf_dic_surface_domus()
        self.batidf.dictionnary_PTF()
        self.batidf.dictionnary_PTF_glass()
        

#         self.build_idf()
#         self.batidf.windowsoption  = self.option_windows 
#         self.batidf.build_mockup()
    def select_var_to_export_old(self):   
        ''' function to say to domus what surface temperature to export and next to run a domus simulation
        '''
        ''' attribution of the different path need in domus simulation'''
        self.domus_comand.Domuspath = self.xml_data.Domuspath.replace('/','\\')     
        self.domus_comand.file_name_idf_domus = self.xml_data.file_name_idf_domus.replace('/','\\') 
        self.domus_comand.modificationtxtpath = self.xml_data.domus_project_directory.replace('/','\\')+'\\domus_comand_modification.txt'
        selection_wall = True
        if selection_wall:
            self.list_id_face_domus = []
            ''' creation of a liste of face wich surface temperature need to be export'''
            for i in xrange(len(self.batidf.dico_surface)):
                self.list_id_face_domus.append(i+7)
            for i in xrange(len(self.batidf.dico_fenes_surface)):
                self.list_id_face_domus.append(i+len(self.batidf.dico_surface)+6)
                
#             self.list_id_face = []
#             self.list_id_face_domus = []
#             for i in self.batidf.id_walls_int:
#                 self.list_id_face_domus.append(self.batidf.dico_surface[i]['domus_face_index'])
#                 self.list_id_face = [i]
#             for i in self.batidf.id_walls_ext:
#                 if self.batidf.dico_surface[i]['domus_face_index'] not in self.list_id_face_domus:
#                     self.list_id_face_domus.append(self.batidf.dico_surface[i]['domus_face_index'])
#                     self.list_id_face = [i]
            self.domus_comand.f = open(self.domus_comand.modificationtxtpath, 'w')
            ''' creation of txtfilescript to create a new class in DOMUS:FACE:RELATORIO named Rel_montemp for relatorio Monitora temperatura =1'''
            self.domus_comand.class_attributs = ['Rel_montemp','1','1','0','0','0','0','0','0']
            self.domus_comand.write_inclusiontxt()
            ''' for all the face in list_id_face the object named the object relative to ralatorio is change in Rel_montemp'''
            self.domus_comand.class_name = 'Domus:Face'
            self.domus_comand.object = 'Identificador da face'
                    # 
            self.domus_comand.attribut_name = 'Opcoes de relatorios'
            self.domus_comand.new_value = self.domus_comand.class_attributs[0]
            for i in self.list_id_face_domus :
                self.domus_comand.object_name = str(i)
#                 self.domus_comand.f.write('\n')           
                self.domus_comand.write_modificationtxt()
            ''' creation of txtfilescript to change class in DOMUS:REGAO:RELATORIO named Rel_Regiao3, for relatorio Monitora zona =1'''
            self.domus_comand.class_name = 'Domus:Regiao:Relatorio'
            self.domus_comand.object = 'Nome do objeto'
            self.domus_comand.object_name = 'Rel_Regiao3'       # 
            self.domus_comand.attribut_name = 'Monitorar  zona'
            self.domus_comand.new_value = '1'   
#             self.domus_comand.f.write('\n') 
            self.domus_comand.write_modificationtxt()
         
            self.domus_comand.f.close()
            self.domus_comand.change_in_idf()
    
    def select_var_to_export(self):   
        ''' function to say to domus what surface temperature to export and next to run a domus simulation
        '''
        ''' attribution of the different path need in domus simulation'''
        self.domus_comand.Domuspath = self.xml_data.Domuspath.replace('/','\\')     
        self.domus_comand.file_name_idf_domus = self.xml_data.file_name_idf_domus.replace('/','\\') 
        self.domus_comand.modificationtxtpath = self.xml_data.domus_project_directory.replace('/','\\')+'\\domus_comand_modification.txt'
        selection_wall = True
        if selection_wall:
            self.list_id_face_domus = []
            ''' creation of a liste of face wich surface temperature need to be export'''
            for i in xrange(len(self.batidf.dico_surface)):
                self.list_id_face_domus.append(self.batidf.dico_surface[i]['domus_name'])#i+7)
#             for i in xrange(len(self.batidf.dico_fenes_surface)):
#                 self.list_id_face_domus.append(i+len(self.batidf.dico_surface)+6)
                
#             self.list_id_face = []
#             self.list_id_face_domus = []
#             for i in self.batidf.id_walls_int:
#                 self.list_id_face_domus.append(self.batidf.dico_surface[i]['domus_face_index'])
#                 self.list_id_face = [i]
#             for i in self.batidf.id_walls_ext:
#                 if self.batidf.dico_surface[i]['domus_face_index'] not in self.list_id_face_domus:
#                     self.list_id_face_domus.append(self.batidf.dico_surface[i]['domus_face_index'])
#                     self.list_id_face = [i]
            self.domus_comand.f = open(self.domus_comand.modificationtxtpath, 'w')
            ''' creation of txtfilescript to create a new class in DOMUS:FACE:RELATORIO named Rel_montemp for relatorio Monitora temperatura =1'''
            self.domus_comand.class_attributs = ['Rel_montemp','1','1','0','0','0','0','0','0']
            self.domus_comand.write_inclusiontxt()
            ''' for all the face in list_id_face the object named the object relative to ralatorio is change in Rel_montemp'''
            self.domus_comand.class_name = 'Domus:FaceIDF'
            self.domus_comand.object = 'Nome da face'
                    # 
            self.domus_comand.attribut_name = 'Opcoes de relatorios'
            self.domus_comand.new_value = self.domus_comand.class_attributs[0]
            for i in self.list_id_face_domus :
                self.domus_comand.object_name = str(i)
#                 self.domus_comand.f.write('\n')           
                self.domus_comand.write_modificationtxt()
                
            ''' creation of txtfilescript to change class in DOMUS:REGAO:RELATORIO named Rel_Regiao3, for relatorio Monitora zona =1'''
            self.domus_comand.class_name = 'Domus:Regiao:Relatorio'
            self.domus_comand.object = 'Nome do objeto'
            self.domus_comand.object_name = 'Rel_Zona 1'       # 
            self.domus_comand.attribut_name = 'Monitorar  zona'
            self.domus_comand.new_value = '1'   
#             self.domus_comand.f.write('\n') 
            self.domus_comand.write_modificationtxt()
            for i in self.batidf.id_zones:
                self.domus_comand.object_name = 'Rel_Zona '+str(i)
                self.domus_comand.write_modificationtxt()
            self.domus_comand.f.close()
            self.domus_comand.change_in_idf()
    
    def run_coupled_domus_cfx_simu(self):
        
        ''' attribution of the hours, day, month,year of simulation'''
        
        self.domus_comand.change_simulation_date(self.monthi,self.daysi,self.hoursi,self.monthf,self.daysf,self.hoursf)
        self.run_domus_simu()
        self.batidf.complete_ts_BC_with_bin_estadosim()
#         self.simu_ansys_using_domus_results()
#         self.batidf.complete_hc_in_bin_estadosim()
#         self.create_domus_results()
    
        hoursresults = time.strftime('%H:%M:%S', time.gmtime(int(self.hoursf)*3600))
        self.read_times('1','1',hoursresults)
   
     
#         self.simu_ansys_using_domus_results()
        
    def copy_estadosim_init(self):
        ''' the estadosim folder in # projet_name/saida is deleted and it is replaced by'''
        lenth = len(self.xml_data.domus_project_directory)
        project_name = self.xml_data.file_name_idf_domus[lenth+1:-4]
        self.xml_data.domus_results_directory = self.xml_data.domus_project_directory+'/#'+project_name+"/saidas/"
        estadoSimdirectory = self.xml_data.domus_results_directory+'estadoSim/'
        if os.path.exists(estadoSimdirectory):
            shutil.rmtree(estadoSimdirectory)
        
        '''and next it is replaced by an estadosim from other simulation'''
        shutil.copytree(self.xml_data.domus_estadoSim_directory_init,self.xml_data.domus_results_directory+'estadoSim/')
        print self.xml_data.domus_estadoSim_directory_init, 'a ete copie dans',self.xml_data.domus_results_directory+'estadoSim/'
        self.xml_data.domus_estadoSim_directory = self.xml_data.domus_results_directory+'estadoSim/'
        self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
        
        
    def run_domus_simu(self,copyestadosim = True):
        ''' before each simulation the folder estadosim in #results is deleted''' 
        """        lenth = len(self.xml_data.domus_project_directory)
        project_name = self.xml_data.file_name_idf_domus[lenth+1:-4]
        self.xml_data.domus_results_directory = self.xml_data.domus_project_directory+'/#'+project_name+"/saidas/"
        estadoSimdirectory = self.xml_data.domus_results_directory+'estadoSim/'
        if os.path.exists(estadoSimdirectory):
            shutil.rmtree(estadoSimdirectory)
        if copyestadosim:
            '''and next it is replaced by an estadosim from other simulation'''
            shutil.copytree(self.xml_data.domus_estadoSim_directory_init,self.xml_data.domus_results_directory+'estadoSim/')"""
            
        

        """ to be able to work domus need '\' and no '/'"""
#         name_project =  self.xml_data.file_name_idf_domus[0]
#         for i in xrange(1,len(self.xml_data.file_name_idf_domus)):
#             if self.xml_data.file_name_idf_domus[i]=='/':
#                 name_project.append('\\')
#             else:
#                 name_project.append(self.xml_data.file_name_idf_domus[i])
# #                 self.xml_data.file_name_idf_domus[i] = '\\'
        name_project = self.xml_data.file_name_idf_domus.replace('/','\\')
        
        subprocess.Popen("%s -q -txt %s" % (self.xml_data.Domuspath, name_project)).wait()
        
        ''' computation and saving of the name of the folder where the domus results were saved'''
        ''' we have to define project_name: the name of the idf use for the domus simulation, it is can be find like this:
        self.xml_data.domus_project_directory+project_name+'.idf
        then :'''
        lenth = len(self.xml_data.domus_project_directory)
        project_name = self.xml_data.file_name_idf_domus[lenth+1:-4]#self.xml_data.file_name_idf_domus.split('/')[-1][:-4]
        self.xml_data.domus_results_directory = self.xml_data.domus_project_directory+'/#'+project_name+"/saidas/"
        estadoSimdirectory = self.xml_data.domus_results_directory+'estadoSim/'
        if os.path.exists(self.xml_data.domus_results_directory):
            ''' if the directory already exist'''
            liste = os.listdir(self.xml_data.domus_results_directory)
            
            number_sim = liste[-1]
            liste.remove('estadoSim')
            if 'lastPixelcount' in liste:
                liste.remove('lastPixelcount')
            if 'pixelcount' in liste:    
                liste.remove('pixelcount')
            date_ref = os.path.getctime(self.xml_data.domus_results_directory+liste[-1])
            for i in xrange(1,len(liste)):
                if os.path.getctime(self.xml_data.domus_results_directory+liste[-1-i])>date_ref:
                    number_sim = liste[-1-i][-3:]
            self.xml_data.domus_results_directory = self.xml_data.domus_results_directory+number_sim+'/'
        else:
            self.xml_data.domus_results_directory = self.xml_data.domus_results_directory+project_name+'/sim001/'
        ''' these new data are saved'''   
        self.xml_data.write_data(self.xml_file)
        if copyestadosim:
            ''' the result of domus simulation are moved to an other result folder where are the coupled simulation results'''
            folder1 = self.xml_data.domus_results_directory
            folder2 = os.path.join(self.xml_data.file_name_results_case,'simDomus')
            to_move_folder1_in_folder2(folder1,folder2)
            print ' the result of domus simulation are moved from ',folder1, 'to ',folder2
            
    #         if os.path.exists(os.path.join(self.xml_data.file_name_results_case,'simDomus')):
    #             shutil.rmtree(os.path.join(self.xml_data.file_name_results_case,'simDomus'))
    #         shutil.copytree(self.xml_data.domus_results_directory,os.path.join(self.xml_data.file_name_results_case,'simDomus'))
    # #         os.remove(self.xml_data.domus_results_directory)
    #         shutil.rmtree(self.xml_data.domus_results_directory)
            to_move_folder1_in_folder2(estadoSimdirectory,os.path.join(self.xml_data.file_name_results_case,'simDomus/estadoSim'))
    #         shutil.copytree(estadoSimdirectory,os.path.join(self.xml_data.file_name_results_case,'simDomus/estadoSim'))
            self.xml_data.domus_estadoSim_directory = os.path.join(self.xml_data.file_name_results_case,'simDomus/estadoSim/')
            self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
            self.batidf.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory_init
        
    def simu_ansys_wiht_cfd_data_base(self,initialisation_folder_name = ''): 
        self.month,self.days,self.hours = self.monthi,self.daysi,self.hoursi
        self.cfx_model.month,self.cfx_model.days,self.cfx_model.hours = self.month,self.days,self.hours    
        self.cfx_model.meteo_directory = self.xml_data.meteo_directory
        
        
        self.define_boundary_CFX()

        print(' direction du vent ='+str( self.cfx_model.direction ))
        print(' vitesse du vent = '+str( self.cfx_model.velocity))
        print ('temperature meteo = '+str( self.cfx_model.Tref))
        
#         self.assign_one_temperature_to_CFX_boundary(self.cfx_model.Tref)
        self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
        self.cfx_model.interactive_mode = self.xml_data.ansysinteractive_mode
        ''' creation of the folder results of the case'''
        case_name = str(int(self.cfx_model.direction))+'_'+str(self.cfx_model.velocity).replace(".", "-")#+'_'+str(self.cfx_model.Tref).replace(".", "-")
        self.xml_data.file_name_results_case = self.xml_data.file_name_cfd_data_base_results+case_name#self.xml_data.file_name_results+case_name
        ''' if the simu case doesn't existe, the folder is created and the simulation is executed'''
        self.cfx_model.create_script()
        if initialisation_folder_name== '':
            initialisation_folder_name = self.check_data_in_meteo_par_simu_cfd(self.cfx_model.direction,self.cfx_model.velocity,
                                              self.cfx_model.Tref,self.xml_data.file_name_results_case)
            
        else:
            self.cfx_model.script.IC_option = True
            self.cfx_model.script.IC_filename = initialisation_folder_name#+r'/simCFX/Fluid Flow CFX.res'
            self.cfx_model.script.max_iteration_number = 50
            
        if self.cfx_model.script.buoyancy_option:
            self.cfx_model.script.max_iteration_number = 300

        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        self.cfx_model.script.def_file = self.xml_data.file_name_ansys_files+r'dp0\CFX\CFX\Fluid Flow CFX.def'
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+r'/changer_TS_et_simuler.wbjn'#+r'\sim_janela_files\creer_projetbis2.wbjn'
        if self.cfx_model.script.ccl_option:
            self.cfx_model.script.ccl_file_name = self.xml_data.domus_project_directory+r'/simu_parameter.ccl'#
        self.run_and_save_ansys_simu()
        
#         result_folder = self.xml_data.file_name_results_case#os.path.join(self.xml_data.file_name_results_case,'simCFX')
#         ''' creation of the folder results of the case'''
#         case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi#+'_'+str(self.cfx_model.Tref).replace(".", "-")
#         
#         self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name
#         if os.path.exists(os.path.join(self.xml_data.file_name_results_case,'simCFX')):
#             shutil.rmtree(os.path.join(self.xml_data.file_name_results_case,'simCFX'))
#         shutil.copytree(result_folder,os.path.join(self.xml_data.file_name_results_case,'simCFX'))
#         if not os.path.exists(self.xml_data.file_name_results_case):
#             os.makedirs(self.xml_data.file_name_results_case)


    def simu_ansys_using_domus_results(self):   

#         self.cfx_model = Model_CFX()
#         self.cfx_model.pickleloading_keys(self.xml_data.file_name_cfx_class,'list_boundary')
        self.cfx_model.month,self.cfx_model.days,self.cfx_model.hours = self.month,self.days,self.hours    
        self.cfx_model.meteo_directory = self.xml_data.meteo_directory
        
        
        self.define_boundary_CFX()
#         self.cfx_model.direction = 180.0
#         self.cfx_model.velocity = 2.0
        print(' direction du vent ='+str( self.cfx_model.direction ))
        print(' vitesse du vent = '+str( self.cfx_model.velocity))
        if self.cfx_model.velocity==0.0:
            self.cfx_model.velocity=0.001
            print (' attention la vitesse de reference est egale a zero, la simulation ne pourra pas marcher')
            print('la vitesse a ete remplace par 0.001')
#             f = input()
        print ('temperature meteo = '+str( self.cfx_model.Tref))
#         print' les temperatures de surfaces interieurs sont'
#         for name in self.domus_results.ts_int_dic.keys():
#             print 'pour ',name,' ts =',self.domus_results.ts_int_dic[name][self.cfx_model.month][self.cfx_model.days][self.cfx_model.hours][0]
#         print' les temperatures de surfaces exterieurs sont'
#         for name in self.domus_results.ts_dic.keys():
#             print 'pour ',name,' ts =',self.domus_results.ts_dic[name][self.cfx_model.month][self.cfx_model.days][self.cfx_model.hours][0]
        self.cfx_model.create_script()
        initialisation_folder_name = self.check_data_in_meteo_par_simu_cfd(self.cfx_model.direction,self.cfx_model.velocity,
                                              self.cfx_model.Tref,self.xml_data.file_name_results_case)
        if initialisation_folder_name==False:
            self.cfx_model.script.IC_option = False
            self.cfx_model.script.IC_filename = ''
        else:
            self.cfx_model.script.IC_option = True
            self.cfx_model.script.IC_filename = initialisation_folder_name+r'/simCFX/Fluid Flow CFX.res'
        print ('results_case :'+self.xml_data.file_name_results_case)
        print ('IC_option :'+str(self.cfx_model.script.IC_option))
        print ('IC_filename :'+self.cfx_model.script.IC_filename)
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        self.cfx_model.script.def_file = self.xml_data.file_name_ansys_files+r'dp0\CFX\CFX\Fluid Flow CFX.def'
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+r'/changer_TS_et_simuler.wbjn'#+r'\sim_janela_files\creer_projetbis2.wbjn'
        self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
        self.run_and_save_ansys_simu()
        

        
    def run_and_save_ansys_simu(self,mode = 'w'):
        
        ''' all the boundary condition are write in the ansys script:'''
        self.cfx_model.script.write_change_boundary_run_simulation_cfx(mode)
#         name_file = self.xml_data.file_name_results_case+'/CHTC_TA.txt'

        ''' a script to save  and export   mean value of Ta, CHTC, Cp,...  the txt file name_file is writed:'''
        name_file = os.path.join(self.xml_data.domus_project_directory+'//'+self.xml_data.project_name+'_CFX_files//dp0//CFX//CFX//CHTC_TA.txt')
        self.cfx_model.save_table_value(name_file)
        ''' results are created to be able to use postprocessing'''
#         self.cfx_model.script.run_cfxsolver()
        
        ''' the ansys script is ran'''
#         print 'attention modification ligne 561 de coupled simulation'
        self.cfx_model.script.run_script()
        ''' after the simulation was done the results are copied in a new folder'''
#         time_of_the_simu = time.strftime('%d_%m_%y_%H_%M_%S',time.localtime()) 
#         result_folder = os.path.join(self.xml_data.domus_project_directory+'//'+self.xml_data.project_name+'_CFX_files//dp0//CFX//CFX//')
#         shutil.copytree(result_folder,os.path.join(self.xml_data.file_name_result_ansys,'time_of_the_simu))
        file_name =  os.path.join(self.xml_data.domus_project_directory+'//'+self.xml_data.project_name+'_CFX_files//dp0//CFX//CFX//')
        
        liste = os.listdir(file_name)
        date = 0
        for i in liste:
            if i[-3:]=='res':
                date_ref = os.path.getctime(file_name+'\\'+i)
                if date_ref>date:
                    name = file_name+'\\'+i
                    date = date_ref
#             else:
#                 os.remove(file_name+'\\'+i)

        if 'Fluid Flow CFX.res' in liste:
            os.remove(file_name+'\\'+'Fluid Flow CFX.res')
        # print'attention les lignes 595 et596 de coupled simulation ne sont pas execute'   
        os.rename(name,file_name+'\\'+'Fluid Flow CFX.res') 
        ''' if there are no bouyancy effect the results are save in the cfd data base:'''
        if self.cfx_model.script.buoyancy_option==False:
            ''' creation of the folder in cfd_data_base'''
            if not os.path.exists(self.xml_data.file_name_results_case):
                
                os.makedirs(self.xml_data.file_name_results_case) 
            result_folder = os.path.join(self.xml_data.domus_project_directory+'//'+self.xml_data.project_name+'_CFX_files//dp0//CFX//CFX//')
            ''' if the folder self.xml_data.file_name_results_case already existe, it is deleted to be able to save in folder with the same name'''
            if os.path.exists(self.xml_data.file_name_results_case):
                shutil.rmtree(self.xml_data.file_name_results_case)
            shutil.copytree(result_folder,self.xml_data.file_name_results_case)#result_folder,os.path.join(self.xml_data.file_name_results_case,'simCFX'))
        else:
            self.xml_data.file_name_results_case = os.path.join(self.xml_data.domus_project_directory+'//'+self.xml_data.project_name+'_CFX_files//dp0//CFX//CFX//')
            ''' the result file .res in this new folder is renamed in '''
        
    def assigned_normal_vector_boundary(self):
        
        ''' function to add in the dictionnary self.list_boundary, the key 'normal_vector'
        '''
    def read_ansys_result_file(self,file_name):
        
        file = open(file_name,'r')
        self.liste_file = file.readlines()
        self.table_idf = []
        for i in xrange(len(self.liste_file)):
#             print(self.liste_idf_file[i])
             
            # vérification lignes vides
            if self.liste_file[i] != '\r\n' and self.liste_file[i] != '\n':
                self.table_idf.append(self.liste_file[i].split())
#                 print(self.table_idf[-1])
    def create_postraitement(self):
        ''' function create a user_surface located at the distance equal to 'distance' from each surface of the model'''
        self.cfx_model.script.file_name_script = self.cfx_model.ansys_directory+ r"/creationresults.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_script()
        self.cfx_model.script.define_script()
        self.cfx_model.script.write_open_project()
        self.cfx_model.script.create_results()
        self.cfx_model.script.f.close()
        self.cfx_model.script.run_script()
        

    def create_postraitement_user_surface(self,distance = '0.5'):
        ''' function create a user_surface located at the distance equal to 'distance' from each surface of the model'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/creationusersurface.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.create_user_surface_and_table()
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):#if name in self.domus_results.ts_dic:       
                name_user_surface = name+'us'
                self.cfx_model.script.create_user_surface_offset(name,distance,name_user_surface)
        self.cfx_model.script.create_table()       
        self.cfx_model.script.save_and_run()
        
    def save_table_value(self,table_title = 'Table 1 '):
        ''' function to save values in the table in CFX (where average values (temperature, velocity,...) are resumed) in a txt file'''
#         hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+self.hours+'H.txt'
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
#         self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.write_save_table(name_file,table_title)         
        
        
    def create_postraitement_user_surface_average_value(self):
        ''' function to compute the average temperature Ta for each user surfaces associated to each surface'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:       
                name_user_surface = name+'us'
                TA_expression_name = 'TA'+name
                Vel_expression_name = 'VEL'+name
                self.cfx_model.script.compute_average_temperature(name_user_surface,TA_expression_name)
                self.cfx_model.script.compute_average_velocity(name_user_surface,Vel_expression_name)
#         self.cfx_model.script.create_table() 
        ''' writing of titles'''   
        self.cfx_model.script.write_value_in_cell_table('A1','nom')  
        self.cfx_model.script.write_value_in_cell_table('B1','Temperature[K]')
        self.cfx_model.script.write_value_in_cell_table('C1','velocity[m.s-1]')
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):#if name in self.domus_results.ts_dic:     
                index+=1  
                
                TA_expression_name = 'TA'+name
                Vel_expression_name = 'VEL'+name
                self.cfx_model.script.write_value_in_cell_table('A'+str(index),name)  
                self.cfx_model.script.write_value_in_cell_table('B'+str(index),'='+TA_expression_name)
                self.cfx_model.script.write_value_in_cell_table('C'+str(index),'='+Vel_expression_name)
        
        self.save_table_value()
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file)         
#         self.cfx_model.script.save_and_run()
        
    def create_postraitement_CHTC_and_temperature_wall(self):
        table_name = 'table_CHTC_TA'
        ''' function to compute the chtc and near wall temperature for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.create_table(table_name)  
        self.cfx_model.script.write_value_in_cell_table('A1','nom','3',table_name)  
        self.cfx_model.script.write_value_in_cell_table('B1','CHTC','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('C1','Ta','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('D1','CHT','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('E1','Cp','3',table_name)
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
                index+=1 
                self.cfx_model.script.write_value_in_cell_table('A'+str(index),name,'3',table_name)
                CHTC_name = 'CHTC'+name
                expression_name = 'areaAve(Wall Heat Transfer Coefficient)@'+name
                self.cfx_model.script.define_cel_expression_result(CHTC_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('B'+str(index),'='+CHTC_name,'6',table_name) 
                Ta_name = 'Ta'+name
                Taexpression_name = 'areaAve(Wall Adjacent Temperature)@'+name
                self.cfx_model.script.define_cel_expression_result(Ta_name , Taexpression_name)
                self.cfx_model.script.write_value_in_cell_table('C'+str(index),'='+Ta_name,'6',table_name) 
                CHT_name = 'CHT'+name
                CHTexpression_name = 'areaAve(Wall Heat Flux)@'+name
                self.cfx_model.script.define_cel_expression_result(CHT_name , CHTexpression_name)
                self.cfx_model.script.write_value_in_cell_table('D'+str(index),'='+CHT_name,'6',table_name) 
                Cp_name = 'Cp'+name
                Cpexpression_name = 'areaAve(Pressurecoef)@'+name
                self.cfx_model.script.define_cel_expression_result(Cp_name , Cpexpression_name)
                self.cfx_model.script.write_value_in_cell_table('E'+str(index),'='+Cp_name,'6',table_name) 
#                 if index>2:
#                     break
                
#         self.cfx_model.script.write_value_in_cell_table('C1','Ta','table_CHTC_TA')
#         index=1 
#         for name in self.cfx_model.list_boundary.keys():
#             if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
#                 index+=1  
#                 Ta_name = 'Ta'+name
#                 expression_name = 'areaAve(Wall Adjacent Temperature)@'+name
#                 self.cfx_model.script.define_cel_expression_result(Ta_name , expression_name)
#                 self.cfx_model.script.write_value_in_cell_table('C'+str(index),'='+Ta_name,'6','table_CHTC_TA') 
        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value('table_CHTC_TA')
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file)
        self.cfx_model.script.ANSYS_path = self.xml_data.ANSYS_path
        self.cfx_model.script.interactive_mode = self.xml_data.ansysinteractive_mode
        self.cfx_model.script.run_script()

    def create_postraitement_CHTC_and_temperature_wall2(self):
        table_name = 'table_CHTC_TA'
        ''' function to compute the chtc and near wall temperature for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.create_table(table_name)  
        self.cfx_model.script.write_value_in_cell_table('A1','nom','3',table_name)  
        self.cfx_model.script.write_value_in_cell_table('B1','CHTC','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('C1','Ta','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('D1','CHT','3',table_name)
        self.cfx_model.script.write_value_in_cell_table('E1','Cp','3',table_name)
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
                index+=1 
                self.cfx_model.script.write_value_in_cell_table('A'+str(index),name,'3',table_name)
                CHTC_name = 'CHTC'+name
                expression_name = 'areaAve(Wall Heat Transfer Coefficient)@'+name
#                 self.cfx_model.script.define_cel_expression_result(CHTC_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('B'+str(index),'='+expression_name,'6',table_name) 
                Ta_name = 'Ta'+name
                Taexpression_name = 'areaAve(Wall Adjacent Temperature)@'+name
#                 self.cfx_model.script.define_cel_expression_result(Ta_name , Taexpression_name)
                self.cfx_model.script.write_value_in_cell_table('C'+str(index),'='+Taexpression_name,'6',table_name) 
                CHT_name = 'CHT'+name
                CHTexpression_name = 'areaAve(Wall Heat Flux)@'+name
#                 self.cfx_model.script.define_cel_expression_result(CHT_name , CHTexpression_name)
                self.cfx_model.script.write_value_in_cell_table('D'+str(index),'='+CHTexpression_name,'6',table_name) 
                Cp_name = 'Cp'+name
                Cpexpression_name = 'areaAve(Pressurecoef)@'+name
#                 self.cfx_model.script.define_cel_expression_result(Cp_name , Cpexpression_name)
                self.cfx_model.script.write_value_in_cell_table('E'+str(index),'='+Cpexpression_name ,'6',table_name) 

        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value('table_CHTC_TA')
        
        table_name = 'table_mass_flow'
        self.cfx_model.script.create_table(table_name)  
        self.cfx_model.script.write_value_in_cell_table('A1','nom','3',table_name)  
        self.cfx_model.script.write_value_in_cell_table('B1','massflow [kg/s]','3',table_name)

        index=1 
        for name in self.cfx_model.list_interfaces.keys():
             
            index+=1 
            self.cfx_model.script.write_value_in_cell_table('A'+str(index),name,'3',table_name)
            
            expression_name = 'sum(Mass Flow)@'+name+' Side 1'
            self.cfx_model.script.write_value_in_cell_table('B'+str(index),'='+expression_name,'6',table_name) 
            

        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value('table_mass_flow')
        self.cfx_model.script.save_and_run()

    def create_postraitement_convective_flux(self):
        ''' function to compute the chtc and near wall temperature for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.create_table()  
        self.cfx_model.script.write_value_in_cell_table('A1','Qconv')
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
                index+=1  
                CHTC_name = 'Qconv'+name
                expression_name = 'sum(Wall Heat Flux*Area)@'+name
                self.cfx_model.script.define_cel_expression_result(CHTC_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('A'+str(index),'='+CHTC_name,'6') 
                
        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value()
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file)   
    def create_postraitement_pressure_coefficent(self):
        ''' function to compute the pressure coefficient for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.write_value_in_cell_table('D1','Cp')
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
                index+=1  
                CP_name = 'CP'+name
                expression_name = 'areaAve(Pressurecoef )@'+name
                self.cfx_model.script.define_cel_expression_result(CP_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('D'+str(index),'='+CP_name,'6') 
        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value()
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file) 
        
    def create_postraitement_h_coefficent(self):
        ''' function to compute the convective heat transfert coefficient (CHTC) for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.write_value_in_cell_table('D1','CHTC')
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:     
                index+=1  
                CHTC_name = 'CHTC'+name
                expression_name = 'areaAve(Pressurecoef )@'+name
                self.cfx_model.script.define_cel_expression_result(CHTC_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('D'+str(index),'='+CHTC_name,'6') 
        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value()
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file)        
#         self.cfx_model.script.save_and_run()
        
    def create_postraitement_coefficent(self,colome_name = 'A',coef_name = 'Cp'):
        ''' function to compute the convective heat transfert coefficient (CHTC0 for each surface of building'''
        self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+ r"/computaveragevalues.wbjn"
        self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.cfx_model.script.write_new_post_proc_script()
        self.cfx_model.script.write_value_in_cell_table(colome_name+'1',coef_name)
        index=1 
        for name in self.cfx_model.list_boundary.keys():
            if name.find('atmosphere')==-1:# name not in self.domus_results.ts_dic:     
                index+=1  
                CP_name = coef_name+name
                expression_name = 'areaAve(Pressurecoef )@'+name
                self.cfx_model.script.define_cel_expression_result(CP_name , expression_name)
                self.cfx_model.script.write_value_in_cell_table('E'+str(index),'='+CP_name,'6') 
        hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        self.save_table_value()
#         name_file = self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+hours+'.txt'
#         self.cfx_model.script.save_table(name_file)        
#         self.cfx_model.script.save_and_run()

    def complet_batidfBC_from_meteo_data(self,m,d,h):      
        temperature = self.meteo_data[str(m)][str(d)][str(h)]['temperature']
        for domus_name in self.batidf.dico_BC.keys():
            #self.batidf.dico_BC[domus_name]['Ta_ext'] = temperature 
            self.batidf.dico_BC[domus_name]['Cond_ext'] = np.zeros(8)
            self.batidf.dico_BC[domus_name]['Cond_extB'] = np.ones(8)
            self.batidf.dico_BC[domus_name]['Cond_int'] = np.zeros(8)
            self.batidf.dico_BC[domus_name]['Cond_intB'] = np.ones(8)
            self.batidf.dico_BC[domus_name]['Cond_ext'][0] = temperature 
            self.batidf.dico_BC[domus_name]['Cond_extB'][0] = 1
            self.batidf.dico_BC[domus_name]['Cond_int'][0] = 0 
            self.batidf.dico_BC[domus_name]['Cond_intB'][0] = 0
            
            
    def complet_batidfBC_from_ansys(self,file_name = ''):
        ''' function to read results value from ansys cfx simulation and complet self.batidf.dico_BC
        '''
#         hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
        if file_name== '':
            file_name = self.xml_data.file_name_results_case+'/simCFX/CHTC_TA.txt'#self.xml_data.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+self.hours+'H.txt'
         
        idf_file = open(file_name,'r')
        liste_idf_file = idf_file.readlines()
        table_idf = []
        for i in xrange(len(liste_idf_file)):
#             print(liste_idf_file[i])
              
                #vérification lignes vides
            if liste_idf_file[i] != '\r\n' and liste_idf_file[i] != '\n':
                table_idf.append(liste_idf_file[i].split())
        dico = {}
        liste_variable = []
        for i in xrange(1,len(table_idf[0])):
            liste_variable.append(table_idf[0][i])
        for i in xrange(1,len(table_idf)):
            nom = table_idf[i][0]
    
            dico[nom] = {}
            for j in xrange(len(liste_variable)):
                dico[nom][liste_variable[j]] = table_idf[i][j+1]
                
        for nom in dico:
#             print'name = ',nom
#             if nom in self.batidf.name_connection:
#                 domus_name = self.batidf.name_connection[nom]
#                 self.batidf.dico_BC[domus_name]['temperature_int'] = str(float(dico[nom]['Temperature[K]'])-273.15)+','
#                 self.batidf.dico_BC[domus_name]['velocity_int'] = dico[nom]['velocity[m.s-1]']+','
#                 self.batidf.dico_BC[domus_name]['hc_int'] = str(5.85+float(dico[nom]['velocity[m.s-1]'])*1.7)+','
#                 self.batidf.dico_BC[domus_name]['Cp_int'] = dico[nom]['Cp']+','
#             elif nom[:-3] in self.batidf.name_connection:
            if nom[-3:]=='ext':
                domus_name = self.batidf.name_connection[nom[:-3]]
                #self.batidf.dico_BC[domus_name]['Ta_ext'] = float(dico[nom]['Ta'])-273.15
                self.batidf.dico_BC[domus_name]['Cond_ext'][0] = float(dico[nom]['Ta'])-273.15
                self.batidf.dico_BC[domus_name]['Cond_extB'][0] = 0
#                 self.batidf.dico_BC[domus_name]['Cond_int'][0] = 27
#                 self.batidf.dico_BC[domus_name]['Cond_intB'][0] = 1

                
                self.batidf.dico_BC[domus_name]['hc_ext'] = float(dico[nom]['CHTC'])
                if 'Cp' in dico[nom].keys():
                    self.batidf.dico_BC[domus_name]['Cp_ext'] = dico[nom]['Cp']
                if 'CHT' in dico[nom].keys():
                    self.batidf.dico_BC[domus_name]['CHT_ext'] = dico[nom]['CHT']
#                 self.batidf.dico_BC[domus_name]['temperature_ext'] = float(dico[nom]['Temperature[K]'])-273.15
#                 self.batidf.dico_BC[domus_name]['velocity_ext'] = float(dico[nom]['velocity[m.s-1]'])
#                 self.batidf.dico_BC[domus_name]['hc_ext'] = 5.85+float(dico[nom]['velocity[m.s-1]'])*1.7
#                 self.batidf.dico_BC[domus_name]['Cp_ext'] = dico[nom]['Cp']+','
            else:
                domus_name = self.batidf.name_connection[nom]
                #self.batidf.dico_BC[domus_name]['Ta_int'] = float(dico[nom]['Ta'])-273.15
                self.batidf.dico_BC[domus_name]['Cond_int'][0] = float(dico[nom]['Ta'])-273.15
                self.batidf.dico_BC[domus_name]['Cond_intB'][0] = 0
                
                self.batidf.dico_BC[domus_name]['hc_int'] = float(dico[nom]['CHTC'])
                if 'Cp' in dico[nom].keys():
                    self.batidf.dico_BC[domus_name]['Cp_int'] = dico[nom]['Cp']
                if 'CHT' in dico[nom].keys():
                    self.batidf.dico_BC[domus_name]['CHT_int'] = dico[nom]['CHT']
#                 self.batidf.dico_BC[domus_name]['temperature_int'] = float(dico[nom]['Temperature[K]'])-273.15
#                 self.batidf.dico_BC[domus_name]['velocity_int'] = float(dico[nom]['velocity[m.s-1]'])
#                 self.batidf.dico_BC[domus_name]['hc_int'] = 5.85+float(dico[nom]['velocity[m.s-1]'])*1.7
#                 self.batidf.dico_BC[domus_name]['Cp_int'] = dico[nom]['Cp']+','
        
        
    def write_result_from_ansys_to_domus(self,file_name_result):
        
        self.complet_idfBC_from_ansys()
                
#         file_name_results =  file_name = 'D:/Users/adrien.gros/Documents/domus_project/casa_1janela/results_1_1_07H00M00.txt'   
        f = open(file_name_result,'w')
        f.write('nome\t')    
        f.write('temperatura_int,temperatura_ext,hc_int,hc_ext,velocidade_int,velocidade_ext,Cp_int,Cp_ext')
        f.write('\n')
        
        for nom in self.batidf.dico_BC:
            f.write('%s'% (nom))
            f.write('\t')        
            f.write('%s'% (self.batidf.dico_BC[nom]['temperature_int']))
            f.write('%s'% (self.batidf.dico_BC[nom]['temperature_ext']))
            f.write('%s'% (self.batidf.dico_BC[nom]['hc_int']))
            f.write('%s'% (self.batidf.dico_BC[nom]['hc_ext']))        
            f.write('%s'% (self.batidf.dico_BC[nom]['velocity_int']))
            f.write('%s'% (self.batidf.dico_BC[nom]['velocity_ext']))
            f.write('%s'% (self.batidf.dico_BC[nom]['Cp_int']))
            f.write('%s'% (self.batidf.dico_BC[nom]['Cp_ext']))
            
            f.write('\n')
        f.close()
        
    def from_idfBC_to_CFD_boundary(self):
        ''' function to transfert temperature result from batidf.dico_BC to cfx_model.list_boundary'''
        
        for i in xrange(len(self.batidf.dico_surface)):
            domus_name =self.batidf.dico_surface[i]['domus_name']
            name = self.batidf.dico_surface[i]['name']
        
            
            nameext = name+'ext'
            if name in self.cfx_model.list_boundary.keys():
                self.cfx_model.list_boundary[name]['temperature_celsius'] = self.batidf.dico_BC[domus_name]['temperature_int']
            if nameext in self.cfx_model.list_boundary.keys():    
                self.cfx_model.list_boundary[nameext]['temperature_celsius'] = self.batidf.dico_BC[domus_name]['temperature_ext']
                
        for i in xrange(len(self.batidf.dico_fenes_surface)):
            domus_name =self.batidf.dico_fenes_surface[i]['domus_name']
            name = self.batidf.dico_fenes_surface[i]['name']
        
            
            nameext = name+'ext'
            if name in self.cfx_model.list_boundary.keys():
                self.cfx_model.list_boundary[name]['temperature_celsius'] = self.batidf.dico_BC[domus_name]['temperature_int']
            if nameext in self.cfx_model.list_boundary.keys():    
                self.cfx_model.list_boundary[nameext]['temperature_celsius'] = self.batidf.dico_BC[domus_name]['temperature_ext']
                
    def assign_one_temperature_to_CFX_boundary(self,temperature = 20):
        ''' function to assigne the same temperature for boundary condition in CFX'''
        
        for name in self.cfx_model.list_boundary:
            self.cfx_model.list_boundary[name]['temperature_celsius'] = temperature
        
        


    def check_data_in_meteo_par_simu_cfd(self,orientation,velocity,temperature,folder_name):
        
        ''' function to check if orientation,velocity and temperature are already in self.meteo_par_simu_cfd''' 
#         self.max_iteration_number = 200          
            
        if orientation not in  self.meteo_par_simu_cfd.keys():
            self.meteo_par_simu_cfd[orientation] = {}                
            self.meteo_par_simu_cfd[orientation][velocity] = {}
            
            initialisation_folder_name = False
            self.meteo_par_simu_cfd[orientation][velocity] = folder_name+r'/Fluid Flow CFX.res'#[temperature] = folder_name
            self.cfx_model.script.max_iteration_number = 600
            

        else:
            if velocity not in self.meteo_par_simu_cfd[orientation].keys():
                liste_vel = self.meteo_par_simu_cfd[orientation].keys()
                id_init_vel = min(range(len(liste_vel)), key=lambda i:abs(liste_vel[i]-velocity))
                init_vel = liste_vel[id_init_vel]
                initialisation_folder_name = self.meteo_par_simu_cfd[orientation][init_vel]
#                 liste_temp = self.meteo_par_simu_cfd[orientation][init_vel].keys()
#                 id_init_temp = min(range(len(liste_temp)), key=lambda i:abs(liste_temp[i]-temperature))
#                 init_temp = liste_temp[id_init_temp]
#                 initialisation_folder_name = self.meteo_par_simu_cfd[orientation][init_vel][init_temp]
              
                
                
                self.meteo_par_simu_cfd[orientation][velocity] = {} 
                self.meteo_par_simu_cfd[orientation][velocity] = folder_name+r'/Fluid Flow CFX.res'#[temperature] = folder_name
                self.cfx_model.script.max_iteration_number = 600
                
            else:
#                 if temperature not in self.meteo_par_simu_cfd[orientation][velocity].keys():
#                     init_temp = max(self.meteo_par_simu_cfd[orientation][velocity].keys())
#                     liste_temp = self.meteo_par_simu_cfd[orientation][velocity].keys()
#                     id_init_temp = min(range(len(liste_temp)), key=lambda i:abs(liste_temp[i]-temperature))
#                     init_temp = liste_temp[id_init_temp]
#                     initialisation_folder_name = self.meteo_par_simu_cfd[orientation][velocity][init_temp]
#                     self.meteo_par_simu_cfd[orientation][velocity][temperature] = folder_name
#                     self.max_iteration_number = 50
#                 else:
                initialisation_folder_name = self.meteo_par_simu_cfd[orientation][velocity]#+r'/Fluid Flow CFX.res'#[temperature]
                self.cfx_model.script.max_iteration_number = 600#50
                    
        cPickle.dump(self.meteo_par_simu_cfd,open(self.xml_data.domus_project_directory+'/meteo_par_simu_cfd','wb'))
        if initialisation_folder_name==False:
            self.cfx_model.script.IC_option = False
            self.cfx_model.script.IC_filename = ''
        else:
            self.cfx_model.script.IC_option = True
            self.cfx_model.script.IC_filename = initialisation_folder_name
        return initialisation_folder_name
#     def initialisation_with_old_result(self):  
    def check_data_in_meteo_par_simu_cfd_anisotherme(self,orientation,velocity,temperature,folder_name):
        
        ''' function to check if orientation,velocity and temperature are already in self.meteo_par_simu_cfd''' 
#         self.max_iteration_number = 200          
        self.meteo_par_simu_cfd_anisotherme = {}    
        if orientation not in  self.meteo_par_simu_cfd.keys():
            self.meteo_par_simu_cfd[orientation] = {}                
            self.meteo_par_simu_cfd[orientation][velocity] = {}
            
            initialisation_folder_name = False
            self.meteo_par_simu_cfd[orientation][velocity] = folder_name+r'/Fluid Flow CFX.res'#[temperature] = folder_name
            self.cfx_model.script.max_iteration_number = 600
            

        else:
            if velocity not in self.meteo_par_simu_cfd[orientation].keys():
                liste_vel = self.meteo_par_simu_cfd[orientation].keys()
                id_init_vel = min(range(len(liste_vel)), key=lambda i:abs(liste_vel[i]-velocity))
                init_vel = liste_vel[id_init_vel]
                #initialisation_folder_name = self.meteo_par_simu_cfd[orientation][init_vel]
                liste_temp = self.meteo_par_simu_cfd[orientation][init_vel].keys()
                id_init_temp = min(range(len(liste_temp)), key=lambda i:abs(liste_temp[i]-temperature))
                init_temp = liste_temp[id_init_temp]
                initialisation_folder_name = self.meteo_par_simu_cfd[orientation][init_vel][init_temp]
              
                
                
                self.meteo_par_simu_cfd[orientation][velocity] = {} 
                self.meteo_par_simu_cfd[orientation][velocity] = folder_name+r'/Fluid Flow CFX.res'#[temperature] = folder_name
                self.cfx_model.script.max_iteration_number = 600
                
            else:

                if temperature not in self.meteo_par_simu_cfd[orientation][velocity].keys():
                    init_temp = max(self.meteo_par_simu_cfd[orientation][velocity].keys())
                    liste_temp = self.meteo_par_simu_cfd[orientation][velocity].keys()
                    id_init_temp = min(range(len(liste_temp)), key=lambda i:abs(liste_temp[i]-temperature))
                    init_temp = liste_temp[id_init_temp]
                    initialisation_folder_name = self.meteo_par_simu_cfd[orientation][velocity][init_temp]
                    self.meteo_par_simu_cfd[orientation][velocity][temperature] = folder_name
                    self.max_iteration_number = 50
#                 else:
                else:
                    initialisation_folder_name = self.meteo_par_simu_cfd[orientation][velocity]#+r'/Fluid Flow CFX.res'#[temperature]
                    self.cfx_model.script.max_iteration_number = 600#50
                    
        cPickle.dump(self.meteo_par_simu_cfd,open(self.xml_data.domus_project_directory+'/meteo_par_simu_cfd','wb'))
        if initialisation_folder_name==False:
            self.cfx_model.script.IC_option = False
            self.cfx_model.script.IC_filename = ''
        else:
            self.cfx_model.script.IC_option = True
            self.cfx_model.script.IC_filename = initialisation_folder_name
        return initialisation_folder_name
#     def initialisation_with_old_result(self):   
    
    def radiative_coupling_method(self,iteration_number = 3):
        ''' creation of the folder results of the case'''
        case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi
        self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_0'
        ''' if the folder is already existing, it is deleted'''
        if not os.path.exists(self.xml_data.file_name_results_case):
            os.makedirs(self.xml_data.file_name_results_case)
            
        ''' the simulation date are changed in idf file'''
        ''' dans DOMUS pour simuler 1h, il faut que l'heure final soit egal a l'heure initial
        exemple si on indique hi = 13h, et hf = 14, domus va simuler 13h et 14h, soit de 13h a 15h
        si on indique hi = 13h, et hf = 13, domus va simuler de 13h a 14h
        '''
        self.domus_comand.change_simulation_date(self.monthi,self.daysi,self.hoursi,self.monthf,self.daysf,self.hoursf)
        print('iteration n°0')
        self.copy_estadosim_init()
        #self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory)(self.domus_estadoSim_directory) 
        self.run_domus_simu()
        initialisation_CFXfolder_name = ''
        for i in xrange(iteration_number):
            print('iteration n°'+str(i+1))
            self.read_AC_heat_source()
            self.batidf.complete_ts_BC_with_bin_estadosim()
            
            tsky = self.meteo_data[str(self.monthi)][str(self.daysi)][str(self.hoursi)]['sky_temp']
            self.radiative_model.lw_model.ts_array = self.build_ts_array(tsky)
            self.radiative_model.lw_model.net_irradiance_from_ts(tsky)
            

            self.complet_batidfBC_with_radiation(self.radiative_model.dict_FF,self.radiative_model.lw_model.net_irradiance_array)
            
            
            self.from_idfBC_to_CFD_boundary()
            self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
            self.month,self.days,self.hours = self.monthi,self.daysi,self.hoursi
            ''' creation of the folder results of the case'''
            case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi#+'_'+str(self.cfx_model.Tref).replace(".", "-")
             
            self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_'+str(i+1)
            
            
            """            if i>=2:
                self.cfx_model.script.buoyancy_option = True
            else:
                self.cfx_model.script.buoyancy_option = False
            
            
            ''' the simulation is writed then runed. The results are saved only if there are no bouyancy effect:''' 
            self.simu_ansys_wiht_cfd_data_base(initialisation_CFXfolder_name)
#         self.simu_ansys_using_domus_results()
            
            result_folder = self.xml_data.file_name_results_case#os.path.join(self.xml_data.file_name_results_case,'simCFX')
            self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_'+str(i+1)
            file_name_results_case_CFX = os.path.join(self.xml_data.file_name_results_case,'simCFX')
            if os.path.exists(file_name_results_case_CFX):
                shutil.rmtree(file_name_results_case_CFX)
            shutil.copytree(result_folder,file_name_results_case_CFX)
            initialisation_CFXfolder_name = os.path.join(file_name_results_case_CFX,'Fluid Flow CFX.res')
            self.complet_batidfBC_from_ansys()"""
            #print ' as linhas 1292 ate 1315 de coupled_simulation estao comentada'
            #self.modify_reference_temperature_for_AC()
            print ' a linha 1314 de coupled_simulation esta comentada'
            ''' the estadosim file from the anterior pasttime is copied in #saida'''
            self.copy_estadosim_init()
            ''' the data from cfd simulation are writed in domus estadosim file'''
            self.complet_batidfBC_from_meteo_data(self.monthi,self.daysi,self.hoursi)
            self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory)
#             if i==0:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)                
#             else:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)
#             self.batidf.complete_hc_in_bin_estadosim()

            self.run_domus_simu()
            self.cfx_model.script.max_iteration_number = 50
        ''' the estadosim actual become the estadosim_init for the nexttime step'''
        self.xml_data.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory_init
    
    def simple_coupling_method(self,iteration_number = 3):
        ''' creation of the folder results of the case'''
        case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi
        self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_0'
        ''' if the folder is already existing, it is deleted'''
        if not os.path.exists(self.xml_data.file_name_results_case):
            os.makedirs(self.xml_data.file_name_results_case)
            
        ''' the simulation date are changed in idf file'''
        ''' dans DOMUS pour simuler 1h, il faut que l'heure final soit egal a l'heure initial
        exemple si on indique hi = 13h, et hf = 14, domus va simuler 13h et 14h, soit de 13h a 15h
        si on indique hi = 13h, et hf = 13, domus va simuler de 13h a 14h
        '''
        self.domus_comand.change_simulation_date(self.monthi,self.daysi,self.hoursi,self.monthf,self.daysf,self.hoursf)
        print('iteration n°0')
        self.copy_estadosim_init()
        if iteration_number==0:
            self.complet_batidfBC_from_meteo_data(self.monthi,self.daysi,self.hoursi)
            self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory) 
        self.run_domus_simu()
        initialisation_CFXfolder_name = ''
        for i in xrange(iteration_number):
            print('iteration n°'+str(i+1))
            self.read_AC_heat_source()
            self.batidf.complete_ts_BC_with_bin_estadosim(self.batidf.domus_estadoSim_directory)
            
            
            self.from_idfBC_to_CFD_boundary()
            self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
            self.month,self.days,self.hours = self.monthi,self.daysi,self.hoursi
            ''' creation of the folder results of the case'''
            case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi#+'_'+str(self.cfx_model.Tref).replace(".", "-")
             
            self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_'+str(i+1)
            
            
            if i>=2:
                self.cfx_model.script.buoyancy_option = True
            else:
                self.cfx_model.script.buoyancy_option = False
            
            
            ''' the simulation is writed then runed. The results are saved only if there are no bouyancy effect:''' 
            self.simu_ansys_wiht_cfd_data_base(initialisation_CFXfolder_name)
#         self.simu_ansys_using_domus_results()
            ''' the results of cfd were saved in folder and they are exported to file_name_results_case_CFX:'''
            
            result_folder = self.xml_data.file_name_results_case#os.path.join(self.xml_data.file_name_results_case,'simCFX')
            self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_'+str(i+1)
            file_name_results_case_CFX = os.path.join(self.xml_data.file_name_results_case,'simCFX')
            if os.path.exists(file_name_results_case_CFX):
                shutil.rmtree(file_name_results_case_CFX)
            shutil.copytree(result_folder,file_name_results_case_CFX)
            initialisation_CFXfolder_name = os.path.join(file_name_results_case_CFX,'Fluid Flow CFX.res')
            self.complet_batidfBC_from_ansys()
            #print ' as linhas 1292 ate 1315 de coupled_simulation estao comentada'
            self.modify_reference_temperature_for_AC()
            print ' a linha 1314 de coupled_simulation esta comentada'
            ''' the estadosim file from the anterior pasttime is copied in #saida'''
            self.copy_estadosim_init()
            ''' the data from cfd simulation are writed in domus estadosim file'''
            self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory)
#             if i==0:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)                
#             else:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)
#             self.batidf.complete_hc_in_bin_estadosim()
            
            self.run_domus_simu()
            
            self.cfx_model.script.max_iteration_number = 50
        ''' the estadosim actual become the estadosim_init for the nexttime step'''
        self.xml_data.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory_init
        
    def kera_coupling_method(self,iteration_number = 0,list_key_ref = ['fachada 1-Zona 2', 'janela 7-fachada 0-Zona 2', 'fachada 3-Zona 2', 'fachada 0-Zona 2', 'fachada 2-Zona 2', 'cobertura 4-Zona 2', 'janela 6-fachada 0-Zona 2']):
        ''' creation of the folder results of the case'''
        case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi
        self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_0'
        ''' if the folder is already existing, it is deleted'''
        if not os.path.exists(self.xml_data.file_name_results_case):
            os.makedirs(self.xml_data.file_name_results_case)
            
        ''' the simulation date are changed in idf file'''
        self.domus_comand.change_simulation_date(self.monthi,self.daysi,self.hoursi,self.monthf,self.daysf,self.hoursf)
        print('iteration n°0')
        self.copy_estadosim_init()
        self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory) 
        self.run_domus_simu()
        
        for i in xrange(iteration_number):
            print('iteration n°'+str(i+1))
            self.read_AC_heat_source()
            self.batidf.complete_ts_BC_with_bin_estadosim()
            
            
            
            temperature_meteo = self.meteo_data[self.monthi][self.daysi][self.hoursi]['temperature']
            vitesse_meteo = self.meteo_data[self.monthi][self.daysi][self.hoursi]['wind_vel']
            orientation_meteo = self.meteo_data[self.monthi][self.daysi][self.hoursi]['wind_dir']
            inputs = []
            inputs.append([temperature_meteo,vitesse_meteo,orientation_meteo])
#             for key in list_key_ref:
#                      
#                 inputs[0].append(self.batidf.dico_BC[key]['temperature_ext'])
            array_inputs = np.array(inputs)
            

            array_ta_predis = self.arn_model.dic['temperature'].model.predict(array_inputs)
            array_chtc_predis = self.arn_model.dic['CHTC'].model.predict(array_inputs)
            
            
            for j in xrange(len(self.arn_model.output_name)):
                key = self.arn_model.output_name[j]
                #self.batidf.dico_BC[key]['Ta_ext'] = array_ta_predis[0][j]             
                self.batidf.dico_BC[key]['Cond_ext'][0] = array_ta_predis[0][j] 
                self.batidf.dico_BC[key]['Cond_extB'][0] = 0  
                self.batidf.dico_BC[key]['hc_ext'] = array_chtc_predis[0][j]
                
            
            
            
            """            result_folder = self.xml_data.file_name_results_case#os.path.join(self.xml_data.file_name_results_case,'simCFX')"""
            ''' creation of the folder results of the case'''
            case_name = self.hoursi+'_'+self.daysi+'_'+self.monthi#+'_'+str(self.cfx_model.Tref).replace(".", "-")
             
            self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name+'/ite_'+str(i+1)
            """            file_name_results_case_kera = os.path.join(self.xml_data.file_name_results_case,'simkera')
            if os.path.exists(file_name_results_case_kera):
                shutil.rmtree(file_name_results_case_kera)
            shutil.copytree(result_folder,file_name_results_case_kera)"""
            
            """self.complet_batidfBC_from_ansys()
            #self.modify_reference_temperature_for_AC()
            print ' a linha 1310 de coupled_simulation esta comentada'"""
            ''' the estadosim file from the anterior pasttime is copied in #saida'''
            self.copy_estadosim_init()
#             if i==0:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)                
#             else:
#                 self.batidf.complete_flux_in_bin_estadosim(hc = True, Ta = True)
#             self.batidf.complete_hc_in_bin_estadosim()
            self.batidf.complete_flux_in_bin_estadosim(self.batidf.domus_estadoSim_directory)
            self.run_domus_simu()
            
        ''' the estadosim actual become the estadosim_init for the nexttime step'''
        self.xml_data.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory = self.xml_data.domus_estadoSim_directory
#         self.batidf.domus_estadoSim_directory_init = self.xml_data.domus_estadoSim_directory_init
    def comput_CFD_database(self):

        self.month,self.days,self.hours = self.monthi,self.daysi,self.hoursi
        self.cfx_model.month,self.cfx_model.days,self.cfx_model.hours = self.month,self.days,self.hours    
        self.cfx_model.meteo_directory = self.xml_data.meteo_directory
        
        
        self.define_boundary_CFX()
        self.assign_one_temperature_to_CFX_boundary(self.cfx_model.Tref)
        self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
        
        ''' creation of the folder results of the case'''
        case_name = str(int(self.cfx_model.direction))+'_'+str(self.cfx_model.velocity).replace(".", "-")#+'_'+str(self.cfx_model.Tref).replace(".", "-")
        self.xml_data.file_name_results_case = self.xml_data.file_name_results+case_name
        ''' if the simu case doesn't existe, the folder is created and the simulation is executed'''
        if not os.path.exists(self.xml_data.file_name_results_case):
            os.makedirs(self.xml_data.file_name_results_case)
            self.simu_ansys_using_domus_results()
            
    def comput_CFD_database_isotherme(self):

        self.month,self.days,self.hours = self.monthi,self.daysi,self.hoursi
        self.cfx_model.month,self.cfx_model.days,self.cfx_model.hours = self.month,self.days,self.hours    
        self.cfx_model.meteo_directory = self.xml_data.meteo_directory
        
        
        self.cfx_model.comput_U_V_ref()
        self.cfx_model.define_boundary_from_meteo()
        self.assign_one_temperature_to_CFX_boundary(self.cfx_model.Tref)
        self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
        self.cfx_model.script.interactive_mode = self.xml_data.ansysinteractive_mode
        ''' creation of the folder results of the case'''
        case_name = str(int(self.cfx_model.direction))+'_'+str(self.cfx_model.velocity).replace(".", "-")#+'_'+str(self.cfx_model.Tref).replace(".", "-")
        self.xml_data.file_name_results_case = self.xml_data.file_name_cfd_data_base_results+case_name
        ''' if the simu case doesn't existe, the folder is created and the simulation is executed'''
        if not os.path.exists(self.xml_data.file_name_results_case):#if os.path.exists(self.xml_data.file_name_results_case):#
#             os.makedirs(self.xml_data.file_name_results_case)
            self.cfx_model.create_script()
            initialisation_folder_name = self.check_data_in_meteo_par_simu_cfd(self.cfx_model.direction,self.cfx_model.velocity,
                                                  self.cfx_model.Tref,self.xml_data.file_name_results_case)
            if initialisation_folder_name==False:
                self.cfx_model.script.IC_option = False
                self.cfx_model.script.IC_filename = ''
            else:
                self.cfx_model.script.IC_option = True
                self.cfx_model.script.IC_filename = initialisation_folder_name#+r'/simCFX/Fluid Flow CFX.res'
            print ('results_case :'+self.xml_data.file_name_results_case)
            print ('IC_option :'+str(self.cfx_model.script.IC_option))
            print ('IC_filename :'+self.cfx_model.script.IC_filename)
            self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
            self.cfx_model.script.def_file = self.xml_data.file_name_ansys_files+r'dp0\CFX\CFX\Fluid Flow CFX.def'
            self.cfx_model.script.file_name_script = self.xml_data.domus_project_directory+r'/changer_TS_et_simuler.wbjn'#+r'\sim_janela_files\creer_projetbis2.wbjn'
            self.cfx_model.script.file_name_result_ansys = self.xml_data.file_name_result_ansys
            self.run_and_save_ansys_simu()
            
    def modify_reference_temperature_for_AC(self):
        wet = self.meteo_data[self.month][self.days][self.hours]['wet']
        humidity = []
        temperature = []
        AC_name = []
        externe_cond = []
        for name in self.liste_AC_wall_temp_ref:
            #domus_name = self.batidf.name_connection[name]
            #temperature.append(self.batidf.dico_BC[name]['Ta_ext'])
            temperature.append(self.batidf.dico_BC[name]['Cond_ext'][0])
            humidity.append(wet)
            zone_number = name.split()[-1]
            AC_name.append('Ac1_Atuadores_Zona '+zone_number)
            externe_cond.append('1')
        
        
        self.domus_comand.change_externe_condition_AC(AC_name ,externe_cond , temperature , humidity)
        
            
    def read_AC_heat_source(self):
        
        name_file = os.path.join(self.xml_data.file_name_results_case,'simDomus')
        for i in self.liste_id_AC_wall:#in xrange(len(self.batidf.dico_surface)):
            Pui_moy = 0
            zone_indice = self.batidf.dico_surface[i]['Zone Name'][5:]
            name_file_ac = os.path.join(name_file,'Zon'+zone_indice+'CRA.txt')
            print name_file_ac
            fichier = lire_fichier_txt(name_file_ac)
            
            for j in xrange(1,len(fichier)):
                Pui_moy+=-float(fichier[j][3])
            Pui_moy = Pui_moy/(len(fichier)-1)
            nameboundary = self.batidf.dico_surface[i]['name']+'ext'
            surface = self.batidf.dico_surface[i]['area']
            self.cfx_model.list_boundary[nameboundary]['heat_source'] = Pui_moy/surface 
            #self.batidf.dico_BC[key]['heat_source_ext'] = Pui_moy
            
                    
           
    def AC_coupling_parameter(self,liste_AC_wall,liste_AC_wall_temp_ref): 
        'fonction temporaire pour parametrise le couplage AC DOMUS CFD'  
        ''' la liste self.liste_AC_wall represente le nom des murs qui vont avoir une source de chaleur dans la cfd
            self.liste_AC_wall_temp_ref represente le nom des murs dont la temperature d'air proche de la parois sera utilis´´pour servir de reference pour le calcul d'AC
            '''
        self.liste_AC_wall = liste_AC_wall
        self.liste_AC_wall_temp_ref = liste_AC_wall_temp_ref
        self.liste_id_AC_wall = []
        for i in xrange(len(self.batidf.dico_surface)):
            if self.batidf.dico_surface[i]['name'] in self.liste_AC_wall:
                self.liste_id_AC_wall.append(i)
        
         
    def build_ts_array(self,Tsky = 25):
        dict_FF = self.radiative_model.dict_FF
        dico_BC = self.batidf.dico_BC
        ts = Tsky*np.ones(len(dict_FF.keys()))
        
        for surface_name in dict_FF.keys():
            #print surface_name
            
            if (surface_name in dico_BC.keys()):
                indice = dict_FF[surface_name]['indice']
                ts[indice] = dico_BC[surface_name]['temperature_ext']
                
#             elif (surface_name[:-4] in dico_BC.keys()):
#                 surface_name = surface_name[:-4]
#                 ts_name.append(surface_name)
#                 ts.append(dico_BC[surface_name]['temperature_ext'])
        return ts
                
    def complet_batidfBC_with_LWnet(self,dict_FF,net_irradiance):
        for surface_name in self.batidf.dico_BC.keys():
            #print surface_name
            if (surface_name in dict_FF.keys()):
                indice = dict_FF[surface_name]['indice']
                dico_BC[surface_name]['LW_net_ext'] = net_irradiance[indice]
                
    def complet_batidfBC_with_SW(self):
        
        ''' load the file where is the solar radiation:
        the folder is :'''
        objheure = datetime.datetime.strptime(self.hoursi, '%H')
        heure = datetime.datetime.strftime(objheure,'%H')
        folder_name = self.xml_data.file_name_solar_results+self.monthi+'_'+self.daysi+'_'+heure
        ray_direct = np.load(folder_name+'/direct.npy')
        ray_diffus = np.load(folder_name+'/diffus.npy')
        ray_tot = ray_direct+ray_diffus
        for i in xrange(len(self.batidf.dico_BC.keys())):
            surface_name = self.batidf.dico_BC.keys()[i]
            self.batidf.dico_BC[surface_name]['SW_net_ext'] = ray_tot[i]
    
    def complet_batidfBC_with_radiation(self,dict_FF,net_irradiance):
        
        ''' load the file where is the solar radiation:
        the folder is :'''
        objheure = datetime.datetime.strptime(self.hoursi, '%H')
        heure = datetime.datetime.strftime(objheure,'%H')
        folder_name = self.xml_data.file_name_solar_results+self.monthi+'_'+self.daysi+'_'+heure
        ray_direct = np.load(folder_name+'/direct.npy')
        ray_diffus = np.load(folder_name+'/diffus.npy')
        ray_tot = ray_direct+ray_diffus
        for i in xrange(len(self.batidf.dico_BC.keys())):
            surface_name = self.batidf.dico_BC.keys()[i]

            if (surface_name in dict_FF.keys()):
                indice = dict_FF[surface_name]['indice']
                self.batidf.dico_BC[surface_name]['Cond_ext'][4] = ray_tot[i]+net_irradiance[indice]
                self.batidf.dico_BC[surface_name]['Cond_extB'][4] = 0


                    


    
class Simu_parameter():    
    
    def __init__(self):
        ''' class that contain all the simulation parameterdirectory and data need to realize simulation in a xml file
        '''
        
        
class Xml_data():
    
    def __init__(self):
        ''' class that contain all the directory and data need to realize simulation in a xml file
        '''
        """the path where is Domus.exe"""
        self.Domuspath = r'C:\Program Files (x86)\Domus - Eletrobras\DomusConsole.exe' 
        self.ANSYS_path = r'C:\Program Files\ANSYS Inc\v171\Framework\bin\Win64\RunWB2.exe'
        self.ANSYS_path = r'C:\Program Files\ANSYS Inc\v182\Framework\bin\Win64\RunWB2.exe'
        self.bdf_geom_path = r'C:\Program Files\ANSYS Inc\v171\Framework\bin\Win64\RunWB2.exe'
        self.ansys_directory = r"D:/Users/adrien.gros/projet_ansys"
        self.gmsh_directory = "C:\Program Files\GMSH\gmsh.exe"
        self.gmsh_directory = "D:\gmsh3\gmsh.exe"
        self.ansysinteractive_mode = 'B'
        
        self.file_name_idf = ''
        self.file_name_idf_domus = ''
        self.file_name_idf_class = ''
        self.file_name_cfx_class = ''
        self.file_name_geo = ''
        self.file_name_msh = ''
        self.file_name_bdf = ''
        self.file_name_project_ansys = ''#'r"D:/Users/adrien.gros/projet_ansys/sim_janelabis3.wbpj"#
        self.file_name_ansys_files = ''
        self.file_name_result_ansys = ''
#         self.ansys_project_directory = ''                
        self.domus_project_directory = ''
        self.domus_results_directory = ''
        self.domus_estadoSim_directory = ''
        self.domus_estadoSim_directory_init = ''
        self.meteo_directory = ''
        self.project_name = ''
        self.file_name_results = ""
        self.file_name_cfd_data_base_results = ""
        self.file_name_solar_results = ""
#         self.file_name_project_ansys =self.ansys_project_directory+'/'#'r"D:/Users/adrien.gros/projet_ansys/sim_janelabis3.wbpj"#
#         self.file_name_idf = self.domus_project_directory+'/'
#         self.file_name_idf_domus = self.domus_project_directory+'/'
#         self.file_name_geo = self.domus_project_directory+'/'
#         self.file_name_msh = self.domus_project_directory+'/'
#         self.file_name_bdf = self.domus_project_directory+'/'
        
        
    def write_data(self,file_name):
        
        
        f = file(file_name, 'w')
        doc = minidom.Document()
        racinexml = doc.createElement("xml")
        doc.appendChild(racinexml)
        
        for keys in self.__dict__.keys():

            nom = keys
            valeur = self.__dict__[keys]

            
            
            hre1 = doc.createElement(nom)        
            racinexml.appendChild(hre1)           
            texte = doc.createTextNode(str(valeur))
            hre1.appendChild(texte)
            
        f.write(doc.toprettyxml('\t'))#.mcode('utf_8'))
        f.close() 
        
    def read_data(self,file_name):

        xmldoc = minidom.parse(file_name) 
        for keys in self.__dict__.keys():
            #print ('clef =',keys)
            if xmldoc.getElementsByTagName(keys)==[]:#os.path.exists(self.__dict__[keys])==False:
                print (' WARNING!! the directory', self.__dict__[keys],"doesn't exist")
            else:
                self.__dict__[keys] = xmldoc.getElementsByTagName(keys)[0].firstChild.data

#                 os.path.isfile(self.__dict__[keys]) or 
        
    def create_all_directory(self,domus_project_directory,project_name = 'model'):
        self.project_name = project_name
        self.domus_project_directory = domus_project_directory
        self.ansys_project_directory = self.domus_project_directory #self.file_name_project_ansys =self.ansys_project_directory+'/'#'r"D:/Users/adrien.gros/projet_ansys/sim_janelabis3.wbpj"#

        self.file_name_idf = self.domus_project_directory+r'/'+project_name+r'_nrjplus.idf'
        self.file_name_idf_domus = self.domus_project_directory+r'/'+project_name+r'.idf'
        self.file_name_idf_class = self.domus_project_directory+r'/'+project_name+r'_idf_class/'
        self.file_name_geo = self.domus_project_directory+r'/'+project_name+r'.geo'
        self.file_name_msh = self.domus_project_directory+r'/'+project_name+r'.msh'
        self.file_name_bdf = self.domus_project_directory+r'/'+project_name+r'.bdf'
        
        self.file_name_project_ansys = self.domus_project_directory+r'/'+project_name+r'_CFX.wbpj'
        self.file_name_ansys_files = self.domus_project_directory+r'/'+project_name+r'_CFX_files/'
        self.file_name_result_ansys = self.file_name_ansys_files+r'user_files/'
        if not os.path.exists(self.file_name_result_ansys):
            os.makedirs(self.file_name_result_ansys)
        self.domus_results_directory = self.domus_project_directory+r'/#'+project_name+r'/saidas/sim001/' 
        self.domus_estadoSim_directory = self.domus_project_directory+r'/#'+project_name+r'/saidas/estadoSim/' 
        self.domus_estadoSim_directory_init = self.domus_project_directory+r'/#'+project_name+r'/saidas/estadoSim/' 
        self.meteo_directory = self.domus_project_directory+r'/meteo.TXT'
        
        self.file_name_idf_class = self.domus_project_directory+r'/'+project_name+r'_idf_class/'
        if not os.path.exists(self.file_name_idf_class):
            os.makedirs(self.file_name_idf_class)
        self.file_name_cfx_class = self.domus_project_directory+r'/'+project_name+r'_cfx_class/'
        if not os.path.exists(self.file_name_cfx_class):
            os.makedirs(self.file_name_cfx_class)
        ''' creation of the foler results'''
        self.file_name_results = self.domus_project_directory+r'/'+project_name+r'_results/'
        if not os.path.exists(self.file_name_results):
            os.makedirs(self.file_name_results)
        ''' creation of the folder results cfd database'''
        self.file_name_cfd_data_base_results = self.domus_project_directory+r'/'+'cfd_database/'
        if not os.path.exists(self.file_name_cfd_data_base_results):
            os.makedirs(self.file_name_cfd_data_base_results)
        
    def create_new_project(self,domus_project_directory,project_name = 'model'):
        self.create_all_directory(domus_project_directory,project_name)
        file_name_parameter_xml = self.domus_project_directory+r'/'+project_name+r'_parameter.xml'
        self.write_data(file_name_parameter_xml)
        return file_name_parameter_xml
        
   

     
if __name__ == "__main__": 
    
#     file_name = r"D:/Users/adrien.gros/Documents/domus_project/casa_2janelasbis"
    project_name = r'casa_2andares'
#     project_name = r'casa_2andares_buraco'
    project_name = r'exemplo'
    project_name = r'edificio'
    project_name = r'exemplo3'
    project_name = r'2edificiosext'
    project_name = r'2edificiosinext'
    project_name = r'2edificiosextzona34'
    project_name = r'casa_2janelasfechada'
    project_name = r'casa_2janelasfechadabis'
    project_name = r'casa_2janelasfechadabiscorrect'
    project_name = r'casa_1janela'
    project_name = r'cube'
    project_name = r'cavite'
    project_name = r'piece_ventile_ext'
    project_name = r'CEDVAL_sol'
    project_name = r'CEDVAL_1batiment'
    project_name = r'piece_ventile_ext_fen'
    project_name = r'piece_ventile_ext_fen_tuto'
    project_name = r'cobogo'
#     project_name = r'CEDVAL_batiments'
    
#     project_name = r'rua_canyon_div'
#     file_name = 'D:/Users/adrien.gros/Documents/domus_project/casa_1janela/casa_1janela_CFX_files/user_files/results_1_1_07H00M00.txt'
#     
#     idf_file = open(file_name,'r')
#     liste_idf_file = idf_file.readlines()
#     table_idf = []
#     for i in xrange(len(liste_idf_file)):
#         print(liste_idf_file[i])
#           
#             vérification lignes vides
#         if liste_idf_file[i] != '\r\n' and liste_idf_file[i] != '\n':
#             table_idf.append(liste_idf_file[i].split())
#     dico = {}
#     liste_variable = []
#     for i in xrange(1,len(table_idf[0])):
#         liste_variable.append(table_idf[0][i])
#     for i in xrange(1,len(table_idf)):
#         nom = table_idf[i][0]
# 
#         dico[nom] = {}
#         for j in xrange(len(liste_variable)):
#             dico[nom][liste_variable[j]] = table_idf[i][j+1]
#         
#     project_name = r'rua_canyon_exp'
#     project_name = r'tuto'
    file_name = r"D:/Users/adrien.gros/Documents/domus_project/"+project_name#casa_2andares"

#     path = "D:\Users\\adrien.gros\\Documents\\domus_project\\casa_2janelasfechadabis\\casa_2janelasfechadabis_CFX_files\\user_files\\10_02_17_11_59_39\\"
#     liste = os.listdir(path)
    
#     file_name = r"D:/Users/adrien.gros/Documents/domus_project/rua_canyon_multi"
#     file_name = r"D:/Users/adrien.gros/Documents/domus_project/rua_canyon_6m"
#     project_name = 'rua_canyon_6m'
    simu = Coupled_simulation()
    simu.coupling_method = 'out_int_door'#'outdoor'
#     simu.option_windows = True
    simu.option_outdoor = True

#     simu.id_zones = [2,3]
#     simu.id_zones = range(0,10000000)
    simu.id_zones = [3]
#     simu.id_zones = []
    simu.id_zones = ['Zona2']
#     simu.id_zones = []
    
    simu.create_mockups(file_name,project_name)
    simu.load_project(file_name+r'/'+project_name+r'_parameter.xml')
     
 
     
     
     
    file_name = simu.xml_data.file_name_result_ansys+r'exportnormalxyz.csv'
    simu.xml_data.meteo_directory = r"D:/Users/adrien.gros/Documents/domus_project/casa_2andares/meteo.txt"
    
#     simu.run_domus_simu()
    
    for i in xrange(0,24,1):
        simu.hoursi,simu.hoursf = i,i+1 
        simu.run_coupled_domus_cfx_simu()
    simu.create_domus_results()
    simu.allocate_ts_result()
    
     
    simu.read_times('1','1','07:00:00')
   
     
    simu.simu_ansys_using_domus_results()
    simu.create_postraitement_pressure_coefficent()
    simu.cfx_model.script.file_name_script = r"D:\Users\adrien.gros\Documents\domus_project\casa_2janelasfechadabis/essaicreationusersurface.wbjn"
    simu.cfx_model.script.project_path = simu.xml_data.file_name_project_ansys
    simu.create_postraitement_user_surface()
    simu.create_postraitement_user_surface_average_value()
#     for i in xrange(1,10):
#         print 'date = ',simu.month,simu.days,simu.hours
#         
#         simu.hours = simu.hours[0]+str(i)+simu.hours[2:]
#         simu.cfx_model.month,simu.cfx_model.days,simu.cfx_model.hours = simu.month,simu.days,simu.hours    
#         simu.cfx_model.meteo_directory = simu.xml_data.meteo_directory
#         simu.cfx_model.read_meteo_data_from_domus()
#         
#         simu.define_boundary_CFX()
# 
#         print' direction du vent =', simu.cfx_model.direction 
#         print' vitesse du vent = ', simu.cfx_model.velocity
#         if simu.cfx_model.velocity==0.0:
#             print ' attention la vitesse de reference est egale a zero, la simulation ne pourra pas marcher'
#             f = input()
#         print 'temperature meteo = ', simu.cfx_model.Tref
# 
# 
#         simu.cfx_model.create_script()
#         simu.cfx_model.script.project_path = simu.xml_data.file_name_project_ansys
#         simu.cfx_model.script.file_name_script = simu.xml_data.domus_project_directory+r'/changer_TS_et_simuler.wbjn'#+r'\sim_janela_files\creer_projetbis2.wbjn'
#         simu.cfx_model.script.write_change_boundary_run_simulation_cfx()
#         ''' results are created to be able to use postprocessing'''
#         hours = simu.hours[:2]+'H'+simu.hours[3:5]+'M'+simu.hours[-2:]
#         name_file = simu.xml_data.file_name_result_ansys+'results_'+simu.month+'_'+simu.days+'_'+hours+'.txt'
#         simu.cfx_model.script.save_table(name_file)         
#         simu.cfx_model.script.save_and_run()
#     simu.cfx_model.script.write_script()
#     simu.cfx_model.script.define_script()
#     simu.cfx_model.script.write_open_project()
#     simu.cfx_model.script.create_results()
#     simu.cfx_model.script.create_user_surface_offset('cobertura0Zona1ext','0.5','user_surface')
#     simu.cfx_model.script.create_user_surface_offset('fachada3Zona2ext','0.5','user_surface2')
#     simu.cfx_model.script.f.close()
#     simu.cfx_model.script.run_script() 
#     simu.read_ansys_result_file(file_name)
     
#     simu.create_mockups(r"D:/Users/adrien.gros/Documents/domus_project/casa_2janelasbis")
 
#     simu.xml_data.write_data(r'D:/Users/adrien.gros/Documents/domus_project/casa_2janelas/parametre.xml')      
    print('acabou')
        