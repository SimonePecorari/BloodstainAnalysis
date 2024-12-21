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

    # 'bbox_inches': how the bounding box of the figure is to be handled when it is saved. 
    # 'pad_inches': amount of space (in inches) to be added as a margin around the figure
    fig.savefig(filename, bbox_inches='tight', pad_inches=0.1) 
    plt.close(fig)

def analyze_substance(substance, file_path):
    # initialising a list to store average spectra for each day
    daily_mean_spectra = [] # the list will be filled in during the function with the average spectra calculated for each day

    suffixes = ['d', 'e', 's'] if substance == 's' else ['d']

    # uploading data and calculating daily averages
    for day in range(4): # '4' represents the days: 0 1 2 3
        day_mean_spectra = [] # this list is used to store the average spectra calculated for each image/process within a given day

        for suffix in suffixes:
            for i in range(1, 5): # 1, 2, 3, 4 represent the numbers of blood samples
                # realising the path to the HDR file
                hdr_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}_ref.hdr')
                
                # loading hyperspectral data
                data_hdr = envi.open(hdr_path)
                data = np.array(data_hdr.load())

                # realising the path to the file image 
                image_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}.png')
                
                # conversion of image into a NumPy array and then into BGR
                image_substance = Image.open(image_path)
                image_substance_np = np.array(image_substance)
                image_substance_bgr = cv2.cvtColor(image_substance_np, cv2.COLOR_RGB2BGR)

                # definition of initial and final wavelengths
                start_wave_length = 402
                end_wave_length = 998

                # image conversion to HSV colour space
                hsv = cv2.cvtColor(image_substance_bgr, cv2.COLOR_BGR2HSV)
                
                # definition of colour range for the mask
                lower_red1 = np.array([0, 50, 50])
                upper_red1 = np.array([15, 255, 255])

                lower_red2 = np.array([165, 50, 50])
                upper_red2 = np.array([180, 255, 255])

                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                
                # meshing of the masks
                mask = cv2.bitwise_or(mask1, mask2)
                
                # finding mask contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # if the contours are found, calculate the centroid
                if contours:
                    c = max(contours, key=cv2.contourArea)
                    M = cv2.moments(c) # calculation of the moments of a contour
                    if M["m00"] != 0: # condition: contour area different from zero
                        cX = int(M["m10"] / M["m00"]) # x of centroid
                        cY = int(M["m01"] / M["m00"]) # y of centroid
                    else:
                        cX, cY = 0, 0

                    # calculate the maximum radius of the blood stain
                    distances = [cv2.pointPolygonTest(c, (cX, cY), True) for point in c]
                    max_radius = abs(int(max(distances)))
                    
                    # reducing the radius of an offset
                    offset = 10
                    reduced_radius = max(max_radius - offset, 0)

                    # creating a reduced circular mask
                    if reduced_radius > 0:
                        mask_reduced = np.zeros_like(mask)
                        cv2.circle(mask_reduced, (cX, cY), reduced_radius, 255, -1)
                        
                        # select spectral data within the reduced circular mask
                        # finding the indices (co-ordinates) of the pixels in the mask 'mask_reduced' that are white (255)
                        indices = np.where(mask_reduced == 255) 
                        # extraction of all spectral data for pixels in the reduced circular mask, preserving all band lengths
                        roi_data = data[indices[0], indices[1], :] 
                        
                        # calculate the mean spectrum
                        mean_spectrum = np.mean(roi_data, axis=0)

                        # calculating spectral band lengths
                        lunghezza_bande = len(mean_spectrum)
                        
                        # generate ticks for the x-axis corresponding to the desired wavelengths
                        ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande)

                        # filter data for wavelengths up to 800 nm
                        filter_lower_limit = 410
                        filter_upper_limit = 800
                        filter_index = np.where((ticks_x >= filter_lower_limit) & (ticks_x <= filter_upper_limit))
                        
                        # filter ticks_x and mean_spectrum
                        ticks_x = ticks_x[filter_index]
                        overall_mean_spectrum = mean_spectrum[filter_index]

                        # add mean spectrum to the list
                        day_mean_spectra.append(overall_mean_spectrum)
                else:
                    print("No contours found!")

        # check: empty list
        if day_mean_spectra:
            day_mean_spectrum = np.mean(day_mean_spectra, axis=0)
            daily_mean_spectra.append(day_mean_spectrum)
    
    return daily_mean_spectra, ticks_x


# definition of main
def main():
    #'substance' represents a list with 3 elements: 'alchermes' ('a'), 'ketchup' ('k'), 'sangue finto' ('sf'), 'sangue' ('s')
    substances = ['a', 'k', 'sf', 's'] 
    file_path = input("Inserire path cartella: ") # user's input: file path

    all_daily_mean_spectra = []
    for day in range(4):
        all_daily_mean_spectra.append({})

    # validation of user's input
    while substances:
        # explanation of substances for the user
        print(f"Le sostanze in elenco sono siglate secondo:\n a: alchermes\n k: ketchup\n sf: Sangue finto\n s: Sangue\n") 
        print(f"Sostanze rimanenti: {', '.join(substances)}")
        substance = input("Scegliere la sostanza tra le rimanenti: ") # message for the user (output)
        
        if substance in substances:
            print(f"Hai scelto la sostanza: {substance}") # message for the user (output)
            daily_mean_spectra, ticks_x = analyze_substance(substance, file_path)
            
            for day in range(4):
                all_daily_mean_spectra[day][substance] = daily_mean_spectra[day]
            substances.remove(substance) # removal of the analysed substance from the overall list
        
        else:
            print("Input non valido. Si prega di scegliere tra le sostanze rimanenti.") # message for the user (output)

        if not substances:
            print("Tutte le sostanze sono state analizzate.") # message for the user (output)
            break

        cont = input("Vuoi continuare con un'altra sostanza? (s/n): ") # user choice on the analysis to be performed
        
        if cont.lower() != 's':
            break

    # averaged combined spectra
    for day in range(4):
        
        if all_daily_mean_spectra[day]:
            fig_combined = plt.figure()
            
            for substance, spectrum in all_daily_mean_spectra[day].items():
                plt.plot(ticks_x, spectrum, label=substance)
            plt.ylim(0, max([max(spectrum) for spectrum in all_daily_mean_spectra[day].values()]))
            plt.title(f'Overlapping average daily spectrum for all substances - Day {day}')
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Reflectance')
            plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
            plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
            plt.axvline(x=550, color='g', linestyle='--', label='550 nm')
            plt.legend()

            save_plot(fig_combined, f'plot_mean_combined_day{day}.png')
            print(f"Plot sovrapposto degli spettri medi giornalieri salvato come: plot_mean_combined_day{day}.png")

if __name__ == "__main__":
    main()
