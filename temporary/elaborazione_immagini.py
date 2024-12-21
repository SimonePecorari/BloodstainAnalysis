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
for suffix in ['d', 'e', 's']:
    for i in range(1, 5):
        data_hdr = envi.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\{suffix}{i}_D0_ref\\{suffix}{i}_D0_ref.hdr')
        data = np.array(data_hdr.load())

        image_blood = Image.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\{suffix}{i}_D0_ref\\{suffix}{i}_d0.png')

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

        # Definisci le lunghezze d'onda iniziale e finale
        start_wave_length = 402 # Lunghezza d'onda iniziale misurata in [nm]
        end_wave_length = 998   # Lunghezza d'onda finale misurata in [nm]

        # Definire il range di colore per la maschera
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        # Combinare le maschere
        mask = cv2.bitwise_or(mask1, mask2)

        # Trovare i contorni della maschera
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Se i contorni sono trovati, calcolare il centroide
        if contours:
            # Assumiamo che il contorno più grande sia la macchia di sangue
            c = max(contours, key=cv2.contourArea)
            
            # Calcolare il centroide della macchia di sangue
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            # Calcolare il raggio massimo della macchia di sangue
            distances = [cv2.pointPolygonTest(c, (cX, cY), True) for point in c]
            max_radius = abs(int(max(distances)))

            # Ridurre il raggio di un offset
            offset = 10
            reduced_radius = max_radius - offset

            # Creare una maschera circolare ridotta
            mask_reduced = np.zeros_like(mask)
            cv2.circle(mask_reduced, (cX, cY), reduced_radius, 255, -1)
            
            # Creare uno sfondo bianco
            white_background = np.full_like(cropped_image, (255, 255, 255), dtype=np.uint8)

            # Applicare la maschera invertita allo sfondo
            mask_inv = cv2.bitwise_not(mask)
            mask_inv = cv2.resize(mask_inv, (cropped_image.shape[1], cropped_image.shape[0]), interpolation=cv2.INTER_NEAREST)
            img_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

            # Applicare la maschera originale all'immagine
            img_foreground = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)

            # Combinare sfondo e primo piano
            highlighted_img = cv2.add(img_background, img_foreground)
            
            # Visualizzare l'immagine originale
            plt.figure()
            plt.imshow(cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2RGB))
            plt.title('Loaded_image')
            plt.axis('off')
            plt.show()


            # Visualizzare l'immagine originale
            plt.figure()
            plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            plt.title('Cropped_image')
            plt.axis('off')
            plt.show()

            # Visualizzare l'immagine con il sangue evidenziato e la ROI circolare
            plt.figure()
            plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
            circle = patches.Circle((cX, cY), reduced_radius, edgecolor='r', facecolor='none')
            plt.gca().add_patch(circle)
            plt.title('Highlighted_Blood_Stain_with_ROI')
            plt.axis('off')
            plt.show()

            # Selezionare i dati spettrali all'interno della maschera circolare ridotta
            indices = np.where(mask_reduced == 255)
            roi_data = data[indices[0], indices[1], :]

            # Calcolare lo spettro medio
            mean_spectrum = np.mean(roi_data, axis=0)

            # Calcolare la lunghezza delle bande spettrali
            lunghezza_bande = len(mean_spectrum)

            # Generare i ticks per l'asse x corrispondenti alle lunghezze d'onda desiderate
            ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande)

            # Filtrare i dati per lunghezze d'onda fino a 800 nm
            filter_limit = 800
            filter_index = np.where(ticks_x <= filter_limit)

            # Filtrare ticks_x e mean_spectrum
            filtered_ticks_x = ticks_x[filter_index]
            filtered_mean_spectrum = mean_spectrum[filter_index]

            # Plottare lo spettro medio filtrato con scala lineare sull'asse y
            plt.plot(filtered_ticks_x, filtered_mean_spectrum)

            # Impostare il limite inferiore dell'asse y a 0
            plt.ylim(0, max(filtered_mean_spectrum))

            # Aggiunta delle rette caratteristiche
            plt.title('Spettro medio nella bounding box')
            plt.xlabel('Lunghezza d\'onda (nm)')
            plt.ylabel('Valore')
            plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
            plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
            plt.axvline(x=550, color='g', linestyle='--', label='550 nm')

            # Trovare e plottare il punto a 620 nm
            idx_620 = np.abs(filtered_ticks_x - 620).argmin()
            y_620 = filtered_mean_spectrum[idx_620]
            plt.plot(620, y_620, 'ro')

            plt.legend()
            plt.show()
        else:
            print("No contours found!")
