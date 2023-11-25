mensaje = "Trabajo de investigación Grupo 8 - Asignatura Programación en Python\n\nIntegrantes: \n   * FUENTES, Lautaro\n   * FUNES, Jésica\n   * PEREZ, Gonzalo\n\n"

print(mensaje)

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

print("\n\nDescarga de red vial de CABA desde OpenStreetMap... \n\n")
ox.config(use_cache=True, log_console=True) # Busca usar los datos desde el directorio cache si es que ya fueron descargados previamente 
_G = ox.graph_from_place('CABA, AR', network_type = 'drive') # Convierte la red vial en un grafo
G = ox.project_graph(_G) # El grafo debe estar proyectado a un sistema de coordenadas UTM para poder calcular distancias en metros

print("\n\nMostrando imagen del grafo... \n\n")
fig, ax = ox.plot_graph(G)

print("\n\nLeyendo Origen-Destino desde el CSV\n\n")
od_table = 'OD_pares.csv'
df = pd.read_csv(od_table, delimiter=' ', header=0, encoding='ascii') # Convierte 

def nodes_to_linestring(path):
    """ Convierte una lista de nodos del grafo en un objeto LineString (geometría de línea) """
    coords_list = [(G.nodes[i]['x'], G.nodes[i]['y']) for i in path ]
    line = LineString(coords_list)
    
    return(line)


def shortestpath(o_long, o_lat, d_long, d_lat):
    """ Calcula sobre la topología el camino más corto dadas las coordendadas de origen y destino """
    
    """ Seleccionar los nodos del grafo más próximos a los puntos recibidos como entrada """
    nearestnode_origin, dist_o_to_onode = ox.nearest_nodes(G, o_long, o_lat, return_dist=True) # Origen
    nearestnode_dest, dist_d_to_dnode = ox.nearest_nodes(G, d_long, d_lat, return_dist=True) # Destino
    
    #Add up distance to nodes from both o and d ends. This is the distance that's not covered by the network
    """ Suma la distancia a los nodos de los extremos origen y destino """
    dist_to_network = dist_o_to_onode + dist_d_to_dnode
    
    """ Calcular camino más corto entre origen y destino """
    shortest_p = nx.shortest_path(G,nearestnode_origin, nearestnode_dest) 
    
    route = nodes_to_linestring(shortest_p) # Genera la geometría de la ruta
    
    """ Para calcular la longitud de la ruta es necesario proyectarla en el sistema UTM """
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326) # Sistema de coordenadas geográficas (Expresadas en grados)
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(32721) # Sistema de coordenadas proyectadas (Expresadas en metros)
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    """ 
    route.wkt devuelve el WKT (Well Known Text) del objeto shapely. Éste paso es necesario ya que
    la transformación sólo es posible desde un objeto OGR solamente. Se utiliza el sistema EPSG:32721 dado que Buenos Aires está en la zona 21S de la malla UTM, que cubre entre 60°O y 54°O, hemisferio sur entre 80°S y el ecuador, en tierra y mar adentro. Argentina, Bolivia, Brasil, Paraguay y Uruguay.
    """
    geom = ogr.CreateGeometryFromWkt(route.wkt)
   
    geom.Transform(coordTransform) # Transformación de coordenadas
    length = geom.Length() # Ya proyectada a EPSG:32721, calcula la longitud de la geometría 
    
    """ La longitud total a cubrir es la longitud a lo largo de la red entre los nodos más la distancia desde los puntos O,D hasta sus nodos más cercanos. """
    total_length = length + dist_to_network # En metros
    
    return(route, total_length )

start_time = time.time() # Inicia un conteo del tiempo de ejecución

def colores_x_distancia(lengths):
    """ 
    Para cada valor del listado de distancias recibido, interpola y asigna un color en hexadecimal dentro de un rango de verde a rojo coincidiendo de menor a mayor y devuelve un objeto de estilo para el GeoJSON 
    """
    valores = np.array(lengths)

    # Crear un colormap que va de verde a rojo
    cmap = cm.get_cmap('RdYlGn')  # RdYlGn es una combinación de Rojo, Amarillo y Verde
    
    # Normalizar los valores en el rango [0, 1] para que coincidan con el colormap
    norm = Normalize(vmin=valores.min(), vmax=valores.max())
    
    # Invertir los colores asignados
    colores = [cmap(1 - norm(valor)) for valor in valores]
    
    # Convertir colores a formato hexadecimal
    colores_hex = [{ "stroke": True, "color": cls.to_hex(color), "opacity": 0.75 } for color in colores]
    
    # Integra la lista de distancias recibida como entrada y la de colores hexadecimales en un diccionario
    dist_colores = dict(zip(lengths, colores_hex))
    # Devuelve el diccionario
    return dist_colores

""" Ejecuta el método shortestpath para cada elemento de la columna geometría """
df['osmnx_geometry'] = df.apply(lambda x: shortestpath(x['o_long'], x['o_lat'], x['d_long'], x['d_lat'])[0] , axis=1)
""" Ejecuta el método shortestpath para cada elemento de la columna distancia """
df['osmnx_length'] = df.apply(lambda x: shortestpath(x['o_long'], x['o_lat'], x['d_long'], x['d_lat'])[1] , axis=1)

lengths = df['osmnx_length'].tolist() # Convierte las distancias a una lista

colores = colores_x_distancia(lengths) # Invoca al método que devuelve colores en base a la distancia

df['styles'] = df['osmnx_length'].map(colores) # Asigna en la tabla de Pandas, los colores según la distancia

print("\n\nTiempo de ejecución: ", (time.time() - start_time), "segundos\n\n") # Muestra el tiempo de ejecución hasta este punto

""" Renombra campo de geometría y distancia """
df = df.rename(columns = {'osmnx_geometry': 'geometry', 'osmnx_length': 'distancia'})

""" Proyecta los datos otra vez a un sistema de coordenadas geográficas """
utm_gpdf = gpd.GeoDataFrame(df, geometry =df['geometry'], crs="EPSG:32721")
gpdf = utm_gpdf.to_crs(4326)

""" Si el directorio resultados no existe, lo crea """
if not os.path.exists('resultados'):
    os.mkdir('resultados')

""" Genera una cadena con la fecha y hora para el nombre del archivo de salida """
timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

""" Guarda los resultados en un archivo GeoJSON """
gpdf.to_file(f'resultados/osmnx_ruta_mas_corta_{timestr}.geojson', driver='GeoJSON')

print(f'Resultados guardados en resultados/osmnx_ruta_mas_corta_{timestr}.geojson\n\n')