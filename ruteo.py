message = f"Ruteo en Buenos Aires."
print(message)

""" Defino los puntos para el ruteo, extraidos de OpenStreetMap con 
Overpass-Turbo - Consulta de puntos https://overpass-turbo.eu/s/1DUw """
punto_a = -58.41539, -34.55522 # Aeroparque Jorge Newbery
punto_b = -58.4374, -34.57041 # Hospital Militar Central Doctor Cosme Argerich
punto_c = -58.4390125, -34.5552663 # Clinica Loiacono
punto_d = -58.4241928, -34.5753459 # Sanatorio de la Trinidad Palermo
punto_e = -58.4299476, -34.5810218 # Sanatorio de los Arcos
punto_f = -58.4460249, -34.5615869 # Clínica La Sagrada Familia
punto_g = -58.4044042, -34.5779615 # Sanatorio Mater Dei
punto_h = -58.4069646, -34.5814036 # Hospital General De Agudos Doctor Juan A. Fernández

""" Proyectar coordenadas al CRS seleccionado """
import geopandas as gpd
from shapely.geometry import Point

""" Convertir listas lat/lng lists en una lista de puntos """
lats = [-34.55522, -34.57041, -34.5552663, -34.5753459, -34.5810218, -34.5615869, -34.5779615, -34.5814036]
lngs = [-58.41539, -58.4374, -58.4390125, -58.4241928, -58.4299476, -58.4460249, -58.4044042, -58.4069646]
points_list = [Point((lng, lat)) for lat, lng in zip(lats, lngs)]

""" Convertir lista a GeoSeries con el CRS original, por ej EPSG:4326. """
points = gpd.GeoSeries(points_list, crs='epsg:4326')

""" Importar OSMnx para calcular rutas """
import osmnx  as ox
ox.config(use_cache=True, log_console=True)

""" Descargar desde OpenStreetMap la red vial de CABA - https://www.openstreetmap.org """
G = ox.graph_from_place('CABA, AR', network_type = 'drive')
Gp = ox.project_graph(G) # proyectado automáticamente a EPSG:32721 WGS 84 / UTM zone 21S
ox.plot_graph(Gp) # Muestra la topología de la red vial
# Gc = ox.consolidate_intersections(Gp, rebuild_graph=True, tolerance=20, dead_ends=False)

""" Proyectar puntos al sistema de coordendas en al que se proyectó la red vial """
points_proj = points.to_crs(Gp.graph['crs'])

# find nearest node in projected graph to each projected point
#method = 'euclidean'
#nearest_nodes = [ox.nearest_nodes(Gp, (pt.y, pt.x), method) for pt in points_proj]
#print(nearest_nodes) # prints [1334, 777, 37]

""" Armar puntos para el cálculo de nodos más próximos """
# X_a = 370143.5913556614, 6175369.676934727 # Point A
# X_b = 368148.09070886706, 6173656.572152557 # Point B
X_a = points_proj[0].x, points_proj[0].y
X_b = points_proj[1].x, points_proj[1].y

nearest_a = ox.distance.nearest_nodes(Gp, X_a[0], X_a[1], return_dist=False) # nodo 10016616693
nearest_b = ox.distance.nearest_nodes(Gp, X_b[0], X_b[1], return_dist=False) # nodo 89300965

""" List comprehension da una lista de índices """
X_a_node = [i for i, x in enumerate(list(Gp)) if x == nearest_a] 
X_b_node = [i for i, x in enumerate(list(Gp)) if x == nearest_b]

print(X_a_node, X_b_node) # [17871] [3247]

orig = list(Gp)[X_a_node[0]]
dest = list(Gp)[X_b_node[0]]

shortest_distance_route = ox.shortest_path(Gp, orig, dest, weight="length")
fig, ax = ox.plot_graph_route(Gp, shortest_distance_route, route_color="r", route_linewidth=6, node_size=0)
