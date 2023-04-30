
# Realizado por: Rodrigo de la Nuez Moraleda

from pyspark import SparkContext, SparkConf 
import sys, string
from time import sleep

# Función para dividir una línea por palabras evitando signos de puntuación
def word_split(line):
    for c in string.punctuation+"¿¡«»":
        line = line.replace(c,' ')
        line = line.lower()
    return len(line.split())

# Función principal para contar el número de palabras en un archivo
def main(infile):
    conf = SparkConf().setAppName("FileWordCount")
    sc = SparkContext(conf = conf)
    sc.setLogLevel("ERROR")
    lines = sc.textFile(infile)
    words_rdd = lines.map(word_split)
    with open("out_" + infile, 'w') as o:
        o.write(infile + ' words_count = ' + str(words_rdd.sum()))
    sleep(20) # para poder ver su ejecución desde http://192.168.135.1:4040/
            
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 {0} <file>".format(sys.argv[0]))
    else:
        main(sys.argv[1])