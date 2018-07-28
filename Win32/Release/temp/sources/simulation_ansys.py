# -*- coding: utf-8 -*-
'''
Created on 17/10/2016

@author: adrien.gros
'''


import subprocess
import pandas as pd
import numpy as np
import math
import cPickle

class Script_Ansys():
    def __init__(self):       

        self.name_domaine = 'canopy'
        self.project_path = "D:/Users/adrien.gros/projet_ansys/sim_janela.wbpj"
        self.file_name_result_ansys = ''
        self.ANSYS_path = r'C:\Program Files\ANSYS Inc\v171\Framework\bin\Win64\RunWB2.exe'
        self.CFX_path = r'C:\Program Files\ANSYS Inc\v171\CFX/'
        self.bdf_geom_path = r'C:\Program Files\ANSYS Inc\v171\Framework\bin\Win64\RunWB2.exe'
        self.file_name_script = r'D:/Users/adrien.gros/projet_ansys/sim_janela_files/enregistrer_projet.wbjn'
        self.ccl_file_name = r'D:/Users/adrien.gros/Documents/domus_project/CEDVAL_batiments/essai3.ccl'
        self.result_file_name = r'D:/Users/adrien.gros/Documents/domus_project/CEDVAL_1batiment/resultat'
        self.ccl_option = False
        self.def_file = r'D:\\Users\\adrien.gros\\projet_ansys\sim_janelabis3_files\dp0\CFX\CFX\Fluid Flow CFX.def'
        self.list_fluid = []
        self.month,self.days,self.hours = '1','1','01:00:00'
        ''' option_parameter if it need to create a new result object to allow to use postraitement'''
        self.create_result_option = True
        self.buoyancy_option = False
        ''' the interactive mode is used to determine how is opened and closed the ansys user interface
        if self.interactive_mode = 'I' the ansys user interface is opened to realise asked instruction and next it keep opened when the instruction is finished
        if self.interactive_mode = 'X' the ansys user interface is opened to realise asked instruction and next it is closed when the instruction is finished
        if self.interactive_mode = 'B' the ansys user interface is not opened, ansys is open in batch mode to realise asked instruction and next it is closed when the instruction is finished
        '''
        self.interactive_mode = 'I'
        self.option_open_workbench = True
        self.max_iteration_number = 300
        self.IC_option = False
        self.IC_filename = ''
        self.version_number = '18.2'
        
    def run_cfxsolver(self):
        solver_path = self.CFX_path+"bin/cfx5solve.exe"
        subprocess.Popen('"%s" -def "%s" -ccl "%s" -ini "%s" -fullname "%s" -batch' % (solver_path, self.def_file,self.ccl_file_name,self.IC_filename,self.result_file_name)).wait()
            
    def run_script(self):
        self.f.write('Save(Overwrite=True)\n') 
        self.f.close()
        if self.option_open_workbench:
            subprocess.Popen("%s -R %s -%s" % (self.ANSYS_path, self.file_name_script,self.interactive_mode)).wait()
            print 'modification ligne 55 de simulation_ansys'
        else:
            subprocess.Popen("%s -B %s" % (self.ANSYS_path, self.file_name_script)).wait()
#         subprocess.Popen("%s -R %s -I" % (self.ANSYS_path, self.file_name_script))
    def write_ccl(self):
        self.f = open(self.ccl_file_name, "w")#self.file_name_script)
        self.f.write('# State file created:  2017/07/31 11:31:37\n')
        self.f.write('# Build %s 2016.04.12-14.50-136032\n'%(self.version_number))
        self.write_ccl_library()
        self.write_ccl_domain()
        self.f.write('COMMAND FILE:\n')
        self.f.write('  Version = %s\n'%(self.version_number))
        self.f.write('END\n')
        self.f.close()
    def write_ccl_library(self):
        self.f.write('LIBRARY:\n')
        self.f.write('  CEL:\n')
        self.f.write('    EXPRESSIONS:\n')
        self.f.write('      Pressurecoef = Pressure /(0.5*Density *Velref *Velref )\n')
        for name in self.list_boundary.keys():
            self.f.write('      TS%s=%s [C]\n'% (name,self.list_boundary[name]['temperature_celsius']))
        self.f.write('      Uref=%s [m s^-1]\n'% (self.Uref))
        self.f.write('      Vref=%s [m s^-1]\n'% (self.Vref))
        self.f.write('      Velref=%s [m s^-1]\n'% (self.velocity))
        self.f.write('      Zref=%s [m]\n'% (self.Zref))
        self.f.write('      Zground=%s [m]\n'% (0.99*self.Zground))
        self.f.write('      Uinlet=Uref*((z-Zground)/Zref)^0.3\n')
        self.f.write('      Vinlet=Vref*((z-Zground)/Zref)^0.3\n')
        self.f.write('      Tref=%s [C]\n'% (self.Tref))
        self.f.write('      dissnrjturb = ((0.09^0.75)*(turbenergy^1.5))/(0.41*(z-Zground))\n')
        self.f.write('      turbenergy = 0.3*Velref *Velref\n')
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('  MATERIAL: Air at 25 C\n')
        self.f.write('    Material Description = Air at 25 C and 1 atm (dry)\n')
        self.f.write('    Material Group = Air Data, Constant Property Gases\n')
        self.f.write('    Option = Pure Substance\n')
        self.f.write('    Thermodynamic State = Gas\n')
        self.f.write('    PROPERTIES:\n')
        self.f.write('      Option = General Material\n')
        self.f.write('      EQUATION OF STATE:\n')
        self.f.write('        Density = 1.185 [kg m^-3]\n')
        self.f.write('        Molar Mass = 28.96 [kg kmol^-1]\n')
        self.f.write('        Option = Value\n')
        self.f.write('      END\n')
        self.f.write('      SPECIFIC HEAT CAPACITY:\n')
        self.f.write('        Option = Value\n')
        self.f.write('       Specific Heat Capacity = 1.0044E+03 [J kg^-1 K^-1]\n')
        self.f.write('        Specific Heat Type = Constant Pressure\n')
        self.f.write('     END\n')
        self.f.write('      REFERENCE STATE:\n')
        self.f.write('        Option = Specified Point\n')
        self.f.write('        Reference Pressure = 1 [atm]\n')
        self.f.write('        Reference Specific Enthalpy = 0. [J/kg]\n')
        self.f.write('        Reference Specific Entropy = 0. [J/kg/K]\n')
        self.f.write('        Reference Temperature = 25 [C]\n')
        self.f.write('      END\n')
        self.f.write('      DYNAMIC VISCOSITY:\n')
        self.f.write('        Dynamic Viscosity = 1.831E-05 [kg m^-1 s^-1]\n')
        self.f.write('        Option = Value\n')
        self.f.write('      END\n')
        self.f.write('      THERMAL CONDUCTIVITY:\n')
        self.f.write('        Option = Value\n')
        self.f.write('        Thermal Conductivity = 2.61E-02 [W m^-1 K^-1]\n')
        self.f.write('      END\n')
        self.f.write('      ABSORPTION COEFFICIENT:\n')
        self.f.write('        Absorption Coefficient = 0.01 [m^-1]\n')
        self.f.write('        Option = Value\n')
        self.f.write('      END\n')
        self.f.write('     SCATTERING COEFFICIENT:\n')
        self.f.write('        Option = Value\n')
        self.f.write('        Scattering Coefficient = 0.0 [m^-1]\n')
        self.f.write('      END\n')
        self.f.write('      REFRACTIVE INDEX:\n')
        self.f.write('        Option = Value\n')
        self.f.write('        Refractive Index = 1.0 [m m^-1]\n')
        self.f.write('      END\n')
        self.f.write('      THERMAL EXPANSIVITY:\n')
        self.f.write('        Option = Value\n')
        self.f.write('        Thermal Expansivity = 0.003356 [K^-1]\n')
        self.f.write('      END\n')
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')
        
    def write_ccl_domain(self):
        self.define_domain(self.list_fluid[0],True,True)
        self.f.write('  OUTPUT CONTROL:\n')
        self.f.write('    RESULTS:\n')
        self.f.write('      File Compression Level = Default\n')
        self.f.write('      Option = Standard\n')
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('  SOLVER CONTROL:\n')
        self.f.write('    Turbulence Numerics = First Order\n')
        self.f.write('    ADVECTION SCHEME:\n')
        self.f.write('      Option = High Resolution\n')
        self.f.write('    END\n')
        self.f.write('    CONVERGENCE CONTROL:\n')
        self.f.write('      Length Scale Option = Conservative\n')
        self.f.write('      Maximum Number of Iterations = %s\n'%(self.max_iteration_number))
        self.f.write('      Minimum Number of Iterations = 1\n')
        self.f.write('      Timescale Control = Auto Timescale\n')
        self.f.write('      Timescale Factor = 1.0\n')
        self.f.write('    END\n')
        self.f.write('    CONVERGENCE CRITERIA:\n')
        self.f.write('      Residual Target = 1.E-4\n')
        self.f.write('      Residual Type = RMS\n')
        self.f.write('    END\n')
        self.f.write('    DYNAMIC MODEL CONTROL:\n')
        self.f.write('      Global Dynamic Model Control = On\n')
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')



      
        
        
        
    def write_script(self,mode = 'w'):  
#         self.file_name_script = file_name_script 
        self.f = open(self.file_name_script,mode)
         
    def define_script(self):
        self.f.write('# encoding: utf-8\n')
        self.f.write('# Release %s\n'%(self.version_number))
        self.f.write('SetScriptVersion(Version="%s")\n'%(self.version_number))
        
    def create_template(self):
        self.f.write('template1 = GetTemplate(\n')
        self.f.write('    TemplateName="Fluid Flow",\n')
        self.f.write('    Solver="CFX")\n')
        self.f.write('system1 = template1.CreateSystem()\n')
        self.f.write('setup1 = system1.GetContainer(ComponentName="Setup")\n')
        self.f.write('setup1.Edit()\n')
        
    def import_geo_bdf(self):
        self.f.write('setup1.SendCommand(Command="""VIEW:View 1\n')
        self.f.write('  Light Angle = 50, 110\n')
        self.f.write('END\n\n')
        self.f.write('> update\n')
        self.f.write('> gtmImport filename=%s, type=MSC, units=m, genOpt= -n, specOpt= -l, nameStrategy= Assembly""")\n'% (self.bdf_geom_path))
                
    def open_project(self):
        self.f.write('Open(FilePath=%s\n'% (self.project_path))
        self.f.write('system1 = GetSystem(Name="CFX")\n')
 
    def open_setup(self):
        self.f.write('setup1 = system1.GetContainer(ComponentName="Setup")\n')
        self.f.write('setup1.Edit()\n') 
              
    def close_setup(self):
        self.f.write('setup1.Edit()\n')
        self.f.write('setup1.Exit()\n')
    def multi_define_surface_boundary(self,liste_value,liste_name_boundary,liste_name_location):
        for i in xrange(len(liste_value)):
            self.define_surface_boundary(liste_value[i],liste_name_boundary[i],liste_name_location[i])
            
    def define_surface_boundary(self,value,name_boundary,name_location):
        self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n  DOMAIN:%s\n'% (self.name_domaine))
        self.f.write('&replace     BOUNDARY:%s\n'% (name_boundary))
        self.f.write('      Boundary Type = WALL\n      Create Other Side = Off\n      Interface Boundary = Off\n')
        self.f.write('      Location:%s\n'% (name_location)) 
        self.f.write('      BOUNDARY CONDITIONS:\n        HEAT TRANSFER:\n')
        self.f.write('          Fixed Temperature = %f [C]\n'% (value)) 
        self.f.write('          Option = Fixed Temperature\n        END # HEAT TRANSFER:\n        MASS AND MOMENTUM: \n')
        self.f.write('          Option = No Slip Wall\n        END # MASS AND MOMENTUM:\n        WALL ROUGHNESS: \n')   
        self.f.write('          Option = Smooth Wall\n        END # WALL ROUGHNESS:\n      END # BOUNDARY CONDITIONS:\n')    
        self.f.write('    END # BOUNDARY:%s\n'% (name_boundary))
        self.f.write('  END # DOMAIN:%s\n'% (self.name_domaine))  
        self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 

    def define_boundary(self,dico,name,ccl = False):
        self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n  DOMAIN:%s\n'% (self.name_domaine))
        self.f.write('&replace   ')
        self.boundary(dico,name)
        self.f.write('  END # DOMAIN:%s\n'% (self.name_domaine))  
        self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
        
    def boundary(self,dico,name,ccl = False):
        self.f.write('    BOUNDARY: %s\n'% (name))
        self.f.write('      Boundary Type = %s\n'% (dico['boundary_type']))
        if dico['boundary_type']=='OUTLET':
            self.define_boundary_outlet(dico,name)
        elif dico['boundary_type']=='INLET':
            self.define_boundary_inlet(dico,name)
        elif dico['boundary_type']=='OPENING':
            self.define_boundary_opening(dico,name)
        elif dico['boundary_type']=='INTERFACE':   

            self.f.write('              Interface Boundary = On\n')
            self.f.write('              Location = %s\n'% (dico['location_name']))
            self.f.write('              BOUNDARY CONDITIONS:\n') 
            self.f.write('                HEAT TRANSFER:\n') 
            self.f.write('                  Option = Conservative Interface Flux\n')
            self.f.write('                END\n') # HEAT TRANSFER:\n')
            self.f.write('                MASS AND MOMENTUM:\n') 
            self.f.write('                  Option = Conservative Interface Flux\n')
            self.f.write('                END\n') # MASS AND MOMENTUM:\n')
            self.f.write('                TURBULENCE:\n') 
            self.f.write('                  Option = Conservative Interface Flux\n')
            self.f.write('                END\n') # TURBULENCE:\n')
            self.f.write('              END\n') # BOUNDARY CONDITIONS:\n')
            

            self.f.write('            END\n') # BOUNDARY:%s\n'% (name))
        else:
            if ccl==False:
                self.f.write('      Create Other Side = Off\n      Interface Boundary = Off\n')
            self.f.write('      Location = %s\n'% (dico['location_name'])) 
            self.f.write('      BOUNDARY CONDITIONS:\n') 
            self.f.write('        HEAT TRANSFER:\n')
            if dico['heat_transfert_option']=='Fixed Temperature':                
                self.f.write('          Fixed Temperature = TS%s\n'% (name))
            self.f.write('          Option = %s\n'% (dico['heat_transfert_option']))
            self.f.write('        END\n') # HEAT TRANSFER:\n')
            self.f.write('        MASS AND MOMENTUM: \n')
            if dico['mass_and_momemtum_option']=='Specified Shear':
                self.f.write('          Option = Specified Shear\n') 
                self.f.write('          SHEAR STRESS:\n            Option = Cartesian Components\n            xValue = 0 [Pa]\n            yValue = 0 [Pa]\n            zValue = 0 [Pa]\n')
                self.f.write('          END\n') # SHEAR STRESS:\n')  
            else:   
                self.f.write('          Option = No Slip Wall\n') 
            self.f.write('        END\n') # MASS AND MOMENTUM:\n        WALL ROUGHNESS: \n')  
            self.f.write('        WALL ROUGHNESS: \n')    
            self.f.write('          Option = Smooth Wall\n        END\n') # WALL ROUGHNESS:\n')    
            self.f.write('      END\n') # BOUNDARY CONDITIONS:\n')
            if dico['heat_source']!=False:
                self.f.write('                  BOUNDARY SOURCE:\n') 
                self.f.write('                    SOURCES:\n') 
                self.f.write('                      EQUATION SOURCE: energy\n')
                self.f.write('                        Flux = %s [W m^-2]\n'% (dico['heat_source']))
                self.f.write('                        Option = Flux\n')
                self.f.write('                      END\n') # EQUATION SOURCE:energy\n')
                self.f.write('                    END\n') # SOURCES:\n')
                self.f.write('                  END\n') # BOUNDARY SOURCE:\n')
            self.f.write('    END\n') # BOUNDARY:%s\n'% (name))
            




            
    def define_boundary_inlet(self,dico,name):
        self.f.write('      Interface Boundary = Off\n')
        self.f.write('      Location = %s\n'% (dico['location_name'])) 
        self.f.write('      BOUNDARY CONDITIONS:\n') 
        self.f.write('        FLOW REGIME: \n')
        self.f.write('          Option = Subsonic\n')
        self.f.write('        END # FLOW REGIME:\n')
        self.f.write('        HEAT TRANSFER:\n')
        self.f.write('          Option = Static Temperature\n')
        self.f.write('          Static Temperature = Tref\n')        
        self.f.write('        END # HEAT TRANSFER:\n')
        self.f.write('        MASS AND MOMENTUM: \n')
        if dico['speed_option']=='Cartesian Velocity':
            self.f.write('          Option = Cartesian Velocity Components\n')
            self.f.write('          U = %s \n'% (dico['U']))
            self.f.write('          V = %s \n'% (dico['V']))
            self.f.write('          W = %s \n'% (dico['W']))  
            self.f.write('        END # MASS AND MOMENTUM:\n')
            self.f.write('        TURBULENCE:\n')
            self.f.write('          Epsilon = dissnrjturb\n')
            self.f.write('          Option = k and Epsilon\n')
            self.f.write('          k = turbenergy\n')
            self.f.write('        END # TURBULENCE:\n')    
        elif dico['speed_option']=='Normal Speed':
            self.f.write('          Normal Speed = %s \n'% (dico['Normal Speed']))
            self.f.write('          Option = Normal Speed\n')  
            self.f.write('        END # MASS AND MOMENTUM:\n')
            self.f.write('        TURBULENCE:\n')
            self.f.write('          Option = Medium Intensity and Eddy Viscosity Ratio\n')
            self.f.write('        END # TURBULENCE:\n')    
        self.f.write('      END # BOUNDARY CONDITIONS:\n')
        self.f.write('    END # BOUNDARY:%s\n'% (name))
#         self.f.write('  END # DOMAIN:%s\n'% (self.name_domaine))  
#         self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
    def define_boundary_opening(self,dico,name):
        if self.ccl_option==False:
                self.f.write('      Interface Boundary = Off\n')
        self.f.write('      Location = %s\n'% (dico['location_name'])) 
        self.f.write('      BOUNDARY CONDITIONS:\n')
        self.f.write('        FLOW DIRECTION:\n') 
        self.f.write('          Option = Normal to Boundary Condition\n') 
        self.f.write('        END # FLOW DIRECTION:\n') 
        self.f.write('        FLOW REGIME: \n')
        self.f.write('          Option = Subsonic\n')
        self.f.write('        END\n') # FLOW REGIME:\n')
        self.f.write('        HEAT TRANSFER:\n')
        self.f.write('          Opening Temperature =  TS%s\n'% (name))
        self.f.write('          Option = Opening Temperature\n')
        
        self.f.write('        END\n') # HEAT TRANSFER:\n')
        self.f.write('        MASS AND MOMENTUM: \n')
        self.f.write('          Option = Opening Pressure and Direction\n')
        self.f.write('          Relative Pressure = 1 [atm]\n')  
        self.f.write('        END\n') # MASS AND MOMENTUM:\n')
        self.f.write('        TURBULENCE:\n')
        self.f.write('          Option = Medium Intensity and Eddy Viscosity Ratio\n')
        self.f.write('        END\n') # TURBULENCE:\n')    
        self.f.write('      END\n') # BOUNDARY CONDITIONS:\n')
        self.f.write('    END\n') # BOUNDARY:%s\n'% (name))
#         self.f.write('  END # DOMAIN:%s\n'% (self.name_domaine))  
#         self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
                
    def define_boundary_outlet(self,dico,name):
        if self.ccl_option==False:
                self.f.write('      Interface Boundary = Off\n')
        self.f.write('      Location = %s\n'% (dico['location_name'])) 
        self.f.write('      BOUNDARY CONDITIONS:\n') 
        self.f.write('        FLOW REGIME: \n')
        self.f.write('          Option = Subsonic\n')
        self.f.write('        END\n') # FLOW REGIME:\n')
        self.f.write('        MASS AND MOMENTUM: \n')
        self.f.write('          Option = Cartesian Velocity Components\n')
        self.f.write('          U = Uinlet\n')
        self.f.write('          V = Vinlet\n')
        self.f.write('          W = 0 [m s^-1]\n')   
        self.f.write('        END\n') # MASS AND MOMENTUM:\n')   
        self.f.write('      END\n') # BOUNDARY CONDITIONS:\n')
        self.f.write('    END\n') # BOUNDARY:%s\n'% (name))
#         self.f.write('  END # DOMAIN:%s\n'% (self.name_domaine))  
#         self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
        
    def define_multiboundary(self):
        for name in self.list_boundary.keys():
            self.define_boundary(self.list_boundary[name],name)
#         self.define_boundary(self.list_boundary[0])

    def multiboundary_canopy(self,ccl = False):
        ''' function to change the boundary of the 4 side of the canopy'''
        for name in self.list_boundary.keys():
            if 'sideatmosphere' in name:
                self.boundary(self.list_boundary[name],name,ccl)
#         self.define_boundary(self.list_boundary[0])

    def multiboundary(self,ccl = False):
        for name in self.list_boundary.keys():
            self.boundary(self.list_boundary[name],name,ccl)
#         self.define_boundary(self.list_boundary[0])
    def write_define_interfaces(self,dico,name): 
        self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n')
        self.f.write('&replace   ')
        self.write_interfaces(dico,name) 
        self.f.write('END # FLOW:Flow Analysis 1\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
    def define_multiinterfaces(self):
        for name in self.list_interfaces.keys():
            self.write_define_interfaces(self.list_interfaces[name],name)
    def write_multiinterfaces(self):
        for name in self.list_interfaces.keys():
            self.write_interfaces(self.list_interfaces[name],name)
    def write_interfaces(self,interface,name):
        self.f.write('    DOMAIN INTERFACE: %s\n'% (name))
        self.f.write('    Boundary List1 =\n') 
        self.f.write('    Boundary List2 =\n') 
        self.f.write('    Filter Domain List1 = -- All Domains --\n')
        self.f.write('    Filter Domain List2 = -- All Domains --\n')
        self.f.write('    Interface Region List1 =  %s\n'% (interface['location_name1']))
        self.f.write('    Interface Region List2 = %s\n'% (interface['location_name2']))
        self.f.write('    Interface Type = Fluid Fluid\n')
        self.f.write('    INTERFACE MODELS: \n')
        self.f.write('      Option = General Connection\n')
        self.f.write('      FRAME CHANGE:\n') 
        self.f.write('        Option = None\n')
        self.f.write('      END # FRAME CHANGE:\n')
        self.f.write('      MASS AND MOMENTUM: \n')
        self.f.write('        Option = Conservative Interface Flux\n')
        self.f.write('        MOMENTUM INTERFACE MODEL:\n') 
        self.f.write('          Option = None\n')
        self.f.write('        END # MOMENTUM INTERFACE MODEL:\n')
        self.f.write('      END # MASS AND MOMENTUM:\n')
        self.f.write('      PITCH CHANGE:\n') 
        self.f.write('        Option = None\n')
        self.f.write('      END # PITCH CHANGE:\n')
        self.f.write('    END # INTERFACE MODELS:\n')
        self.f.write('    MESH CONNECTION:\n') 
        self.f.write('      Option = Automatic\n')
        self.f.write('    END # MESH CONNECTION:\n')
        self.f.write('  END # DOMAIN INTERFACE:%s\n'% (name))
        


  
    def define_boundary_sideatmosphere(self):
        
        self.define_boundary(self.list_boundary['sideatmosphere1'],'sideatmosphere1')
        self.define_boundary(self.list_boundary['sideatmosphere2'],'sideatmosphere2')
        self.define_boundary(self.list_boundary['sideatmosphere3'],'sideatmosphere3')
        self.define_boundary(self.list_boundary['sideatmosphere4'],'sideatmosphere4')
        
    def define_domain(self,fluid,boundary = True,ccl = False):
        ''' boundary is an option,
        if boundary is thrue all the boundary are defined'''
        if ccl:
            self.f.write('FLOW: Flow Analysis 1\n')
            self.f.write('  SOLUTION UNITS:\n')
            self.f.write('    Angle Units = [rad]\n')
            self.f.write('    Length Units = [m]\n')
            self.f.write('    Mass Units = [kg]\n')
            self.f.write('    Solid Angle Units = [sr]\n')
            self.f.write('    Temperature Units = [K]\n')
            self.f.write('    Time Units = [s]\n')
            self.f.write('  END\n')
            self.f.write('  ANALYSIS TYPE:\n')
            self.f.write('    Option = Steady State\n')
            self.f.write('    EXTERNAL SOLVER COUPLING:\n')
            self.f.write('      Option = None\n')
            self.f.write('    END\n')
            self.f.write('  END\n')
            self.f.write('  DOMAIN: canopy\n')
            
        else:
            self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n')
            self.f.write('&replace     DOMAIN:%s\n'% (fluid.name))
        self.f.write('      Coord Frame = Coord 0\n')
        self.f.write('      Domain Type = Fluid\n')
        self.f.write('      Location = Primitive 3D\n')
        if boundary:
#             self.multiboundary_canopy(ccl)
            self.multiboundary(ccl)
#             self.write_multiinterfaces()
        self.f.write('      DOMAIN MODELS:\n')
        self.f.write('        BUOYANCY MODEL:\n')
        if self.buoyancy_option:

            self.f.write('        Buoyancy Reference Temperature = 25 [C]\n')
            self.f.write('        Gravity X Component = 0 [m s^-2]\n')
            self.f.write('        Gravity Y Component = 0 [m s^-2]\n')
            self.f.write('        Gravity Z Component = -9.81 [m s^-2]\n')
            self.f.write('        Option = Buoyant\n')
            self.f.write('        BUOYANCY REFERENCE LOCATION: \n')
            self.f.write('          Option = Automatic\n')
            self.f.write('        END\n') # BUOYANCY REFERENCE LOCATION:\n')

        else:
            self.f.write('          Option = Non Buoyant\n')
        self.f.write('        END\n') # BUOYANCY MODEL:\n')
        self.f.write('        DOMAIN MOTION:\n')
        self.f.write('          Option = Stationary\n')
        self.f.write('      END\n') # DOMAIN MOTION:\n')
        self.f.write('      MESH DEFORMATION:\n')
        self.f.write('          Option = None\n')
        self.f.write('        END\n') # MESH DEFORMATION:\n')
        self.f.write('        REFERENCE PRESSURE:\n')
        self.f.write('            Reference Pressure = 1 [atm]\n')
        self.f.write('        END\n') # REFERENCE PRESSURE:\n')
        self.f.write('        END\n') # DOMAIN MODELS:\n')
        self.f.write('        FLUID DEFINITION: Fluid 1\n')
        self.f.write('          Material = Air at 25 C\n')
        self.f.write('          Option = Material Library\n')
        self.f.write('          MORPHOLOGY:\n')
        self.f.write('            Option = Continuous Fluid\n')
        self.f.write('        END\n') # MORPHOLOGY:\n')
        self.f.write('        END\n') # FLUID DEFINITION:Fluid 1\n')
        self.f.write('        FLUID MODELS:\n')
        self.f.write('          COMBUSTION MODEL:\n')
        self.f.write('            Option = None\n')
        self.f.write('          END\n') # COMBUSTION MODEL:\n')
        self.f.write('          HEAT TRANSFER MODEL:\n')
        if fluid.heat_transfert_option == 'Thermal Energy':
            self.f.write('            Option = Thermal Energy\n')
        else:
            self.f.write('            Fluid Temperature = 25 [C]\n')
            self.f.write('            Option = Isothermal\n')
        self.f.write('          END\n') # HEAT TRANSFER MODEL:\n')
        self.f.write('          THERMAL RADIATION MODEL:\n')
        self.f.write('            Option = None\n')
        self.f.write('          END\n') # THERMAL RADIATION MODEL:\n')
        self.f.write('          TURBULENCE MODEL:\n')
        self.f.write('            Option = k epsilon\n')
        if self.buoyancy_option:
            self.f.write('        BUOYANCY TURBULENCE:\n')  
            self.f.write('          Dissipation Coefficient = 1.0\n') 
            self.f.write('          Option = Production and Dissipation\n') 
            self.f.write('          Turbulent Schmidt Number = 0.9\n') 
            self.f.write('        END\n') # BUOYANCY TURBULENCE:\n')

        self.f.write('          END\n') # TURBULENCE MODEL:\n')
        self.f.write('          TURBULENT WALL FUNCTIONS:\n')
        self.f.write('            Option = Scalable\n')
        self.f.write('          END\n') # TURBULENT WALL FUNCTIONS:\n')
        self.f.write('        END\n') # FLUID MODELS:\n')
        self.f.write('        INITIALISATION:\n') 
        self.f.write('      Option = Automatic\n')
        self.f.write('      INITIAL CONDITIONS:\n') 
        self.f.write('        Velocity Type = Cartesian\n')
        self.f.write('        CARTESIAN VELOCITY COMPONENTS:\n') 
        self.f.write('          Option = Automatic with Value\n')
        self.f.write('          U = Uinlet\n')
        self.f.write('          V = Vinlet\n')
        self.f.write('          W = 0 [m s^-1]\n')
        self.f.write('        END\n') # CARTESIAN VELOCITY COMPONENTS:\n')
        self.f.write('        STATIC PRESSURE:\n') 
        self.f.write('          Option = Automatic\n')
        self.f.write('        END\n') # STATIC PRESSURE:\n')
        self.f.write('        TEMPERATURE:\n') 
        self.f.write('          Option = Automatic with Value\n')
        self.f.write('          Temperature = Tref\n')
        self.f.write('        END\n') # TEMPERATURE:\n')
        self.f.write('        TURBULENCE INITIAL CONDITIONS: \n')
        self.f.write('          Option = Medium Intensity and Eddy Viscosity Ratio\n')
        self.f.write('        END\n') # TURBULENCE INITIAL CONDITIONS:\n')
        self.f.write('      END\n') # INITIAL CONDITIONS:\n')
        self.f.write('    END\n') # INITIALISATION:\n')
        self.f.write('  END\n') # DOMAIN:%s\n'% (fluid.name))
#         self.f.write('END\n') # FLOW:Flow Analysis 1\n')
        if ccl==False:
            self.f.write('END\n') # FLOW:Flow Analysis 1\n')
            self.f.write('\n\n\nPARAMETERIZATION:\nEND""")\r\n') 
        
    def define_velocity_profil(self):
        
        self.define_U_V_ref()
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Zref=%s [m]\n'% (self.Zref))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Uinlet=Uref*((z-Zground)/Zref)^0.3\n')
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Vinlet=Vref*((z-Zground)/Zref)^0.3\n')
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        
    def define_turbulence(self):
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('turbenergy=0.3*Velref *Velref\n')
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('dissnrjturb=((0.09^0.75)*(turbenergy^1.5))/(0.41*(z-Zground))\n')
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        

    def define_cel_expression(self, name = 'Tref', expression = '20 [C]'):
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('%s = %s \n'% (name,expression))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        
    def define_pressur_coef(self):
        self.define_cel_expression( 'Pressurecoef',  'Pressure /(0.5*Density *Velref *Velref )')
            
    def define_temperature_ref(self):
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Tref=%s [C]\n'% (self.Tref))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
    def write_import_ccl(self): 
        self.f.write('setup1.SendCommand(Command="""VIEW:View 1\n')
        self.f.write('  Camera Mode = User Specified\n')
        self.f.write('  CAMERA:\n')
        self.f.write('    Option = Pivot Point and Quaternion\n')
        self.f.write('    Pivot Point = 0, 0, 9.1\n')
        self.f.write('    Scale = 0.0127544\n')
        self.f.write('    Pan = 0, 0\n')
        self.f.write('    Rotation Quaternion = 0.279848, -0.364705, -0.115917, 0.880476\n')
        self.f.write('\n')    
        self.f.write('  END\n')
        self.f.write('\n')
        self.f.write('END\n')
        self.f.write('\n')
        self.f.write('VIEW:View 1\n')
        self.f.write('  Light Angle = 50, 110\n')
        self.f.write('END\n')
        self.f.write('\n')
        self.f.write('> update\n')
        self.f.write('>importccl filename=%s, mode = replace, autoLoadLibrary = none""")\n'%(self.ccl_file_name))
        self.f.write('Save(Overwrite=True)\n')
        self.f.write('setup1.Exit()\n')
    def define_U_V_ref(self):    
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Uref=%s [m s^-1]\n'% (self.Uref))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Vref=%s [m s^-1]\n'% (self.Vref))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('Velref=%s [m s^-1]\n'% (self.velocity))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        
    def define_TS(self,name,value):
        '''function to write a script to define an expression in CFX that define a surface temperature with a name and a value
        name: name of this new expression
        value: value in Celcius of this new expression
        '''
        self.f.write('setup1.SendCommand(Command="""\n')
        self.f.write('LIBRARY:\n')
        self.f.write('CEL:\n')
        self.f.write('EXPRESSIONS:\n')
        self.f.write('TS%s=%s [C]\n'% (name,value))
        self.f.write('END\n')
        self.f.write('END\n')
        self.f.write('END""")\n')
        
    def create_all_TS(self):
        for name in self.list_boundary.keys():
            self.define_TS(name,self.list_boundary[name]['temperature_celsius'])
               
    def save_as_project(self):
        self.f.write('Save(\n')
        self.f.write('    FilePath="%s",\n'% (self.project_path))
        self.f.write('    Overwrite=True)\n')
        self.f.write('setup1.Exit()\n')
                
        
    def close_and_save_project(self):
        self.f.write('Save(Overwrite=True)\nsetup1.Exit()\n')
        self.f.close()
    
    def write_open_project(self):
        self.f.write('Open(FilePath="%s")\n'%(self.project_path))
        self.f.write('system1 = GetSystem(Name="CFX")\n')
        
    def write_change_solver_control(self):
        self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n')
        self.f.write('&replace   SOLVER CONTROL: \n')
        self.f.write('    Turbulence Numerics = First Order\n')
        self.f.write('    ADVECTION SCHEME: \n')
        self.f.write('      Option = High Resolution\n')
        self.f.write('    END # ADVECTION SCHEME:\n')
        self.f.write('    CONVERGENCE CONTROL: \n')
        self.f.write('      Length Scale Option = Conservative\n')
        self.f.write('      Maximum Number of Iterations = %s\n'%(self.max_iteration_number))
        self.f.write('      Minimum Number of Iterations = 1\n')
        self.f.write('      Timescale Control = Auto Timescale\n')
        self.f.write('      Timescale Factor = 1.0\n')
        self.f.write('    END # CONVERGENCE CONTROL:\n')
        self.f.write('    CONVERGENCE CRITERIA: \n')
        self.f.write('      Residual Target = 1.E-4\n')
        self.f.write('      Residual Type = RMS\n')
        self.f.write('    END # CONVERGENCE CRITERIA:\n')
        self.f.write('    DYNAMIC MODEL CONTROL: \n')
        self.f.write('      Global Dynamic Model Control = On\n')
        self.f.write('    END # DYNAMIC MODEL CONTROL:\n')
        self.f.write('  END # SOLVER CONTROL:\n')
        self.f.write('END # FLOW:Flow Analysis 1\n')


        self.f.write('PARAMETERIZATION:\n')
        self.f.write('END""")\n')
        
        
    def write_run_solution(self,IC_option = False,IC_filename = ''):
        """ function to write the script to run the simulation in CFX,
        parameters:
        IC_option : if it is True, the file named IC_filename is used as initial condition
        """
        ''' in first step, the solver control is write, to control the number of iteration'''
#         if self.ccl_option:
#             print 'bou'
#         else:
        if self.ccl_option==False:
            self.write_change_solver_control()
        self.f.write('solutionComponent1 = system1.GetComponent(Name="Solution")\n')
        self.f.write('solutionComponent1.Reset()\n')
        self.f.write('solution1 = system1.GetContainer(ComponentName="Solution")\n')
        self.f.write('solution1.SetExecutionControl(CCL=r"""&replace SIMULATION CONTROL:\n')
        self.f.write('  EXECUTION CONTROL:\n')
        self.f.write('    EXECUTABLE SELECTION:\n')
        self.f.write('      Double Precision = On\n')
        self.f.write('      Large Problem = Off\n')
        self.f.write('    END\n')
        self.f.write('    INTERPOLATOR STEP CONTROL:\n')
        self.f.write('      Runtime Priority = Standard\n')
        self.f.write('      MEMORY CONTROL:\n')
        self.f.write('        Memory Allocation Factor = 1.0\n')
        self.f.write('      END\n')
        self.f.write('    END\n')
        self.f.write('    PARTITIONER STEP CONTROL:\n')
        self.f.write('      Multidomain Option = Automatic\n')
        self.f.write('      Runtime Priority = Standard\n')
        self.f.write('      MEMORY CONTROL:\n')
        self.f.write('        Memory Allocation Factor = 1.0\n')
        self.f.write('      END\n')
        self.f.write('      PARTITION SMOOTHING:\n')
        self.f.write('        Maximum Partition Smoothing Sweeps = 100\n')
        self.f.write('        Option = Smooth\n')
        self.f.write('      END\n')
        self.f.write('      PARTITIONING TYPE:\n')
        self.f.write('        MeTiS Type = k-way\n')
        self.f.write('        Option = MeTiS\n')
        self.f.write('        Partition Size Rule = Automatic\n')
        self.f.write('      END\n')
        self.f.write('    END\n')
        self.f.write('    RUN DEFINITION:\n')
        self.f.write('      Run Mode = Full\n')
        self.f.write('      Solver Input File = %s \n'%(self.def_file))#D:\\Users\\adrien.gros\\projet_ansys\sim_janelabis3_files\dp0\CFX\CFX\Fluid Flow CFX.def\n'%(self.def_file))
        if self.IC_option:
            self.f.write('      INITIAL VALUES SPECIFICATION:\n')
            self.f.write('        INITIAL VALUES CONTROL:\n')
            self.f.write('          Continue History From = Initial Values 1\n')
            self.f.write('          Use Mesh From = Solver Input File\n')
            self.f.write('        END\n')
            self.f.write('        INITIAL VALUES: Initial Values 1\n')
            self.f.write('          File Name = %s \n'%(self.IC_filename))
            self.f.write('          Option = Results File\n')
            self.f.write('        END\n')
            self.f.write('      END\n')
        self.f.write('    END\n')
        self.f.write('    SOLVER STEP CONTROL:\n')
        self.f.write('      Runtime Priority = Standard\n')
        self.f.write('      MEMORY CONTROL:\n')
        self.f.write('        Memory Allocation Factor = 1.0\n')
        self.f.write('      END\n')
        self.f.write('      PARALLEL ENVIRONMENT:\n')
        self.f.write('        Number of Processes = 1\n')
        self.f.write('        Start Method = Serial\n')
        self.f.write('      END\n')
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')
        self.f.write('""")\n')
        self.f.write('solutionComponent1 = system1.GetComponent(Name="Solution")\n')
        self.f.write('solutionComponent1.Update(Force=True)\n')
        self.f.write('solution1.Exit()\n')
    def save_project(self):
        self.f.write('Save(Overwrite=True)\n')   
    def create_results(self): 
        self.open_results()
        self.f.write('results1.Edit()\n')  
#         self.f.write('results1.Exit()\n')
    
    def write_new_post_proc_script(self):
        self.write_script()
        self.define_script()
        self.write_open_project()
        self.open_results()
        
    def save_and_run(self):
        self.save_project()
#         self.f.close()
        self.run_script()
        
    
    def open_results(self): 
        self.f.write('results1 = system1.GetContainer(ComponentName="Results")\n')
        
    def create_user_surface_offset(self,surface_name,distance,surface_user_name):
#         self.f.write('# encoding: utf-8\n')
#         self.f.write('# Release 17.1\n')
#         self.f.write('SetScriptVersion(Version="17.1.127")\n')
#         self.f.write('system1 = GetSystem(Name="CFX")\n')

        self.f.write('results1.SendCommand(Command="> autolegend plot=/USER SURFACE:%s, view=VIEW:View 1")\n'%(surface_user_name))
        self.f.write('results1.SendCommand(Command="""USER SURFACE:%s\n'%(surface_user_name))
        self.f.write('Apply Instancing Transform = On\n')
        self.f.write('Apply Rotation = On\n')
        self.f.write('Apply Scale = On\n')
        self.f.write('Apply Texture = Off\n')
        self.f.write('Apply Translation = Off\n')
        self.f.write('Associated Boundary = %s\n'%(surface_name))
        self.f.write('Associated Boundary Specified = On\n')
        self.f.write('Blend Texture = On\n')
        self.f.write('Colour = 0.75, 0.75, 0.75\n')
        self.f.write('Colour Map = Default Colour Map\n')
        self.f.write('Colour Mode = Constant\n')
        self.f.write('Colour Scale = Linear\n')
        self.f.write('Colour Variable = Pressure\n')
        self.f.write('Colour Variable Boundary Values = Hybrid\n')
        self.f.write('Contour Level = 1\n')
        self.f.write('Culling Mode = No Culling\n')
        self.f.write('Domain List = /DOMAIN GROUP:All Domains\n')
        self.f.write('Draw Faces = On\n')
        self.f.write('Draw Lines = Off\n')
        self.f.write('File Units = m\n')
        self.f.write('Input File =  \n')
        self.f.write('Instancing Transform = /DEFAULT INSTANCE TRANSFORM:Default Transform\n')
        self.f.write('Lighting = On\n')
        self.f.write('Line Colour = 0, 0, 0\n')
        self.f.write('Line Colour Mode = Default\n')
        self.f.write('Line Width = 1\n')
        self.f.write('Maintain Conservative Values = Off\n')
        self.f.write('Max = 0.0 [Pa]\n')
        self.f.write('Min = 0.0 [Pa]\n')
        self.f.write('Offset Direction = 1 , 0 , 0 \n')
        self.f.write('Offset Distance = -%s [m]\n'%(distance))
        self.f.write('Offset Mode = Uniform\n')
        self.f.write('Offset Type = Normal\n')
        self.f.write('Offset Variable = Eddy Viscosity\n')
        self.f.write('Option = Offset From Surface\n')
        self.f.write('Principal Axis = Z\n')
        self.f.write('Range = Global\n')
        self.f.write('Render Edge Angle = 0 [degree]\n')
        self.f.write('Rotation Angle = 0 [degree]\n')
        self.f.write('Rotation Axis From = 0 [m], 0 [m], 0 [m]\n')
        self.f.write('Rotation Axis To = 1 [m], 0 [m], 0 [m]\n')
        self.f.write('Rotation Axis Type = Principal Axis\n')
        self.f.write('Scale Factor = 1.0\n')
        self.f.write('Specular Lighting = On\n')
        self.f.write('Surface Drawing = Smooth Shading\n')
        self.f.write('Surface Name = %s\n'%(surface_name))
        self.f.write('Texture Angle = 0\n')
        self.f.write('Texture Direction = 0 , 1 , 0 \n')
        self.f.write('Texture File =  \n')
        self.f.write('Texture Material = Metal\n')
        self.f.write('Texture Position = 0 , 0 \n')
        self.f.write('Texture Scale = 1\n')
        self.f.write('Texture Type = Predefined\n')
        self.f.write('Tile Texture = Off\n')
        self.f.write('Transform Texture = Off\n')
        self.f.write('Translation Vector = 0 [m], 0 [m], 0 [m]\n')
        self.f.write('Transparency = 0.0\n')
        self.f.write('Use Mid Side Nodes = On\n')
        self.f.write('  OBJECT VIEW TRANSFORM:\n')
        self.f.write('  Apply Reflection = Off\n')
        self.f.write('  Apply Rotation = On\n')
        self.f.write('  Apply Scale = On\n')
        self.f.write('  Apply Translation = Off\n')
        self.f.write('  Principal Axis = Z\n')
        self.f.write('  Reflection Plane Option = XY Plane\n')
        self.f.write('  Rotation Angle = 0 [degree]\n')
        self.f.write('  Rotation Axis From = 0 [m], 0 [m], 0 [m]\n')
        self.f.write('  Rotation Axis To = 1 [m], 0 [m], 0 [m]\n')
        self.f.write('  Rotation Axis Type = Principal Axis\n')
        self.f.write('  Scale Vector = 1 , 1 , 1 \n')
        self.f.write('  Translation Vector = 0 [m], 0 [m], 0 [m]\n')
        self.f.write('  X = 0.0 [m]\n')
        self.f.write('  Y = 0.0 [m]\n')
        self.f.write('  Z = 0.0 [m]\n')
        self.f.write('  END\n')
        self.f.write('END""")\n')
        self.f.write('results1.SendCommand(Command="""# Sending visibility action from ViewUtilities\n')
        self.f.write('>show /USER SURFACE:%s, view=/VIEW:View 1""")\n'%(surface_user_name))
        
    def define_cel_expression_result(self, name = 'Tref', expression = 'areaAve(Temperature )@'):
        ''' function to write expression in the post_processing of ANSY
        parameter:
            *name is the string with the name of the new expression
            * expression is the string with the expression of this new expression
        ex :
        name = Ta
        expression = 22[C]
        '''
        
        self.f.write('results1.SendCommand(Command="""LIBRARY:\n')
        self.f.write('  CEL:\n')
        self.f.write('    EXPRESSIONS:\n')
        self.f.write('      %s = %s\n'%(name,expression))
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')
        self.f.write('EXPRESSION EVALUATOR:\n')
        self.f.write('  Evaluated Expression = %s\n'%(name))
        self.f.write('END\n')
        self.f.write('> forceupdate EXPRESSION EVALUATOR""")\n') 
        
    def compute_average_temperature(self,surface_user_name,expression_name):
        self.f.write('results1.SendCommand(Command="""LIBRARY:\n')
        self.f.write('  CEL:\n')
        self.f.write('    EXPRESSIONS:\n')
        self.f.write('      %s = areaAve(Temperature )@%s\n'%(expression_name,surface_user_name))
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')
        self.f.write('EXPRESSION EVALUATOR:\n')
        self.f.write('  Evaluated Expression = %s\n'%(expression_name))
        self.f.write('END\n')
        self.f.write('> forceupdate EXPRESSION EVALUATOR""")\n')
    def compute_average_velocity(self,surface_user_name,expression_name):
        self.f.write('results1.SendCommand(Command="""LIBRARY:\n')
        self.f.write('  CEL:\n')
        self.f.write('    EXPRESSIONS:\n')
        self.f.write('      %s = areaAve(Velocity)@%s\n'%(expression_name,surface_user_name))
        self.f.write('    END\n')
        self.f.write('  END\n')
        self.f.write('END\n')
        self.f.write('EXPRESSION EVALUATOR:\n')
        self.f.write('  Evaluated Expression = %s\n'%(expression_name))
        self.f.write('END\n')
        self.f.write('> forceupdate EXPRESSION EVALUATOR""")\n')
        
    def create_table(self,title = 'Table 1'):
        self.f.write('results1.SendCommand(Command="""TABLE: %s\n'%(title))
        self.f.write('  Table Exists = True\n')
        self.f.write('END""")\n')
        self.f.write('results1.SendCommand(Command="""CALCULATOR:\n')
        self.f.write('  Function = area\n')
        self.f.write('  Location = \n')
        self.f.write('  Case Name = Case CFX\n')
        self.f.write('END""")\n')
    def write_value_in_cell_table(self,cell_name,value,decimal_number = '3',table_title = 'Table 1'):
        ''' function to write value in a cell of table (named table1) created in an ansys model'''
        
        self.f.write('results1.SendCommand(Command="""TABLE:%s\n'%(table_title))
        self.f.write('  TABLE CELLS:\n')
        self.f.write('    %s = \"'%(cell_name))
        self.f.write('%s'%(value))
        self.f.write('\", False, False, False, Left, True, 0, Font Name, 1|1, %6.')
        self.f.write('%sf,False, ffffff, 000000, True\n'%(decimal_number))
        self.f.write('  END\n')
        self.f.write('END""")\n')
        
    def write_save_table(self,name_file,table_title):
        self.f.write('results1.SendCommand(Command="""SCALAR VARIABLE:Wall Heat Transfer Coefficient\n')
        self.f.write('Boundary Values = Hybrid\n')
        self.f.write('Expression = CHTC\n')
        self.f.write('User Units = W m^-2 K^-1\n')
        self.f.write('END\n')
        self.f.write('>writevariable variable=Wall Heat Transfer Coefficient""")\n')
        ''' function to save the table named Table 1 created in CFX postprocessing in the file name_file'''
        self.f.write('results1.SendCommand(Command="""TABLE:%s\n'%(table_title))
        self.f.write('  Export Table Only = True\n')
        self.f.write('  Table Export HTML Title = \n')
        self.f.write('  Table Export HTML Caption Position = Bottom\n')
        self.f.write('  Table Export HTML Caption = \n')
        self.f.write('  Table Export HTML Border Width = 1\n')
        self.f.write('  Table Export HTML Cell Padding = 5\n')
        self.f.write('  Table Export HTML Cell Spacing = 1\n')
        self.f.write('  Table Export Lines = All\n')
        self.f.write('  Table Export Trailing Separators = True\n')
        self.f.write('  Table Export Separator = Tab\n')
        self.f.write('END\n')
        self.f.write('>table save=%s, name=%s""")\n'%(name_file,table_title))
        self.f.write('results1.Exit()\n') 
        
        
    def write_run_simulation_cfx(self,close = True):
        self.write_script()
        self.define_script()
        self.write_open_project()
        self.write_run_solution()
        if close:
            self.f.close()  
        
  
        
    def write_change_boundary_run_simulation_cfx(self,mode = 'w'):
        if self.ccl_option:
            
            self.write_ccl()
        self.write_script(mode)
        self.define_script()
        self.write_open_project()
        if self.ccl_option:
            self.f.write('setup1 = system1.GetContainer(ComponentName="Setup")\n')
            self.write_import_ccl()

        else:

            self.open_setup()
            self.define_U_V_ref()
            self.define_temperature_ref()
            self.define_turbulence()
    #         self.define_boundary_sideatmosphere()
            self.create_all_TS()
    #         self.define_multiboundary()
            self.define_domain(self.list_fluid[0])
            
            self.close_setup()
        self.write_run_solution()
        ''' results are created to be able to use postprocessing'''
        if self.create_result_option :
            self.create_results()
#             self.create_result_option = False
#         self.save_project()
        
        
    def write_change_boundary_run_simulation_cfx_init(self):
        self.write_script()
        self.define_script()
        self.write_open_project()
        self.open_setup()
        self.define_U_V_ref()
        self.define_temperature_ref()
        self.define_turbulence()
        self.define_boundary_sideatmosphere()
        self.create_all_TS()
        self.define_multiboundary()
        self.define_domain(self.list_fluid[0])
        
        self.close_setup()
        self.write_run_solution()
        ''' results are created to be able to use postprocessing'''
        if self.create_result_option :
            self.create_results()
            self.create_result_option = False
        self.save_project()
          
        
    def write_project_creation(self):
        self.write_script()
        self.define_script()
        self.create_template()
        self.import_geo_bdf()
        self.define_cel_expression( 'Zground',  '0.99[m]')
        self.define_velocity_profil()
        self.define_turbulence()
        self.define_temperature_ref()
        self.define_pressur_coef()
        self.define_cel_expression( 'coefvitess1',  '5.85[W m^-2 K^-1]')
        self.define_cel_expression( 'coefvitess2',  '1.7[W s m^-3 K^-1]')
        self.define_cel_expression( 'CHTC',  'coefvitess1 +coefvitess2 *Velocity')
        self.define_domain(self.list_fluid[0], False)
        self.create_all_TS()
        self.define_multiboundary()
        self.define_multiinterfaces() 
        self.max_iteration_number = 2000 
        self.write_change_solver_control()     
        self.save_as_project()
        
#         self.run_simulation_cfx()
#         self.f.close()
        
        
    def write_expert_mode(self):
        ''' function write the command to activate the expert mode to activate/desactivate fluid solver'''
        self.f.write('setup1.SendCommand(Command="""FLOW: Flow Analysis 1\n')
        self.f.write('&replace   EXPERT PARAMETERS: \n')
        self.f.write('    solve energy = t\n')
        self.f.write('    solve fluids = f\n')
        self.f.write('    solve turbulence = f\n')
        self.f.write('  END # EXPERT PARAMETERS:\n')
        self.f.write('END # FLOW:Flow Analysis 1\n')
        self.f.write('PARAMETERIZATION:\n')
        self.f.write('END""")\n')
        
    


        
        

        

                

        
class Fluid():
    def __init__(self):
        self.name = 'canopy'   
        self.heat_transfert_option = 'Thermal Energy'        
class Model_CFX():
    
    def __init__(self):
        self.ansys_directory = r"D:/Users/adrien.gros/projet_ansys"
        self.list_boundary ={}
        self.list_fluid = []
        self.Zref = 10
        self.Uref = 3
        self.Vref = 0
        self.Tref = 18
        self.Zground = 1
        self.velocity = 3
        self.month,self.days,self.hours = '1','1','1'#01:00:00'

        self.name_domaine = 'canopy'
        self.meteo_directory = ''
        self.option_outdoor_indoor = False


    def record_name(self,name):
        newname = name[0]
        for j in xrange(1,len(name)):
            if name[j]!='-':
                newname+=name[j]
        return newname  
    def create_script(self):  
#         self.script = Script_Ansys()

        
        self.script.list_fluid  = self.list_fluid 
        self.script.list_boundary  = self.list_boundary 
        self.script.list_interfaces = self.list_interfaces
        self.script.month,self.script.days,self.script.hours  = self.month,self.days,self.hours 
        self.script.Zref , self.script.Uref ,self.script.Vref , self.script.Tref, self.script.velocity, self.script.Zground = self.Zref , self.Uref ,self.Vref , self.Tref, self.velocity, self.Zground
        self.script.name_domaine = self.name_domaine


        
    def create_dico_surface_from_idf(self,dico_idf):
        """ function that use dico_idf the dictionnary created by the class IDF to create a liste of dictionnary 
        with all the informations need to define boundary in Ansys"""
        self.list_boundary = []
        for key in dico_idf.keys():
            self.list_boundary.append({})
            self.list_boundary[-1]['name'] = self.record_name(key)
            nom = self.list_boundary[-1]['name'][0]
            for i in xrange(1,len(self.list_boundary[-1]['name'])):
                
#                 if self.list_boundary[-1]['name'][i]=='-':
#                     nom = nom+'_'
#                 else:
#                     nom+=self.list_boundary[-1]['name'][i] 
                if self.list_boundary[-1]['name'][i]!='-':
                    nom+=self.list_boundary[-1]['name'][i] 
            self.list_boundary[-1]['name'] = nom        
            self.list_boundary[-1]['location_name'] = 'PSHELL '+str(dico_idf[key][0])
            self.list_boundary[-1]['temperature_celsius'] = 20
            self.list_boundary[-1]['heat_transfert_option'] = 'Fixed Temperature'
            self.list_boundary[-1]['boundary_type'] = 'WALL'
            if self.list_boundary[-1]['name']=='sideatmosphere2':
                self.list_boundary[-1]['boundary_type'] = 'OUTLET'
            elif self.list_boundary[-1]['name']=='sideatmosphere4':
                self.list_boundary[-1]['boundary_type'] = 'INLET'
                self.list_boundary[-1]['heat_transfert_option'] = 'Static Temperature'
            elif (self.list_boundary[-1]['name']=='sideatmosphere1') or (self.list_boundary[-1]['name']=='sideatmosphere3') or (self.list_boundary[-1]['name']=='solatmosphere') or (self.list_boundary[-1]['name']=='topatmosphere'):
                self.list_boundary[-1]['heat_transfert_option'] = 'Adiabatic'
            
    def create_dico_boundary_from_idf(self,dico_idf,suffix ='',list_intersurface = []):
        """ function that use dico_idf: the dictionnary created by the class IDF to create a dictionnary of boundary
        with all the informations need to define boundary in Ansys CFX"""
        self.list_boundary = {}
        self.list_interface = {}
        self.pshell_number = 1
        for key in dico_idf.keys():
            
            nom = key[0]
            
            for i in xrange(1,len(key)):
                
#                 if self.list_boundary[-1]['name'][i]=='-':
#                     nom = nom+'_'
#                 else:
#                     nom+=self.list_boundary[-1]['name'][i] 
                if (key[i]!='-')&(key[i]!='(')&(key[i]!=')'):
                    nom+=key[i] 
#             if 'atmosphere' not in nom:
#                 nom = nom+'int'
#             print 'nom = ',nom
#             if nom not in list_intersurface:
#                 if 'Zona1' in nom:
#                     nom = nom+'ext'
#                 if 'atmosphere' not in nom:
#                     nom = nom+'ext
            if dico_idf[key]['side']=='out':
                nom = nom+'ext'
            if suffix not in nom:
                nom = nom+suffix
            print 'nom = ',nom
            self.list_boundary[nom] = {}     
            self.list_boundary[nom]['location_name'] = 'PSHELL '+str(dico_idf[key]['id_surface'][0])
            if self.pshell_number < dico_idf[key]['id_surface'][0]:
                self.pshell_number = dico_idf[key]['id_surface'][0]
            self.list_boundary[nom]['temperature_celsius'] = 20
            self.list_boundary[nom]['heat_source'] = False
            self.list_boundary[nom]['heat_transfert_option'] = 'Fixed Temperature'
            self.list_boundary[nom]['boundary_type'] = 'WALL'
            self.list_boundary[nom]['type'] = dico_idf[key]['type']
            self.list_boundary[nom]['mass_and_momemtum_option'] = 'No Slip Wall'
            if nom=='sideatmosphere2':
                self.list_boundary[nom]['boundary_type'] = 'OUTLET'
                self.list_boundary[nom]['speed_option'] = 'Cartesian Velocity'
                self.list_boundary[nom]['U']='Uinlet'
                self.list_boundary[nom]['V']='Vinlet'
                self.list_boundary[nom]['W']='0 [m s^-1]'
            elif nom=='sideatmosphere4':
                self.list_boundary[nom]['boundary_type'] = 'INLET'
                self.list_boundary[nom]['heat_transfert_option'] = 'Static Temperature'
                self.list_boundary[nom]['speed_option'] = 'Cartesian Velocity'
                self.list_boundary[nom]['U']='Uinlet'
                self.list_boundary[nom]['V']='Vinlet'
                self.list_boundary[nom]['W']='0 [m s^-1]'
            elif (nom=='sideatmosphere1') or (nom=='sideatmosphere3') or (nom=='solatmosphere') or (nom=='topatmosphere'):
                self.list_boundary[nom]['heat_transfert_option'] = 'Adiabatic'
            if (nom=='sideatmosphere1') or (nom=='sideatmosphere3')  or (nom=='topatmosphere'):
                self.list_boundary[nom]['mass_and_momemtum_option'] = 'Specified Shear'
                
#                 
#         self.list_boundary['topatmosphere']['mass_and_momemtum_option'] = 'Specified Shear'
#         self.list_boundary['sideatmosphere1']['mass_and_momemtum_option'] = 'Specified Shear'
#         self.list_boundary['sideatmosphere3']['mass_and_momemtum_option'] = 'Specified Shear'
              

               
    def create_dico_boundary_from_idf_outdoor_indoor(self,batidf):#dico_idf,list_intersurface, suffix = '', list_indoor_wall):
        """ function that use batidf.dico_surf_gr_phy: the dictionnary created by the class IDF to create a dictionnary of boundary
        with all the informations need to define boundary in Ansys CFX
        this function allows too to calculate the location name ( PSHELL number for each surface)"""
        self.create_dico_boundary_from_idf(batidf.dico_surf_gr_phy,'' , batidf.list_intersurface)


        '''the higher pshell number correspond to the pschell_number of the solatmosphere'''
#         self.pshell_number = batidf.dico_surf_gr_phy['solatmosphere']['id_surface'][0] 
        for gr_phy_name in batidf.list_intersurface:
            name = self.record_name(gr_phy_name)+'ext'
            self.pshell_number+=1
            self.list_boundary[name] = {}     
            self.list_boundary[name]['location_name'] = 'PSHELL '+str(self.pshell_number)

            self.list_boundary[name]['temperature_celsius'] = 20
            self.list_boundary[name]['heat_source'] = False
            self.list_boundary[name]['heat_transfert_option'] = 'Fixed Temperature'
            self.list_boundary[name]['boundary_type'] = 'WALL'
            self.list_boundary[name]['type'] = batidf.dico_surf_gr_phy[gr_phy_name]['type']
            self.list_boundary[name]['mass_and_momemtum_option'] = 'No Slip Wall'
            
           
        self.create_dico_interface_from_boundary()
    def modify_heat_source_boundary(self,nameboundary,value):
        ''' function to assign the heat source for the boundary named 'nameboundary' with value'''
        self.list_boundary[nameboundary]['heat_source'] = value
    def create_dico_interface_from_boundary(self):
        ''' function create the dictionnary self.list_interfaces
        it will check all the keys of self.list_boundary and transform it'''
        self.list_interfaces = {}
        list_already_used = []
        for key in self.list_boundary.keys():
            if key not in list_already_used:
                if self.list_boundary[key]['type']=='INTERFACE':               

                    if key[-3:]=='ext':
                        name = key[:-3]
                        nameext = key
                        nameside1 = name+' Side 1'
                        nameside2 = name+' Side 2'
                        
                    else:
                        name = key
                        nameext = name+'ext'
                        nameside1 = name+' Side 1'
                        nameside2 = name+' Side 2'
                    self.list_interfaces[name] =  {}
                    self.list_interfaces[name]['location_name1'] = self.list_boundary[name]['location_name'] 
                    self.list_interfaces[name]['location_name2'] = self.list_boundary[nameext]['location_name'] 
#                     self.list_boundary[nameside2] = self.list_boundary[nameext]
#                     self.list_boundary[nameside1] = self.list_boundary[name]
#                     self.list_boundary[nameside1]['boundary_type'] = 'INTERFACE'
#                     self.list_boundary[nameside2]['boundary_type'] = 'INTERFACE'
                    del self.list_boundary[nameext]
                    del self.list_boundary[name]
                    list_already_used.append(name)
                    list_already_used.append(nameext)
                    
    def create_dico_boundary_from_interface(self):
        
        list_already_used = []
        for name in self.list_interfaces.keys():
#             if name not in list_already_used:
            nameside1 = name+' Side 1'
            nameside2 = name+' Side 2'
            
            self.list_boundary[nameside1] =  {}
            self.list_boundary[nameside2] =  {}
            self.list_boundary[nameside1]['boundary_type'] = 'INTERFACE'
            self.list_boundary[nameside2]['boundary_type'] = 'INTERFACE'
            self.list_boundary[nameside1]['location_name'] = self.list_interfaces[name]['location_name1']
            self.list_boundary[nameside2]['location_name'] = self.list_interfaces[name]['location_name2']
            self.list_boundary[nameside1]['temperature_celsius'] = 20
            self.list_boundary[nameside1]['heat_transfert_option'] = 'Fixed Temperature'
            self.list_boundary[nameside1]['type'] = 'INTERFACE'
            self.list_boundary[nameside2]['temperature_celsius'] = 20
            self.list_boundary[nameside2]['heat_transfert_option'] = 'Fixed Temperature'
            self.list_boundary[nameside2]['type'] = 'INTERFACE'  
            
#             del self.list_interfaces[name]
    
                
#                 list_already_used.append(nameside1)
#                 list_already_used.append(nameside2)
                     
    def create_user_surface_and_table(self,distance = '0.5'):    
        for name in self.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):#if name in self.domus_results.ts_dic:       
                name_user_surface = name+'us'
                self.script.create_user_surface_offset(name,distance,name_user_surface)
        self.script.create_table()
        
    def create_average_value_for_table(self):
        for name in self.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):# name not in self.domus_results.ts_dic:       
                name_user_surface = name+'us'
                TA_expression_name = 'TA'+name
                Vel_expression_name = 'VEL'+name
                self.script.compute_average_temperature(name_user_surface,TA_expression_name)
                self.script.compute_average_velocity(name_user_surface,Vel_expression_name)
#         self.create_table() 
        ''' writing of titles'''   
        self.script.write_value_in_cell_table('A1','nom')  
        self.script.write_value_in_cell_table('B1','Temperature[K]')
        self.script.write_value_in_cell_table('C1','velocity[m.s-1]')
        index=1 
        for name in self.list_boundary.keys():
            if (name.find('atmosphere')==-1) and (name.find('Side')==-1):#if name in self.domus_results.ts_dic:     
                index+=1  
                
                TA_expression_name = 'TA'+name
                Vel_expression_name = 'VEL'+name
                self.script.write_value_in_cell_table('A'+str(index),name)  
                self.script.write_value_in_cell_table('B'+str(index),'='+TA_expression_name)
                self.script.write_value_in_cell_table('C'+str(index),'='+Vel_expression_name)
                
        
        
    def save_table_value(self,name_file):
        ''' function to save values in the table in CFX (where average values (temperature, velocity,...) are resumed) in a txt file'''
#         hours = self.hours[:2]+'H'+self.hours[3:5]+'M'+self.hours[-2:]
#         name_file = self.script.file_name_result_ansys+'results_'+self.month+'_'+self.days+'_'+self.hours+'H.txt'
#         self.cfx_model.script.project_path = self.xml_data.file_name_project_ansys
        
        self.script.write_save_table(name_file,'table_CHTC_TA')   
             
        
              
    def assign_ts_from_domus_results(self,domus_results):
        
#         for i in xrange(len(self.list_boundary)):
#             name = self.list_boundary[i]['name']
#             if name in domus_results.ts_dic:
#                 value = domus_results.ts_dic[name][self.month][self.days][self.hours][0]
#                 self.list_boundary[i]['temperature_celsius'] = value
                
        for name in self.list_boundary.keys():
            if name in domus_results.ts_dic:
                value = domus_results.ts_dic[name][self.month][self.days][self.hours][0]
                self.list_boundary[name]['temperature_celsius'] = value
    
    def assign_ts_from_domus_results_outdoor_indoor(self,domus_results):
        self.assign_ts_int_from_domus_results(domus_results)
        self.assign_ts_ext_from_domus_results(domus_results)
        
    def assign_ts_from_domus_bin_results(self):                
        for name in self.list_boundary.keys():
            domus_name
            if name in domus_results.ts_int_dic:
                value = domus_results.ts_int_dic[name][self.month][self.days][self.hours][0]
                self.list_boundary[name]['temperature_celsius'] = value 
                
    
              
    def assign_ts_int_from_domus_results(self,domus_results):

                
        for name in self.list_boundary.keys():
            if name in domus_results.ts_int_dic:
                value = domus_results.ts_int_dic[name][self.month][self.days][self.hours][0]
                self.list_boundary[name]['temperature_celsius'] = value
                
    def assign_ts_ext_from_domus_results(self,domus_results):

                
        for name in self.list_boundary.keys():
            if name in domus_results.ts_dic:
                value = domus_results.ts_dic[name][self.month][self.days][self.hours][0]
                self.list_boundary[name]['temperature_celsius'] = value
            
                

        
    def read_meteo_data_from_domus(self):
        month,days,hours = [],[],[]
        temperature,wet,direct_rad,diffus_rad,wind_dir,wind_vel = [],[],[],[],[],[]
        
        f = open(self.meteo_directory, "r")
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
#         print self.meteo_data
    def assign_meteo_data_boundary(self):
        ''' function to read meterological data
        in the table self.meteo_data, month,days and hours have to be str()'''
#         hours = str(int(self.hours.split(':')[0]))
        self.Tref = self.meteo_data[self.month][self.days][self.hours]['temperature']
        self.direction = self.meteo_data[self.month][self.days][self.hours]['wind_dir']
        self.direction = round(float(self.direction)/10)*10-90# on soustrait 90 car dans domus le nord est dans la direction -X
        if self.direction<0:
            self.direction = self.direction+360
        print 'in the climatic file the direction is ',self.meteo_data[self.month][self.days][self.hours]['wind_dir'],' and the cfd it will be ',self.direction
        
        self.velocity = self.meteo_data[self.month][self.days][self.hours]['wind_vel']
        if self.velocity==0.0:
            self.velocity=0.01
        
    def assign_meteo(self,temp,direction,velocity):
        self.Tref = temp
        self.direction = direction
        self.velocity = velocity
        
    def comput_U_V_ref(self):
        self.Uref = round(-math.sin(self.direction*2*math.pi/360)*self.velocity,6)
        self.Vref = round(-math.cos(self.direction*2*math.pi/360)*self.velocity,6)
        
    def define_boundary_from_meteo(self):
        ''' function to define boundary type for sideatmosphere1,2,3,4 according to the direction to the wind'''
        if self.direction==0 or self.direction==360:
            self.list_boundary['sideatmosphere1']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere1
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere2'])# corresponding to sideatmosphere2
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere3'])
            #  self.list_boundary['sideatmosphere3']['boundary_type'] = 'INLET'# corresponding to sideatmosphere3
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere4'])# corresponding to sideatmosphere4
            
        elif self.direction==90:
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere1'])# corresponding to sideatmosphere1

            #  self.list_boundary['sideatmosphere2']['boundary_type'] = 'INLET'# corresponding to sideatmosphere2
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere2'])
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere3'])# corresponding to sideatmosphere3
            self.list_boundary['sideatmosphere4']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere4
            
        elif self.direction==180:
            #self.list_boundary['sideatmosphere1']['boundary_type'] = 'INLET'# corresponding to sideatmosphere1
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere1'])
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere2'])# corresponding to sideatmosphere2

            self.list_boundary['sideatmosphere3']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere3
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere4'])# corresponding to sideatmosphere4

        elif self.direction==270 or self.direction== -90:
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere1'])# corresponding to sideatmosphere1
            self.list_boundary['sideatmosphere2']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere2
            self.define_boundary_wal_atmo(self.list_boundary['sideatmosphere3'])# corresponding to sideatmosphere3
            #self.list_boundary['sideatmosphere4']['boundary_type'] = 'INLET'# corresponding to sideatmosphere4
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere4'])
        elif self.direction<90:
            self.list_boundary['sideatmosphere1']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere1
            self.list_boundary['sideatmosphere2']['boundary_type'] = 'INLET'# corresponding to sideatmosphere2
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere2'])
            self.list_boundary['sideatmosphere3']['boundary_type'] = 'INLET'# corresponding to sideatmosphere3
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere3'])
            self.list_boundary['sideatmosphere4']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere4
        elif self.direction<180:
            self.list_boundary['sideatmosphere1']['boundary_type'] = 'INLET'# corresponding to sideatmosphere1
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere1'])
            self.list_boundary['sideatmosphere2']['boundary_type'] = 'INLET'# corresponding to sideatmosphere2
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere2'])
            self.list_boundary['sideatmosphere3']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere3
            self.list_boundary['sideatmosphere4']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere4
        elif self.direction<270:
            self.list_boundary['sideatmosphere1']['boundary_type'] = 'INLET'# corresponding to sideatmosphere1
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere1'])
            self.list_boundary['sideatmosphere2']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere2
            self.list_boundary['sideatmosphere3']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere3
            self.list_boundary['sideatmosphere4']['boundary_type'] = 'INLET'# corresponding to sideatmosphere4
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere4'])
        else:
            self.list_boundary['sideatmosphere1']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere1
            self.list_boundary['sideatmosphere2']['boundary_type'] = 'OUTLET'# corresponding to sideatmosphere2
            self.list_boundary['sideatmosphere3']['boundary_type'] = 'INLET'# corresponding to sideatmosphere3
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere3'])
            self.list_boundary['sideatmosphere4']['boundary_type'] = 'INLET'# corresponding to sideatmosphere4
            self.define_boundary_inlet_atmo(self.list_boundary['sideatmosphere4'])
            
    def define_boundary_wal_atmo(self,boundary):
        
        boundary['boundary_type'] = 'WALL'
        boundary['heat_transfert_option'] = 'Adiabatic'
        boundary['mass_and_momemtum_option']='Specified Shear'
        
    def define_boundary_inlet_atmo(self,boundary):
        
        boundary['boundary_type'] = 'INLET'
        boundary['speed_option'] = 'Cartesian Velocity'#'Normal Speed'#speed_option = Cartesian Velocity
        boundary['U']='Uinlet'
        boundary['V']='Vinlet'
        boundary['W']='0 [m s^-1]'

        
    def picklesaving_key(self,foldername,key):
#         print ' on va sauver'

        cPickle.dump(self.__dict__[key],open(foldername+key,'wb'))
        
                
    def pickleloading_keys(self,foldername,keys):
        
        self.__dict__[keys] = cPickle.load(open(foldername+keys))
if __name__ == "__main__": 
    
    cfx_simu = Model_CFX()
    cfx_simu.meteo_directory = r'D:/Users/adrien.gros/Documents/domus_project/casa_2janelas/meteo_curitiba.txt'
    cfx_simu.read_meteo_data_from_domus()
#     script = Script_Ansys()
#     script.name_domaine = 'canopyyybis'
#     script.project_path = r"D:/Users/adrien.gros/projet_ansys/sim_janelabisbisbis.wbpj"
#     script.bdf_geom_path = r'D:/Users/adrien.gros/Documents/domus_project/sem_janela/sem_janela.bdf'
#     script.file_name_script = r'D:\Users\adrien.gros\projet_ansys\sim_janela_files\creer_projetbis.wbjn'
#     script.Zref = 10
#     script.Uref = 3
#     script.name_domaine = 'canopyyyyy3'
#     script.write_project_creation()
#     script.run_script()
#     nom_fichier = r'D:\Users\adrien.gros\projet_ansys\sim_janela_files\journal_execution_simupython.wbjn'
#     
#     
#     nom_fichier = r'D:\Users\adrien.gros\projet_ansys\sim_janela_files\journal_execution_simupython.wbjn'
#     script_ansys = Script_Ansys(nom_fichier)
#     script_ansys.modify_surface_temperature_boundary(34,'wall2','PSHELL 2')
#     ANSYSpath = r'C:\Program Files\ANSYS Inc\v171\Framework\bin\Win64\RunWB2.exe'
# #     filepath4 = r'-R D:\Users\adrien.gros\projet_ansys\casa_sol_janelas_files\journal_execution_simu.wbjn'
# #     filepath4 = r'-R D:\Users\adrien.gros\projet_ansys\casa_sol_janelas_files\changement_temperature.wbjn'
#     filepath4 = r'-R D:\Users\adrien.gros\projet_ansys\sim_janela_files\journal_execution_simupythonbis.wbjn'
#     filepath4 = r'-R D:\Users\adrien.gros\projet_ansys\sim_janela_files\ouvrir_projet_et_changer_temperature_wall2.wbjn'
#     filepath4 = r'-R D:\Users\adrien.gros\projet_ansys\sim_janela_files\ouvrir_projet_et_changer_temperature_wall2bis.wbjn'
#     subprocess.Popen("%s %s -B" % (ANSYSpath, filepath4))
    print 'la simulation ANSYS a ete effectue'