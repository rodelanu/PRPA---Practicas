
# Realizado por: Rodrigo de la Nuez Moraleda

"""

Dados nprod procesos que producen números no negativos de forma creciente.
Cuando un proceso acaba de producir, produce un -1.
Cada proceso almacena el valor almacenado en una variable compartida consumidor,
 un -2 indica que el almacén está vacío.
 
Hay un proceso merge que debe tomar los números y almacenarlos de forma creciente
 en una única lista (o array). El proceso debe esparar a que los productores
 tengan listo un elemento e introducir el menor de ellos.
 
Se debe crear listas de semáforos. Cada productor solo maneja sus semáforos para
 sus datos. El proceso merge debe manejar todos los semáforors.

"""


from multiprocessing import Process
from multiprocessing import Semaphore, BoundedSemaphore, Lock
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


# Función para generar los números de un proceso de producción
def producer(valor, empty, non_empty, pos, temp, ended):
    
    # valor      -> Value con inicialmente valor -2 
    # global_sem -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # local_sem  -> Lock() que controla cuando se produce un nuevo valor
    # pos        -> valor entero con la posición asociada del proceso
    # temp       -> Array de tamaño el número de procesos para la comparación
    # ended      -> BoundedSemaphore(nprod) para el nº de procesos terminados
    
    for _ in range(n):
        
        # Vemos en que proceso de producción está el programa
        print(f"producer {current_process().name} producing")
        
        # Bloqueamos el semáforo del proceso actual y actualizamos el valor
        empty.acquire()
        valor.value += random.randint(2,7)
        delay()  # lo introducimos para que el orden no sea el usual
        
        # Guardamos el valor en la posición correspondiente para comparar luego
        temp[pos] = valor.value
        non_empty.release()
        print(f"producer {current_process().name} produced {valor.value}")
        delay()  # igual que el delay anterior, además podemos pasar a merge
    
    # Al producir todos los números asignamos el valor a -1 y bloqueamos ended
    empty.acquire()
    ended.acquire() 
    valor.value = -1   
    temp[pos] = valor.value    
    non_empty.release()   
    

# Función para consumir los números generados y guardarlos en el almacén        
def merge(storage, empty_semaphores, non_empty_semaphores, temp, ended):
    
    # storage    -> Array de tamaño n*nprod para guardar los productos ordenados
    # global_sem -> BoundedSemaphore(nprod) para el nº de procesos ejecutados
    # semaphores -> lista de los semáforos locales, de tipo Lock()
    # temp       -> Array de tamaño el número de procesos para la comparación
    # ended      -> BoundedSemaphore(nprod) para el nº de procesos terminados
    
    merge_index = 0  # índice en el que se guardara el siguiente valor    
    lst = range(nprod)
    
    while True:
        
        for i in lst:
            non_empty_semaphores[i].acquire()
            
        # Si todos los procesos han terminado se acaba el bucle
        if ended.get_value() == 0:
            break
            
        # Obtenemos el valor mínimo de los generados
        minimo = get_minimum(temp[:])
        print("temp: ", temp[:])
        print("minimum: ", minimo)
            
        # Guardamos el valor mínimo y aumentamos la posición de guardado                   
        storage[merge_index] = minimo
        print("storage: ", storage[:])
        merge_index += 1
            
        pos = temp[:].index(minimo) 
        empty_semaphores[pos].release()  # liberamos el proceso del mínimo valor
        lst = [pos]

        
def main():
    storage = Array('i', n*nprod)
    temp = Array('i', nprod)    
    
    for i in range(nprod):
        temp[i] = -2
        
    for i in range(n * nprod):
        storage[i] = -2
        
    values = [Value('i', -2) for _ in range(nprod)]
    empty_semaphores = [Lock() for _ in range(nprod)]
    non_empty_semaphores = [Semaphore(0) for _ in range(nprod)]
    ended = BoundedSemaphore(nprod)
    
    procesos = [Process(target = producer, name = f'p_{i}', 
                        args = (values[i], empty_semaphores[i], non_empty_semaphores[i],
                              i, temp, ended)) for i in range(nprod)]
    
    merge_process = Process(target = merge, 
                               args = (storage, empty_semaphores, non_empty_semaphores, temp, ended))
    
    for p in procesos:
        p.start()
    merge_process.start()
    
    for p in procesos:
        p.join()
    merge_process.join()
    
    
if __name__ == "__main__":
    main()
       