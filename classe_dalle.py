import psycopg2
import random as r
import sys
import time
import pickle

largeur_dalle=100000    #Eviter les problèmes de coordonnées
nb_dalle_h=0
nb_dalle_v=0

def lance_connection():
    # on crée la  connection 
    #90.23.160.189
    connect=psycopg2.connect(dbname="Zombicide", user="postgres", host="192.168.1.122", password="digifab")
    # on crée un curseur
    cur = connect.cursor()
    #execution requete
    return cur

class point:            #Permet de créer des points X/Y facilement à travers le code
    def __init__ (self,X,Y):
        self.X=X
        self.Y=Y

def changement_repere(p_c=point(0,0),orientation=0,p_d=point(0,0)):  # Formules de calcul pour l'orientation des dalles (0°,90°,180°,270°)
        
        global largeur_dalle
        L=largeur_dalle
        
        X_A=p_c.X #coordonnées de base
        Y_A=p_c.Y
        if(orientation==90): 
            X_A=p_c.Y #coordonnées 90°
            Y_A=L-p_c.X
        if(orientation==180):
            X_A=L-p_c.X #coordonnées 180°
            Y_A=L-p_c.Y
        if(orientation==270):
            X_A=L-p_c.Y #coordonnées 270°
            Y_A=p_c.X        
        X_A=X_A+L*p_d.X #formules de calcul
        Y_A=Y_A+L*p_d.Y

        point_retour=point(X_A,Y_A)

        return point_retour

def ordonne_donnees(V1,V2): # Euh...What ? O_o ?

    if (V2<V1):
        PIVOT=V1
        V1=V2
        V2=PIVOT
    return V1,V2


# Définitions des differentes classes nécessaires


class sorties:  #Les accès possibles entre chaques dalles
    
    def __init__(self,point1=point(0,0),point2=point(0,0),id_s=0):       
        self.point_s1=point(point1.X,point1.Y)  # objet de type point
        self.point_s2=point(point2.X,point2.Y)  # objet de type point
        self.id_s=id_s
        self.utilise=False
      
class dalle:  #Pour differencier les differentes dalles
    
    def __init__(self,nom_dalle="",p=point(0,0),orientation=0):
        
        self.nom_dalle=nom_dalle
        self.point_d=point(p.X,p.Y)
        self.orientation=orientation
                        
class zone:  #situer et séparer les dalles en plusieurs parties (rues, interieurs, égoûts)

    def __init__(self,curseur=None,id_zone="",egout=False,interieur="0",nom_dalle="",orientation=0,p_d=point(0,0)):
        
        
        self.liste_dalle_egout=[""]  
        self.liste_nom_dalle=[""]
        self.liste_zone_sortie=[""]
        self.liste_fusion=[""]
        self.liste_coordonnees=[point(0,0)]

        self.liste_dalle_egout.clear()  
        self.liste_nom_dalle.clear()
        self.liste_zone_sortie.clear()
        self.liste_fusion.clear()
        self.liste_coordonnees.clear()

        self.id_zone=id_zone

        self.i_zone=info_zone()
        
        if (egout=="1"):  #Règle d'exception pour les dalles ayant un égoût à gérer
            self.liste_dalle_egout.append(nom_dalle)
        
        self.interieur=interieur
        
        self.liste_nom_dalle.append(nom_dalle)           
        
        self.cle_sel=False       


        if (curseur==None):
            return

        curseur.execute('select "id_coordonnees","X_C","Y_C"  from "Coordonnees" where "id_zone"='+"'"+str(id_zone)+"'")

        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes
       
        for ligne in lignes:
            
            p_c=point(ligne[1],ligne[2])
            p=changement_repere(p_c,orientation,p_d)        
            self.liste_coordonnees.append(p)

        self.i_zone=info_zone(self.liste_coordonnees)

class info_zone:

    def __init__(self,L_C=[]):
        ID_C=0
        self.xmin=1000000
        self.xmax=-1000000
        self.ymin=1000000
        self.ymax=-1000000
        
        while (ID_C<len(L_C)):
            
            if (self.xmin>L_C[ID_C].X):
                self.xmin=L_C[ID_C].X

            if (self.xmax<L_C[ID_C].X):
                self.xmax=L_C[ID_C].X

            if (self.ymin>L_C[ID_C].Y):
                self.ymin=L_C[ID_C].Y

            if (self.ymax<L_C[ID_C].Y):
                self.ymax=L_C[ID_C].Y

            ID_C=ID_C+1

            self.h=self.ymax-self.ymin
            self.l=self.xmax-self.xmin

class porte:
    def __init__(self,Ouvert=True,Zone_1="",Zone_2=""):
        self.Ouvert=Ouvert
        self.Zone_1=Zone_1
        self.Zone_2=Zone_2






class plateau:  # Nommer, positionner et orienter les dalles sur la plateau de jeu 


    

    def __init__(self,curseur):

        self.liste_dalle=[dalle()]
        self.dict_zone={"":zone()}   
        self.liste_sorties=[sorties()]
        self.liste_porte=[porte(True,"","")]

        self.liste_porte.clear()   

        self.dict_zone.clear()             
        self.liste_sorties.clear()
        self.liste_dalle.clear()

        self.nb_dalle_h=0
        self.nb_dalle_v=0

        

        
        curseur.execute('select "nom_dalle","X_D","Y_D","orientation"  from "Plateaux"')

        ligne_dalles = curseur.fetchall()
        
        for ligne_dalle in ligne_dalles:
            nom_dalle=ligne_dalle[0]
            p_d=point(ligne_dalle[1],ligne_dalle[2])
            orientation= ligne_dalle[3]
            if (p_d.X>self.nb_dalle_h):
                self.nb_dalle_h=p_d.X
            if (p_d.Y>self.nb_dalle_v):
                self.nb_dalle_v=p_d.Y
            self.liste_dalle.append(dalle(nom_dalle,p_d,orientation))

        
        
            curseur.execute('select "id_sortie","X1","Y1","X2","Y2"  from "Sorties" where "nom_dalle"='+"'"+ nom_dalle+"'")

            lignes = curseur.fetchall()
        
            for ligne in lignes:
                id_sortie=ligne[0]
                p1=point(ligne[1],ligne[2])
                p2=point(ligne[3],ligne[4]) 
                p1=changement_repere(p1,orientation,p_d)
                p2=changement_repere(p2,orientation,p_d)

                self.liste_sorties.append(sorties(p1,p2,id_sortie))

            curseur.execute('select "id_zone","egout","interieur","nom_dalle"  from "Zones" where "nom_dalle"='+"'"+nom_dalle+"'")

            ligne_zones = curseur.fetchall()
            
            for ligne_zone in ligne_zones:
                id_zone=ligne_zone[0]
                egout=ligne_zone[1]
                interieur=ligne_zone[2]
                nom_dalle= ligne_zone[3]
                
                #self.liste_zone.append(zone(curseur,id_zone,egout,interieur,nom_dalle,orientation,p_d))

                self.dict_zone[id_zone]=zone(curseur,id_zone,egout,interieur,nom_dalle,orientation,p_d)

        
        self.nb_dalle_h=self.nb_dalle_h+1
        self.nb_dalle_v=self.nb_dalle_v+1
              
        #Création des portes

        curseur.execute('select "Ouvert","Zone_1","Zone_2" from "Porte"')

        ligne_portes = curseur.fetchall()
            
        for ligne_porte in ligne_portes:
            Ouvert=ligne_porte[0]
            Zone_1=ligne_porte[1]
            Zone_2=ligne_porte[2]

            self.liste_porte.append(porte(Ouvert,Zone_1,Zone_2)) #Youpi j'ai une liste de porte



        # recherche si zone à fusionner  (zone de rue)
        for cle_z,valeur_z in self.dict_zone.items():
            cle_test=cle_z
            if (valeur_z.interieur!="1") and (valeur_z.cle_sel==False):
                fusion_possible=True
                
                while (fusion_possible):



                    self.dict_zone[cle_test].cle_sel=True
                    retour_cle= self.recherche_suivante(cle_test)
                    if (retour_cle==""):
                        fusion_possible=False
                    else:
                        cle_test=retour_cle
                        valeur_z.liste_fusion.append(cle_test)





        liste_cle_des_zonez_a_supprimer=[]        
        for cle_z,valeur_z in self.dict_zone.items():

            xmin=valeur_z.i_zone.xmin
            xmax=valeur_z.i_zone.xmax
            ymin=valeur_z.i_zone.ymin
            ymax=valeur_z.i_zone.ymax


            
            if (len(valeur_z.liste_fusion)>0):

                for cle_suinvante in valeur_z.liste_fusion:


                    for dalle_egout_z in self.dict_zone[cle_suinvante].liste_dalle_egout:
                        valeur_z.liste_dalle_egout.append(dalle_egout_z)


                    for nom_dalle_z in self.dict_zone[cle_suinvante].liste_nom_dalle:
                        valeur_z.liste_nom_dalle.append(nom_dalle_z)


                    if (self.dict_zone[cle_suinvante].i_zone.xmin<xmin):
                        xmin= self.dict_zone[cle_suinvante].i_zone.xmin

                    if (self.dict_zone[cle_suinvante].i_zone.xmax>xmax):
                        xmax= self.dict_zone[cle_suinvante].i_zone.xmax

                    if (self.dict_zone[cle_suinvante].i_zone.ymin<ymin):
                        ymin= self.dict_zone[cle_suinvante].i_zone.ymin

                    if (self.dict_zone[cle_suinvante].i_zone.ymax>ymax):
                        ymax= self.dict_zone[cle_suinvante].i_zone.ymax

                    liste_cle_des_zonez_a_supprimer.append(cle_suinvante)
            



                valeur_z.liste_coordonnees.clear()

                p=point(xmin,ymin)
                valeur_z.liste_coordonnees.append(p)
                p=point(xmin,ymax)
                valeur_z.liste_coordonnees.append(p)
                p=point(xmax,ymax)
                valeur_z.liste_coordonnees.append(p)
                p=point(xmax,ymin)
                valeur_z.liste_coordonnees.append(p)
                p=point(xmin,ymin)
                valeur_z.liste_coordonnees.append(p)


                valeur_z.i_zone=info_zone(valeur_z.liste_coordonnees)


                valeur_z.liste_fusion=[]

            valeur_z.cle_sel=False


        #suppression des cle fusionne

        for cle in liste_cle_des_zonez_a_supprimer:
            del self.dict_zone[cle]


        #affecter en logique les sorties par rapport au dessin
            
        id_s=0

        while( id_s<len(self.liste_sorties)):  # Trouver et reperer les différentes sorties sur les dalles
            
            liste_zone_sortie=[]
            X1_S=self.liste_sorties[id_s].point_s1.X
            Y1_S=self.liste_sorties[id_s].point_s1.Y
            X2_S=self.liste_sorties[id_s].point_s2.X
            Y2_S=self.liste_sorties[id_s].point_s2.Y

            X1_S,X2_S=ordonne_donnees(X1_S,X2_S)
            Y1_S,Y2_S=ordonne_donnees(Y1_S,Y2_S)

            # reduction segment pour eviter contact_bord

            if (X1_S==X2_S):
                Y1_S=Y1_S+1
                Y2_S=Y2_S-1

            if (Y1_S==Y2_S):
                X1_S=X1_S+1
                X2_S=X2_S-1

            if (id_s==3):
                id_s=id_s

            for  id_zone,v_zone in self.dict_zone.items():

                id_c=0
                sortie_trouve=False

                while ((id_c<len(v_zone.liste_coordonnees)-1) and sortie_trouve==False):

                    X1=v_zone.liste_coordonnees[id_c].X
                    Y1=v_zone.liste_coordonnees[id_c].Y
                    X2=v_zone.liste_coordonnees[id_c+1].X
                    Y2=v_zone.liste_coordonnees[id_c+1].Y
                    X1,X2=ordonne_donnees(X1,X2)
                    Y1,Y2=ordonne_donnees(Y1,Y2)

                    if (X1_S==X2_S and X1==X2 and X1_S==X1):
                        
                        if (Y2>=Y1_S and Y2_S>=Y1):

                            liste_zone_sortie.append(id_zone)
                            sortie_trouve=True

                    if (Y1_S==Y2_S and Y1==Y2 and Y1_S==Y1):
                        
                        if (X2>=X1_S and X2_S>=X1):

                            liste_zone_sortie.append(id_zone)
                            sortie_trouve=True

                    id_c=id_c+1

            if (len(liste_zone_sortie)==2):


                self.liste_sorties[id_s].utilise=True

                if ((liste_zone_sortie[1] in self.dict_zone[liste_zone_sortie[0]].liste_zone_sortie)==False):
                    self.dict_zone[liste_zone_sortie[0]].liste_zone_sortie.append(liste_zone_sortie[1])
                
                if ((liste_zone_sortie[0] in self.dict_zone[liste_zone_sortie[1]].liste_zone_sortie)==False):
                    self.dict_zone[liste_zone_sortie[1]].liste_zone_sortie.append(liste_zone_sortie[0])

                

            else :
                if (len(liste_zone_sortie)>2):
                    liste_zone_sortie.append(liste_zone_sortie)
                    #sortie_trouve=True
                    self.dict_zone[liste_zone_sortie[2]].liste_zone_sortie.append(liste_zone_sortie[1])
                    self.dict_zone[liste_zone_sortie[1]].liste_zone_sortie.append(liste_zone_sortie[2])
                    # fonction a ecrire
                    id_s=id_s

            id_s=id_s+1

        for v_s in self.liste_sorties:

            if (v_s.utilise==False):
                v_s.utilise=False


        # rercherche segment commun pour chaque porte et direction de sortie

        #1-Faire correspondre Zone_1 et Zone_2 aux zones disponibles dans dict_zone
        #2-Récupérer liste_coordonnées des 2 zones
        #3- Appliquer la formule magique d'Eric (celle du tableau)
            
                Zone_1 = '7BZ6' in  self.dict_zone
                Zone_2 = '7BZ4E' in self.dict_zone

                print(Zone_1)
        #Plusieurs problèmes majeurs:
        # 1-La correspondance entre les colonnes de la bdd et les valeurs ne fonctionnent pas, pour le programme, Zone_1=ouvert  et si l'on
        # met les vrais valeurs, on tombe sur un out of range des familles
        # 2- La connexion au serveur déconne dès lors que je souhaite accéder à ma base zombicide,chez Guillaume, pas de problème O_o?
        # 3- J'ai d'énormes difficultés à faire communiquer les différents éléments du code (variable,fonction,classe,objet,attributs) et je
        #trouve qu'un cours de communication entre les différents moyen d'appeler tel ou tel élément ne serait pas de refus
        

       
            

            

            

#            if (Ouvert=="False"):
                 #C'est à peu près à ça que va ressembler le code au final mais avec les vrais valeurs :D
#                if(zone_1.xmax==zone_2.xmax or zone_2.xmax==Zone_1.xmin):
#                    cote_ok=True
#                if (zone_1.ymax==zone_2.ymin or zone_2==zone1.ymin):
#                    cote_ok=True

#                liste_zone_sortie.append() #Ajoute la sortie à la liste sortie (ceci permettra de faire apparaître la sortie à notre plateau de jeu)
#                liste_porte.append() #Ajoute la sortie à la liste porte (ceci permettra de dessiner la porte)       

                #On fera le dessinage du porte dans Zombicide

#                if (cote_ok==False):
#                    print ("Zones non associable !")   

#                if (Ouvert=="True"):

          

             
             

                 #Comparaison zone_1/zone_2 (est_ce qu'il se touche ?)
                 #Si oui, lancez la procédure
                 #Procédure:
                 #Ajouter une sortie à la liste zone sortie
                 # calculer la longueur du côté qui se touche et le diviser par 2
                 # faire le dessin de la porte à partir de cette valeur
        

    def recherche_suivante(self,cle_test):

        for cle_z,valeur_z in self.dict_zone.items():


            
            if (valeur_z.interieur!="1" and valeur_z.cle_sel==False and cle_test[0:2]!=cle_z[0:2]):

                fusion_ok=False

                z1=self.dict_zone[cle_test]
                
                z2= valeur_z

                if (z1.i_zone.xmin==z2.i_zone.xmin):
                    if (z1.i_zone.ymax==z2.i_zone.ymin):
                        fusion_ok=True
                    if (z2.i_zone.ymax==z1.i_zone.ymin):
                        fusion_ok=True
                    
                if (z1.i_zone.ymin==z2.i_zone.ymin):
                    if (z1.i_zone.xmin==z2.i_zone.xmax):
                        fusion_ok=True
                    if (z2.i_zone.xmin==z1.i_zone.xmax):
                        fusion_ok=True
                    
                if (fusion_ok):
                    return cle_z

                    

        return ""

def pas_passe_par_la(cle_a_ajoute,list_chemin_en_cours=[""]):

    id_l=0
    while (id_l<len(list_chemin_en_cours)):
        if (cle_a_ajoute==list_chemin_en_cours[id_l]):
            return False
        id_l=id_l+1
    
    return True

def recherche_chemin(cle_d="",cle_a="",d_z={"":zone()},liste_chemin=[],liste_finale=[]):

    
    id_s=0

    while (id_s<len(d_z[cle_d].liste_zone_sortie)):

        cle_s = d_z[cle_d].liste_zone_sortie[id_s]

        if (pas_passe_par_la(cle_s,liste_chemin)==True):
            
            liste_suite=list(liste_chemin)
            liste_suite.append(cle_s)
            
            if (cle_s!=cle_a):
#                print (cle_s)
                
                recherche_chemin(cle_s,cle_a,d_z,liste_suite,liste_finale)
            else:
                liste_finale.append(liste_suite)
                min(liste_finale)

  

 

        id_s=id_s+1

#recherche_chemin()  
#    def porte(liste_suite):
#        x=0
#        y=0
#        x1=0
#        y2=0
#        porte=x,y,x1,y2,ouvert=False
#        if (porte in zone != "interieur"):
#            print("ajouter une porte au milieu d'une rue ne fera pas office de bouclier")
#            porte()    


                


#    def chemin_le_plus_court():
#        for element in liste_finale:
#            if (element < element+1):
#                return element as cheminlepluscourt
#                break
  
#    chemin_le_plus_court()    




curseur= lance_connection()

plateau_jeux = plateau(curseur)

class armes:
    def __init__(self,id_arme,nom_arme,cac_dist,nb_des,touche,degats,silence,ouverture_porte,ouverture_silencieuse,nb_en_jeu,special,is_arme=True):
        self.id_arme=id_arme
        self.nom_arme=nom_arme
        self.cac_dist=cac_dist
        self.nb_des=nb_des
        self.touche=touche
        self.degats=degats
        self.silence=silence
        self.ouverture_porte=ouverture_porte
        self.ouverture_silencieuse=ouverture_silencieuse
        self.nb_en_jeu=nb_en_jeu
        self.special=special
        self.is_arme=is_arme

        curseur.execute('select "id_arme","nom_arme","cac_dist","nb_des","touche","degats","silence","ouverture_porte","ouverture_silencieuse","nb_en_jeu","special","is_arme"  from "Pioche"')

        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

        for ligne in lignes: # correspondance entre les lignes de la table et les variables
            id_arme=ligne[0]
            nom_arme=ligne[1]
            cac_dist=ligne[2] 
            nb_des=ligne[3]
            touche=ligne[4]
            degats=ligne[5]
            silence=ligne[6]
            ouverture_porte=ligne[7]
            ouverture_silencieuse=ligne[8]
            nb_en_jeu=ligne[9]
            special=ligne[10]
            is_arme=ligne[11]



class objet:
    def __init__(self,id_arme,nom_arme,nb_en_jeu,special,is_arme=False):
        self.id_arme=id_arme
        self.nom_arme=nom_arme
        self.nb_en_jeu=nb_en_jeu
        self.special=special
        self.is_arme=is_arme

        curseur.execute('select "id_arme","nom_arme","nb_en_jeu","special","is_arme" from "Pioche"')

        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

        for ligne in lignes: # correspondance entre les lignes de la table et les variables
            id_arme=ligne[0]
            nom_arme=ligne[1]
            nb_en_jeu=ligne[9]
            special=ligne[10]
            is_arme=is_arme[11]

class invasion:
    def __init__(self,id_carte,attaque_bleue,attaque_jaune,attaque_orange,attaque_rouge,egouts):
        self.id_carte=id_carte
        self.attaque_bleue=attaque_bleue
        self.attaque_jaune=attaque_jaune
        self.attaque_orange=attaque_orange
        self.attaque_rouge=attaque_rouge
        self.egouts=egouts

        curseur.execute('select "id_carte","attaque_bleue","attaque_jaune","attaque_orange","attaque_rouge","egouts" from "zombies"')

        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

        for ligne in lignes: # correspondance entre les lignes de la table et les variables
            id_carte=ligne[0]
            attaque_bleue=ligne[1]
            attaque_jaune=ligne[2]
            attaque_orange=ligne[3]
            attaque_rouge=ligne[4]
            egouts=ligne[5]


class personnage:
    def __init__(self,ID_Personnage,Nom,Skill_bleu=1,Skill_jaune=0,Skill_rouge=0,XP=0,Action=3,Carte_en_main=0,Carte_en_reserve=0,Blessure=0,Position=0):
        self.ID_Personnage=ID_Personnage
        self.Nom=Nom 
        self.Skill_bleu=Skill_bleu
        self.Skill_jaune=Skill_jaune
        self.Skill_rouge=Skill_rouge
        self.XP=XP
        self.Action=Action
        self.Carte_en_main=Carte_en_main
        self.Carte_en_reserve=Carte_en_reserve
        self.Blessure=Blessure
        self.Position=Position

        curseur.execute('select "ID_Personnage","Nom","Skill_bleu","Skill_jaune","Skill_orange",Skill_rouge","XP","Action","Carte_en_main","Carte_en_reserve","Blessure","Position" from "Personnage"')

        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

        for ligne in lignes: # correspondance entre les lignes de la table et les variables
            ID_Personnage=ligne[0]
            Nom=ligne[1]
            Skill_bleu=ligne[2]
            Skill_jaune=ligne[3]
            Skill_orange=ligne[4]
            Skill_rouge=ligne[5]
            XP=ligne[6]
            Action=ligne[7]
            Carte_en_main=ligne[8]
            Carte_en_reserve=ligne[9]
            Blessure=ligne[10]
            Position=ligne[11]


    
#def lancer_Des(nbDes=0):   #la liste des dés, pour l'instant  vide
#    resultat=r.choice([1,2,3,4,5,6])
#    nbDes * resultat
#    print (resultat)

def lancer_des():
    from random import sample
    nb_des = 10
    nb_faces = 6
    tirage = sample(list(range(1,nb_faces+1))*nb_des,nb_des)
    print(tirage)



#lancer_des()


#def armes():

#        curseur.execute('select "id_arme","nom_arme","cac_dist","nb_des","touche","degats","silence","ouverture_porte","ouverture_silencieuse","nb_en_jeu","special"  from "armes"')

#        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

#        for ligne in lignes: # correspondance entre les lignes de la table et les variables
#                id_arme=ligne[0]
#                nom_arme=ligne[1]
#                cac_dist=ligne[2] 
#                nb_des=ligne[3]
#                touche=ligne[4]
#                degats=ligne[5]
#                silence=ligne[6]
#                ouverture_porte=ligne[7]
#                ouverture_silencieuse=ligne[8]
#                nb_en_jeu=ligne[9]
#                special=ligne[10]
#                is_arme=ligne[11]


#                for values in [nb_en_jeu]: #Permet d'établir la liste complète des cartes à partir du nombre d'occurence des cartes
#                    liste_complete=values * [ligne] 


#                y=list(liste_complete)
#                for values in [y]:
#                    print (reversed(y))
#                print ([liste_complete])
#                print (choice(ligne in [lignes]))
#                print (liste_complete)
#                resultat= r.shuffle(liste_complete)
#                print(resultat)
#                print (lignes)
#                for valeurs in [liste_complete]:
#                    random.choice(valeurs)
           
#armes()            
#self,id_arme,nom_arme,cac_dist,nb_des,touche,degats,silence,ouverture_porte,ouverture_silencieuse,nb_en_jeu,special

#class personnage:
#    def __init__(self,ID_Personnage,Nom,Skill_bleu=1,Skill_jaune="+1action",Skill_rouge=0,XP=0,Action=3,Carte_en_main=0,Carte_en_reserve=0,Blessure=0,Position):
#        self.ID_Personnage=ID_Personnage
#        self.Nom=Nom 
#        self.Skill_bleu=Skill_bleu
#        self.Skill_jaune=Skill_jaune
#        self.Skill_rouge=Skill_rouge
#        self.XP=XP
#        self.Action=Action
#        self.Carte_en_main=Carte_en_main
#        self.Carte_en_reserve=Carte_en_reserve
#        self.Blessure=Blessure
#        self.Position=Position

#        curseur.execute('select "ID_Personnage","Nom","Skill_bleu","Skill_jaune","Skill_orange",Skill_rouge","XP","Action","Carte_en_main","Carte_en_reserve","Blessure","Position" from "Personnage"')

#        lignes = curseur.fetchall() # fetchall retourne un tableau contenant toutes les lignes

#        for ligne in lignes: # correspondance entre les lignes de la table et les variables
#            ID_Personnage=ligne[0]
#            Nom=ligne[1]
#            Skill_bleu=ligne[2]
#            Skill_jaune=ligne[3]
#            Skill_orange=ligne[4]
#            Skill_rouge=ligne[5]
#            XP=ligne[6]
#            Action=ligne[7]
#            Carte_en_main=ligne[8]
#            Carte_en_reserve=ligne[9]
#            Blessure=ligne[10]
#            Position=ligne[11]


#def Save_state():
#    question = input("Voulez-vous sauvegarder en l'état ?\n--> ").upper()
#    if question == "O" or question == "Oui":
#        Save = Joueur(Personnage.nom) 
#        pickle.dump(Save, open("Save File", "wb")) #Créer le fichier et met les données dedans
#    elif question == "N" or question == "Non":
#        print("Courez, pauvres fous!")
#        return
#    else:
#        print("Y'a une couille dans l'pôté, veuillez réessayer")
#        Save_state()            

#Save_state()

#def load():
#    me = pickle.load(open("Save File","rb"))
#    me.display(Personnage.display)
    #return Zombicide()
