#-*-coding: utf-8 -*-
'''
Created on 18 mars 2014

@author: agros01
'''
#import numpy as np


class Vecteur():
    '''
    class qui définit l'objet vecteur
    '''
    def __init__(self,A,B):
        '''
        un vecteur est défini par 2 point:
        '''
        self.vec=[B[0]-A[0],B[1]-A[1],B[2]-A[2]]
        #self.vec=np.array(self.vec)
        """ et une norme """
        self.norm=((B[0]-A[0])**2+(B[1]-A[1])**2+(B[2]-A[2])**2)**0.5
        """ le vecteur est normalisé"""
        self.vec = self.vec/self.norm
        
def pscalaire(u,v):
    '''
    produit scalaire ente le vecteur u et v
    '''
    p=u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
    return p  

def pvectoriel(u,v):
    '''
    produit vectoriel ente le vecteur u et v
    '''
    p=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    return p    
def svec(a1,a2):
    "somme de deux vecteur a1 et a2"
    a3=[a2[0]+a1[0],a2[1]+a1[1],a2[2]+a1[2]]
    return a3        
def norme_vec(u):
    norme=(u[0]**2+u[1]**2+u[2]**2)**0.5
    return norme
def calcul_centre_gravite(liste):
    '''
    Calcul du centre de gravité
    '''

    xg=0
    yg=0
    zg=0
    for i in range (len(liste)):
        xg+=liste[i][0]
        yg+=liste[i][1]
        zg+=liste[i][2]
    xg=xg/len(liste)
    yg=yg/len(liste)
    zg=zg/len(liste)
    G=[xg,yg,zg]
    return G

class Plan():
    '''
    caractéristique d'un plan défini par 3 ou 4 points
    Ces Plan sont les mailles générés par GMSH ou celles d'un cir
    '''
    def __init__(self, points):
        '''
        un plan est définit par:
        '''
        """ un plan peut auusi etre defini à l'aide d'indice de noeuds"""
#         self.noeuds = []
        '''un indice d'interface auquelle il est associé
        '''
#         self.i_inter=-1
        '''
         trois points A,B et C
        '''
        if len(points)== 3: 
            self.A, self.B, self.C = points
            self.nature=['triangle']

            """ 
            ou 4 points
            """       
        
        elif len(points)== 4:
            self.A, self.B, self.C, self.D = points
            '''
            si les points sont tous à altitude égal:c'est un quadrangle
            '''
            if (self.A[2]==self.B[2])&(self.A[2]==self.C[2])&(self.A[2]==self.D[2]):
                self.nature=['quadrangle']
                '''
                sinon c'est un rectangle qui est vertical
                '''
            else:
                self.nature=['rectangle']
                '''
                il faut déterminer des extremités xmin,xmax,ymin, ymax, zmin et zmax
                '''
                # Recherche du plus grand élément d'une liste
                # Liste fournie au départ :
                #tt = [32, 5, 12, 8, 3, 75, 2, 15]
                # Au fur et à mesure du traitement de la liste, on mémorisera dans
                # la variable ci-dessous la valeur du plus grand élément déjà trouvé :
                self.xmax = 0
                self.xmin=points[0][0]
                self.ymax = 0
                self.ymin=points[0][1]
                self.zmax = 0
                self.zmin=points[0][2]
                # Examen de tous les éléments :
                for i in range(len(points)):
                    if points[i][0] > self.xmax:
                        self.xmax = points[i][0] # mémorisation d'un nouveau maximum
                    if points[i][1] > self.ymax:
                        self.ymax = points[i][0]    
                    if points[i][2] > self.zmax:
                        self.zmax = points[i][0]
                    if points[i][0] < self.xmin:
                        self.xmin = points[i][0]
                    if points[i][1] < self.ymin:
                        self.ymin = points[i][0]
                    if points[i][2] < self.zmin:
                        self.zmin = points[i][0]
                
                                 
        else:
             print "nb de points incorrect"
             self.nature=['polygone']
             self.A=points[0]
             """cela correspond a des toits qui font plus de 4 points et sont horizontaux"""
             self.n=[0,0,1]
        '''
        *un tableau de point:
        '''
        self.points= list(points)  
        """une surface"""
        self.S = Polygone(self.points).S      
        '''
        *4 segments (ou 3)(cela suppose que les point sont données dans un ordre précis:ABCD forme un rectangle):
        '''
        self.segment=[]
        for i in range(len(self.points)):

#            self.segment.append({})
#            self.segment[i]['prop']=Droite(self.points[i-1],self.points[i]).prop
            self.segment.append(Droite(self.points[i-1],self.points[i]))
            '''
            si c'est un triangle ou un quadrangle il y a 3 ou 4 équations (y=mx+p ou x=m) de droite qui définisse ce plan
            NB:ces équation de droite sont définis dans la classe Plan et non dans la classe Droite,
            car ces équations de droite ne sont utilisées que pour les segment délimitant ces plan
            alors que la classe Droite est aussi utilisés pour définir les arrétes des mailles
            '''
        if self.nature==['triangle'] or self.nature==['quadrangle']:
            for i in range(len(points)):             
                if (self.points[i-1][0]-self.points[i][0])!=0:
                    '''
                    si xa-xb!=0 alors l'équation de la droite est y=ax+b
                    '''
#                    self.segment[i]['equation']='y'
#                    self.segment[i]['coef']={}
#
#                    self.segment[i]['coef']['a']=(points[i-1][1]-points[i][1])/(points[i-1][0]-points[i][0])
#                    self.segment[i]['coef']['b']=points[i][1]-points[i][0]*self.segment[i]['coef']['a']
                    '''
                    pour chacune de ces droite il faut savoir si  les points constituants le plan sont supérieures ou inférieures à cette droite
                    '''
                    testinf,testsup=0,0
                    for j in range (len(points)):
                        """dans un premier temps on verifie que ce points n'est pas une extremités du segment:"""
                        if (points[j]!=self.segment[i].A)&(points[j]!=self.segment[i].B):
                            '''
                            si jy>ai*xj+bi
                            '''
                            if points[j][1]>(self.segment[i].a*points[j][0]+self.segment[i].b):
                                '''
                                il y a au moins 1 points qui est au dessus de la droite
                                '''
                                testsup+=1
                            '''
                            si jy<ai*xj+bi
                            '''
                            if points[j][1]<(self.segment[i].a*points[j][0]+self.segment[i].b):
                                '''
                                il y a au moins 1 points qui est en dessous de la droite
                                '''
                                testinf+=1
                    if testsup>0:
                        '''
                        si les points sont au dessus de la droite c'est une borne inferieur ('inf')
                        '''
                        self.segment[i].borne='inf'

                    if testinf>0:
                        '''
                        si les points sont en dessous de la droite c'est une borne superieur ('sup')
                        '''
                        self.segment[i].borne='sup'

                else:
                    '''
                    si xa=xb alors l'équation de la droite est x=a=xa=xb
                    '''
#                    self.segment[i]['equation']='x'
#                    self.segment[i]['coef']={}
#                    self.segment[i]['coef']['a']=points[i][0]
                    testinf,testsup=0,0
                    for j in range (len(points)):
                        """dans un premier temps on verifie que ce points n'est pas une extremités du segment:"""
                        if (points[j]!=self.segment[i].A)&(points[j]!=self.segment[i].B):
                            '''
                            si jx>ai
                            '''
                            if points[j][0]>(self.segment[i].a):
                                '''
                                il y a au moins 1 points dont la coordonnées x est superieur à a
                                '''
                                testsup+=1
                            '''
                            si jx<ai
                            '''
                            if points[j][0]<(self.segment[i].a):
                                '''
                                il y a au moins 1 points dont la coordonnées x est infrieur à a
                                '''
                                testinf+=1
                    if testsup>0:
                        '''
                        si il y a au moins 1 point au dessus de la droite c'est une borne inferieur ('inf')
                        '''
                        self.segment[i].borne='inf'

                    if testinf>0:
                        '''
                        si il y a au moins 1 point en dessous de la droite c'est une borne superieur ('sup')
                        '''
                        self.segment[i].borne='sup'
        '''
        Pour résumer:
        self.segment[i]={'borne':'inf'/'sup','prop':{'point1','point2','vec'},'équation':'x'/'y','coef':{'a','b'}}
        '''                       
        '''
        *par trois vecteur a1,a2, et a3
        '''
        '''
        *vecteur AB
        '''
        self.a1 = Vecteur(self.points[0],self.points[1])
        
#        self.a2 = Vecteur(self.A,self.D)
#        '''
#        *vecteur AC
#        '''
#        self.a3 = Vecteur(self.A,self.C)
        '''        
        *vecteur AC
        '''
        self.a2 = Vecteur(self.points[0],self.points[2])
        '''
        *vecteur AC??? ne sert a rien?
        '''
        self.a3 = svec(self.a1.vec,self.a2.vec)
        '''
        par une équation ax+by+cz+d=0
        '''
        self.a=self.a1.vec[1]*self.a2.vec[2]-self.a1.vec[2]*self.a2.vec[1]
        self.b=self.a1.vec[2]*self.a2.vec[0]-self.a1.vec[0]*self.a2.vec[2]
        self.c=self.a1.vec[0]*self.a2.vec[1]-self.a1.vec[1]*self.a2.vec[0]
        self.d=-(self.a*self.A[0]+self.b*self.A[1]+self.c*self.A[2])
        '''
        par un vecteur normal unitaire
        
        le vecteur normal se calcul comme le produit vectoriel du vecteur AB et du vecteur AC divisé par sa norme
        '''
        self.n=pvectoriel(self.a1.vec,self.a2.vec)
        """si la norme du vecteur est different de zero:"""
        if norme_vec(self.n)!=0:
            for i in range(len(self.n)):
                self.n[i]=-self.n[i]/norme_vec(self.n)
        self.n=[self.a,self.b,self.c]#pvectoriel(self.a1.vec,self.a2.vec)/(pvectoriel(self.a1.vec,self.a2.vec))
        
        
        for i in range(len(self.n)):
            self.n[i]=((self.a**2+self.b**2+self.c**2)**(-0.5))*self.n[i]
        '''
        un tableau de propriété
        '''
        if self.nature!=['polygone']:
            self.prop={"point":self.points,'vecteur':[self.a1,self.a2,self.a3],'coef':{'a':self.a,'b':self.b,'c':self.c,'d':self.d},'vecteur normal':self.n}
     
    def attribution_indice_noeuds(self,noeuds):
        """ un plan peut auusi etre defini à l'aide d'indice de noeuds"""
        self.noeuds = noeuds   
    def test_point_dans_rectangle(self, p):
        test=1
        '''
        Si le point est compris entre xmin et xmax
        '''
        if (p[0]<=self.xmax)&(p[0]>=self.xmin):
            '''
            Si le point est compris entre ymin et ymax
            '''
            if (p[1]<=self.ymax)&(p[1]>=self.ymin):
                '''
                Si le point est compris entre zmin et zmax
                '''
                if (p[2]<=self.zmax)&(p[2]>=self.zmin):
                    test=0
                else:
                    test=1
        '''
        si le test==0 le point est dans le rectangle
        '''
        return test
    
    
    
    def test_point_dans_plan(self, p):
        '''
        fonction qui permet de savoir si un point est dans un plan triangulaire ou quadrangulaire horizontal
        '''
        test=0
        '''
        On test que p.y est sup (ou inf) à a*p.x+b
        '''
        for i in range(len(self.segment)):
            if self.segment[i].coef=='y':
                if self.segment[i].borne=='inf':
                    '''
                    Si le segment i est une borne inférieur('inf') l'ordonnée du point à tester doit être supérieur
                    '''
                    if p[1]>=(self.segment[i].a*p[0]+self.segment[i].b):
                        test+=0
                    else:
                        test+=1
                if self.segment[i].borne=='sup':
                    '''
                    Si la droite i est une borne supérieur('sup') le point à tester doit être inférieur
                    '''
                    if p[1]<=(self.segment[i].a*p[0]+self.segment[i].b):
                        test+=0
                    else:
                        test+=1
            elif self.segment[i].coef=='x':
                if self.segment[i].borne=='inf':
                    '''
                    Si le segment i est une borne inférieur('inf') l'abcisse du point à tester doit être supérieur
                    '''
                    if p[0]>=(self.segment[i].a):
                        test+=0
                    else:
                        test+=1
                elif self.segment[i].borne=='sup':
                    '''
                    Si la droite i est une borne supérieur('sup') l'abcisse point à tester doit être inférieur
                    '''
                    if p[0]<=(self.segment[i].a):
                        test+=0
                    else:
                        test+=1

        '''
        si le test==0 le point est dans le plan
        '''
        return test
class Droite():
    def __init__(self,A,B):
        '''
        une droite est définis par deux point A et B
        '''
        self.A=A
        self.B=B
        """"
        par deux coefficient a et b (y=ax+b)"""
        """si c'est une droite avec x constant"""
        if A[0]==B[0]:
            self.a=A[0]
            self.b=0
            self.coef='x'
        else:
            self.coef='y'
            if A[1]==B[1]:
                self.a=0
                self.b=A[1]
            else:
                self.a=(A[1]-B[1])/(A[0]-B[0])
                self.b=A[1]-A[0]*self.a
        self.borne='inf'#ou sup   

        "par un vecteur directeur orienté positivement normalisé"
#        self.v=[abs(B[0]-A[0]),abs(B[1]-A[1]),abs(B[2]-A[2])]
        norme=((B[0]-A[0])**2+(B[1]-A[1])**2+(B[2]-A[2])**2)**0.5
#        print "norme=",norme
#        if norme==0:
#            self.v=[0,0,0]
#        else:
        self.v=[(B[0]-A[0])/norme,(B[1]-A[1])/norme,(B[2]-A[2])/norme]
        

        self.prop={'point1':A,'point2':B,'vec':self.v}
        
        "on defini les extremité min et max du segment pour pouvoir tester ensuite si des points sont compris dans les extremités "

        if A[0]<B[0]:
            self.xmax=B[0]
            self.xmin=A[0]
        else:
            self.xmax=A[0]
            self.xmin=B[0]
            
        if A[1]<B[1]:
            self.ymax=B[1]
            self.ymin=A[1]
        else:
            self.ymax=A[1]
            self.ymin=B[1]
        if A[2]<B[2]:
            self.zmax=B[2]
            self.zmin=A[2]
        else:
            self.zmax=A[2]
            self.zmin=B[2]
        
        
    def test_point_dans_segment(self, p):
        test=1
        '''
        Si le point est compris entre xmin et xmax
        '''
        if (p[0]<=self.xmax)&(p[0]>=self.xmin):
            '''
            Si le point est compris entre ymin et ymax
            '''
            if (p[1]<=self.ymax)&(p[1]>=self.ymin):
                '''
                Si le point est compris entre zmin et zmax:
                '''
                if (p[2]<=self.zmax)&(p[2]>=self.zmin):
                    test=0
                else:
                    test=1
        return test
    def test_droite_confondu(self,droite):
        if self.coef==droite.coef:
            if self.a==droite.a:
                if sef.b==droite.b:
                    """alors droite est confondu"""
                    return 0
        else:
            return 1
    def point_intersection_droite_plan(self,droite):
        if (self.coef=='y')& (droite.coef=='y'):
            """a1x+b1=a2x+b2, x(a1-a2)=b2-b1"""
            x=(droite.b-self.b)/(self.a-droite.a)
            y=self.a*x+self.b
            z=self.zmax
        elif (self.coef=='x')& (droite.coef=='y'):
            """on cherche le y de  droite tel que x= a de self"""
            """y=a2a1+b2"""
            x=self.a
            y=self.a*droite.a+droite.b
            z=self.zmax
        elif (self.coef=='y')& (droite.coef=='x'):  
            """on cherche le y de  self tel que x= a de droite"""
            """y=a2a1+b2"""
            x=droite.a
            y=droite.a*self.a+self.b
            z=droite.zmax
        return [x,y,z]

    
class Triangle():
    def __init__(self,A,B,C):
        '''
        un triangle est caractérisé par trois points A B C
        '''
        '''
        calcul de la longueur du coté a du triangle
        
        '''
        self.a=((B[0]-A[0])**2+(B[1]-A[1])**2+(B[2]-A[2])**2)**0.5
        '''        
        calcul de la longueur du coté b du triangle
        
        '''
        self.b=((C[0]-B[0])**2+(C[1]-B[1])**2+(C[2]-B[2])**2)**0.5
        '''        
        calcul de la longueur du coté c du triangle
        
        '''
        self.c=((A[0]-C[0])**2+(A[1]-C[1])**2+(A[2]-C[2])**2)**0.5
        '''
        calcul de la surface du triangle
        '''
        '''
        p est le demi perimetre
        '''
        p=(self.a+self.b+self.c)/2
        self.s=(abs(p*(p-self.a)*(p-self.b)*(p-self.c)))**0.5
        #self.prop={'surface':self.s}

class Polygone():
    
    def __init__(self,liste):  
        '''
        la liste contient les points qui sont les sommet du polygone
        
        ''' 
        '''
        vecteur normal =vecteur normal du plan coupant la section
          
        '''
        self.n=[]#[1,1,1]
        '''
        Calcul du centre de gravité
        '''

        self.xg=0
        self.yg=0
        self.zg=0
        for i in range (len(liste)):
            self.xg+=liste[i][0]
            self.yg+=liste[i][1]
            self.zg+=liste[i][2]
        self.xg=self.xg/len(liste)
        self.yg=self.yg/len(liste)
        self.zg=self.zg/len(liste)
        self.G=[self.xg,self.yg,self.zg]
        self.S=0
        '''
        Si le nombre de point de la liste est supérieur à 3, le polygone formé est décomposé en plusieurs triangles
        le centre de gravité forme un triangle avec chaque sommet du polygone
        Caclul de la surface polygone: somme des surface des triangles 
        '''
        if len(liste)>3:
            for i in range (len(liste)):
                t=Triangle(liste[i],liste[i-1],self.G)
                self.S+=t.s
        elif len(liste)==3:
            t=Triangle(liste[0],liste[1],liste[2])
            self.S+=t.s

