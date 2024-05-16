import os
import glob
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

input_nome_immagine = input(" inserisci la radice e l'estensione dei file che vuoi aprire, es *_Dk_60.fit per selezionare solo i file dark da 60sec, altrimenti premi invio e verranno selezionati tutti file con estensione .fit")
if not input_nome_immagine:
    nome_immagine='*.fit'
else:
    nome_immagine=str(input_nome_immagine)  
print (f"la scelta dei file da analizzare è riferita a: {nome_immagine}")

nome_file=str(input("inserisci il NOME del file di uscita: "))
print (f"il NOME del file di uscita è: {nome_file}")

threshold_value = int(input("inserisci il valore di SOGLIA MAX: "))
print (f"il valore di SOGLIA MAX inserito è: {threshold_value}")

input_x_min= input("inserisci il valore di X MINIMO (premi invio se vuoi il valore 0 di default)")
if not input_x_min:
    x_min=0
else:
    x_min=int(input_x_min)    
print (f"il valore di X MINIMO inserito è: {x_min}")

input_y_min= input("inserisci il valore di Y MINIMO (premi invio se vuoi il valore 0 di default)")
if not input_y_min:
    y_min=0
else:
    y_min=int(input_y_min) 
print (f"il valore di Y MINIMO inserito è: {y_min}")

input_x_max= input("inserisci il valore di X MASSIMO (premi invio se vuoi il valore 6252 di default Camera Moravian C3-26000)")
if not input_x_max:
    x_max=6252
else:
    x_max=int(input_x_max) 
print (f"il valore di X MASSIMO è: {x_max}")

input_y_max= input("inserisci il valore di Y MASSIMO (premi invio se vuoi il valore 6252 di default Camera Moravian C3-26000)")
if not input_y_max:
    y_max=4176
else:
    y_max=int(input_y_max) 

print (f"il valore di Y MASSIMO è: {y_max}")
section_min = (x_min, y_min)
section_max = (x_max,y_max)


def find_high_value_pixels(image_file, threshold):
    with fits.open(image_file) as hdul:
        image_data = hdul[0].data
        high_value_pixels = np.where(image_data > threshold)

        # Estrai le coordinate x e y dei pixel fuori soglia
        x_coords = high_value_pixels[1]
        y_coords = high_value_pixels[0]

        # Calcola i valori assoluti dei pixel fuori soglia
        high_values = np.abs(image_data[y_coords, x_coords])

        # Combinazione di coordinate e valori assoluti
        coordinates = [(x, y, value) for x, y, value in zip(x_coords, y_coords, high_values)]
        #print(coordinates)      
        
        return coordinates

def process_fits_files_in_directory(directory, threshold):
    fits_files = glob.glob(os.path.join(directory, '*.fit'))

    coordinates_by_file = {}
    abs_values_by_file = {}

    for image_file in fits_files:
        high_value_pixels = find_high_value_pixels(image_file, threshold)
        for coord in high_value_pixels:
            if coord[:2] in coordinates_by_file:
                c=(coord[:2])
                c_x=(c[0])
                c_y=(c[1])
                if x_min < c_x < x_max and y_min < c_y < y_max:
                    
                    coordinates_by_file[coord[:2]].append(image_file)
                    abs_values_by_file[coord[:2]].append(coord[2])
            else:
                coordinates_by_file[coord[:2]] = [image_file]
                abs_values_by_file[coord[:2]] = [coord[2]]
    return coordinates_by_file, abs_values_by_file

def find_duplicate_coordinates_with_files(coordinates_by_file_tuple):
    
    coordinates_by_file, abs_values_by_file = coordinates_by_file_tuple
    duplicate_coords_with_files = {}
    
    # Cicla su tutte le coordinate e i file nel dizionario coordinates_by_file
    for coord, files in coordinates_by_file.items():
        if len(files) > 1:
            # Estrai i valori assoluti dei pixel associati alla coordinata
            abs_values = abs_values_by_file[coord]
            files = [os.path.basename(path) for path in files]     

            # Aggiungi la coordinata duplicata con i file corrispondenti e i valori assoluti
            duplicate_coords_with_files[coord] = {'files': files, 'abs_values': abs_values}

    return duplicate_coords_with_files

def plot_absolute_values(coordinates_by_file, abs_values_by_file):
    plt.figure(figsize=(8, 6))
    for (x, y), abs_values in abs_values_by_file.items():
        x_coords = [x] * len(abs_values)
  
        y_coords = [y] * len(abs_values)

        plt.scatter(x_coords, y_coords, c=abs_values, cmap='viridis', alpha=0.7)
    plt.xlim(x_min,x_max)
    plt.ylim(y_min,y_max)
    plt.colorbar(label='Valore Assoluto')
    plt.xlabel('Coordinate X')
    plt.ylabel('Coordinate Y')
    plt.title('Valori Assoluti delle Coordinate')
    plt.grid(True)
    plt.savefig('/home/raniero/django/test_pixelexctract/'+nome_file+'_'+str(threshold_value)+'.png')

    plt.show()

# Directory contenente i file FITS
fits_directory = '/home/raniero/django/test_pixelexctract'

# Soglia per i valori dei pixel


# Trova le coordinate dei pixel con valori superiori alla soglia per ogni file FITS nella directory
coordinates_by_file_tuple = process_fits_files_in_directory(fits_directory, threshold_value)

# Trova le coordinate duplicate con i file corrispondenti e i valori assoluti dei pixel
duplicate_coords_with_files = find_duplicate_coordinates_with_files(coordinates_by_file_tuple)

# Stampa le coordinate duplicate con i nomi dei file e i valori assoluti dei pixel
if duplicate_coords_with_files:
    print(f"Coppie di coordinate duplicate trovate per un valore di soglia impostato pari a: {threshold_value}")
    with open('/home/raniero/django/test_pixelexctract/' + nome_file + "_" + str(threshold_value) +str(section_min)+str(section_max)+'.txt', 'w') as f:
        for coord, info in duplicate_coords_with_files.items():
            section = f"sezione di immagine valutata: {section_min},{section_max}"
            coord_str = f"Coord px over soglia: {coord}"
            files_str = f"In: {info['files']}"
            abs_values_str = f"Valori assoluti px: {info['abs_values']}"
            values=(info['abs_values'])
            median_value = np.median(values)
            median=f"Mediana: {median_value}"
            dev_std_value = ("%.3f" % (np.std(values)))
            dev_std=f"DevStd:{dev_std_value}"
            #result = f"{coord_str}, {files_str}, {abs_values_str}, {median}, {dev_std}"
            result0 = f"{coord_str}, {files_str}, {abs_values_str}, {median}, {dev_std}"
            result1 = f"{section}, {threshold_value}, {coord_str}"
            result2 = f"{files_str}"
            result3 = f"{abs_values_str}, {median}, {dev_std}"
            print(result1, file=f)
            print(result2, file=f)
            print(result3, file=f)
            print( " ", file=f)
            print(result0)

    print(f"Output scritto sul file di uscita {nome_file}_{threshold_value}_{section_min}{section_max}.txt")
else:
    print("Nessuna coppia di coordinate duplicate trovata.")

coordinates_by_file, abs_values_by_file=process_fits_files_in_directory(fits_directory, threshold_value)
plot_absolute_values(coordinates_by_file, abs_values_by_file)

print(f"     routine conclusa  ")
