import spectral
import cv2
import os
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from PIL import Image

spectral.settings.envi_support_nonlowercase_params = True

# Funzione per ritagliare l'immagine e processarla
def process_image(i):
    # Carica i dati
    # data_hdr = envi.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\D{i}_D3_ref\\D{i}_D0_ref.hdr')
    # data = np.array(data_hdr.load())
    image_blood = Image.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\images_d3\\s{i}_d3.png')

    # Converti l'immagine PIL in un array NumPy e poi in BGR
    image_blood_np = np.array(image_blood)
    image_blood_bgr = cv2.cvtColor(image_blood_np, cv2.COLOR_RGB2BGR)

    # Definisci i limiti per il ritaglio dell'immagine
    top = 200
    bottom = image_blood_bgr.shape[0] - 150
    left = 250
    right = image_blood_bgr.shape[1] - 200

    # Ritaglia l'immagine
    cropped_image = image_blood_bgr[top:bottom, left:right]

    # Convertire l'immagine nello spazio colore HSV
    hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    # Definire il range di colore per la maschera (rosso)
    lower_red1 = np.array([0, 40, 40]) #prima era [0, 50, 50]
    upper_red1 = np.array([15, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([110, 20, 20] ) #prima era [110, 30, 30] >>> [110, 20, 30] 
    upper_red2 = np.array([180, 190, 190]) #prima era [180, 255, 255] >>> [180, 220, 220]
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combinare le maschere per coprire l'intero intervallo di rosso
    mask = cv2.bitwise_or(mask1, mask2)

    # Invertire la maschera per ottenere lo sfondo
    mask_inv = cv2.bitwise_not(mask)

    # Creare uno sfondo bianco
    white_background = np.full_like(cropped_image, (255, 255, 255))

    # Applicare la maschera invertita allo sfondo
    img_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

    # Applicare la maschera originale all'immagine
    img_foreground = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)

    # Combinare sfondo e primo piano
    highlighted_img = cv2.add(img_background, img_foreground)


    # Definizione dei contorni
    #vengono individuati i contorni nella maschera binaria
    #cv2.RETR_EXTERNAL recupera SOLO i contorni esterni
    #cv2.CHAIN_APPROX_SIMPLE comprime i segmenti orizzontali, verticali e diagonali
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    

    # # Disegno dei contorni (verde) con spesso pari a 2 pixel
    # #contourIdx: L'indice del contorno da disegnare. Se è -1, tutti i contorni nella lista contours verranno disegnati.
    # #2 rappresenta lo spessore misurato in pixel
    cv2.drawContours(highlighted_img, contours, -1, (0, 255, 0), 1)
    
    
    # Visualizzazione dell'immagine originale 
    plt.figure()
    plt.imshow(cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2RGB))
    plt.title(f'Image_blood D{i}')
    plt.axis('off')
    plt.show()

    # Visualizzazione dell'immagine originale ritagliata
    plt.figure()
    plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    plt.title(f'Cropped_Image D{i}')
    plt.axis('off')
    plt.show()

    # Visualizzazione dell'immagine con lo sfondo bianco e il sangue evidenziato
    plt.figure()
    plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
    plt.title(f'Highlighted Blood Stain D{i}')
    plt.axis('off')
    plt.show()

# Loop through all images
for i in range(1, 5):
    process_image(i)
