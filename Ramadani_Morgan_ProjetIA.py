from __future__ import print_function
from copy import deepcopy
import math
from random import randint
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import numpy as np
import time



class Etat : # c'est la classe qui décrit nos différents états pour la recherche informée
    def __init__(self, visited=[], tovisit=[], startingcity = '', currentcity='', costs=[], cost=0, value = (-1), cities=[], hist = []):
        self.visited = visited #les villes deja visitees 
        self.tovisit = tovisit # les villes a visiter
        self.startingcity = startingcity # ville de départ qui devra etre la ville d'arrivee
        self.currentcity = currentcity # la ville ou on en est
        self.costs = costs # une liste de liste [[a,b,3], [a,c,5], etc...]
        self.cost = cost # le coût de ce chemin à l'étape currentcity servira de g
        self.value = value # resultat de f = h + g
        self.cities = cities # l'ensemble des villes
        self.hist = hist # historique des chemins empreintés
        
    def addpath(self, path): #path de la forme ['Paris','Lyon',45] et l'ajoute à self
        nouv = deepcopy(self)
        nouv.hist.append([path[0], path[1]]) # on met à jour l'historique de chaque etat
        if (path[0] in nouv.visited):
            nouv.currentcity = path[1]
        else:
            nouv.currentcity = path[0]
        nouv.visited.append(path[0])
        nouv.visited.append(path[1])
        nouv.visited = list(set(nouv.visited))
        nouv.cost+= path[2]
        if (path[0] in nouv.tovisit ) : nouv.tovisit.remove(path[0]) # ce qui est visité n'est plus à visiter
        if (path[1] in nouv.tovisit ) :nouv.tovisit.remove(path[1])
        return nouv 

    def heuristic(self): # sera notre heuristic via calcul du minspantree
        nouv = deepcopy(self)
        cop = nouv.getcosts()
        vis = nouv.getvisited()
        edg = []
        cos = nouv.getcost() # totalcost
        index = 0
        frontier = []
        if len(vis)==0: # to get started
            for i in range(len(cop)):
                for j in range(len(cop)):
                    if (cop[i][2]<=cop[j][2]) and (cop[index][2]>cop[i][2]):
                        index = i    
            cos+=cop[index][2] # le cout total
            edg.append(cop[index])
            vis.extend((cop[index][0],cop[index][1])) # on met les villes visited dans vis
        if len(vis) != 0:
            for k in range(len(nouv.getcities())-len(vis)):
                index = 0
                for i in range(len(cop)):
                    if not((cop[i][0] in vis) and (cop[i][1] in vis)) and not((cop[i][0] not in vis) and (cop[i][1] not in vis)):
                        if (k == 0): #la frontier pour le premier coup
                            frontier.append(cop[i]) # les edges encore candidats
                        for j in range(len(cop)):
                            if not((cop[j][0] in vis) and (cop[j][1] in vis)) and not((cop[j][0] not in vis) and (cop[j][1] not in vis)): # ici on a l'ensemble frontière
                                if (cop[i][2]<=cop[j][2]) and (cop[index][2]>cop[i][2]):
                                    index = i
                vis.extend((cop[index][0],cop[index][1]))
                vis = list(set(vis)) #pour supprimer les doublons
                cos+=cop[index][2]
                edg.append(cop[index])
                nouv.currentcity = edg[-1][1]
                nouv.visited = vis
                nouv.tovisit = list(set(nouv.tovisit)- set(nouv.visited))
                new_f = []
                for elem in frontier:
                    if elem not in new_f:
                        new_f.append(elem)
                frontier = new_f # il y a toutes les frontières ici mais on peut voir à les avoir pour une certaine étape ou faire une liste de liste
        return (cos - nouv.getcost())

    def openfront(self): # donne les etapes suivantes possibles
        op = []
        vis = self.getvisited()
        cop = self.costs.copy()
        for i in range(len(cop)):
            if ((cop[i][0] == self.getcurrentcity()) and (cop[i][1] not in vis)) or ((cop[i][1] == self.getcurrentcity()) and (cop[i][0] not in vis)): #on veut que les coups suivants partent de la dernière ville visitée
                op.append(cop[i]) # les edges encore candidats
        return op

    def addvisited(self, city): # serves to add a city to the visited ones
        try:
            assert(city in self.tovisit)
            self.visited.append(city)
        except:
            print("Cette ville n'est pas dans la liste des villes encore disponibles \n Essayer la fonction ShowUnvisitedCities")

    def getvisited(self):
        return self.visited

    def getcosts(self):
        return self.costs

    def getcost(self):
        return self.cost

    def getcurrentcity(self):
        return self.currentcity

    def getstartingcity(self):
        return self.startingcity

    def getcities(self):
        return self.cities
    
    def gethist(self):
        return self.hist

    def show_unvisited_cities(self):
        print(f"There are the cities left to visit {self.tovisit}")

    def prettyprint(self):
        print('Villes déjà visitées :' + str(self.visited))
        print('Villes à visiter :' + str(self.tovisit))
        print('Ville de départ :' + self.startingcity)
        print('Villeactuelle :' + self.currentcity)
        print('Données :' + str(self.costs))
        print('Coût à cette étape :' + str(self.cost))
        print('valeur de f = h + g :' + str(self.value))
        print('Toutes les villes :' + str(self.cities))
        print('Historique des chemins empreintés :' + str(self.hist))
        
    def setvalue(self):
        self.value = self.cost + self.heuristic()
    
    def getvalue(self):
        return self.value


def astar(etat):
    cop = deepcopy(etat)
    cop.setvalue()
    op = [cop] #la frontière, à voire comment représenter ça, ce sera une liste d'états, à ranger dans l'ordre croissant de f = g + h ou alors avoir une fonction qui nous donne le min
    maxop = op.copy()
    closed = [] # c'est les états validés et ce sera le resultat final je pense
    closed.append(op.pop()) # initialisation
    toadd = closed[-1].openfront() # on récupère les étapes suivantes possibles
    for i in toadd:
        temp = deepcopy(closed[-1]) # et on crée les etats correspondants
        tempi = temp.addpath(i)
        tempi.setvalue()
        op.append(tempi) # on continue de peupler op
    while (len(closed[-1].getvisited()) != len(etat.getcities())): # tant qu'on a pas visité toutes les villes
        indice = 0
        indsuppr = 0
        first = math.inf
        for i in op: # on va prendre dans indice l'indice de ce qui nous intéresse dans op sans oublier de le suppr de op
            indice+=1
            val = i.getvalue()
            if (val)< first:
                first = val
                indsuppr = indice
        closed.append(op.pop(indsuppr-1)) #on déplace ce qui nous interesse de op vers closed sans oublier de le suppr de op
        toadd = closed[-1].openfront() # on récupère les étapes suivantes possibles
        for i in toadd:
            temp = deepcopy(closed[-1]) # et on crée les etats correspondants
            tempi = temp.addpath(i)
            tempi.setvalue()
            op.append(tempi) # on continue de peupler op
            if len(op) > len(maxop):
                maxop = op
    chemin = closed[-1].gethist()
    print('La taille max de l\'ensemble frontière est de', len(maxop))
    last = chemin[-1][0] # dernière ville visitée
    if chemin[-1][0] in chemin[-2]:
        last = chemin[-1][1]
    recherche = closed[-1].getcosts() # le graph
    derniercout = 0
    for i in recherche:
        if (i[0] == closed[-1].getstartingcity()) and (i[1] == last):
            derniercout = i[2]
    der = closed[-1].addpath([closed[-1].getstartingcity(),last, derniercout])
    print('Le cout finalement trouvé est de ', der.getcost())
    chemin = der.gethist()
    print('Le chemin optimal trouvé est : ', chemin)
    return chemin

def make(nb):
    villeFrance = ['Paris','Marseille','Lyon','Nantes','Rennes','Toulouse','Bordeaux','Lille','Fontainebleau','Saint-Malo','Verdun','Nice','Strasbourg',
                    'Montpellier','Aix-en-Provence','Angers','Dijon','Grenoble','Annecy','Avignon','Nîmes','Le Havre','Toulon','Brest','Tours',
                    'Clermont-Ferrand','Rouen','Limoges','Caen','Le Mans','Nancy','Amiens','Metz','Perpignan','Orléans','Besancon','Vichy','Mulhouse','Tourcoing',
                    'Poitiers','Saint-Denis','Roubaix','Montreuil','Sevran','Nanterre','Cannes','La Rochelle', 'Biarritz','Cabourg','Deauville']
    graph = []
    avisiter = []
    depart = villeFrance[0]
    for i in range(nb):
        avisiter.append(villeFrance[i])
        for j in range (i+1, nb):
            graph.append([villeFrance[i],villeFrance[j], randint(1, 100)])#On dit arbitrairement que la distance est comprise entre 1 et 100
    ori = Etat([depart],avisiter, depart,depart, graph, 0, 0, avisiter, [])
    return astar(ori)


########## On passe à l'autre algo

#On va prendre pour solution initiale le chemin 0-1-2-3-4-5-

class Local:

    def __init__(self, circuit=[], cost = 0, costs=[]):
        self.circuit = circuit #le chemin qu'on prend
        self.cost = cost #le cout courant
        self.costs = costs # la matrice avec tous les couts

    def getcircuit(self):
        return self.circuit

    def getcost(self):
        return self.cost

    def setcost(self): # calcul le cout de l'instance de Local à partir de la matrice de cout et de la liste des villes traversées
        newcost = 0
        mat = self.getcosts()
        cir = self.getcircuit()
        taille = len(self.getcircuit())
        for i in range(taille-1):
            newcost+= mat[cir[i]][cir[i+1]]
        self.cost = newcost
        
    def getcosts(self):
        return self.costs

    def hillclimb(self):
        res = deuxopt(self.getcircuit(), self.getcosts())
        self.circuit = res
        self.setcost()
        return self.circuit

def deuxopt(route, matgraph):
    result = route
    continuer = True
    taille = len(route)
    while continuer:
        continuer = False
        for i in range(1, taille - 2): #On test tous les voisins dans ces deux boucles on démarre à un car on ne change pas le point de départ
            for j in range(i + 1, taille):
                if (j != (i+1)):# on ignore le cas où i et j sont consécutifs
                    if (matgraph[result[i - 1]][result[i]] + matgraph[result[j - 1]][result[j]]) - (matgraph[result[i - 1]][result[j - 1]] + matgraph[result[i]][result[j]]) > 0: #si on a un cout testé plus intéressant, ce sera notre condition d'arret
                        result[i:j] = result[j - 1:i - 1:-1] #on doit modifier le sens de parcours entre les deux arcs qu'on a modifié
                        continuer = True # si c'est à False c'est qu'on a rien pu modifier pour améliorer l'algo, on est donc dans un creux de notre hill, un minimum local quoi 
    return result

def AlgoHill(loc):
    loc.setcost()
    chInit = deepcopy(loc).getcircuit()
    v1 = loc.getcost()
    loc.hillclimb()
    chFinal = loc.getcircuit()
    v2 = loc.getcost()
    var = round(((v2-v1)/v1)*100,2) # on arrondit le pourcentage pour la lisibilité
    print('La variation a été de', var, '%', 'Avec un coût initial de', v1, 'et un coût finale de', v2)
    print('le chemin initial était :', chInit)
    print('Le chemin final est :', chFinal)
    return var


def aff(nb):
    first = list(range(nb))
    matgraph = np.random.randint(100, size=(nb, nb))
    matgraph[range(len(matgraph)), range(len(matgraph))] = 0 # on met des 0 sur la diag 
    matgraph = matgraph + matgraph.T # on additionne la matrice et sa transposée pour avoir une matrice symétrique  
    test = Local(first,0, matgraph) # on crée notre instance
    return AlgoHill(test)

def presentation():
    print('Bonjour, vous allez pouvoir tester un projet qui tente de résoudre le problème du voyagerur de commerce!')
    cont = True
    while (cont == True):
        a = input('Entrez 0 pour tester A* et 1 pour tester Hill Climbing : ')
        print(a)
        a = int(a)
        if a == 0 :
            b = 0
            while (b<3 or b>10):
                b = input('Veuillez entrer le nombre de villes que vous voulez tester, \n le graph sera ensuite généré de façon automatique avec des valeurs aléatoires, \n le nombre de villes doit être inférieur ou égale à 10 et supérieur ou égal à 3 : ')
                b = int(b)
                if (b<3 or b>10):
                    print('La valeur entrée n\'est pas valide, veuillez recommencer')
                else :
                    start_time = time.time()
                    make(b)
                    print("Execution en %s secondes " % (time.time() - start_time))
        elif a == 1:
            c = 0
            while (c<3 or c>2000):
                c = input('Veuillez entrer le nombre de villes que vous voulez tester, \n le graph sera ensuite généré de façon automatique avec des valeurs aléatoires, \n le nombre de villes doit être inférieur ou égale à 2000 et supérieur ou égal à 3 : ')
                c = int(c)
                if (c<3 or c>2000):
                    print('La valeur entrée n\'est pas valide, veuillez recommencer')
                else : 
                    start_time = time.time()
                    aff(c)
                    print("Execution en %s secondes " % (time.time() - start_time))
        val = input('Pour continuer tapez 0, pour quitter tapez 1 :')
        val = int(val)
        if val == 1 :
            cont = False
            


presentation()


'''# code utilisé pour calculer le temps d'execution moyen de A*
tpsmoyen = 0
n = 5 #paramètre
m = 10 # nombre d'itérations
for i in range(m):
    start = time.time()
    make(n)
    tpsmoyen+= (time.time() - start)
    
tpsmoyen = tpsmoyen/m
print('Le temps moyen pour', n, 'villes : ' ,tpsmoyen) 
'''

'''# code pour caclculer le taux d'amélioration dans A*
z = 5 # nb d'itérations
y = 11 # nombre de villes
tot = 0
for k in range(z):
    fin = taux(y)
    fin2 = astar2(fin)  #etat après astar
    c = fin.getcosts()
    nbvilles = len(fin.getcities())
    i=1
    j=0
    while j<len(c):
        fin = fin.addpath(c[j])
        j = j+(nbvilles-i)
        i+=1
    tot = tot + round(((fin2.getcost() - fin.getcost())/fin.getcost())*100, 2)
print('Taux d\'amelioration moyen pour',y,'villes avec astar:', (tot/z)
'''

'''
# calcul du taux d'amélioration moyen pour le Hillclimb
def AlgoHill2(loc):
    loc.setcost()
    chInit = deepcopy(loc).getcircuit()
    v1 = loc.getcost()
    loc.hillclimb()
    chFinal = loc.getcircuit()
    v2 = loc.getcost()
    var = round(((v2-v1)/v1)*100,2) # on arrondit le pourcentage pour la lisibilité
    return var


def aff2(nb):
    first = list(range(nb))
    matgraph = np.random.randint(100, size=(nb, nb))
    matgraph[range(len(matgraph)), range(len(matgraph))] = 0 # on met des 0 sur la diag 
    matgraph = matgraph + matgraph.T # on additionne la matrice et sa transposée pour avoir une matrice symétrique
    test = Local(first,0, matgraph) # on crée notre instance
    return(AlgoHill2(test))



z = 500 # nb d'itérations
y = 11 # nombre de villes
tot = 0
for k in range(z):
    aff2(y)
    tot = tot + aff2(y)
print('Taux d\'amelioration moyen pour',y,'villes avec HillClimbing:', round(tot/z,3))


'''
