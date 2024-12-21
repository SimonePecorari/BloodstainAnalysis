import spectral
import cv2
import os
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from skimage.filters import gaussian

spectral.settings.envi_support_nonlowercase_params = True

# Carica i dati
data_hdr = envi.open('C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\D1_D0_ref\\D1_D0_ref.hdr')
data = np.array(data_hdr.load())

image_blood = Image.open('C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\D1_D0_ref\\d1_d0.png')

# Converti l'immagine PIL in un array NumPy e poi in BGR
image_blood_np = np.array(image_blood)
image_blood_bgr = cv2.cvtColor(image_blood_np, cv2.COLOR_RGB2BGR)

# Ottieni le dimensioni dell'immagine
width, height = image_blood.size

x_position = width // 2   # Definizione della X del centro della ROI
y_position = height // 2  # Definizione della Y del centro della ROI
range_w = 40 # Estensione della ROI (complessiva) lungo asse X
range_h = 30 # Estensione della ROI (complessiva) lungo asse Y

start_wave_length = 402 # Lunghezza d'onda iniziale misurata in [nm]
end_wave_length = 998 # Lunghezza d'onda finale misurata in [nm]

# Convertire l'immagine nello spazio colore HSV
hsv = cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2HSV)

# Definire il range di colore per la maschera
lower_red = np.array([0, 50, 50])
upper_red = np.array([10, 255, 255])
mask1 = cv2.inRange(hsv, lower_red, upper_red)

lower_red = np.array([170, 50, 50])
upper_red = np.array([180, 255, 255])
mask2 = cv2.inRange(hsv, lower_red, upper_red)

# Combinare le maschere
mask = cv2.bitwise_or(mask1, mask2)

# Invertire la maschera per ottenere lo sfondo
mask_inv = cv2.bitwise_not(mask)

# Creare uno sfondo bianco
white_background = np.full_like(image_blood_bgr, (255, 255, 255))

# Applicare la maschera invertita allo sfondo
img_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

# Applicare la maschera originale all'immagine
img_foreground = cv2.bitwise_and(image_blood_bgr, image_blood_bgr, mask=mask)

# Combinare sfondo e primo piano
highlighted_img = cv2.add(img_background, img_foreground)

# Visualizzazione dell'immagine originale
plt.figure()
plt.imshow(cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2RGB))
plt.title('Loaded_image')
plt.axis('off')
plt.show()

# Visualizzazione dell'immagine con il sangue evidenziato
plt.figure()
plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
plt.title('Highlighted_Blood_Stain')
plt.axis('off')
plt.show()

# Rappresentazione della ROI sull'immagine del sangue evidenziato
plt.figure()
plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
bbox = patches.Rectangle((x_position - range_w // 2, y_position - range_h // 2), range_w, range_h, edgecolor='r', facecolor='none')
plt.gca().add_patch(bbox)
plt.title('Highlighted_Blood_Stain_with_ROI')
plt.axis('off')
plt.show()

# Seleziona i dati spettrali all'interno della bounding box correttamente centrata tenendo conto dei valori shiftati a destra e sinistra di un valore pari al range dimezzato
roi_data = data[y_position - (range_h // 2): y_position + (range_h // 2), x_position - (range_w // 2): x_position + (range_w // 2), :]

# Calcola lo spettro medio
mean_spectrum = np.mean(roi_data, axis=(0, 1))

# Calcola la lunghezza delle bande spettrali
lunghezza_bande = len(mean_spectrum)

# Genera i ticks per l'asse x corrispondenti alle lunghezze d'onda desiderate
ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande)

# Filtra i dati per lunghezze d'onda fino a 800 nm
filter_limit = 800
filter_index = np.where(ticks_x <= filter_limit)

# Filtra ticks_x e mean_spectrum
filtered_ticks_x = ticks_x[filter_index]
filtered_mean_spectrum = mean_spectrum[filter_index]

# Plotta lo spettro medio filtrato con scala lineare sull'asse y
plt.plot(filtered_ticks_x, filtered_mean_spectrum)

# Imposta il limite inferiore dell'asse y a 0
plt.ylim(0, max(filtered_mean_spectrum))

# Aggiunta della rette caratteristiche
plt.title('Spettro medio nella bounding box')
plt.xlabel('Lunghezza d\'onda (nm)')
plt.ylabel('Valore')
plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
plt.axvline(x=550, color='g', linestyle='--', label='550 nm')

# Trova e plota il punto a 620 nm
idx_620 = np.abs(filtered_ticks_x - 620).argmin()
y_620 = filtered_mean_spectrum[idx_620]
plt.plot(620, y_620, 'ro')

plt.legend()
plt.show()
