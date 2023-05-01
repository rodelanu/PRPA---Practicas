
# Realizado por: Rodrigo de la Nuez Moraleda

from pyspark import SparkContext
import itertools as it


# Establecer las variables de entorno para el intérprete Python de Spark
import os
import sys
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable


# Esta función toma un RDD que contiene el grafo del fichero y lo procesa para que
#  cada elemento del RDD sea una tupla de la forma (nodo1, nodo2) 
def fileToList(file_rdd):  
    
    """
    
       1. Transformammos cada línea tipo "A,B" a una tupla "(A,B)".
       2. Evitamos considerar aristas de un nodo a sí mismo
       3. Tomamos los nodos de manera que "el camino sea ascendente" (nodo1 < nodo2)
            Esto nos permitirá crear las matrices de adyacencia correspondientes.
            Además, los triciclos obtenidos se presentarán también en orden ascendente.
       4. Eliminamos posibles aristas repetidas para simplificara el grafo
       
    """
    
    graph_rdd = file_rdd.map(lambda x : tuple(x.split(','))) \
                        .filter(lambda x : x[0] != x[1]) \
                        .map(lambda x : (x[1], x[0]) if x[1] < x[0] else (x[0], x[1])) \
                        .distinct()
                        
    return graph_rdd


# Esta función toma un RDD de nodos y encuentra todos los ciclos de tres nodos en el grafo
def graphToTricycles(graph_rdd):
    
    # Creamos la matriz de adyacencia correspondiente al grafo
    adj_rdd = graph_rdd.groupByKey()\
                       .mapValues(set)\
                       .mapValues(sorted)\
                       .map(lambda x: 
                               (x[0], list(filter(lambda y: y > x[0], x[1]))))

    # Guardamos las aristas existentes en un RDD -> ((node1, node2), exists)
    exist_rdd = adj_rdd.flatMapValues(lambda x: x)\
                       .map(lambda x: (x,'exists'))

    # Guardamos las posibilidades de otras aristas del RDD -> ((node1, node2), (pending, node3))
    # Para ello, consideramos únicamente aristas que puedan generar triciclos de existir 
    pending_rdd = adj_rdd.flatMapValues(lambda x: it.combinations(x,2))\
                         .map(lambda x: (x[1], ('pending', x[0])))

    # Juntamos los dos RDD anteriores mediante la unión
    union_rdd = exist_rdd.union(pending_rdd)
    
    """
    
       Calculamos los triciclos del grafo del fichero
         1. agrupamos valores en listas según la arista del RDD 
         2. consideramos solo aquellas aristas que aparezcan en pending_rdd
         3. aplicamos la función de cálculo auxiliar y agrupamos los resultados
    
    """
    
    result_rdd = union_rdd.groupByKey()\
                      .mapValues(list )\
                      .filter(lambda x: len(x[1]) > 1) \
                      .flatMap(listToTricycle)
                      
    return result_rdd


# Función auxiliar para el cálculo de triciclos a partir del RDD de 'exists' y 'pending'
def listToTricycle(union_rdd_grouped):
    tricycles = [] # creamos una lista en la que guardar el triciclo si existe
    boolean = 0
    for edge in union_rdd_grouped[1]:
        if edge != 'exists': 
            current = (edge[1], ) + union_rdd_grouped[0]
            tricycles.append(current)
        else:
            boolean = 1      
            
    # guardamos el triciclo siempre que la arista exista
    return tricycles if boolean else []

   
if __name__ == '__main__':
    if len(sys.argv) > 1:
        sc = SparkContext()
        filenames = sys.argv[1:]
        tricycle_list = []
        for filename in filenames:
            txt_rdd = sc.textFile(filename)
            tricycles_rdd = graphToTricycles(fileToList(txt_rdd))
            tricycles = tricycles_rdd.collect()
            tricycle_list.extend(tricycles)
        print(tricycle_list)
        
    else:
        print('Debes introducir los nombres de los ficheros a examinar.')