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
# OpenCV richiede che l'immagine sia in formato BGR, di conseguenza si esegue una doppia conversione in modo da garantire l'utilizzo dell'immagine corretto
image_blood_np = np.array(image_blood)
image_blood_bgr = cv2.cvtColor(image_blood_np, cv2.COLOR_RGB2BGR)

# Ottieni le dimensioni dell'immagine
width, height = image_blood.size

x_position = width // 2   # Definizione della X del centro della ROI
y_position = height // 2  # Definizione della Y del centro della ROI
range = 20 # Estensione della ROI (complessiva)

start_wave_length = 402 # Lunghezza d'onda iniziale misurata in [nm]
end_wave_length = 998 # Lunghezza d'onda finale misurata in [nm]

#########################################################################
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

############################################################################

# 1. Visualizzazione dell'immagine originale
plt.figure()
plt.imshow(cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2RGB))
plt.title('Immagine Originale')
plt.axis('off')
plt.show()

# 2. Visualizzazione dell'immagine con il sangue evidenziato
plt.figure()
plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
plt.title('Macchia di Sangue Evidenziata')
plt.axis('off')
plt.show()

# 3. Rappresentazione della ROI sull'immagine del sangue evidenziato
plt.figure()
plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))

# Trova i contorni della maschera binaria
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Trova il contorno più grande
largest_contour = max(contours, key=cv2.contourArea)

# Trova il rettangolo di bounding box che circonda il contorno più grande
x, y, w, h = cv2.boundingRect(largest_contour)

# Estendi la ROI verso l'interno della macchia di sangue
expanded_roi_x = max(0, x + 5)  # Estendi la ROI di 5 pixel verso l'interno
expanded_roi_y = max(0, y + 5)  # Estendi la ROI di 5 pixel verso l'interno
expanded_roi_w = max(1, w - 10)  # Riduci la larghezza della ROI di 10 pixel
expanded_roi_h = max(1, h - 10)  # Riduci l'altezza della ROI di 10 pixel

# Assicura che la ROI estesa rimanga all'interno dei limiti dell'immagine
expanded_roi_x = min(expanded_roi_x, width)
expanded_roi_y = min(expanded_roi_y, height)
expanded_roi_w = min(expanded_roi_w, width - expanded_roi_x)
expanded_roi_h = min(expanded_roi_h, height - expanded_roi_y)

# Disegna il rettangolo esteso sulla figura corrente
bbox = patches.Rectangle((expanded_roi_x, expanded_roi_y), expanded_roi_w, expanded_roi_h, edgecolor='r', facecolor='none')
plt.gca().add_patch(bbox)

plt.title('Macchia di Sangue Evidenziata con ROI Estesa')
plt.axis('off')
plt.show()

# Seleziona i dati spettrali all'interno della bounding box correttamente centrata tenendo conto dei valori shiftati a destra e sinistra di un valore pari al range dimezzato
roi_data = data[y_position - (range // 2): y_position + (range // 2), x_position - (range // 2): x_position + (range // 2), :]

# 1. Applica un'operazione di thresholding sull'immagine filtrata per ottenere una maschera binaria che evidenzia solo la zona di interesse
ret, thresh = cv2.threshold(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2GRAY), 127, 255, 0)


# 2. Trova i contorni nella maschera binaria per identificare la forma della macchia di sangue
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 3. Trova il rettangolo di bounding box che circonda la macchia di sangue
x, y, w, h = cv2.boundingRect(contours[0])


# 4. Espandi il rettangolo di bounding box per includere un'area più ampia intorno alla macchia di sangue
expanded_roi_x = max(0, x - 5)  # Espande la ROI di 10 pixel a sinistra
expanded_roi_y = max(0, y - 5)  # Espande la ROI di 10 pixel verso l'alto
expanded_roi_w = min(image_blood_bgr.shape[1], w + 10)  # Espande la ROI di 10 pixel in larghezza
expanded_roi_h = min(image_blood_bgr.shape[0], h + 10)  # Espande la ROI di 10 pixel in altezza

# Definisci la ROI estesa
extended_roi = image_blood_bgr[expanded_roi_y:expanded_roi_y + expanded_roi_h, expanded_roi_x:expanded_roi_x + expanded_roi_w]


# Calcola lo spettro medio
mean_spectrum = np.mean(roi_data, axis=(0, 1))

# Calcola la lunghezza delle bande spettrali
lunghezza_bande = len(mean_spectrum)

# Genera i ticks per l'asse x corrispondenti alle lunghezze d'onda desiderate
ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande)

# Plotta lo spettro medio con scala lineare sull'asse y
plt.plot(ticks_x, mean_spectrum)

# Imposta il limite inferiore dell'asse y a 0
plt.ylim(0, max(mean_spectrum))


# Aggiunta della retta rappresentaztiva della lunghezza d'onda del rosso
line_color_red = (0,0,255)
line_thickness = 5

plt.title('Spettro medio nella bounding box')
plt.xlabel('Lunghezza d\'onda (nm)')
plt.ylabel('Valore')
plt.axvline(x=620, color = 'r', linestyle = '--', label = '620 nm') #rappresentazione retta verticale della lunghezza d'onda del rosso
plt.axvline(x=450, color = 'b', linestyle = '--', label = '450 nm') #rappresentazione retta verticale della lunghezza d'onda del blu
plt.axvline(x=550, color = 'g', linestyle = '--', label = '495 nm') #rappresentazione retta verticale della lunghezza d'onda del verde
plt.show()
