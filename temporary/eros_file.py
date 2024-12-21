'''
codice generale
'''
import spectral
import cv2
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Carica i dati
data_hdr = envi.open('C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\D1_D0_ref\\D1_D0_ref.hdr')
data = np.array(data_hdr.load())

image = Image.open("C:\\Users\\erosm\\OneDrive\\Desktop\\blood_acquisiition\\d0\\d1_d0_ref\\image_d1_d0.png")

# Visualizza l'immagine
plt.imshow(image)

# Disegna una bounding box sulla zona interessata
bbox = patches.Rectangle((480, 305), 20, 20, edgecolor='r', facecolor='none')
plt.gca().add_patch(bbox)

plt.show()

# Seleziona i dati spettrali all'interno della bounding box
roi_data = data[305:305+20, 480:480+20, :]

# Calcola lo spettro medio
mean_spectrum = np.mean(roi_data, axis=(0, 1))

# Calcola la lunghezza delle bande spettrali
lunghezza_bande = len(mean_spectrum)

# Genera i ticks per l'asse x corrispondenti alle lunghezze d'onda desiderate
ticks_x = np.linspace(402, 998, lunghezza_bande)

# Plotta lo spettro medio con scala lineare sull'asse y
plt.plot(ticks_x, mean_spectrum)

# Imposta il limite inferiore dell'asse y a 0
plt.ylim(0, max(mean_spectrum))

plt.title('Spettro medio nella bounding box')
plt.xlabel('Lunghezza d\'onda (nm)')
plt.ylabel('Valore')
plt.show()
