# Bloodstain Analysis

![CSI, Crime Investigation style scene with dominant colors blue, azure, and classic police lights, crime scene tape, no people or weapons, outdoor background like a street or neighborhood](https://github.com/user-attachments/assets/0243b436-5c5f-4ce7-80ba-639f6cbb459a)

This project focuses on the processing and analysis of data obtained from images in HDR and PNG format. A series of operations are carried out to extract useful information from the samples acquired over time, and a qualitative analysis of the blood samples is made in relation to substances such as:
- Ketchup
- Fake blood
- Alchermes

Programming language:
- [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

IDE:
- [![VS Code](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)](https://code.visualstudio.com/)


## Input Data

The input data for the code are the files:

- **HDR**: file containing the spectral data of the sample.
- **PNG**: image representing the sample at a specific time instant.

## Executed Macro-Steps

The code performs the following main steps:

1. **Automatic selection via ROI (Region of Interest)**:
   - A portion of pixels is automatically selected for analysis.
   
2. **Average calculation of spectra for daily samples**:
   - Calculation of average spectra for each substance on a daily basis.
   
3. **Average reflectance plots**:
   - Creation of graphs showing the average reflectance for each substance analysed.

4. **Comparison over time**:
   - A comparison of reflectances over time is performed to observe any changes.

5. **Variation in characteristic points and slope of the blood curve**:
   - Analysis of the variation in characteristic points and slope of the blood reflectance curve over time.


## Using Masks in Image Processing

Three-channel image processing (BGR - Blue, Green, Red) is handled using masks to isolate specific colour portions. The values of each BGR channel in the mask are interpreted as binary. The use of BGR masks offers several advantages:

- Preservation of colour information.
- Use of the original image data to apply filters or overlay elements.

Lines are included in the code that define masks for the image, applying specific limits to the red colour. The two generated masks are subsequently combined to obtain a single mask applied to the analysed image.

<p align="center">
  <img src="https://github.com/user-attachments/assets/3352f6fc-3917-4143-8e96-c5dabdad5c0d" alt="image"/>
</p>


## ROI
A Region of Interest (abbreviated as ROI) is a specific area or subset of data within an image. In vision systems, the ROI defines the boundaries of an object under examination and can be of any shape or size.

It is generally used to select specific regions of an image or scene, reducing computational complexity.
In the developed script, once the input image is loaded, a search is performed for the contours of the analysed substance trace in the image.

<p align="center">
  <img src="https://github.com/user-attachments/assets/c0043e6f-ae4d-416a-9edc-9083c3dd7bef" alt="image1"/>
</p>

The centroid that identifies the ROI is defined with the following lines of code:
<p align="center">
  <img src="https://github.com/user-attachments/assets/e0c032bf-4f44-4e34-9ad0-5e155f0ab61a" alt="image2"/>
</p>

Once this has been done, the data for the highlighted area is extracted and saved in the variable mean_spectrum, using the following code block:
<p align="center">
  <img src="https://github.com/user-attachments/assets/610ef861-b731-4f5b-ae68-e1d561a57bd1" alt="image3"/>
</p>

This methodology allows the automatic and dynamic ROI to be plotted as a function of the track under consideration, so as to guarantee an optimal amount of data for subsequent processing.

## Average spectrum calculation
The calculation of the average spectrum for blood was performed considering the logical scheme defined by the following image:
<p align="center">
  <img src="https://github.com/user-attachments/assets/c23e2bc0-70e5-4b48-87da-6da7eabf56a3" alt="image4"/>
</p>
D: subject 1
E: subject 2
S: subject 3

For substances, a similar procedure was followed, characterised by the following steps:
<p align="center">
  <img src="https://github.com/user-attachments/assets/b7a6d07e-97a6-439e-8e40-c4799b35d643" alt="image5"/>
</p>

## Analysis of the characteristic parameters of the blood spectrum
In the literature, some of the parameters that characterise the blood spectrum are the points corresponding to wavelengths 𝜆1= 540 [𝑛𝑚] and 𝜆2 =577 [𝑛𝑚], these correspond to Oxyhaemoglobin α and β, respectively. The last important parameter is the slope of the spectrum curve in the wavelength range 𝜆 = 577 ÷ 650 [𝑛𝑚].
The script evaluates the relative variation of these parameters over time, taking the value of each on the first day of measurement as a reference.
Once the average spectra of the blood for each day have been calculated, the reflectance values at the two characteristic points are plotted and these pairs of values are added to the respective lists, which will be used later for plots.

<p align="center">
  <img src="https://github.com/user-attachments/assets/3779d3c9-58c9-49dc-a9d9-fb0561529f0f" alt="image6"/>
</p>

In order to calculate the slope of the curve, it is decided to refer to the slope of the line found by linear interpolation of the data within the previously established range. In the programme, there is the linear interpolation of the line and immediately afterwards there is the calculation of its angle of inclination with respect to the x-axis, which is added in each cycle to the slope_changes list.

<p align="center">
  <img src="https://github.com/user-attachments/assets/243c3d5f-9ef6-48b5-a4a7-18079ae10b68" alt="image7"/>
</p>

Using the code just presented, explanatory plots were obtained for changes in reflectance over time for all substances analysed.
The blood-averaged plots for the four days of analysis are shown below.

<p align="center">
  <img src="https://github.com/user-attachments/assets/739891bf-c5c3-4dab-9d07-cc48f59a6d58" alt="image8"/>
</p>

The blood undergoes the following reflectance changes over time. In particular, it can be seen that the wavelengths of haemoglobin alpha and beta show an increase in reflectance, due to oxygen binding
<p align="center">
  <img src="https://github.com/user-attachments/assets/c7cda579-c343-48b0-b442-e897be07c66d" alt="image9"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/3b950d08-198f-427b-96ef-d66da2160dba" alt="image10"/>
</p>

The same analyses were carried out by evaluating the variation of blood in relation to other substances over time and the results shown below were obtained. It can be seen that blood is much more clearly affected by the reduction in red reflectance values at the wavelength of 620 [nm].
<p align="center">
  <img src="https://github.com/user-attachments/assets/60df2f59-b5c6-4d45-a1ba-7079b80c568f" alt="image11"/>
</p>

## Conclusions
Experience with hyperspectral analysis has led to the following conclusions:
-
Negative variation of the slope of the curve of the mean spectrum of blood in the range 577 - 650 [nm] due to the chromatic change of blood over time from red to black.
-
Positive variation of the characteristic points at 540 [nm] and 577 [nm] due to the Oxyhaemoglobin α and β contained in the blood which, when exposed to oxygen, continues oxidation by increasing its reflectance by about 5% as can be seen in the graph in Figure 5.3.
-
Absence of blood-like characteristic points for the other substances analysed.
-
Almost zero decay of the slope of the average spectrum curve of the other substances compared to that of the blood.
-
Initial and final noise on the spectrum curves due to thermal and voltage ripple phenomena.

