
"""
Problema del Puente de Ambite
Realizado por: Rodrigo de la Nuez Moraleda
"""

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 10
TIME_CARS_NORTH = 5  # intervalo de tiempo en que se genera un coche en dirección norte
TIME_CARS_SOUTH = 5  # intervalo de tiempo en que se genera un coche en dirección sur
TIME_PED = 15 # intervalor de tiempo en que se genera un nuevo peatón
TIME_IN_BRIDGE_CARS = (1, 0.5) # distribución normal del tiempo de un coche en el puente
TIME_IN_BRIDGE_PEDESTRIAN = (10, 5) # distribución normal del tiempo de un peatón en el puente

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        
        # número de cuerpos en el puente
        self.number_north = Value('i', 0)
        self.number_south = Value('i', 0)
        self.number_pedestrian = Value('i', 0)
        
        # variables de condición para los que pasan por el puente
        self.condition_north = Condition(self.mutex)
        self.condition_south = Condition(self.mutex)
        self.condition_pedestrian = Condition(self.mutex)

        # número de cuerpos esperando de cada tipo
        self.north_waiting = Value('i', 0)
        self.south_waiting = Value('i', 0)
        self.pedestrian_waiting = Value('i', 0)
     
        # variables de condición para los que están esperando
        self.ncondition = Condition(self.mutex)
        self.scondition = Condition(self.mutex)
        self.pcondition = Condition(self.mutex)
        
    
    "Reglas de Seguridad en el puente"
    def north_rule(self):
        return self.number_south.value == 0 and self.number_pedestrian.value == 0 
    
    def south_rule(self):
        return self.number_north.value == 0 and self.number_pedestrian.value == 0 
    
    def pedestrian_rule(self):
        return self.number_north.value == 0 and self.number_south.value == 0 
    
    "Reglas para la espera en el puente"
    def waiting_north(self):
        return self.pedestrian_waiting.value == 0 and self.south_waiting.value == 0 
    
    def waiting_south(self):
        return self.north_waiting.value == 0 and self.pedestrian_waiting.value == 0 
    
    def waiting_pedestrian(self):
        return self.south_waiting.value == 0 and self.north_waiting.value == 0 
    

    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        ####
        
        if direction == NORTH:
            self.ncondition.wait_for(self.waiting_north)
            self.north_waiting.value += 1
            self.condition_north.wait_for(self.north_rule)            
            self.north_waiting.value -= 1
            self.number_north.value += 1
            self.scondition.notify_all()
            
        else:
            self.scondition.wait_for(self.waiting_south)
            self.south_waiting.value += 1
            self.condition_south.wait_for(self.south_rule)
            self.south_waiting.value -= 1
            self.number_south.value += 1
            self.ncondition.notify_all()
            
        self.pcondition.notify_all()
        
        ####
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        ####
        
        if direction == NORTH:
            self.number_north.value -= 1
            self.condition_south.notify_all()
   
        else:
            self.number_south.value -= 1
            self.condition_north.notify_all()
            
        self.condition_pedestrian.notify_all()  
        
        ####
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        #### 
        
        self.pcondition.wait_for(self.waiting_pedestrian)
        self.pedestrian_waiting.value += 1
        self.condition_pedestrian.wait_for(self.pedestrian_rule)
        self.pedestrian_waiting.value -= 1
        self.number_pedestrian.value += 1
        self.ncondition.notify_all()
        self.scondition.notify_all()
        
        ####
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        #### 
        
        self.number_pedestrian.value -= 1
        self.condition_north.notify_all()
        self.condition_south.notify_all()
        
        ####
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north() -> None:
    time.sleep(abs(random.normalvariate(*TIME_IN_BRIDGE_CARS)))

def delay_car_south() -> None:
    time.sleep(abs(random.normalvariate(*TIME_IN_BRIDGE_CARS)))

def delay_pedestrian() -> None:
    time.sleep(abs(random.normalvariate(*TIME_IN_BRIDGE_PEDESTRIAN)))

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
