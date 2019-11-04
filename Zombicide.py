import os
from tkinter import *   # Librairie permettant de dessiner

from classe_dalle import *
#Connexion permettant de lier notre programme python à la base de donnée située dans Postgre


#----------------
#Catégorie Zoom#
#----------------


def zoom_X(X,L_F,X_V,NB_DH):

    global largeur_dalle


 
    la_avant=largeur_dalle*(NB_DH-X_V)

    return (X-X_V*largeur_dalle)*L_F/(la_avant)


def zoom_Y(Y,H_F,Y_V,NB_DV):

    global largeur_dalle


 
    ht_avant=largeur_dalle*(NB_DV-Y_V)

    return (Y-Y_V*largeur_dalle)*H_F/(ht_avant)


#----------------
#Catégorie Dessin
#----------------


def dessine_polygones_sortie(liste_sorties=[sorties()],canvas=None,largeur_fenetre=0,hauteur_fenetre=0,X_V=0,Y_V=0,nb_dalle_h=0,nb_dalle_v=0): 

    id_s=0


    while (id_s<len(liste_sorties)):
    
        if (liste_sorties[id_s].utilise==True):


            

            list_point=[]

            p1=liste_sorties[id_s].point_s1
            p2=liste_sorties[id_s].point_s2

            list_point.append(zoom_X(p1.X,largeur_fenetre,X_V,nb_dalle_h))
            list_point.append(zoom_Y(p1.Y,hauteur_fenetre,Y_V,nb_dalle_v))

            list_point.append(zoom_X(p2.X,largeur_fenetre,X_V,nb_dalle_h))
            list_point.append(zoom_Y(p2.Y,hauteur_fenetre,Y_V,nb_dalle_v))

                
            canvas.create_polygon(list_point, outline='white',fill='white', width=4)

        id_s=id_s+1



def dessine_polygones_zone(dict_zone,canvas,largeur_fenetre,hauteur_fenetre,X_V,Y_V,nb_dalle_h,nb_dalle_v):


    for zone_v in dict_zone.values(): # pour chaque valeur contenu dans le dictionnaire, remplir zone_v
    
        list_point=[]


        xmin=1000000
        ymin=1000000
        xmax=-1000000
        ymax=-1000000

        for coo in zone_v.liste_coordonnees:
            
  
            x_apres=zoom_X(coo.X,largeur_fenetre,X_V,nb_dalle_h)
            y_apres=zoom_Y(coo.Y,hauteur_fenetre,Y_V,nb_dalle_v)

            if (xmin>x_apres):
                xmin=x_apres

            if (ymin>y_apres):
                ymin=y_apres

            if (xmax<x_apres):
                xmax=x_apres

            if (ymax<y_apres):
                ymax=y_apres

            list_point.append(x_apres)
            list_point.append(y_apres)

         

            if (zone_v.interieur=='1'):                   
                canvas.create_polygon(list_point, outline='blue',fill='red', width=1)
  


            else:
                if (len(zone_v.liste_dalle_egout)==0):
                    canvas.create_polygon(list_point, outline='blue',fill='gray', width=1)
                else:
                    canvas.create_polygon(list_point, outline='blue',fill='black', width=1)


    for zone_v in dict_zone.values(): # pour chaque valeur contenu dans le dictionnaire, remplir zone_v
    
        list_point=[]


        xmin=1000000
        ymin=1000000
        xmax=-1000000
        ymax=-1000000

        for coo in zone_v.liste_coordonnees:
            
  
            x_apres=zoom_X(coo.X,largeur_fenetre,X_V,nb_dalle_h)
            y_apres=zoom_Y(coo.Y,hauteur_fenetre,Y_V,nb_dalle_v)

            if (xmin>x_apres):
                xmin=x_apres

            if (ymin>y_apres):
                ymin=y_apres

            if (xmax<x_apres):
                xmax=x_apres

            if (ymax<y_apres):
                ymax=y_apres

            list_point.append(x_apres)
            list_point.append(y_apres)

            #if (zone_v.id_zone=="5BZ2E"):
            #    canvas.create_polygon(list_point, outline='blue',fill='yellow', width=1)




            

        

      
        canvas.create_text((xmax+xmin)/2,(ymax+ymin)/2,fill='white',text=zone_v.id_zone)
        



def print_polygones_zone(dict_zone):


        for cle,zone_v in dict_zone.items():  #  Parcoure les valeurs de dict_zone et zone_v = une zone de dict_zone

            if (zone_v.interieur=='1'):
                print (cle)                             #C'est ici que je décide du contenu que je vais mettre dans zone_v


#        canvas.create_polygon(self.position_x,self.position_y,self.position_x1,self.position_y2,outline='blue',fill='gray', width=1)
                
#porte1=porte(5,5,5,5,FALSE)                



curseur=lance_connection()
plateau_jeux=plateau(curseur)


#print_polygones_zone(plateau_jeux.dict_zone)



#class point_zone:
#    def __init__(self,x,y,h,l)
#    self.x=x
#    self.y=y
#    self.h=h
#    self.l=l


#On cree une fenetre et un canvas:
tk = Tk()
largeur_fenetre = 1600

hauteur_fenetre=900


largeur_fenetre = tk.winfo_screenwidth()

hauteur_fenetre=tk.winfo_screenheight()


list_chemin=["1BZ8"]
liste_finale=[]

recherche_chemin("1BZ8","4CZ4",plateau_jeux.dict_zone,list_chemin,liste_finale)



canvas =  Canvas(tk,width = largeur_fenetre, height = hauteur_fenetre , bd=0, bg="white")
#canvas.pack(padx=0,pady=0)
canvas.pack(fill='both')
tk.attributes('-fullscreen',True )
#tk.geometry("{0}x{1}+0+0".format(tk.winfo_screenwidth(), tk.winfo_screenheight()))

#Creation  d'un bouton "Quitter":
#Bouton_Quitter=Button(tk, text ='Quitter', command = tk.destroy)
#On ajoute l'affichage du bouton dans la fenêtre tk:
#Bouton_Quitter.pack()

#print (len(plateau_jeux.liste_zone))

#def dessine_polygones_porte(canvas=None,largeur_fenetre=5,hauteur_fenetre=5,X_V=0,Y_V=0,nb_dalle_h=0,nb_dalle_v=0):
     



X_V=0

Y_V=0

dessine_polygones_zone(plateau_jeux.dict_zone,canvas,largeur_fenetre,hauteur_fenetre,X_V,Y_V,plateau_jeux.nb_dalle_h,plateau_jeux.nb_dalle_v)

dessine_polygones_sortie(plateau_jeux.liste_sorties,canvas,largeur_fenetre,hauteur_fenetre,X_V,Y_V,plateau_jeux.nb_dalle_h,plateau_jeux.nb_dalle_v)

#dessine_polygones_porte(plateau_jeux.dict_zone,canvas,largeur_fenetre,hauteur_fenetre,X_V,Y_V)

list_point_porte_complete=[6,4,7,9]
porte=TRUE

if (porte==TRUE):
    canvas.create_polygon(list_point_porte_complete,outline="yellow",fill='green',width=2)


#def dessin():
#        canvas.create_polygon(zone,outline='blue',fill='red', width=2)

#dessin()

tk.mainloop()

