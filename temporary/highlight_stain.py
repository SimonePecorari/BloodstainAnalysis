import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from skimage.filters import gaussian
import cv2
import os
import spectral

# Caricare una serie di immagini utilizzando come path il percorso della cartella all'interno della quale sono presenti le immagini
image_folder = 'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\blood_images'

# Opening and loading blood_images_d
images_blood_d = []
image_path_d = os.path.join(image_folder, 'd1_d0.png')
image_blood_d = cv2.imread(image_path_d)

if image_blood_d is not None:
    images_blood_d.append(image_blood_d)
else:
    print('image not found or not loaded')

# Convertire l'immagine nello spazio colore HSV
hsv = cv2.cvtColor(image_blood_d, cv2.COLOR_BGR2HSV)

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


#######################################################################################
# # Creare uno sfondo blu
# blue_background = np.full_like(image_blood_d, (255, 0, 0))

# Creare uno sfondo bianco
white_background = np.full_like(image_blood_d, (255, 255, 255))

# # Applicare la maschera invertita allo sfondo
# img_background = cv2.bitwise_and(blue_background, blue_background, mask=mask_inv)

# Applicare la maschera invertita allo sfondo
img_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

# Applicare la maschera originale all'immagine
img_foreground = cv2.bitwise_and(image_blood_d, image_blood_d, mask=mask)


########################################################################################

# Combinare sfondo e primo piano
highlighted_img = cv2.add(img_background, img_foreground)

# Convertire le aree della macchia di sangue in giallo fluo
# highlighted_img[np.where((highlighted_img == [0, 0, 255]).all(axis=2))] = [255, 255, 0]

# Visualizzare l'immagine originale e quella con la macchia di sangue evidenziata
for index, img in enumerate(images_blood_d):
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title('Immagine Originale')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(highlighted_img, cv2.COLOR_BGR2RGB))
    plt.title('Macchia di Sangue Evidenziata')
    plt.axis('off')

    plt.show()
