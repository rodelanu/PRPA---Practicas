
# Realizado por: Rodrigo de la Nuez Moraleda

from pyspark import SparkContext, SparkConf 
import random, sys
from time import sleep

# Porcentaje de líneas a extraer (entre 0 y 1)
percentage = 0.5

# Función que devuelve True o False si se debe mantener o no una línea
def keep_line(line):
    return random.random() < percentage

# Función principal para extraer un porcentaje de líneas de un archivo
def main(infile, outfile):
    conf = SparkConf().setAppName("RandomLineExtraction")
    sc = SparkContext(conf = conf)
    sc.setLogLevel("ERROR")
    rdd = sc.textFile(infile).filter(keep_line)
    with open(outfile, 'w') as o:
        for line in rdd.collect():
            o.write(line + "\n")
    sleep(20) # para poder ver su ejecución desde http://192.168.135.1:4040/
            
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python3 {0} <file>".format(sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2])