# Trabajo de investigación Grupo 8 - Asignatura Programación en Python

## Integrantes

* FUENTES, Lautaro
* FUNES, Jésica
* PEREZ, Gonzalo

## Introducción

El scrpt descarga la red vial de la Ciudad de Buenos Aires sobre la cual, teniendo como entrada un punto de origen y varios de destino, calcula la ruta hacia cada uno generando
su correspondiente línea en un archivo GeoJSON que incluye la distancia en metros que puede servir para estimar el camino más conveniente. 

## Uso

Ejecutar con Python el script ruta_mas_corta.py el cual requiere como entrada un listado en formato CSV de coordenadas de origen y otras de destino con el siguiente formato:

```
o_id o_long o_lat d_id d_long d_lat
o1 -58.41539 -34.55522 d1 -58.4374 -34.57041
o2 -58.41539 -34.55522 d2 -58.4390125 -34.5552663
o3 -58.41539 -34.55522 d3 -58.4241928 -34.5753459
o4 -58.41539 -34.55522 d4 -58.4299476 -34.5810218
o5 -58.41539 -34.55522 d5 -58.4460249 -34.5615869
o6 -58.41539 -34.55522 d6 -58.4044042 -34.5779615
o7 -58.41539 -34.55522 d7 -58.4069646 -34.5814036
```

  Donde:
  
  * o_id es el identificador del punto de origen
  * o_long es la coordenadada de longitud del punto de origen
  * o_lat es la coordenadada de latitud del punto de origen
  * d_id es el identificador del punto de destino
  * o_long es la coordenadada de longitud del punto de destino
  * o_lat es la coordenadada de latitud del punto de destino

Las coordenadas deben estar proyectadas a UTM, en los archivos incluidos se incluye la tabla 'OD_pares.csv' la cual ya tiene los datos convertidos que utilizará el script.

Cuando termina la ejecución el script genera un archivo GeoJSON en el directorio 'resultados' con las rutas calculadas que incluyen entra sus datos el valor de la distancia total de cada una en metros.
En ese directorio se encuentra un archivo ejemplo.geojson que sirve para revisar antes de ejecutar.
Los datos son descargados automáticamente del proyecto OpenStreetMap por lo que es necesaria una conexión a Internet.

## Origen del problema o tema

La necesidad de encontrar rutas óptimas entre ubicaciones ha sido un desafío constante en diversas disciplinas. 
Con el auge de la tecnología y la creciente disponibilidad de datos geoespaciales, surge la oportunidad de abordar este problema mediante el empleo de análisis basados en redes neuronales.
