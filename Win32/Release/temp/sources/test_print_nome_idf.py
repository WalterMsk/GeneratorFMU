# -*- coding: utf-8 -*-
'''
Created on 18/07/2018

@author: adrien.gros
'''
from IDF_script import IDF

def mostrar_nome_idf(nome_arquivo):
    return str(' le fichier idf est dans ' + nome_arquivo)
    

def construir_geo_com_idf(nome_arquivo_idf,nome_arquivo_geo):

    batidf = IDF()
    batidf.file_name_idf_domus = nome_arquivo_idf
    batidf.build_mockup()
    batidf.built_gmsh(nome_arquivo_geo)