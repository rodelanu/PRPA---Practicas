
# Práctica 1. Merge concurrente

# Realizado por: Rodrigo de la Nuez Moraleda 


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep
import random

nprod = 3  # número de procesos
n = 5      # número de productos por proceso

# Función para buscar el mínimo de una lista cuando este sea mayor o igual que 0
def find_minimum(lst):
    return min([x for x in lst if x >= 0])


# value -> Value con inicialmente valor -2, indica el número producidoç
# global_sem -> BoundedSemaphore(nprod) que indica el número de procesos que 
#                están esperando a ser consumidos tras haber producido

# semaphore -> Lock() asociado a un proceso, controla cuando ha producido
# index -> Value con la posición del proceso en el que vamos a hacer cambios
# temp -> Array de temaño nprod, guardamos los números que serán comparados en 'merge'
# terminate -> BoundedSemaphore(nprod) que indica el número de procesos que han terminado

def producer(value, global_sem, semaphore, index, temp, terminate):
    for _ in range(n):
        
        # Vemos en que proceso se está produciendo el número
        print(f"producer {current_process().name} produciendo")
        
        # Bloqueamos el semáforo del proceso actual y actualizamos el valor
        semaphore.acquire()
        value.value += random.randint(2,5)
        
        # Guardamos el valor en la posición correspondiente para comparar después
        temp[index.value] = value.value
        index.value += 1
        global_sem.acquire()
        
        # Indicamos que se ha guardado el valor en el Array 'temp'
        print (f"producer {current_process().name} almacenado {value.value}")
    
    # Al producir todos los números asginamos el valor a (-1) y bloqueamos el Lock()
    semaphore.acquire()
    terminate.acquire()
    value.value = -1
    temp[index.value] = -1
    global_sem.acquire()
    
    

# buffer -> Array de tamaño n * nprod en el que guardaremos los valores producidos
        
def merge(buffer, global_sem, semaphores, temp, index, terminate):
    
    # Creamos un índice para saber donde guardar en el almacén
    merge_index = 0
    
    while True:
        
        # Miramos el semáforo global para ver si todos los procesos han producido
        if global_sem.get_value() == 0:
            
            # Si todos los procesos han terminado salimos del bucle
            if terminate.get_value() == 0:
                break
            
            # Encontramos el mínimo y lo añadimos al buffer, y actualizamos
            #  el índice para que ese proceso sea el próximo que genere un valor
            minimo = find_minimum(temp[:])
            print("El mínimo de la lista temp es:" , minimo)
            index.value = temp[:].index(minimo)
            
            buffer[merge_index] = minimo
            merge_index += 1
            
            semaphores[index.value].release()
            print("comparación actual:", temp[:])
            print("almacen por el momento", buffer[:])
            
            # Liberamos un espacio en el semáforo global
            global_sem.release()
        
        # Si hay procesos que no han producido esperamos para que tomen el control
        else:
            sleep(0.1)
        
def main():
    buffer = Array('i', n * nprod)
    global_sem = BoundedSemaphore(nprod)
    temp = Array('i', nprod)    
    index = Value('i', 0)
    
    for i in range(nprod):
        temp[i] = -2
        
    for i in range(n * nprod):
        buffer[i] = -2
        
    values = [Value('i', -2) for _ in range(nprod)]
    semaphores = [Lock() for _ in range(nprod)]
    terminate = BoundedSemaphore(nprod)
    
    procesos = [Process(target=producer, name=f'p_{i}', args=(values[i], global_sem, semaphores[i], index, temp, terminate)) for i in range(nprod)]
    merge_process = Process(target=merge, args=(buffer, global_sem, semaphores, temp, index, terminate))
    
    for p in procesos:
        p.start()
    merge_process.start()
    
    for p in procesos:
        p.join()
    merge_process.join()
    
    print("almacen final", buffer[:])
    
if __name__ == "__main__":
    main()
