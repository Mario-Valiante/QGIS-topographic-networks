
from PyQt4.QtCore import *
from PyQt4.QtGui import * #this is only for the message box !!
import numpy as np

class TopoGraph:


    # tu sve radnje!!!
    #assembly etc
    def __init__(self):
        self.nodes = {} #Fields : class_i, ID_tree_i, step_i, z
        self.edges = {} #Fields: slope_f
        self.relations={}
        self.entities={} 
        
        # where: _i = integer, _f = float

    def Assembly(self, DEM_array, radius=1, adaptable=False):
    # TODO numpy mowing window....

        raster_size_x = len(DEM_array[0])

        #distance matrix for slope calculation
        side= (np.arange(radius*2+1) - radius ) **2
        mx_dist = np.sqrt(side[:,None] + side[None,:])
        
        for j in xrange(radius, len(DEM_array)-radius):
            for i in xrange(radius, raster_size_x-radius):

                target = (i,j)
                z = DEM_array[j,i]
                temp=DEM_array[j-radius : j+ radius+1, i- radius : i+radius +1]

                if z == np.amax(temp): #skip, it's a peak!
                    self.nodes[target]={"class_i": 0, 'ID_tree_i':0}
                    continue 
                else: self.nodes[target]={"class_i": 1, 'ID_tree_i':0}
           
                if adaptable: #not implemented !!
                    delta_x= DEM_array[j,i-1] - DEM_array[j,i+1]
                    delta_y= DEM_array[j-1,i] - DEM_array[j+1,i]

                    temp += mx_x * delta_x + mx_y * delta_y

               #convert to slopes
                slope_mx = (temp-z) / mx_dist 
                slope_mx [radius,radius]=0 #division with zero, makes problems....
                jj, ii = np.unravel_index(slope_mx.argmax(), slope_mx.shape) 
                #we can only get the highest value of the entire array or of each sub-array
                #so we need to fing coordinates of the "flat" index in 2D array.. messy..

                source = (i + (ii-radius), j + (jj-radius)) #offset coordinate

                try:    self.relations[source].append(target)
                except: self.relations[source] = [target]
                
                self.edges[source, target]= {'slope_f': slope_mx[jj,ii]}

            #CANNOT : entities get erased on merge !!                    
                   # self.entities[j*raster_size_x + i]={'point' : target}
        #nije dobro: entities se popunjava nakon merge, ali ako nema merge !!??

# not working!!! cant delete on iteration
    def clean(dict_object): #remove nodes without ID: makes problems..
        if dict_object=='nodes':
            for key, sub_dict in n.items():
                if not 'ID_tree_i' in sub_dict: del n[key]
        elif dict_object=='edges':
            # DO!
            pass

    def merge_peaks(self, radius, DEM_array):

        entity_id=0

        raster_size_x = len(DEM_array[0])
        
        #cannot use Z values from nodes: no relations...
        for k in self.nodes:
            if self.nodes[k]['class_i']==0:
                x,y=k

                z = DEM_array[y,x]
                max_z = z
                source =0
                for j in xrange(y- radius, y+ radius + 1):
                    for i in xrange(x- radius, x+ radius +1):
                        if j<0 or i<0: continue   #Numpy can see negative indices !!!

                        try: z2= DEM_array[j,i]
                        except: continue # out of raster!
                            
                        if z2 > max_z:
                            max_z = z2    
                            source = (i, j)
                            
                if source:           
                    self.nodes[k]['class_i'] = 1 # has one source, NOT PEAK ANYMORE
                    self.edges[source,k]= {'slope_f': max_z - z}
                    try: self.relations[source].append(k) 
                    except: self.relations[source]=[k]
            #choose entities AFTER MERGE
                else :
                    #fomula for ids : 0 rests as unclassified
                    entity_id += 1
                    self.entities[entity_id]={'point' : k, 'saddles':[], 'nodes':[]}


    def BFS_traversal(self):# breadth first search

        
        for k in self.entities: 
                 
            id_root = k #given in merge_peaks routine
            key= self.entities[k]['point']
            

            self.nodes[key]["step_i"]=0
            self.nodes[key]["ID_tree_i"]= id_root
                 
            cnt1 = 1; cnt2 = 0; step=0
            # maintain a queue of paths
            queue = []
 #           parent= {} # to nicemu ne sluzi !!!!!!!!

            # push the first path into the queue
            queue.append(key)
            #except: continue #IMA VRHOVAZ KOJI NISU U GRAFU ???

            while queue:
                # get the first path from the queue
                node = queue.pop(0)
                # get the last node from the path
    ##            # path found  PATH FINDING
    ##            if node == end:
    ##                return path
                # ------ counting steps ----------------
                if cnt2 == 0:
                    step += 1
                    cnt2 = cnt1
                    cnt1 = 0
                
                cnt2 -= 1 # record popped node
                # --------------------------------------
                # enumerate all adjacent nodes, construct a new path and push it into the queue
                is_sink=True           
                for adjacent in self.relations.get(node, []):
                
                   # parent[adjacent]= node
                    queue.append(adjacent)
                    
        #            out_list.append ([[adjacent, node], id_root, step, node, adjacent])
                    cnt1 += 1
                    is_sink= False
                    
                    self.nodes[adjacent]["ID_tree_i"]= id_root
                    self.nodes[adjacent]["step_i"]= step
                    
                    self.edges[node,adjacent]["ID_tree_i"]=id_root
                    self.entities[id_root]['nodes'].append(adjacent)
                    
                if is_sink:
                    #register sinks - good to have
                    #NOT Working!!!
                    self.nodes[node]['class_i'] = -9
                    
       # QMessageBox.information(None, "podatak:", str(self.relations))
    
    # THIS CREATES A NEW GRAPH (and takes the full topographic network)
    #repeating most of the code from assembly : but on dict, not on an array!
    def SN_assembly (self,topo_graph, DEM_array):

        tg=topo_graph


        #step 1 - borders
        for n in tg.nodes: #find opposite = border
            
            id1 = tg.nodes[n]['ID_tree_i']
            i,j=n

            temp=[]
            
            for m in [(1,0),(0,-1)]: #no diagonal ! no-need, recessed pixels are always too high
                
                opposite=(i+ m[0], j + m[1])
                
                try :
                    id2 = tg.nodes[opposite]['ID_tree_i']
                    if id1 != id2:
                        self.nodes[opposite]={"class_i": 0, "ID_tree_i": id2} #fill new graph
                        self.nodes[n]={"class_i": 0, "ID_tree_i": id1}
                except: continue #out of limits...

        #step 2, connect
        
        for n in self.nodes:
        #min z - trazi najdublju
            
            i,j = n
            min_z = DEM_array[j,i] 
            cnt = 0
            
            for jj in xrange(j- 1, j+2): # allows diagonal connections !
                for ii in xrange(i- 1, i+ 2):
                
                    if (ii,jj) in self.nodes : 
                        z2 = DEM_array[jj,ii]
                        
                        if z2 < min_z  :
                            min_z = z2
                            source=(ii,jj)
                            cnt +=1
                                  
            if cnt > 0:

                self.nodes[n]["class_i"] = cnt

                try:    self.relations[source].append(n)
                except: self.relations[source] = [n]

                self.edges[source,n]= {'slope_f': z2 - min_z}
        #QMessageBox.information(None, "podatak:", str(c))

    def getNodes (self): return self.nodes
    # ----------------------   NOT USED ------------------------------

    def addVertex(self,key):
        self.numVertices = self.numVertices + 1
        newVertex = Vertex(key)
        self.vertList[key] = newVertex
        return newVertex

    def getVertex(self,n):
        if n in self.vertList:
            return self.vertList[n]
        else:
            return None

    def __contains__(self,n):
        return n in self.vertList

    def addEdge(self,f,t,cost=0):
        if f not in self.vertList:
            nv = self.addVertex(f)
        if t not in self.vertList:
            nv = self.addVertex(t)
        self.vertList[f].addNeighbor(self.vertList[t], cost)

    def getVertices(self):
        return self.vertList.keys()

    def __iter__(self):
        return iter(self.vertList.values())
