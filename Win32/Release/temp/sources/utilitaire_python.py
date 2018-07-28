# -*- coding: utf-8 -*-
'''
Created on 02/10/2017

@author: adrien.gros
'''
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import shutil

def construire_graphique_multiresultats(resultat,abcisse = [],liste_mark = ['r--','b--','r','b'],liste_label=[],xlabel = 'vitesse ( m/s)',ylabel = 'CHTC (W/m^2.K^-1)',
                                        title = 'name',resultat2 = [],liste_mark2 = ['--','b--','r','b'],liste_label2=['Irradiance'],ylabel2 = 'Solar radiation (W/m^2)', location = 'upper right',
                                        enregistre_figure = False,nom_fichier = ''):

    ''' fonction pour creer un graphique'''
    #     plt.ylabel('temperature °C')
    #     plt.xlabel('time h')
    #     plt.title(name)
    fig, ax = plt.subplots()
    handles = []
    if abcisse==[]:
        abcisse = range(len(resultat[0]))
    for i in xrange(len(resultat)):
        if len(abcisse)!=len(resultat[i]):
            print 'il y a un probleme, len(liste des abcisse) = ',len(abcisse),' et len(resultat[',i,"]) = ",len(resultat[i])
        handles.append(ax.plot(abcisse, resultat[i], liste_mark[i],label = liste_label[i]))

    
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ''' si dans resultat2 la liste n'est pas vide, creation d'une seconde echelle a droite du graphique'''
    if len(resultat2)!=0:
        ax2 = ax.twinx()
        for i in xrange(len(resultat2)):
            if len(abcisse)!=len(resultat2[i]):
                print 'il y a un probleme, len(liste des abcisse) = ',len(abcisse),' et len(resultat[',i,"]) = ",len(resultat[i])
            handles.append(ax2.plot(abcisse, resultat2[i], liste_mark2[i],label = liste_label2[i]))
        ax2.set_ylabel(ylabel2)
        liste_label+=liste_label2
    line = handles[0]
    for i in xrange(1,len(handles)):
        line+=handles[i]
        
    ax.legend(line,liste_label,loc = location , shadow=True)
#     plt.plot(t, tint, 'r--', t, text, 'b--',label=['tem_int','tem_ext'])
#         fig.savefig(filename+name+'.png')
#         fig.savefig(filename+name+'.svg')
# #         plt.show()
#         deltatext = text-textbis
#         deltatint = tint-tintbis
#         deltafig, deltaax = plt.subplots()

#     legend = deltaax.legend(loc='upper left', shadow=True)

#         deltafig.savefig(filename+name+'delta.png')
#         deltafig.savefig(filename+name+'delta.svg')
#     plt.show()
    if enregistre_figure:
        plt.savefig(nom_fichier)
    else:
        plt.show()
    
    plt.close('all')
  
  
def construire_graphique_multiresultats_with_date(resultat,abcisse = [],liste_mark = ['r--','b--','r','b'],liste_label=[],xlabel = 'vitesse ( m/s)',ylabel = 'CHTC (W/m^2.K^-1)',title = 'name',filename=''):

     
    #     plt.ylabel('temperature °C')
    #     plt.xlabel('time h')
    #     plt.title(name)
    fig, ax = plt.subplots()
    
    if abcisse==[]:
        abcisse = range(len(resultat[0]))
    for i in xrange(len(resultat)):
        if len(abcisse)!=len(resultat[i]):
            print 'il y a un probleme, len(liste des abcisse) = ',len(abcisse),' et len(resultat[',i,"]) = ",len(resultat[i])
        ax.plot(abcisse, resultat[i], liste_mark[i],label = liste_label[i])

    
    legend = ax.legend(loc='upper left', shadow=True)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
#     plt.plot(t, tint, 'r--', t, text, 'b--',label=['tem_int','tem_ext'])
#         fig.savefig(filename+name+'.png')
#         fig.savefig(filename+name+'.svg')
# #         plt.show()
#         deltatext = text-textbis
#         deltatint = tint-tintbis
#         deltafig, deltaax = plt.subplots()

#     legend = deltaax.legend(loc='upper left', shadow=True)

#         deltafig.savefig(filename+name+'delta.png')
#         deltafig.savefig(filename+name+'delta.svg')
    plt.show()
    plt.close('all')
    
def to_move_folder1_in_folder2(folder1,folder2,deleted = True):
    ''' function to move the contents of the folder1 in the folder2'''
    ''' we check the folder2 doesn't already exist, if exist it is deleted to be able to copy folder1 in '''
    if os.path.exists(folder2):
        shutil.rmtree(folder2)
    ''' folder 1 is copy in folder 2'''
    shutil.copytree(folder1,folder2)
#         os.remove(self.xml_data.domus_results_directory)
    ''' the folder 1 is deleted'''
    if deleted:
        shutil.rmtree(folder1)

def creer_nouveau_dossier(nom_dossier,delete_option = True):
    ''' fonction pour creer un nouveau dossier
    la fonction verifie en premier si ce dossier existe deja'''
    if os.path.exists(nom_dossier):
        if delete_option:
            ''' si il existe , le document est supprime'''
            shutil.rmtree(nom_dossier)
            ''' ensuite le dossier est cree'''
            os.makedirs(nom_dossier)
    else:
        os.makedirs(nom_dossier)
    
def lire_fichier_txt(file_name):  
    file = open(file_name,'r')
    liste_file = file.readlines()
    table_idf = []
    for i in xrange(len(liste_file)):
#             print(self.liste_idf_file[i])
         
        # vérification lignes vides
        if liste_file[i] != '\r\n' and liste_file[i] != '\n':
            table_idf.append(liste_file[i].split()) 
    return table_idf

if __name__ == "__main__":
    project_name = r'BESTEST'
#     project_name = r'BESTEST_dense'
    file_name = r"D:/Users/adrien.gros/Documents/domus_project/"+project_name#casa_2andares"
    file_name_a_netoyer = r'D:\Users\adrien.gros\Documents\domus_project\BESTEST_dense\cfd_database'
    liste_ne_passupprimer = ['.txt', '.cfx', '.def', '.res', '.out']
    liste_dossier = os.listdir(file_name_a_netoyer)
    for dossier in liste_dossier:
        liste_dossierbis = os.listdir(file_name_a_netoyer+'/'+dossier)
        for nom_dossier in liste_dossierbis:
            if nom_dossier[-4:] not in liste_ne_passupprimer:
                directory_to_delete = file_name_a_netoyer+'/'+dossier+'/'+nom_dossier
                shutil.rmtree(directory_to_delete)

                print ' the directory',directory_to_delete,' is deleted'
                
