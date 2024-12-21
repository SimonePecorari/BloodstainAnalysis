import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from skimage.filters import gaussian
import cv2
import os
import spectral

#Caricare una serie di immagini utilizzando come path il percorso della cartella all'interno della quale sono presenti le immagini
image_folder = 'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\blood_images'


#Opening and loading blood_images_d
images_blood_d= []
for i in range(1,5):
    for j in range(0,4):
        image_path_d = os.path.join(image_folder, f'd{i}_d{j}.png')
        image_blood_d = cv2.imread(image_path_d)
        
        image_path_s = os.path.join(image_folder, f's{i}_d{j}.png')
        image_blood_s = cv2.imread(image_path_s)
        if (image_blood_d is not None): #or (image_blood_e is not None) or (image_blood_s is not None):
            images_blood_d.append(image_blood_d)
        else:
            print('image not found or not loaded')

for index, img in enumerate(images_blood_d):
    plt.figure()
    #plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2LUV))
    plt.title(f'image_blood_d_{index+1}')
    plt.show()


#opening and loading blood_images_e
images_blood_e= []
for i in range(1,5):
    for j in range(0,4):
        image_path_e = os.path.join(image_folder, f'e{i}_d{j}.png')
        image_blood_e = cv2.imread(image_path_e)

        if (image_blood_e is not None): #or (image_blood_e is not None) or (image_blood_s is not None):
            images_blood_e.append(image_blood_e)
        else:
            print('image not found or not loaded')

for index, img in enumerate(images_blood_e):
    plt.figure()
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(f'image_blood_e_{index+1}')
    plt.show()


#opening and loading blood_images_s
images_blood_s= []
for i in range(1,5):
    for j in range(0,4):
        image_path_s = os.path.join(image_folder, f's{i}_d{j}.png')
        image_blood_s = cv2.imread(image_path_s)
        if (image_blood_s is not None): #or (image_blood_e is not None) or (image_blood_s is not None):
            images_blood_s.append(image_blood_s)
        else:
            print('image not found or not loaded')

for index, img in enumerate(images_blood_s):
    plt.figure()
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(f'image_blood_s_{index+1}')
    plt.show()