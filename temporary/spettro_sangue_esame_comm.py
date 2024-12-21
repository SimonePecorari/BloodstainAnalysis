import spectral
import cv2
import os
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from skimage.filters import gaussian
import math

spectral.settings.envi_support_nonlowercase_params = True #letters entered can be either upper or lower case (without distinction)

# function: saving plots
# this function is defined to save the various plots obtained from the simulation
def save_plot(fig, filename):
    #'bbox_inches': how the bounding box of the figure is to be handled when it is saved. 
    #'pad_inches': amount of space (in inches) to be added as a margin around the figure
    fig.savefig(filename, bbox_inches='tight', pad_inches=0.1) 
    plt.close(fig) #closing the figure to free the memory


# initialise a list to store average spectra
all_mean_spectra = {suffix: [] for suffix in ['d', 'e', 's']}
lista_spettri = []    # definition of the list
reflectance_540 = []  # List to store reflectance at 540 nm for each day
reflectance_577 = []  # List to store reflectance at 577 nm for each day
slope_changes = []    # Declaration that initialises a variable as an empty list


# loading data
for day in range(4): # '4' represents the days: 0 1 2 3
    for suffix in ['d', 'e', 's']: #the suffixes correspond to the samples respectively: d-David, e-Eros, s-Simone
        for i in range(1, 5): # 1, 2, 3, 4 represent the numbers of blood samples
            data_hdr = envi.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\ALL_D{day}\{suffix}{i}_D{day}_ref\\{suffix}{i}_D{day}_ref.hdr') #definition of path to load hdr files
            data = np.array(data_hdr.load()) #loading data from HDR file to NumPy array

            image_blood = Image.open(f'C:\\Users\\simon\\OneDrive\\Desktop\\UNIVPM MAGISTRALE\\SECONDO ANNO\\SISTEMI_MISURA_E_VISIONE\\HYPERSPECTRAL\\BLOOD_ACQUISITION\\ALL_D{day}\{suffix}{i}_D{day}_ref\\{suffix}{i}_D{day}.png') #definition of path to load png images
           
            # conversion of PIL image into a NumPy array and then into BGR
            image_blood_np = np.array(image_blood) #convertion of a PIL (Python Imaging Library) image into a NumPy array

            #this command uses the OpenCV library to convert the image from an RGB colour space to a BGR colour space
            image_blood_bgr = cv2.cvtColor(image_blood_np, cv2.COLOR_RGB2BGR) 

            # getting image size
            width, height = image_blood.size #size of the image 

            # definition of initial and final wavelengths
            start_wave_length = 402 # initial wavelength [nm]
            end_wave_length = 998   # final wavelength [nm]

            # image conversion to HSV colour space
            hsv = cv2.cvtColor(image_blood_bgr, cv2.COLOR_BGR2HSV)

            # definition of colour range for the mask
            #mask_1: 
            lower_red = np.array([0, 50, 50]) #code defined as GBR
            upper_red = np.array([10, 255, 255]) #code defined as GBR
            mask1 = cv2.inRange(hsv, lower_red, upper_red) #combining lower and upper

            #mask_2:
            lower_red = np.array([170, 50, 50]) #code defined as GBR
            upper_red = np.array([180, 255, 255]) #code defined as GBR
            mask2 = cv2.inRange(hsv, lower_red, upper_red) #combining lower and upper red

            # meshing of the masks
            mask = cv2.bitwise_or(mask1, mask2)

            # finding mask contours
            #RETR_EXTERNAL: only external bounds. 'CHAIN_APPROX_SIMPLE':it is a contour approximation method
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

            # if the contours are found, calculate the centroid
            if contours:
                # it is assumed that the largest contour is the blood stain
                c = max(contours, key=cv2.contourArea)
                
                # calculate the centroid of the blood stain
                M = cv2.moments(c) # calculation of the moments of a contour
                if M["m00"] != 0:  # condition: contour area different from zero
                    cX = int(M["m10"] / M["m00"]) # x of centroid
                    cY = int(M["m01"] / M["m00"]) # y of centroid
                else:
                    cX, cY = 0, 0

                # calculate the maximum radius of the blood stain
                # calculation of the distance between a point and the contour
                distances = [cv2.pointPolygonTest(c, (cX, cY), True) for point in c] 
                max_radius = abs(int(max(distances))) # returns the maximum distance between the centroid

                # reducing the radius of an offset
                offset = 10
                reduced_radius = max_radius - offset

                # creating a reduced circular mask
                mask_reduced = np.zeros_like(mask)
                cv2.circle(mask_reduced, (cX, cY), reduced_radius, 255, -1)
                
                # creation of a white background
                white_background = np.full_like(image_blood_bgr, (255, 255, 255))

                # applying an inverted mask to the background
                mask_inv = cv2.bitwise_not(mask)  #calculating the  inversion of the mask
                img_background = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

                # applying the original mask to the image
                img_foreground = cv2.bitwise_and(image_blood_bgr, image_blood_bgr, mask=mask) #isolated blood stain

                # combining background and foreground
                highlighted_img = cv2.add(img_background, img_foreground)

                # select spectral data within the reduced circular mask
                # binary matrix where 255 represents the area within the reduced circle where the bloodstain is present
                indices = np.where(mask_reduced == 255)
                
                # extraction of all spectral data for pixels in the reduced circular mask, preserving all band lengths
                roi_data = data[indices[0], indices[1], :] 

                # calculate the mean spectrum
                # 'roi_data' is the array of spectral data selected within the reduced circular mask
                mean_spectrum = np.mean(roi_data, axis=0) 


                # calculating spectral band lengths
                # number of elements corresponding to the length of the spectral bands for which the average reflectance is available
                lunghezza_bande = len(mean_spectrum) 

                # generate ticks for the x-axis corresponding to the desired wavelengths
                # array of equidistant values. 'ticks_x':positions of wavelength (x-axis)
                ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande) 

                # filter data for wavelengths up to 800 nm
                filter_lower_limit = 410
                filter_upper_limit = 800

                # return of index arrays where the values in ticks_x are between filter_lower_limit and filter_upper_limit
                filter_index = np.where((ticks_x >= filter_lower_limit) & (ticks_x <= filter_upper_limit)) 

                # filter ticks_x and mean_spectrum
                filtered_ticks_x = ticks_x[filter_index]

                # average spectra calculated only for wavelengths between filter_lower_limit and filter_upper_limit
                filtered_mean_spectrum = mean_spectrum[filter_index] 

                # add mean spectrum to the list
                all_mean_spectra[suffix].append(filtered_mean_spectrum)

                # plot and save the filtered mean spectrum with linear scale on the y-axis
                fig3 = plt.figure()
                plt.plot(filtered_ticks_x, filtered_mean_spectrum)

                # set the lower limit of the y-axis to 0
                plt.ylim(0, max(filtered_mean_spectrum))

                # adding characteristic lines
                plt.title(f'Average Bounding Box Spectrum {suffix}{i}')
                plt.xlabel('Wavelength (nm)')
                plt.ylabel('Reflectance')
                plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
                plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
                plt.axvline(x=550, color='g', linestyle='--', label='550 nm')

                
                # finding and plotting the point at 620 nm
                idx_620 = np.abs(filtered_ticks_x - 620).argmin()
                y_620 = filtered_mean_spectrum[idx_620]
                plt.plot(620, y_620, 'ro')

                plt.legend()
                #save_plot(fig3, f'plot_image_{suffix}{i}_spectrum_d{day}.png')
            else:
                print("No contours found!")

    # averaging of spectra for each suffix
    #calculation of the average spectra stored in all_mean_spectra for each suffix
    average_spectra = {suffix: np.mean(all_mean_spectra[suffix], axis=0) for suffix in ['d', 'e', 's']} 

    # calculate the average of the three average spectra
    # combined average spectra from the three different types of average spectra stored in the average_spectra dictionary
    overall_mean_spectrum = np.mean(list(average_spectra.values()), axis=0) 
    singular_spectrum = [filtered_ticks_x, overall_mean_spectrum]
    lista_spettri.append(singular_spectrum)

    # plot of the mean spectra combined in one image: corresponding to the three averages of the 4 samples 'd' 'e' 's'
    fig_combined = plt.figure()
    for suffix in ['d', 'e', 's']:
        plt.plot(filtered_ticks_x, average_spectra[suffix], label=f'Mean Spectrum {suffix}')


    # adding characteristic lines
    plt.title('Combined Average Spectrum')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
    plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
    plt.axvline(x=550, color='g', linestyle='--', label='550 nm')
    plt.legend()
    #save_plot(fig_combined, f'combined_average_spectrum_d{day}.png')
    
    
    # finding and plotting the point at: 540, 577 and 650 nm
    # 540 nm: haemoglobin type A
    idx_540 = np.abs(filtered_ticks_x - 540).argmin()
    y_540 = overall_mean_spectrum[idx_540]
    reflectance_540.append(y_540)  # adding reflectance at 540 nm for this day

    # 540 nm: haemoglobin type B
    idx_577 = np.abs(filtered_ticks_x - 577).argmin()
    y_577 = overall_mean_spectrum[idx_577]
    reflectance_577.append(y_577)  # adding reflectance at 577 nm for this day

    # 650 nm: blood wavelength
    idx_650 = np.abs(filtered_ticks_x - 650).argmin()
    y_650 = overall_mean_spectrum[idx_650]

    # interpolating a line between points between 577 nm and 650 nm
    interp_indices = np.where((filtered_ticks_x >= 577) & (filtered_ticks_x <= 650))
    x_values = filtered_ticks_x[interp_indices]
    y_values = overall_mean_spectrum[interp_indices]
    fit = np.polyfit(x_values, y_values, 1)  # linear interpolation
    fit_fn = np.poly1d(fit)  # interpolated line function

    # calculate the angle in degrees with respect to the horizontal
    angle_rad = math.atan(fit[0])
    angle_deg = math.degrees(angle_rad)
    slope_changes.append(angle_deg)
    
    # plot of the overall spectrum obtained by further averaging the three spectra defined above
    fig_combined_overall = plt.figure()
    point_540 = plt.plot(540, y_540, 'mo', label='540 nm')
    point_577 = plt.plot(577, y_577, 'co', label='577 nm')
    plt.plot(filtered_ticks_x, overall_mean_spectrum, label='Overall Mean Spectrum', color='k', linestyle='-')
    plt.title("Overall Mean Spectrum")
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
    plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
    plt.axvline(x=550, color='g', linestyle='--', label='550 nm')

    # find the intersection point
    intersection_x = 620  # Replace with the actual x-value at 620 nm

    # find the corresponding y-value on the overall mean spectrum
    intersection_y = np.interp(intersection_x, filtered_ticks_x, overall_mean_spectrum)

    # plot the horizontal line
    plt.axhline(y=intersection_y, color='purple', linestyle='-', label='Intersection at 620 nm')

    plt.legend()
    save_plot(fig_combined_overall, f'overall_mean_spectrum_d{day}.png')

# reflectance normalisation referred to day 1
# creation of a list of reflectance values at 540 nm normalised to the first day value, expressed as a percentage of the first day value.
reflectance_540_relative = [100 * (r / reflectance_540[0]) for r in reflectance_540]
reflectance_577_relative = [100 * (r / reflectance_577[0]) for r in reflectance_577]
slope_changes_relative = [100 * (s / slope_changes[0]) for s in slope_changes]

# plotting the change in reflectance at 540 nm over the four days
reflectance_540 = plt.figure()
plt.plot(range(1, 5), reflectance_540_relative, marker='o', linestyle='-', color='b')
plt.xlabel('Day')
plt.ylabel('Relative Reflectance at 540 nm')
plt.title('Change in Relative Reflectance at 540 nm over Four Days')
plt.xticks([1, 2, 3, 4], ['Day 1', 'Day 2', 'Day 3', 'Day 4'])
plt.grid(True)
save_plot(reflectance_540, 'reflectance_540_relative.png')
#plt.show()

# plotting the change in reflectance at 577 nm over the four days
reflectance_577 = plt.figure()
plt.plot(range(1, 5), reflectance_577_relative, marker='o', linestyle='-', color='r')
plt.xlabel('Day')
plt.ylabel('Relative Reflectance at 577 nm')
plt.title('Change in Relative Reflectance at 577 nm over Four Days')
plt.xticks([1, 2, 3, 4], ['Day 1', 'Day 2', 'Day 3', 'Day 4'])
plt.grid(True)
save_plot(reflectance_577, 'reflectance_577_relative.png')
#plt.show()

# plotting the change in slope of the interpolated line over the four days
slope_changes = plt.figure()
plt.plot(range(1, 5), slope_changes_relative, marker='o', linestyle='-', color='purple')
plt.xlabel('Day')
plt.ylabel('Relative Slope Change (%)')
plt.title('Change in Relative Slope of Interpolated Line over Four Days')
plt.xticks([1, 2, 3, 4], ['Day 1', 'Day 2', 'Day 3', 'Day 4'])
plt.grid(True)
save_plot(slope_changes, 'slope_changes_relative.png')
#plt.show()


# overlapped plots during the days (0, 1, 2, 3)
overlapped_spectra = plt.figure()
for i in range(4):
    over_x_values = lista_spettri[i][0]
    over_y_values = lista_spettri[i][1]
    plt.plot(over_x_values, over_y_values, label = f'Day_{i}')

plt.title("Time Averaged Spectra")
plt.xlabel("Wavelength [nm]")
plt.ylabel('Reflectance')
plt.legend(loc = 'lower right')
plt.axvline(x=620, color='r', linestyle='--', label='620 nm')
plt.axvline(x=450, color='b', linestyle='--', label='450 nm')
plt.axvline(x=550, color='g', linestyle='--', label='550 nm')
save_plot(overlapped_spectra,'overlapped_spectra.png')