import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from skimage.filters import gaussian
import cv2
import os
import spectral

spectral.settings.envi_support_nonlowercase_params = True

blood_d0 = envi.open('C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\D0\\D1_D0_ref\\D1_D0_ref.hdr')

blood_data = np.array(blood_d0.load())



#Caricare una serie di immagini utilizzando come path il percorso della cartella all'interno della quale sono presenti le immagini
image_folder = 'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\temporary'

# #caricamento delle immagini a singolo index
# images = []
# #il for in range considera valori che vanno da 1 (compreso) a 4
# for i in range(1,5): 
#     image_path = os.path.join(image_folder, f'{i}.jpeg') #in maniera dinamica attraverso f-string vengono caricate le immagini presenti nel folder 'temporary' che hanno come nome: 1, 2, 3, 4
#     image = cv2.imread(image_path) #caricamento dell'immagine
    
#     if image is not None: #se l'immagine è stata caricata correttamente viene aggiunta alla lista 
#         images.append(image)
#     else:
#         print(f"Image {i} not found or not loaded")


# for idx, img in enumerate(images):
#     plt.figure()
#     plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) 
#     plt.title(f'image {idx+1}')
#     plt.show()


#Caricamento immagini con più indici i e j (ok per implementazione delle immagini iperspettrali)
images_wolf = []
for i in range(0,4):
    for j in range(0,4):
        image_path = os.path.join(image_folder, f'wolf_{i}_{j}.jpeg') #in maniera dinamica attraverso f-string vengono caricate le immagini presenti nel folder 'temporary' che hanno come nome: 1, 2, 3, 4
        image_wolf = cv2.imread(image_path)
        if image_wolf is not None:
            images_wolf.append(image_wolf)
            #plt.imshow(cv2.cvtColor(image_wolf, cv2.COLOR_BGR2GRAY)) 

        else:
            print(f"Image wolf_{i}_{j} not found or not loaded")

line_color_1 = (0,255,0)
line_thickness = 5

line_color_2 = (0,165,255)
line_angular_thickness = 5



for index, img in enumerate(images_wolf):
    #dimensioni dell'immagine
    height, width = img.shape[:2]

    #posizionamento della linea al centro dell'immagine (verticale)
    x_position = width // 2
    y_position = height // 2

    circle_centre = (x_position, y_position)
    radius = 100
    circle_color = (0, 0, 255) #colore cerchio centrale
    circle_thickness = 7

    origin = (0,0)

    #disegno della linea con cv2
    cv2.circle(img, circle_centre, radius, circle_color, circle_thickness)
    cv2.line(img, (x_position, 0), (x_position, height), line_color_1, line_thickness)
    cv2.line(img, (0, y_position), (width, y_position), line_color_2, line_thickness)

    plt.figure()
    #plt.imshow(img, cmap = 'gray') 
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) 
    plt.title(f'image_wolf_{index+1}')
    plt.show()
    







