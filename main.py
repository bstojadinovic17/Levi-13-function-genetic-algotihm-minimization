import random
import sys
import math
import configparser as cfgp
import matplotlib.pyplot as plt

# funkcija koju treba minimizovati
# U ovom slucaju Levijeva funkcija br. 13:
# f(x, y) = sin^2(3πx) + (x − 1)^2 * (1 + sin^2(3πy) ) + (y - 1)^2 * (1 + sin^2 * 2πy)
# na intervalu -10 ≤ x , y ≤ 10
# ocekivani minimun f(1,1) = 0


# Ucitavanje potrebnih parametara iz konfiguracionog fajla
konfiguracija = cfgp.ConfigParser()
konfiguracija.read_file(open('configFile'))

repetitions = int(konfiguracija.get('algoritam', 'broj_ponavljanja'))
max_iter = int(konfiguracija.get('algoritam' , 'max_iteracija'))


pop_sizes = []
pop_sizes.append(int(konfiguracija.get('population', 'size1')))
pop_sizes.append(int(konfiguracija.get('population', 'size2')))
pop_sizes.append(int(konfiguracija.get('population', 'size3')))
scope = []
scope.append(int(konfiguracija.get('population', 'scope_min')))
scope.append(int(konfiguracija.get('population', 'scope_max')))
mut_rate = float(konfiguracija.get('population', 'mutation_rate'))
alpha = float(konfiguracija.get('population', 'alpha'))
round_value = 10


# u ovom slucaju nasu fitness funkciju predstavlja data funkcija koju je potrebno minimizovati
def funkcija_vrednosti(hromozom):

    x = float(hromozom[0])
    y = float(hromozom[1])


    return round(math.pow(math.sin(3 * math.pi * x), 2) + math.pow(x - 1, 2) * (
                1 + math.pow(math.sin(3 * math.pi * y), 2)) + math.pow(y - 1, 2) * (
                       1 + math.pow(math.sin(2 * math.pi * y), 2)), round_value)


def turnir_selekcija(fja, populacija, velicina):
    a = []
    while len(a) < velicina:
        a.append(random.choice(populacija))

    najbolji = None
    najbolji_value = None

    # nalazenje najboljeg hromozoma iz populacije koriscenjem vrednosti date funkcije
    for selektovan in a:
        selektovan_value = fja(selektovan)
        if najbolji is None or selektovan_value < najbolji_value:
            najbolji_value = selektovan_value
            najbolji = selektovan
    return najbolji

# f-ja za mutiranje - Tackasta normalna mutacija za kontinualni GA
def mutiraj(hromozom, rate):
    if random.random() < rate:
        rand = round(random.gauss(0,1), 2)

        for i in range(len(hromozom)):
            hromozom[i] = hromozom[i] + rand
    return hromozom

# BLX-alpha algoritam za ukrstanje hromozoma
def ukrsti(hrom1, hrom2):
    novi = [[] , []]
    for i in range(len(novi)):
        for j in range(2):
            d = abs(hrom1[j] - hrom2[j])
            novi[i].append(random.uniform(min(hrom1[j], hrom2[j]) - alpha * d, max(hrom1[j], hrom2[j]) + alpha * d))
    return novi


# Glavna funkcija za genetski algoritam
def genetski_algoritam(pop_velicina):
    npop_velicina = pop_velicina

    outfile = sys.stdout

    best_values_arr = []
    average_values_arr = []
    print('-----------------------------------------------------------------------')
    print('Algoritam je poceo za populaciju od {} hromozoma'.format(pop_velicina), file=outfile)
    for k in range(repetitions):
        najbolji_hromozom = None
        najbolja_vrednost_fitnesa= None
        iter = 0

        best_vals = []
        average_vals = []

        # generisanje pocetne populacije
        populacija = [[random.uniform(*scope) for i in range(2)] for j in range(pop_velicina)]

        # pravi se nova generacija sve dok broj iteracija ne premasi maksimalan broj od 500 iteracija ili dok najbolja
        # vrednost funkcije vrednosti ne bude jednak 0, sto predstavlja nas trazeni ocekivani minimum.
        while najbolja_vrednost_fitnesa != 0 and iter < max_iter:
            nova_populacija = populacija[:]

            while len(nova_populacija) < pop_velicina + npop_velicina:
                hromozom1 = turnir_selekcija(funkcija_vrednosti, populacija, 3)
                hromozom2 = turnir_selekcija(funkcija_vrednosti, populacija, 3)
                hromozom3, hromozom4 = ukrsti(hromozom1, hromozom2)
                mutiraj(hromozom3, mut_rate)
                mutiraj(hromozom4, mut_rate)
                nova_populacija.append(hromozom3)
                nova_populacija.append(hromozom4)

            # hromozomi se sortiraju po funkciji vrednosti i ostavlja se gornja polovina hromozoma za narednu generaciju
            populacija = sorted(nova_populacija, key=lambda chrom: funkcija_vrednosti(chrom))[:pop_velicina]

            # proverava se vrednost fitnesa trenutnog najboljeg hromozoma i hromozom se cuva u populaciji
            fit_value = funkcija_vrednosti(populacija[0])
            if najbolja_vrednost_fitnesa is None or najbolja_vrednost_fitnesa > fit_value:
                najbolja_vrednost_fitnesa = fit_value
                najbolji_hromozom = populacija[0]
                print('Najbolji trenutni: ' + str(najbolji_hromozom))
            iter += 1

            # izracunavanje srednje vrednosti prilagodjenosti
            generation_average_fitness = round(sum(map(funkcija_vrednosti, populacija)) / pop_velicina, 5)
            best_vals.append(fit_value)
            average_vals.append(generation_average_fitness)
            print('Srednja vrednost prilagodjenosti u trenutnoj generaciji: ' + str(generation_average_fitness))

        # Dodavanje najboljih vrednosti i prosecnih prilagodjenosti na niz zbog iscrtavanja grafika
        best_values_arr.append(best_vals)
        average_values_arr.append(average_vals)
        print('Algoritam je zavrsen u {} iteracija.'.format(iter))
        print('Najbolji hromozom: ', [round(najbolji_hromozom[0], 2), round(najbolji_hromozom[1], 2)])

    # Iscrtavanje grafika za prilagodjenosti najboljih resenja u odnosu na redni broj generacije i
    # grafika prosecne prilagodjenosti populacije u odnosu na redni broj generacije.
    # Za svaki od 3 eksperimenta bice iscrtana ova dva grafika.
    for li in best_values_arr:
        plt.plot(list(range(1, len(li) + 1)), li)
    plt.xlim(left=0.0)
    plt.ylim(bottom=0.0)
    plt.xlabel('Number of generations')
    plt.ylabel('Best fitness value')
    plt.show()

    for li in average_values_arr:
        plt.plot(list(range(1, len(li) + 1)), li)
    plt.xlim(left=0.0)
    plt.ylim(bottom=0.0)
    plt.xlabel('Number of generations')
    plt.ylabel('Average generation fitness value')
    plt.show()

# funkcija za prikaz ucitanih konfiguracija iz config fajla.
def start():
    outfile = sys.stdout
    print('\n')
    print('Ucitavanje konfiguracije...', file=outfile)
    print('\n')


    print('Parametri  za pokretanje algoritama: ')
    print('Broj pokretanja algoritma: '+ str(repetitions), file=outfile)
    print('Broj iteracija: '+ str(max_iter), file=outfile)
    print('\n')
    print('Parametri za populaciju:')
    print('Velicine populacije: ' + str(pop_sizes), file=outfile)
    print('Interval: ' + str(scope) , file=outfile)
    print('Koeficijent mutacije hromozoma: ' + str(mut_rate), file=outfile)
    print('Koeficijent alpha za BLX-alpha ukrstanje hromozoma: ' + str(alpha), file=outfile)


def main():
    start()
    for velicina in pop_sizes:
        genetski_algoritam(velicina)

if __name__ == '__main__':
    main()

