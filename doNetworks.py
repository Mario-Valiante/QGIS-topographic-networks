
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import gdal
import os
#import numpy  -- not used??
import osgeo
from qgis.utils import iface
from qgis import core

from collections import deque
from operator import itemgetter



import doImportExport
from TopoGraph import TopoGraph

import sys, os


def NetworkAnalysis(output, DEM_ly, out_file, class_ly, search, merge, inverse, min_slope):
    
   

    entities ={}
        

# 2 a: ------------  flow accumulation -------------------------
    def flow (topo_network_object, use_slope):
        use_slope=True
        
        test=0
        # sort so that it begins from sinks and advances step wise
        def keyfunc(tup):
            key, v = tup
            try: return v["step_i"]
            except: return 0

        tg = topo_network_object
        
        for key, sub_dict in sorted(tg.nodes.items(), key=keyfunc, reverse=True):#reverse = descending, key 0 = dict key, key 1 - x = values


            flow=[]
            top_flow =0
            cnt = 0
                    
            try:
                f = tg.relations[key]
                for ch in f:
                    #collect prevoius flow + its own slope
                    flow.append( tg.nodes[ch]["flow_f"] + tg.edges[key,ch]["slope_f"])

            except :#SINKS, ne klassificira dobro u BFS !!...
                if use_slope: tg.nodes[key]["flow_f"]=0  #to initialize sinks
                else: tg.nodes[key]["flow_f"]=1 #start with 1 for accumulation
                continue #exit loop!!
            


                     
            try:tg.nodes[key]["flow_f"] = sum(flow)/len(flow)
            except: QMessageBox.information(None, "0 class",str(flow)); return
            
      #  QMessageBox.information(None, "0 class",str(test2))
        return tg.nodes
 
    # 2a - 2 --------------- difference (on flow raster) -------------------------------
    # calculate symetry in relations of each peak
    # NOT A CONTINUOUS VALUE !!! entity based!
    def flow_diff():

        l=[]
        for nd in n:
            if n[nd][2]==0: #peaks
                for ch in g[nd]: l.append(n[ch][3])
            l.sort
            diff=0
            for i in xrange(7): #each peak must have 8 connections (8th is i+1)!! IS THIS 
               diff += l[i]-l[i+1] # if the number is odd!!
               
            n[nd]["flow_diff_f"]=flow

# 2c ---------------- degree ----------------------------------
    def degree():
        for node in g:
            n[node]["degree_i"]=len(g[node])
           
    

    # 3 --------------------- BORDER LINES ------------------------

  
    
    def border_lines(nodes, method='centreline', reeb=False): #method 2 = pixel
        

        def find_opposite(node):
            
            id1 = nodes[node] ['ID_tree_i']
            i,j=node

            temp=[]
            
            for m in [(1,0),(0,-1)]:
                
                opposite=(i+ m[0], j + m[1])
                
                try :
                    id2 = nodes[opposite]['ID_tree_i']
                    if id1 != id2: temp.append([opposite, m])
                except: continue #out of limits...
                
            return temp

    
                
        
        lst=[]; lst2=[] #testiranje
        links={} # polygon boundaries
        move={} #channel pixels

        for n in nodes:
            i,j = n
            id1 = nodes[n] ['ID_tree_i'] # for n, val in nodes:  val['ID_tree_i'] - doesn't work
            if id1 == 0: continue
            
            for o in find_opposite(n):
                opposite, direction = o
                id2 = nodes[opposite]['ID_tree_i']
                if id2 == 0 : continue

                #draw vertical (move all to right : i+1)
                if direction[0]==1:
                    pt1 = opposite # (i+1, j)
                    pt2 = (i+1, j+1)

##                    if z1<z2:
##                            move[pt1]=n
##                            move [pt2] = (i,j+1)
##                            pt1=n
##                            pt2 = (i,j+1)
                    #draw horizontal (do not move)
                else :
                    pt1 =  n #(i,j)
                    pt2 = (i+1, j)

##                       if z1>z2:
##                            move[pt1]=opposite_n 
##                            move[pt2]= (i+1, j-1)
##                            pt1 = opposite_n
##                            pt2 = (i,j)
                    # to ensure the same direction of edges!!
                if id1 > id2:
                    ident = (id2,id1)
                    pt1,pt2 = pt2,pt1
                else: ident = (id1,id2)

                try: links[ident]+= [[pt1, pt2]]# add a list of two points ( a line) 
                except: links[ident]= [[pt1, pt2]]


        
        #QMessageBox.information(None, "Broken lines! ",str(links))
                
    # ---------------- 3b : sorting and simplifying lines --------------------------
    #    def line_chains():
    # SREDJIVANJE LANCA : Ne MOZE se UKRCATI GORe DA SE RADI DIREKTNO : krivudave linije koje se rezu u horizontali...
    # sort lists with points so that we can make regular chains of coordinates
    # convert to list because the function for line drawing takes lists (ugly ....)

        output={}
        output2 ={}
        errors = []
        t=0
        for n in links:
          

            #for key, value in links.iteritems():
            pts = links[n]
        
            temp = pts.pop()
            i=0
            doublon=0
            
            while pts:

                try: e=pts[i]
                except:
                    # jebu ga otoci koji su na granici dva veca poligona: isti id granice, ali nije spojeno!
                    # istrapj kao da je kraj pa pocni novu liniju s istim ID-om
                    if len(pts)>0: #we need GOTO here!!
                        doublon+=1
                        output[(n ,doublon)]={'points' : temp, 'ID_s' : n}
                        temp = pts.pop()
                        
                        try: i=0; e=pts[i]
                        except : break #this will force it to write temp

                        errors.append([doublon * 99, n ])
                        
                    # a solution is to use loop with while, but then the dictionary cannot be popped??
                    else: break

                #sorting vertices to form a chain : in front or to the back             
                if e[0] == temp[-1]:
                     
                    temp.append(e[1]) #to the back
                    pts.pop(i)
                    i=0
                    
                elif e[1] == temp[0]:

                    temp.insert(0,e[0])
                    pts.pop(i)
                    i=0

                    
                # not found, go to next one
                else: i+=1

           
    #sredivanje/ pojednostavljivanje: ne dodaj nista ako je 45 ili ako je ravno
            output[n]={'points' : temp, 'ID_s' : n }

        
        #QMessageBox.information(None, "Broken lines! ",str(links)) 
        links=None


         #straighten lines
          #approach 2 : register direction 1,-1 / 1,1 / -1,1 / -1,-1 => on change : draw point (less points!)
        
        for k in output:
            x0,y0 = output[k]['points'][0]
            step=0
            temp=[(x0,y0)]
            
            for pt in output[k]['points']:
                x,y=pt
                if x <> x0 and y<>y0:
                    try:
                        if tg.nodes[pt]['class_i']==0 : step = 99 #force to write peaks/pits
                    except: pass
                    if step > 1 :
                        temp.append((x_old,y_old))
                        x0,y0 = x_old, y_old
                        step=0
                    
                step+=1
                x_old, y_old = x,y
                
            temp.append ((x,y))  #end
            output[k]['points'] = temp
        
       # QMessageBox.information(None, "Broken lines! ",str(output))
        if not reeb: return output

        #QMessageBox.information(None, "podatak:", str(output))
#EXIT IF NOT REEB GRAPH

        #---------KRAJ SURFACE NETWORKA ==> REEB GRAPH -------------------------------
        # ------- dodatak za pronalazelje sedla ------------
        
        test=[]
        saddles=[]
        s_test={}
        for n in output:
            
            #QMessageBox.information(None, "Double saddles! ",str(output))
            
                
            id1,id2 = n
            #PROBLEM of multiple borders - same entities
#NOT FIXED !!!!!
            if  isinstance(id1, tuple):
                sufix=id2
                id1, id2=id1
                test+=[id1,id2]
            else: sufix=None    

            max_z = -9999
            
            for pt in output[n]['points']:
                i,j = pt

                try: z= gdalData [j,i]#because of line drawing routine there are always points max_x + 1 / max_y +1
                except: continue

                if z > max_z:
                    max_z = z
                    saddle = pt
                    
            # sedla mogu biti DUPLA - uzrokuje LOOPS
            # isti ID1 , id2 (tijekom kolapsa grafa)= continue
            
##            if saddle in s_test:
##                s_test[saddle] += 1 #ensure a unique ID
##                saddle = (saddle[0], saddle[1], s_test[saddle])
##            #track saddles 
##            else: s_test[saddle]=0

            
                
            #NORMALLY THEY ARE NEVER 0 !!(unclassified)
            if id1 >0 and id2 >0  :
                tg.entities[id1]['saddles'] += [saddle]
                tg.entities[id2]['saddles'] += [saddle]
                    
            saddles.append([max_z, saddle,[id1,id2]])

#--------------------------------------------
        st = ''
        if test:
            for t in test: st += str(t) + '\n'
            QMessageBox.information(None, "Double saddles! ",str(st))
       # QMessageBox.information(None, "Double saddles! ",str(tg.entities))
# -------------- graph collapse---------------
        out = {}# screen print
        out2 =[]
        id_reeb=0
        order=0
        #initialize: top parts will have positive IDs
        for n in tg.nodes: tg.nodes[n]['ID_reeb_i']=tg.nodes[n]['ID_tree_i']

        #COULD BE DONE WITH heapq ?:
        # add last to que, delete first (only problem with node ids - should get ids sorted by height!)
        current_reeb= {} 
        track_ids= {}
                #saddles have old tree_ids
        for s in sorted(saddles, reverse=True): #sort by first vaule = z
            id_reeb -= 1 #negative so it doesn't mix with positive node IDs
            zs = s[0]
            saddle_pt= s[1]
            id1,id2=s[2]

            members = [] #tracking old ids to rewrite : this fuss is to avoid looping through all ids and
                        # verifying for each if it should be asssignes a new reeb_id

            try: #if not in dict = first visit
                id1_n = current_reeb[id1]
                members += track_ids[id1_n]['nodes']
                pt1= track_ids[id1_n]['point']
                step1=track_ids[id1_n]['step']
            except:
                id1_n=id1
                members += [id1]
                pt1= tg.entities[id1]['point']
                step1=0
                
            try:
                id2_n = current_reeb[id2]
                members += track_ids[id2_n]['nodes']
                pt2= track_ids[id2_n]['point']
                step2=track_ids[id2_n]['step']
            except:
                id2_n = id2
                members += [id2]
                pt2= tg.entities[id2]['point']
                step2=0
            
            #SKIP! if saddle was already connected before
            if id1_n == id2_n: continue

            order +=1
            step =min(step1, step2) + 1
            track_ids[id_reeb]={'nodes': members, 
                                 'point': saddle_pt,
                                'step': step,
                                'order': order}
            
            for m in members: current_reeb[m]=id_reeb
    

            # nodes are listed in entities - for speed
            # delete nodes after SECOND visit to same tree- speed up or not?
            for n in tg.entities[id1]['nodes']:    
                i,j = n
                if gdalData[j,i] <= zs:
                    tg.nodes[n]['ID_reeb_i']=id_reeb
            for n in tg.entities[id2]['nodes']:    
                i,j = n
                if gdalData[j,i] <= zs:
                    tg.nodes[n]['ID_reeb_i']=id_reeb        

            out[id1_n, id_reeb]={'points':[pt1, saddle_pt], 'step': step1, 'order':order}
            out[id2_n, id_reeb]={'points':[pt2, saddle_pt], 'step': step2, 'order':order}
            
                   
        #inform if an error happened!!  NOT USED!!!! 
        #if errors:
        st = 'Source,Target\n'
        for o in out: st += str(o) + '\n'
        #QMessageBox.information(None, "Reeb graph",str(st))
        st = 'ID,z,kolicina\n'
        for o in out2: st += str(o) +  '\n'
        #QMessageBox.information(None, "Reeb graph NODES",str(st))
      #  QMessageBox.information(None, "Broken lines! ",str(st))
        
          #  exit
            
        #QMessageBox.information(None, "Broken lines! ",str(temp))
          
        #return
        return out
       

# ---------------------------
    def summit_extraction (topo_network_object, method):

        if method == 'min_degree':
            pass            
        
    def pix_count_id(id_tuple): #raster size is global

        if len(id_tuple)==3: x,y,n=id_tuple
        else: x,y=id_tuple; n=0
        new_id = y * xsize + x +1
        if n: 
            return (y * xsize + x +1 ) + xsize + ysize + n
        else:
            return new_id
        
    # ------------------------- MAIN -------------------------



    RasterPath= str(QgsMapLayerRegistry.instance().mapLayer(DEM_ly).dataProvider().dataSourceUri())
    src_ds = gdal.Open(RasterPath)

    projection= src_ds.GetProjection()

    #PROVJERITI ! za shapefile ponekad ne funkcionira GDAL projekcija
    raster_ly= QgsMapLayerRegistry.instance().mapLayer(DEM_ly)# za izvlacenje crs
    # --------------------------
    
    gt=src_ds.GetGeoTransform()#raster metadata 

    #This should logically be in the Assembly function, but then it would require NUMPY ??
    #check performance....
    gdalData = src_ds.ReadAsArray()
    if inverse: gdalData *=  -1
        
    xsize = len(gdalData[0])
    ysize = len(gdalData)

# --------- DO STUFF -----------
    # required for all analyses
    tg = TopoGraph()#INSTANCE OF TOPOGRAPH CLASS > ()
    tg.Assembly(gdalData, radius=search)

    tg.merge_peaks(merge, gdalData)#OBLIGATORY, even when 0
    
    tg.BFS_traversal()
    
    out=[]
    
    if output == 'Complete':
        
        #add field 'points' to edge list

        
        for key in tg.edges:

                                    
            tg.edges[key] ['points']= key
            try:
                tg.edges[key] ['tree_i'] = tg.nodes[key[0]]['ID_tree_i']
            except :
                tg.edges[key] ['tree_i'] = 0
           
        
       # QMessageBox.information(None, "podatak:", str(tg.edges[tg.edges.keys()[10
        
        success = doImportExport.write_shp (out_file + '_topo_network' , tg.edges,
                                              raster_ly.crs(), gt, center_pixel=True)

        if success :out.append(success)                                      

    elif output == 'Ridge':

        #izlaz = border_lines(gdalData, tg)
        
        #SN = TopoGraph()
        #SN.SN_assembly(tg, gdalData)
        #SN.BFS_traversal()
        #izlaz = {}
        #for n in SN.edges: izlaz[n]={"key_s":n,'points':[n[0],n[1]]}#n is a touple ((7,8),(5,3)) - has to be list...

        #QMessageBox.information(None, "podatak:", str(SN.edges))
        izlaz = border_lines(tg.nodes)
        #success = doImportExport.write_raster(izlaz,'ID_tree_i', out_file, xsize, ysize, projection, gt)
        success = doImportExport.write_shp (out_file + '_surface_network' , izlaz,
                                            raster_ly.crs(), gt,  center_pixel=False)
        if success :out.append(success)
        
        izlaz = {}
        for n in tg.nodes:
            if tg.nodes[n]['class_i'] == 0:
                izlaz[n]={"key_s":n,'points':[n]}#n is a touple ((7,8),(5,3)) - has to be list...


        success = doImportExport.write_shp (out_file + '_min-max' , izlaz,
                                            raster_ly.crs(), gt,  center_pixel=True,
                                            shp_type ='point')
    
    elif output == 'ID':

                                    
        s=doImportExport.write_raster(tg.nodes,'ID_tree_i', out_file, xsize, ysize, projection, gt)
        if s: out.append(s)

    elif output == 'Flow':
        izlaz = flow(tg, use_slope=True) 
        success = doImportExport.write_raster(izlaz,'flow_f', out_file, xsize, ysize, projection, gt)        
        if success :out.append(success)

    elif output == 'Reeb':
        reeb = border_lines(tg.nodes, reeb=True) 

     #   QMessageBox.information(None, "podaci ", str(tg.entities))
#metoda pomocu entities

                                             #ID_tree_i
        s=doImportExport.write_raster(tg.nodes,'ID_reeb_i', out_file, xsize, ysize, projection, gt)
        if s: out.append(s)
#vector
        izlaz ={} 
        for r in reeb:
            izlaz[r]={'points':reeb[r]['points'],
                        'source_i':r[1],
                            'target_i':r[0],
                      'step_f':reeb[r]['step'],
                      'order_f': reeb[r]['order'] }
               
        success = doImportExport.write_shp (out_file + '_Reeb' , izlaz,
                                            raster_ly.crs(), gt,  center_pixel=True)
        if success :out.append(success)

        
        
        graph=pydot.Dot(graph_type='graph')
        for r in reeb:
            edge= pydot.Edge(r[0],r[1])
            graph.add_edge(edge)
        #graph=graph_from_adjacency_matrix(g_out)


        import subprocess
        #= same folder
        dot_path = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        
        p=subprocess.Popen([(os.path.join(dot_path,'dot.exe')),
                            "-oU:/Users/zcuckovi/test.png ","-Tpng" ],
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        QMessageBox.information(None, "podaci ", graph.to_string())
        p.communicate(input=graph.to_string())#[0]

        #out_data = p.communicate ...
   # clean('nodes') #izbacuje nodes bez ID

    
    return out

