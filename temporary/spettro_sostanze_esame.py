import spectral
import cv2
import os
import numpy as np
import spectral.io.envi as envi
import matplotlib.pyplot as plt
from PIL import Image

spectral.settings.envi_support_nonlowercase_params = True

# Funzione per salvare i plot
def save_plot(fig, filename):
    fig.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

def analyze_substance(substance, file_path):
    daily_mean_spectra = []

    suffixes = ['d', 'e', 's'] if substance == 's' else ['d']

    for day in range(4):
        day_mean_spectra = []

        for suffix in suffixes:
            for i in range(1, 5):
                hdr_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}_ref.hdr')
                data_hdr = envi.open(hdr_path)
                data = np.array(data_hdr.load())
                image_path = os.path.join(file_path, f'all_d{day}', f'{substance}{i}_d{day}_ref', f'{substance}{i}_d{day}.png')
                image_substance = Image.open(image_path)
                image_substance_np = np.array(image_substance)
                image_substance_bgr = cv2.cvtColor(image_substance_np, cv2.COLOR_RGB2BGR)

                start_wave_length = 402
                end_wave_length = 998

                hsv = cv2.cvtColor(image_substance_bgr, cv2.COLOR_BGR2HSV)
                lower_red1 = np.array([0, 50, 50])
                upper_red1 = np.array([15, 255, 255])
                lower_red2 = np.array([165, 50, 50])
                upper_red2 = np.array([180, 255, 255])
                mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = cv2.bitwise_or(mask1, mask2)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    c = max(contours, key=cv2.contourArea)
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = 0, 0

                    distances = [cv2.pointPolygonTest(c, (cX, cY), True) for point in c]
                    max_radius = abs(int(max(distances)))
                    offset = 10
                    reduced_radius = max(max_radius - offset, 0)

                    if reduced_radius > 0:
                        mask_reduced = np.zeros_like(mask)
                        cv2.circle(mask_reduced, (cX, cY), reduced_radius, 255, -1)
                        indices = np.where(mask_reduced == 255)
                        roi_data = data[indices[0], indices[1], :]
                        mean_spectrum = np.mean(roi_data, axis=0)

                        lunghezza_bande = len(mean_spectrum)
                        ticks_x = np.linspace(start_wave_length, end_wave_length, lunghezza_bande)

                        filter_lower_limit = 410
                        filter_upper_limit = 800
                        filter_index = np.where((ticks_x >= filter_lower_limit) & (ticks_x <= filter_upper_limit))
                        ticks_x = ticks_x[filter_index]
                        overall_mean_spectrum = mean_spectrum[filter_index]

                        day_mean_spectra.append(overall_mean_spectrum)
                else:
                    print("No contours found!")

        if day_mean_spectra:
            day_mean_spectrum = np.mean(day_mean_spectra, axis=0)
            daily_mean_spectra.append(day_mean_spectrum)
    
    return daily_mean_spectra, ticks_x

def main():
    substances = ['a', 'k', 'sf', 's']
    file_path = input("Inserire path cartella: ")

    all_daily_mean_spectra = []
    for day in range(4):
        all_daily_mean_spectra.append({})

    while substances:
        print(f"Le sostanze in elenco sono siglate secondo:\n a: alchermes\n k: ketchup\n sf: Sangue finto\n s: Sangue\n")
        print(f"Sostanze rimanenti: {', '.join(substances)}")
        substance = input("Scegliere la sostanza tra le rimanenti: ")
        if substance in substances:
            print(f"Hai scelto la sostanza: {substance}")
            daily_mean_spectra, ticks_x = analyze_substance(substance, file_path)
            for day in range(4):
                all_daily_mean_spectra[day][substance] = daily_mean_spectra[day]
            substances.remove(substance)
        else:
            print("Input non valido. Si prega di scegliere tra le sostanze rimanenti.")

        if not substances:
            print("Tutte le sostanze sono state analizzate.")
            break

        cont = input("Vuoi continuare con un'altra sostanza? (s/n): ")
        if cont.lower() != 's':
            break

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
