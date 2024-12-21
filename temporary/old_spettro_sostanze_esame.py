import spectral
import cv2
import os
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from PIL import Image

spectral.settings.envi_support_nonlowercase_params = True

# function: saving plots
# this function is defined to save the various plots obtained from the simulation
def save_plot(fig, filename):
    fig.savefig(filename, bbox_inches='tight', pad_inches=0.1) #'bbox_inches': how the bounding box of the figure is to be handled when it is saved. 'pad_inches': amount of space (in inches) to be added as a margin around the figure
    plt.close(fig)

def analyze_substance(substance, file_path):
    # initialising a list to store average spectra for each day
    daily_mean_spectra = [] # the list will be filled in during the function with the average spectra calculated for each day

    # uploading data and calculating daily averages
    for day in range(4): # '4' represents the days: 0 1 2 3
        day_mean_spectra = [] # this list is used to store the average spectra calculated for each image/process within a given day

        for i in range(1, 5): # 1, 2, 3, 4 represent the numbers of blood samples
            # realising the path to the HDR file
            hdr_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}_ref.hdr')
            
            # loading hyperspectral data
            data_hdr = envi.open(hdr_path) 
            data = np.array(data_hdr.load()) # loading data from HDR file to NumPy array

            # realising the path to the file image 
            image_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}.png') # subdirectories and file names are defined according to the directory structure and the names of substances and days
            
            # conversion of image into a NumPy array and then into BGR
            image_substance = Image.open(image_path)
            image_substance_np = np.array(image_substance) # convertion of image into a NumPy array
            image_substance_bgr = cv2.cvtColor(image_substance_np, cv2.COLOR_RGB2BGR) # this command uses the OpenCV library to convert the image from an RGB colour space to a BGR colour space

            # definition of initial and final wavelengths
            start_wave_length = 402
            end_wave_length = 998

            # image conversion to HSV colour space
            hsv = cv2.cvtColor(image_substance_bgr, cv2.COLOR_BGR2HSV)

            # definition of colour range for the mask
            lower_red1 = np.array([0, 50, 50])      # code defined as GBR
            upper_red1 = np.array([15, 255, 255])   # code defined as GBR

            lower_red2 = np.array([165, 50, 50])    # code defined as GBR
            upper_red2 = np.array([180, 255, 255])  # code defined as GBR

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1) # combining lower and upper
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2) # combining lower and upper

            # meshing of the masks
            mask = cv2.bitwise_or(mask1, mask2)

            # finding mask contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # RETR_EXTERNAL: only external bounds. 'CHAIN_APPROX_SIMPLE':it is a contour approximation method

            # if the contours are found, calculate the centroid
            if contours:
                # it is assumed that the largest contour is the blood stain
                c = max(contours, key=cv2.contourArea) 

                # calculate the centroid of the blood stain
                M = cv2.moments(c) # calculation of the moments of a contour
                if M["m00"] != 0: # condition: contour area different from zero
                    cX = int(M["m10"] / M["m00"]) # x of centroid
                    cY = int(M["m01"] / M["m00"]) # y of centroid
                else:
                    cX, cY = 0, 0

                # calculate the maximum radius of the blood stain
                distances = [cv2.pointPolygonTest(c, (cX, cY), True) for point in c] # calculation of the distance between a point and the contour
                max_radius = abs(int(max(distances))) # returns the maximum distance between the centroid

                # reducing the radius of an offset
                offset = 10
                reduced_radius = max(max_radius - offset, 0)


                # creating a reduced circular mask
                if reduced_radius > 0:
                    mask_reduced = np.zeros_like(mask)
                    cv2.circle(mask_reduced, (cX, cY), reduced_radius, 255, -1)

                    # select spectral data within the reduced circular mask
                    indices = np.where(mask_reduced == 255) # finding the indices (co-ordinates) of the pixels in the mask 'mask_reduced' that are white (255)
                    roi_data = data[indices[0], indices[1], :] # extraction of all spectral data for pixels in the reduced circular mask, preserving all band lengths

                    # calculate the mean spectrum
                    mean_spectrum = np.mean(roi_data, axis=0) # 'roi_data' is the array of spectral data selected within the reduced circular mask

                    # calculating spectral band lengths
                    lunghezza_bande = len(mean_spectrum) # number of elements corresponding to the length of the spectral bands for which the average reflectance is available
                    
                    # generate ticks for the x-axis corresponding to the desired wavelengths
                    ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande) # array of equidistant values. 'ticks_x':positions of wavelength (x-axis)

                    # filter data for wavelengths up to 800 nm
                    filter_lower_limit = 402
                    filter_upper_limit = 800
                    filter_index = np.where((ticks_x >= filter_lower_limit) & (ticks_x <= filter_upper_limit)) # return of index arrays where the values in ticks_x are between filter_lower_limit and filter_upper_limit

                    # filter ticks_x and mean_spectrum
                    ticks_x = ticks_x[filter_index]
                    overall_mean_spectrum = mean_spectrum[filter_index] # subset of mean_spectrum corresponding to the average spectra calculated only for wavelengths between filter_lower_limit and filter_upper_limit

                    # add mean spectrum to the list
                    day_mean_spectra.append(overall_mean_spectrum) 


                    fig_substance = plt.figure()
                    plt.plot(ticks_x, overall_mean_spectrum)
                    plt.ylim(0, max(overall_mean_spectrum))
                    plt.title(f'Spettro medio nella bounding box {substance}{i}')
                    plt.xlabel('Lunghezza d\'onda (nm)')
                    plt.ylabel('Valore')
                    plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
                    plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
                    plt.axvline(x=550, color='g', linestyle='--', label='550 nm')


                    # finding and plotting the point at 620 nm
                    idx_620 = np.abs(ticks_x - 620).argmin()
                    y_620 = overall_mean_spectrum[idx_620]
                    plt.plot(620, y_620, 'ro')

                    intersection_y = np.interp(620, ticks_x, overall_mean_spectrum)

                    plt.axhline(y=intersection_y, color='purple', linestyle='-', label='Intersection at 620 nm')

                    # definition of the legend for the intersection line
                    x_offset = 100
                    y_offset = 0.1
                    plt.text(620 + x_offset, intersection_y + y_offset, f'({620}, {intersection_y:.2f})', color='purple', fontsize=9, ha='right')
                    plt.legend()

                    #save_plot(fig_substance, f'plot_sample_{substance}{i}_day{day}.png')
            else:
                print("No contours found!")

        if day_mean_spectra: 
            day_mean_spectrum = np.mean(day_mean_spectra, axis=0)
            daily_mean_spectra.append(day_mean_spectrum)
            fig_day_mean = plt.figure()
            plt.plot(ticks_x, day_mean_spectrum)
            plt.ylim(0, max(day_mean_spectrum))
            plt.title(f'Averaged daily spectrum {substance}_day{day}')
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Reflectance')
            plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
            plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
            plt.axvline(x=550, color='g', linestyle='--', label='550 nm')

            # finding and plotting the point at 620 nm
            idx_620 = np.abs(ticks_x - 620).argmin()
            y_620 = day_mean_spectrum[idx_620]
            plt.plot(620, y_620, 'ro')

            intersection_y = np.interp(620, ticks_x, day_mean_spectrum)

            plt.axhline(y=intersection_y, color='purple', linestyle='-', label='Intersection at 620 nm')


            # definition of the legend for the intersection line
            x_offset = 100 # x-position
            y_offset = 0.1 # y-position
            plt.text(620 + x_offset, intersection_y + y_offset, f'({620}, {intersection_y:.2f})', color='purple', fontsize=9, ha='right')
            plt.legend()
            
            save_plot(fig_day_mean, f'plot_mean_{substance}_day{day}.png')
            print(f"Plot dello spettro medio giornaliero per il giorno {day} salvato come: plot_mean_{substance}_day{day}.png")

    # check: empty list
    if daily_mean_spectra:
        fig_combined = plt.figure()

        # iteration through the list 
        for day, spectrum in enumerate(daily_mean_spectra): # function 'enumerate()' is used to obtain both index (day) and element (spectrum) of the list
            plt.plot(ticks_x, spectrum, label=f'Day {day}')

        plt.ylim(0, max([max(spectrum) for spectrum in daily_mean_spectra]))
        plt.title(f'Spettro medio giornaliero sovrapposto per {substance}')
        plt.xlabel('Lunghezza d\'onda (nm)')
        plt.ylabel('Valore')
        plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
        plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
        plt.axvline(x=550, color='g', linestyle='--', label='550 nm')
        plt.legend()

        #save_plot(fig_combined, f'plot_mean_combined_{substance}.png')
        #print(f"Plot sovrapposto degli spettri medi giornalieri salvato come: plot_mean_combined_{substance}.png")


# definition of main
def main():
    substances = ['a', 'k', 'sf'] #'substance' represents a list with 3 elements: 'alchermes' ('a'), 'ketchup' ('k'), 'sangue finto' ('sf')
    file_path = input("Inserire path cartella: ") # user's input: file path

    # validation of user's input
    while substances:
        print(f"Le sostanze in elenco sono siglate secondo:\n a: alchermes\n k: ketchup\n sf: Sangue finto\n") # explanation of substances for the user
        print(f"Sostanze rimanenti: {', '.join(substances)}")
        substance = input("Scegliere la sostanza tra le rimanenti: ") # message for the user (output)
        if substance in substances:
            print(f"Hai scelto la sostanza: {substance}") # message for the user (output)
            analyze_substance(substance, file_path)
            substances.remove(substance) # removal of the analysed substance from the overall list
        else:
            print("Input non valido. Si prega di scegliere tra le sostanze rimanenti.") # message for the user (output)

        if not substances:
            print("Tutte le sostanze sono state analizzate.") # message for the user (output)
            break

        cont = input("Vuoi continuare con un'altra sostanza? (s/n): ") # user choice on the analysis to be performed
        if cont.lower() != 's':
            break




if __name__ == "__main__":
    main()


