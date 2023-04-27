## practica2

Este fichero contiene los archivos que resuelven el problema del puente de Ambite, que es compartido por peatones y vehículos y no permite el paso de vehículos en sentidos contrarios ni el de personas y automóviles, simultáneamente, por motivos de seguridad al no tener suficiente anchura. 

Se ha implementado una solución eficiente a este problema utilizando monitores. 
Todo el desarrollo teórico que justifica el uso de las ideas presentadas en el código, puede encontrarse en el documento PDF del mismo nombre (<desarrollo.pdf>) en el que se ha definido el invariante del monitor solución junto con la demostración de que no presenta problemas de seguridad (exclusión mutua), deadlocks ni inanición.

En primer lugar, se ha partido de una solución sencilla que cumpla la seguridad pero que, sin embargo, presentaba problemas de inanición que siempre se buscará evitar en un buen programa que se sirva de la concurrencia en la ejecución. Partiendo de esta solución se ha logrado resolver dichos problemas al añadir variables de condición que permitan saber si hay *cuerpos* de cada uno de los tipos esperando por entrar.

En el archivo <initial_bridge.py> se han creado variables de condición y reglas para asegurar que cuando cada uno de los tipos de *cuerpo* quiera pasar, deba hacerlo cuando no haya ninguno de los otros tipos dentro del puente. Esta solución presenta problemas de inanición, pues dos de los tres tipos de *cuerpo* podrían ponerse de acuerdo para no cederle los recursos compartidos (el espacio del puente) al tercer y último tipo restante.

La solución definitiva puede encontrarse en el archivo <final_bridge.py> donde además se tiene en cuenta el número de *cuerpos* de cada tipo que está esperando por entrar al puente para que así se impida el escenario en que uno de estos tipos no pueda entrar al puente de forma indefinida.
