
# Realizado por: Rodrigo de la Nuez Moraleda

"""
Cada proceso tendrá un buffer de tamaño fijo para poner los valores generados.
"""


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep
import random

nprod = 3
n = 5

# Función para 'dormir'/detener el proceso actual durante un tiempo aleatorio
def delay(factor = 3):
    sleep(random.random()/factor)

# Función para obtener el mínimo valor de entre los producidos
def get_minimum(lst):
    return min([x for x in lst if x >= 0])


# Función para generar los números de un proceso y guardarlos en un buffer local
def producer(valor, empty, non_empty, buffer, pos, indexes, mutex):
    
    # valor        -> Value con inicialmente valor -2 
    # emtpy
    # non_empty    -> Semaphore(0) para el nº de procesos ejecutados
    # buffer       -> Array(n) en el que se guardan los números del proceso
    # pos          -> valor entero con la posición asociada del proceso
    # indexes      -> Array(nprod) con las posiciones de los valores a comparar
    # mutex        -> Lock() para que solamente una sección crítica se ejecute
    
    for i in range(n):
        
        # Vemos en que proceso de producción está el programa
        print(f"producer {current_process().name} producing")        
        
        # Bloqueamos el semáforo del proceso actual y generamos un nuevo valor
        empty.acquire()
        
        mutex.acquire()
        valor.value += random.randint(2,7)
        delay() 
        buffer[i] = valor.value  # guardamos el valor en el buffer local
        mutex.release()
        
        non_empty.release()
        print (f"producer {current_process().name} produced {valor.value}")
        delay()
        

# Función para consumir los números generados y guardarlos en el almacén
def merge(storage, empty_semaphores, non_empty_semaphores, indexes, buffers, mutex):
    
    # storage    -> Array de tamaño n*nprod para guardar los productos ordenados
    # empty_semaphores     -> lista de los semáforos locales 'empty'
    # non_empty_semaphores -> lista de los semáforos locales 'non_empty'
    # indexes    -> Array(nprod) con las posiciones de los valores de cada proceso
    # buffers    -> lista de los buffers locales, de tipo Array(n) 
    # mutex      -> Lock() para que solamente una sección crítica se ejecute
     
    merge_index = 0   # índice en el que se guardara el siguiente valor
    ended = BoundedSemaphore(nprod) # para el nº de procesos terminados
    lst = list(range(nprod))
    
    # Comprobamos que todos los procesos han producido al menos un valor
    for i in lst:
        non_empty_semaphores[i].acquire()
        
    # Liberamos los anteriores semáforos para devolverlos a sus estados originales
    for i in lst:
        non_empty_semaphores[i].release()
    
    while True:
        
        
        # Si todos los procesos han terminado se acaba el bucle
        if ended.get_value() == 0:
            break
                
        # Obtenemos el valor mínimo de los generados
        mutex.acquire()
        temp = []
        for i in range(nprod):
            if indexes[i] < n:
                temp.append(buffers[i][indexes[i]])
            else:
                temp.append(-1) 
        
        minimo = get_minimum(temp[:]) 
        pos = temp[:].index(minimo)
        print("comparando: ", temp[:])  
        empty_semaphores[pos].release()              
            
        # Guardamos el valor mínimo y aumentamos la posición de guardado en el almacén  
        storage[merge_index] = minimo            
        print("storage: ", storage[:])
        merge_index += 1
            
        # Marcamos el espacio del almacén como consumido y avanzamos en la posición del buffer local  
        buffers[pos][indexes[pos]] = -1
        indexes[pos] += 1                    
        
        # Si la siguiente posición está fuera de rango, el proceso terminó
        if indexes[pos] == n:
            ended.acquire()
        mutex.release()
            
        non_empty_semaphores[pos].acquire()  
        print(f"consumer {current_process().name} consumiendo {minimo}")
        sleep(0.3)

                  
def main():
    storage = Array('i', n*nprod)
    indexes = Array('i', nprod)
    
    for i in range(nprod):
        indexes[i] = 0
        
    for i in range(n * nprod):
        storage[i] = -2
        
    values = [Value('i', -2) for _ in range(nprod)]
    empty_semaphores = [Lock() for _ in range(nprod)]
    non_empty_semaphores = [Semaphore(0) for _ in range(nprod)]
    buffers = [Array('i', n) for _ in range(nprod)]
    
    for b in buffers:
        for i in range(n):
            b[i] = -2
    
        
    mutex = Lock()
    procesos = [Process(target = producer, name = f'p_{i}', 
                        args=(values[i], empty_semaphores[i], non_empty_semaphores[i], 
                              buffers[i], i, indexes, mutex)) for i in range(nprod)]
    
    
    merge_process = Process(target = merge, name = 'merger',
                               args = (storage, empty_semaphores, non_empty_semaphores, 
                                       indexes, buffers, mutex))
    
    for p in procesos:
        p.start()
    merge_process.start()
    
    for p in procesos:
        p.join()
    merge_process.join()
    
    print("storage final: ", storage[:])

    
if __name__ == "__main__":
    main()
    