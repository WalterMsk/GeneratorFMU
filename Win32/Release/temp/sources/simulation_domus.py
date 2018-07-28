# -*- coding: utf-8 -*-
'''
Created on 17/10/2016

@author: adrien.gros
'''

from IDF_script import IDF
import subprocess
import pandas as pd
from types import *

class Domus_results():
    
    def __init__(self):
        self.list_surface_temperature = {}
        self.directory_name = ''
        self.estadoSim_directory = ''
        self.dico_surface = []
        self.list_id_face = []
        self.ts_dic = {}
        self.ts_int_dic = {}
        self.tin_dic = {}
    def zone_and_wall_numbering(self):
        ''' function to number each wall for each zone'''
        self.zonewall_number = []
        self.zonewall_numberbis = []
        zone_name = 'asdf'
        for wall in self.dico_surface:
            if wall['Zone Name']!=zone_name:
                zone_name = wall['Zone Name']
                indice = 1
            else:
                indice+=1
            wall['zone_&_wall_id'] = zone_name+'_Parede'+str(indice)+'_PerfilTemperatura.txt'
            self.zonewall_number.append(wall['zone_&_wall_id'])
#         indice = 0   
#         for i in self.list_id_face:
#             if self.dico_surface[i]['Zone Name']!=zone_name: 
#                 zone_name = self.dico_surface[i]['Zone Name']['Zone Name']
#                 indice = 1
#             else:
#                 indice+=1
#             self.dico_surface[i]['zone_&_wall_id'] = zone_name+'_Parede'+str(indice)+'_PerfilTemperatura.txt'
#             self.zonewall_numberbis.append(self.dico_surface[i]['zone_&_wall_id'])
            
            
    def multi_extract_surface_temperature(self):
        
        self.ts_dic = {}        
        for i in xrange(len(self.dico_surface)):
            name_file = self.directory_name+self.dico_surface[i]['zone_&_wall_id']

            serie = self.extract_surface_temperature(name_file,node_id = 1)
            key_name = self.dico_surface[i]['name']
            self.ts_dic[key_name] = serie
    def multi_extract_surface_temperature_ext(self):
        
                
        for i in xrange(len(self.dico_surface)):
            name_file = self.directory_name+self.dico_surface[i]['zone_&_wall_id']
            ''' spaces in name_file have to be deleted'''
            namefile=name_file[0]
            for l in name_file[1:]:
                if l!= ' ':
                    namefile+=l
            name_file = namefile
            serie = self.extract_surface_temperature(name_file,node_id = 1)
            key_name = self.dico_surface[i]['domus_name']+'ext'
            self.ts_dic[key_name] = serie
            
    def multi_extract_surface_temperature_int(self):
        
        for i in xrange(len(self.dico_surface)):
            name_file = self.directory_name+self.dico_surface[i]['zone_&_wall_id']
            ''' spaces in name_file have to be deleted'''
            namefile=name_file[0]
            for l in name_file[1:]:
                if l!= ' ':
                    namefile+=l
            name_file = namefile

            serie = self.extract_surface_temperature_int(name_file)
            key_name = self.dico_surface[i]['domus_name']
            self.ts_int_dic[key_name] = serie
            
            
    def extract_temperature_int(self,name_file):        
        month,days,hours = [],[],[]
        te = []
        
#         for i in xrange(node_id):
#             nodes_values.append([])
        f = open(name_file, "r")
        liste_file = f.readlines()
        for i in xrange(3,len(liste_file)):
            value = liste_file[i].split()
            month.append(value[4])
            days.append(value[5])
            hours.append(value[6])
            te.append(value[0])
#             if len(nodes_values)+4>len(value):
#                 print " the number of node asked is superior to the number of availaible nodes"
#                 break

#             for j in xrange(len(nodes_values)):
#                 nodes_values[j].append(value[3+j])
        ''' all these data are multiindexed with the multiindex function from pandas'''        
        data = [month,days,hours]
        name=['month', 'days','hours']
#         for i in xrange(len(nodes_values)):
#             data.append(nodes_values[i])
#             name.append('nodes'+str(i))

        index = pd.MultiIndex.from_arrays(data, names = name)
        s = pd.Series(te, index=data)
        #print s
        
        
        return s
    
    def extract_surface_temperature(self,name_file,node_id = 1):        
        month,days,hours = [],[],[]
        nodes_values = []
        
#         for i in xrange(node_id):
#             nodes_values.append([])
        f = open(name_file, "r")
        liste_file = f.readlines()
        for i in xrange(1,len(liste_file)):
            value = liste_file[i].split(';')
            month.append(value[0])
            days.append(value[1])
            hours.append(value[2])
#             if len(nodes_values)+4>len(value):
#                 print " the number of node asked is superior to the number of availaible nodes"
#                 break
            nodes_values.append([])
            for j in xrange(node_id):
                nodes_values[-1].append(value[3+j])
#             for j in xrange(len(nodes_values)):
#                 nodes_values[j].append(value[3+j])
        ''' all these data are multiindexed with the multiindex function from pandas'''        
        data = [month,days,hours]
        name=['month', 'days','hours']
#         for i in xrange(len(nodes_values)):
#             data.append(nodes_values[i])
#             name.append('nodes'+str(i))

        index = pd.MultiIndex.from_arrays(data, names = name)
        s = pd.Series(nodes_values, index=data)
        #print s
        
        
        return s
    
    def extract_surface_temperature(self,name_file,node_id = 1):        
        month,days,hours = [],[],[]
        nodes_values = []
        
#         for i in xrange(node_id):
#             nodes_values.append([])
        f = open(name_file, "r")
        liste_file = f.readlines()
        for i in xrange(1,len(liste_file)):
            value = liste_file[i].split(';')
            month.append(value[0])
            days.append(value[1])
            hours.append(value[2])
#             if len(nodes_values)+4>len(value):
#                 print " the number of node asked is superior to the number of availaible nodes"
#                 break
            nodes_values.append([])
            for j in xrange(node_id):
                nodes_values[-1].append(value[3+j])
#             for j in xrange(len(nodes_values)):
#                 nodes_values[j].append(value[3+j])
        ''' all these data are multiindexed with the multiindex function from pandas'''        
        data = [month,days,hours]
        name=['month', 'days','hours']
#         for i in xrange(len(nodes_values)):
#             data.append(nodes_values[i])
#             name.append('nodes'+str(i))

        index = pd.MultiIndex.from_arrays(data, names = name)
        s = pd.Series(nodes_values, index=data)
        #print s
        
        
        return s
    
#     def multiindexing_data
            

class Domus_comand():
    
    def __init__(self): 
        ''' class to realize operation on domus idf file : 
        
        i :  inclusion (Inclusão)
        s : substitution (Substituição)
        r : delete (remover) 
        or to run domus
        '''
        self.Domuspath = r'C:\Program Files (x86)\Domus - Eletrobras\DomusConsole.exe'       
        self.file_name_idf_domus = r'D:\Users\adrien.gros\Documents\domus_project\casa_2janelas\casa_2janelasinit.idf'
        self.modificationtxtpath = r'D:\Users\adrien.gros\Documents\domus_project\modification.txt'
        self.infoextractiontxtpath =  r'D:\Users\adrien.gros\Documents\domus_project\extractinfo.txt'
        self.change_option = 's'# or 'i' or 'r'
        self.class_name = 'Domus:Face:Relatorio'        
        self.object = 'Nome do objeto'# or '*'
        self.object_name = 'Rel_Face8'# 
        self.attribut_name = 'Monitora temperatura'
        self.new_value = '1'
        self.class_attributs = ['Rel_Face9','1','1','0','0','0','0','0','0']
        
    def change_in_idf(self):
        ''' function to change an object in a domus idf file'''
        subprocess.Popen("%s %s -m %s" % (self.Domuspath, self.file_name_idf_domus,self.modificationtxtpath)).wait()
        
    def write_inclusiontxt(self):
#         self.f = open(self.modificationtxtpath, 'w')
        self.f.write('i,%s'% (self.class_name))
        for i in self.class_attributs :
            self.f.write(',%s'% (i))
        self.f.write(';')
        self.f.write('\n')
#         self.f.close()  
        
    def write_modificationtxt(self):
        ''' exemple (that work) to attribute 1 to the 'Monitora temperatura' to class Domus:Face:Relatorio where 'Nome do objeto'  is Rel_Face8 :
        s,Domus:Face:Relatorio,Nome do objeto,Rel_Face8,Monitora temperatura,1;
        '''
#         self.f = open(self.modificationtxtpath, 'w')
        self.f.write('s,%s,%s,%s,%s,%s;'% (self.class_name,self.object, self.object_name,self.attribut_name,self.new_value))
        self.f.write('\n')
#         self.f.close()  
        
#     def change_
#     def extract_information(self):
#         ''' function to extract value from idf'''
#         DomusConsole.exe -C NomeProjeto.idf ArquivoConsulta.txt
#         subprocess.Popen("%s -C %s -m %s" % (self.Domuspath, self.file_name_idf_domus,self.modificationtxtpath)).wait()
    def change_simulation_date(self,monthi,dayi,hoursi,monthf,dayf,hoursf):
        self.f = open(self.modificationtxtpath, 'w')
        self.class_name = 'DOMUS:PARAMETROSGERAIS'
        self.object = ''
        self.object_name = '' 
        self.attribut_name = 'Tempo de simulacao - mes inicial'
        self.new_value = monthi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de simulacao - dia inicial'
        self.new_value = dayi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de simulacao - Hora inicial'
        self.new_value = hoursi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de simulacao - mes final'
        self.new_value = monthf
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de simulacao - dia final'
        self.new_value = dayf
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de simulacao - Hora final'
        self.new_value = hoursf
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - mes inicial'
        self.new_value = monthi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - dia inicial'
        self.new_value = dayi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - Hora inicial'
        self.new_value = hoursi
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - mes final'
        self.new_value = monthf
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - dia final'
        self.new_value = dayf
        self.write_modificationtxt()
        self.attribut_name = 'Tempo de relatorio - Hora final'
        self.new_value = hoursf
        self.write_modificationtxt()
        self.f.close() 
        self.change_in_idf()
        
    def change_externe_condition_AC(self,object_name_list = ['Ac1_Atuadores_Zona 2'],externe_cond = ['0'], temperature = ['0'], humidity = ['0']):
        
        self.f = open(self.modificationtxtpath, 'w')
        self.class_name = 'DOMUS:ATUADOR:ARCONDICIONADO'
        
        self.change_option = 's'# or 'i' or 'r'
        
        self.class_name = 'Domus:Atuador:ArCondicionado' 
        for i in xrange(len(object_name_list)):       
            self.object = 'Nome do objeto'# or '*'
            self.object_name = object_name_list[i] 
            self.attribut_name = 'Fixar Condicoes Externas'
            self.new_value = externe_cond[i]
            self.write_modificationtxt()
            self.attribut_name = 'Temperatura Externa Fixa (C)\t   '
            self.new_value = temperature[i]
            self.write_modificationtxt()
            self.attribut_name = 'Umidade Relativa Externa Fixa\t   '
            self.new_value = humidity[i]
            self.write_modificationtxt()
        self.f.close() 
        self.change_in_idf()
        
        
if __name__ == "__main__":
    import struct
    ''' lecture d'un fichier binaire'''
    name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1'
    name_filebis = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\#piece_ventile_ext_fen_tuto\\saidas\estadoSim\\Zona 1 - cobertura 0-Zona 1bis'
#     name_file = 'D:\Users\\adrien.gros\\Documents\\domus_project\\piece_ventile_ext_fen_tuto\\test_data.dat'
    mon_fichier = open(name_file, "rb")
    mon_fichierbis = open(name_filebis, "rb")
#     try:
#         s = struct.Struct("<dffflfffffffl") # Binary data format
#         while True:
#             record = mon_fichier.read(56) # read the next /byte/
#             if len(record) != 56:
#                 break;
# #             if bytes == "":
# #                 break;
#             # Do stuff with byte
#             # e.g.: print as hex
# #             print "%02X " % ord(bytes[0]) 
#             print s.unpack(record)
#     except IOError:
#         # Your error handling here
#         # Nothing for this example
#         pass
#     finally:
#         mon_fichier.close()
#     
    
    
    
    a = len(mon_fichier.read())
    print"a:",a
    abis = len(mon_fichierbis.read())
    print"abis:",abis



    fichier = open(name_file, 'rb')
    fichierbis = open(name_filebis, 'rb')
    i=0
    while i<a/4:
#         print 'i=',i+1
#    for i in range(nb_triangles**2):
        val_oct = fichier.read(4)
        
        val_float = struct.unpack('f', val_oct)[0]
#         lst_facform[i] = float32(val_float)
        print 'i=',i+1,val_float
        val_octbis = fichierbis.read(4)
        
        val_floatbis = struct.unpack('f', val_octbis)[0]
#         lst_facform[i] = float32(val_float)
        print 'ibis=',i+1,val_floatbis
#         if type((i+1.0)/48)==int:
# #         if val_float==0:
#             print 'i=',i+1,val_float
#         else:
#             print 'i=',i+1,val_float,
#         val_octbis = fichier.read(2)
#         
#         val_floatbis = struct.unpack('f', val_octbis)[0]
# #         lst_facform[i] = float32(val_float)
#         print 'val_floatbis=',val_floatbis
        i+=1

    alteracao = Domus_comand()
#     alteracao.write_modificationtxt()
    ''' para cambiar horario de simulacao'''
    alteracao.file_name_idf_domus = r'D:\Users\adrien.gros\Documents\domus_project\piece_ventile_ext_fen_tuto\piece_ventile_ext_fen_tuto.idf'
    alteracao.modificationtxtpath = r'D:\Users\adrien.gros\Documents\domus_project\piece_ventile_ext_fen_tuto\modification.txt'
    alteracao.infoextractiontxtpath = r'D:\Users\adrien.gros\Documents\domus_project\piece_ventile_ext_fen_tuto\extractinfo.txt'
    alteracao.class_name = 'DOMUS:PARAMETROSGERAIS'
    alteracao.object = ''
    alteracao.object_name = ''       # 
    alteracao.attribut_name = 'Tempo de simulacao - Hora inicial'
    alteracao.new_value = '1'   
    alteracao.f = open(alteracao.modificationtxtpath, 'w')
    alteracao.write_modificationtxt()
    alteracao.f.close()
    alteracao.change_in_idf()
    alteracao.write_inclusiontxt()
    alteracao.change_in_idf()
    
    
    Domuspath = r'C:\Program Files (x86)\Domus - Eletrobras\DomusConsole.exe'
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\casa_2janelas\casa_2janelasinit.idf'
    alteraciontxt = r'D:\Users\adrien.gros\Documents\domus_project\alteration.txt'
    
    subprocess.Popen("%s -m %s" % (Domuspath, projectname))
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\casa_2janelasbis\model.idf'
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\casa_2andares\model.idf'
    subprocess.Popen("%s -q -txt %s" % (Domuspath, projectname))
    filenameresults = r'D:\Users\adrien.gros\Documents\domus_project\sem_janela\#sem_janela\saidas\sim002\Zona1_Parede1_PerfilTemperaturabis.txt'
    resultat = Domus_results()
    batidf = IDF()
    batidf.file_name_idf = r"D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela_nrj.idf"
    batidf.parsing(batidf.file_name_idf)
    batidf.dictionnary_surface()
    resultat.dico_surface = batidf.dico_surface
#     resultat.zone_and_wall_numbering()
#     resultat.extract_surface_temperature(filenameresults,2)
    Domuspath = r'D:\Users\adrien.gros\Domus - Eletrobras\DomusConsole.exe'
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\test.idf'
    Domuspath = r'C:\Program Files (x86)\Domus - Eletrobras\DomusConsole.exe'
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\sem_janela\sem_janela.idf'
    projectname = r'D:\Users\adrien.gros\Documents\domus_project\rua_canyon_multi\rua_canyon.idf'
    subprocess.Popen("%s -q -txt %s" % (Domuspath, projectname))
    filenameresults = r'D:\Users\adrien.gros\Documents\domus_project\#test\saidas\sim009\Zona1_Parede1_PerfilTemperatura.txt'
    filenameresults = r'D:\Users\adrien.gros\Documents\domus_project\sem_janela\#sem_janela\saidas\sim002\Zona1_Parede1_PerfilTemperatura.txt'
    f = open(filenameresults, "r")
    liste_file = f.readlines()
    table = []
    for i in xrange(len(liste_file)):
#             print(self.liste_idf_file[i])
         
        # vérification lignes vides
        if liste_file[i] != '\r\n' and liste_file[i] != '\n':
            table.append(liste_file[i].split())
#     Domuspath = r'D:\Users\adrien.gros\Domus - Eletrobras\DomusConsole.exe'
#     projectname = r'D:\Users\adrien.gros\Documents\domus_project\test.idf'
#     subprocess.Popen("%s -q %s" % (Domuspath, projectname))
    print 'la simulation domus a ete effectue'
    ''' lecture des resultats sous forme de binaire'''
    filename = r'D:\Users\adrien.gros\Documents\domus_project\sem_janela\Zon2Pr2.sda'
    f = open(filename, "rb")
    try:
        while True:
            bytes = f.read(1) # read the next /byte/
            if bytes == "":
                break;
            # Do stuff with byte
            # e.g.: print as hex
            print "%02X " % ord(bytes[0]) 
 
    except IOError:
        # Your error handling here
        # Nothing for this example
        pass
    finally:
        f.close()