import os
from shapely.geometry import shape
from shapely.geometry import LineString

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as cls
from matplotlib import cm
from matplotlib.colors import Normalize

from osgeo import ogr, osr
import geopandas as gpd
import pandas as pd
import time
import networkx as nx
import osmnx as ox

ox.config(use_cache=True, log_console=True)
_G = ox.graph_from_place('CABA, AR', network_type = 'drive')
G = ox.project_graph(_G) # Si no se proyecta devuelve el error "ImportError: scikit-learn must be installed to search an unprojected graph"

# fig, ax = ox.plot_graph(G)

#Read the Origin-Destination csv
od_table = 'OD_pares.csv'
df = pd.read_csv(od_table, delimiter=' ', header=0, encoding='ascii')

def nodes_to_linestring(path):
    coords_list = [(G.nodes[i]['x'], G.nodes[i]['y']) for i in path ]
    #print(coords_list)
    line = LineString(coords_list)
    
    return(line)

""" Parte 1 """

def shortestpath(o_long, o_lat, d_long, d_lat):
    
    # nearestnode_origin, dist_o_to_onode = ox.nearest_nodes(G, (o_lat, o_long), method='haversine', return_dist=True)
    nearestnode_origin, dist_o_to_onode = ox.nearest_nodes(G, o_long, o_lat, return_dist=True)
    nearestnode_dest, dist_d_to_dnode = ox.nearest_nodes(G, d_long, d_lat, return_dist=True)
    
    #Add up distance to nodes from both o and d ends. This is the distance that's not covered by the network
    dist_to_network = dist_o_to_onode + dist_d_to_dnode
    
    shortest_p = nx.shortest_path(G,nearestnode_origin, nearestnode_dest) 
    
    route = nodes_to_linestring(shortest_p) #Method defined above
    
    # Calculating length of the route requires projection into UTM system.  
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(32721)
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    #route.wkt returns wkt of the shapely object. This step was necessary as transformation can be applied 
    #only on an ogr object. Used EPSG 32721 as Bangalore is in 43N UTM grid zone.
    geom = ogr.CreateGeometryFromWkt(route.wkt)
   
    geom.Transform(coordTransform)
    length = geom.Length()
    
    #Total length to be covered is length along network between the nodes plus the distance from the O,D points to their nearest nodes
    total_length = length + dist_to_network
    #in metres
    
    return(route, total_length )

start_time = time.time()

def colores_x_distancia(lengths):
    # Crear un conjunto de valores decimales de ejemplo
    # valores = np.array([6802.3191983519682, 7131.4521161371558, 4929.2584152915197, 5895.3489320999106, 7300.9307860684003, 4691.3260118363341, 5100.6321171520931])
    valores = np.array(lengths)

    # Crear un colormap que va de verde a rojo
    cmap = cm.get_cmap('RdYlGn')  # RdYlGn es una combinación de Rojo, Amarillo y Verde
    
    # Normalizar los valores en el rango [0, 1] para que coincidan con el colormap
    norm = Normalize(vmin=valores.min(), vmax=valores.max())
    
    # Invertir los colores asignados
    colores = [cmap(1 - norm(valor)) for valor in valores]
    
    # Convertir colores a formato hexadecimal
    # colores_hex = [cls.to_hex(color) for color in colores] 
    colores_hex = [{ "stroke": True, "color": cls.to_hex(color), "opacity": 0.75 } for color in colores]
    
    # Imprimir la lista de colores hexadecimales
    dist_colores = dict(zip(lengths, colores_hex))
    # print(dist_colores)
    return dist_colores

df['osmnx_geometry'] = df.apply(lambda x: shortestpath(x['o_long'], x['o_lat'], x['d_long'], x['d_lat'])[0] , axis=1)
df['osmnx_length'] = df.apply(lambda x: shortestpath(x['o_long'], x['o_lat'], x['d_long'], x['d_lat'])[1] , axis=1)

lengths = df['osmnx_length'].tolist()

colores = colores_x_distancia(lengths)

df['styles'] = df['osmnx_length'].map(colores)

print("Time taken: ", (time.time() - start_time), "seconds")

""" Parte 2 """
df = df.rename(columns = {'osmnx_geometry': 'geometry', 'osmnx_length': 'distancia'})
utm_gpdf = gpd.GeoDataFrame(df, geometry =df['geometry'], crs="EPSG:32721")
gpdf = utm_gpdf.to_crs(4326)

# fig, ax = ox.plot_graph(G)

# IF no such folder exists, create one automatically
if not os.path.exists('resultados'):
    os.mkdir('resultados')

timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
gpdf.to_file(f'resultados/osmnx_ruta_mas_corta_{timestr}.geojson', driver='GeoJSON')