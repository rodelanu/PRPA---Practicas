
# Realizado por: Rodrigo de la Nuez Moraleda

"""

Cada proceso tendrá un buffer de tamaño fijo para poner los valores generados.

"""


from multiprocessing import Process
from multiprocessing import BoundedSemaphore
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep
import random

nprod = 3
n = 5

# Función para 'dormir'/detener el proceso actual durante un tiempo aleatorio
def delay(factor = 3):
    sleep(random.random()/factor)

# Función para obtener el mínimo número de los valores producidos
def get_minimum(lst):
    return min([x for x in lst if x >= 0])


# Función para generar los números de un proceso y guardarlo en un buffer local
def producer(valor, global_sem, local_sem, local_buffer, pos, indexes):
        
    # valor        -> Value con inicialmente valor -2 -> value
    # global_sem   -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # local_sem    -> Lock() que controla cuando se ha producido un valor
    # local_buffer -> Array(n) en el que se guardan los números del proceso
    # pos          -> entero con el valor de la posición asociada del proceso
    # indexes      -> Array(nprod) con las posiciones para comparar después
    
    for i in range(n):
        
        # Vemos en que proceso esta el programa
        print(f"producer {current_process().name} producing")
        
        # Bloqueamos el semáforo del proceso actual y generamos un nuevo valor
        local_sem.acquire()        
        valor.value += random.randint(2,7)
        delay()
        
        # Guardamos el valor en el buffer local y bloqueamos global_sem 
        #  para llevar el conteo de los procesos que pueden ser comparados
        local_buffer[i] = valor.value        
        if local_sem.get_value() == n - indexes[pos] - 1:            
            global_sem.acquire()
            
        # Indicamos que se ha producido un nuevo valor en el proceso
        print (f"producer {current_process().name} produced {valor.value}")
        delay()
        

# Función para consumir los números generados y guardarlos en el almacén
def merge(storage, global_sem, semaphores, indexes, buffers):
    
    # storage    -> Array de tamaño n*nprod para guardar los productos ordenados
    # global_sem -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # semaphores -> lista de los semáforos locales, de tipo BoundedSemaphore(nprod)
    # indexes    -> Array(nprod) con las posiciones para comparar después
    # buffers    -> lista de los buffers locales, de tipo Array(n) 
     
    merge_index = 0   # índice en el que se guardara el siguiente valor
    ended = BoundedSemaphore(nprod) # para el nº de procesos terminados
    while True:
        
        # Comprobamos si todos los procesos tienen algún valor generado
        if global_sem.get_value() == 0:
            
            # Si todos los procesos han terminado se acaba el bucle
            if ended.get_value() == 0:
                break
                      
            temp = [alm[i] if i<len(alm) else -1 for alm, i in zip(buffers, indexes)]            
            minimo = get_minimum(temp[:]) 
            print("temp:", temp[:]) 
            print("minimum: ", minimo)                 
            
            # Aunque cambiamos variables globales, al estar el resto de procesos
            #  bloqueados con Lock's no es necesasrio proteger la sección crítica
            pos = temp[:].index(minimo)
            storage[merge_index] = minimo            
            print("storage: ", storage[:])
            merge_index += 1
            
            # Marcamos el espacio del almacén como consumido y avanzamos la posición
            buffers[pos][indexes[pos]] = -1
            indexes[pos] += 1                    
            
            # Si la siguiente posición está fuera de rango, el proceso terminó
            if indexes[pos] == n:
                ended.acquire()
            
            # Si falta por generarse un valor, liberamos un espacio en el semáforo global                
            elif buffers[pos][indexes[pos]] == -2:
                global_sem.release() 
        
        # Si algún proceso no ha generado un valor, se duerme darle la opción
        else:
            sleep(0.1)
           

        
def main():
    storage = Array('i', n * nprod)
    global_sem = BoundedSemaphore(nprod)
    indexes = Array('i', nprod)
    
    for i in range(nprod):
        indexes[i] = 0
        
    for i in range(n * nprod):
        storage[i] = -2
        
    values = [Value('i', -2) for _ in range(nprod)]
    semaphores = [BoundedSemaphore(n) for _ in range(nprod)]
    buffers = [Array('i', n) for _ in range(nprod)]
    
    for b in buffers:
        for i in range(n):
            b[i] = -2
        
    procesos = [Process(target = producer, name = f'p_{i}', 
                        args=(values[i], global_sem, semaphores[i], 
                              buffers[i], i, indexes)) for i in range(nprod)]
    
    merge_process = Process(target = merge, 
                               args = (storage, global_sem, semaphores, indexes, buffers))
    
    for p in procesos:
        p.start()
    merge_process.start()
    
    for p in procesos:
        p.join()
    merge_process.join()

    
if __name__ == "__main__":
    main()
    