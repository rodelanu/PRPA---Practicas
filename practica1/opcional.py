
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

# Función para obtener el mínimo valor de entre los producidos
def get_minimum(lst):
    return min([x for x in lst if x >= 0])


# Función para generar los números de un proceso y guardarlos en un buffer local
def producer(valor, global_sem, local_sem, local_buffer, pos, indexes):
        
    # valor        -> Value con inicialmente valor -2 
    # global_sem   -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # local_sem    -> Lock() que controla cuando se produce un nuevo valor
    # local_buffer -> Array(n) en el que se guardan los números del proceso
    # pos          -> valor entero con la posición asociada del proceso
    # indexes      -> Array(nprod) con las posiciones de los valores a comparar
    
    for i in range(n):
        
        # Vemos en que proceso de producción está el programa
        print(f"producer {current_process().name} producing")
        
        # Bloqueamos el semáforo del proceso actual y generamos un nuevo valor
        local_sem.acquire()        
        valor.value += random.randint(2,7)
        delay()  # lo introducimos para que el orden no sea el usual
        
        # Guardamos el valor en el buffer local y bloqueamos global_sem 
        #  para llevar el conteo de los procesos que pueden ser comparados
        local_buffer[i] = valor.value        
        if local_sem.get_value() == n - indexes[pos] - 1:            
            global_sem.acquire()
            
        # Indicamos que se ha producido un nuevo valor en el proceso
        print (f"producer {current_process().name} produced {valor.value}")
        delay()  # igual que el delay anterior, además podemos pasar a merge
        

# Función para consumir los números generados y guardarlos en el almacén
def merge(storage, global_sem, semaphores, indexes, buffers):
    
    # storage    -> Array de tamaño n*nprod para guardar los productos ordenados
    # global_sem -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # semaphores -> lista de los semáforos locales, de tipo BoundedSemaphore(n)
    # indexes    -> Array(nprod) con las posiciones de los valores a comparar
    # buffers    -> lista de los buffers locales, de tipo Array(n) 
     
    merge_index = 0   # índice en el que se guardara el siguiente valor
    ended = BoundedSemaphore(nprod) # para el nº de procesos terminados
    while True:
        
        # Comprobamos si todos los procesos tienen algún valor generado
        if global_sem.get_value() == 0:
            
            # Si todos los procesos han terminado se acaba el bucle
            if ended.get_value() == 0:
                break
            
            # Obtenemos el valor mínimo de los generados
            temp = []
            for i in range(nprod):
                if indexes[i] < n:
                    temp.append(buffers[i][indexes[i]])
                else:
                    temp.append(-1)  
                    
            minimo = get_minimum(temp[:]) 
            print("temp:", temp[:]) 
            print("minimum: ", minimo)                 
            
            # Guardamos el valor mínimo y aumentamos la posición de guardado en el almacén  
            storage[merge_index] = minimo            
            print("storage: ", storage[:])
            merge_index += 1
            
            # Marcamos el espacio del almacén como consumido y avanzamos en la posición del buffer local
            pos = temp[:].index(minimo)
            buffers[pos][indexes[pos]] = -1
            indexes[pos] += 1                    
            
            # Si la siguiente posición está fuera de rango, el proceso terminó
            if indexes[pos] == n:
                ended.acquire()
            
            # Si falta por generarse un valor, liberamos un espacio en el semáforo global                
            elif buffers[pos][indexes[pos]] == -2:
                global_sem.release() 
        
        # Si algún proceso no ha generado un valor, se duerme para que lo haga
        else:
            sleep(0.1)
           

        
def main():
    storage = Array('i', n*nprod)
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
    