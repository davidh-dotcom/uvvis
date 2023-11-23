import sys
import matplotlib.pyplot as plt
import numpy as np

def parse_orca_output(file_path):
    wavelengths = []
    fosc_values = []
    parsing_data = False

    with open(file_path, 'r') as file:
        for line in file:
            if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
                parsing_data = True
                next(file)  # Skip the header line
                continue
            elif not parsing_data:
                continue

            if line.strip() == "":
                break  # Stop parsing when an empty line is encountered

            if "Wavelength" in line:
                continue  # Skip the header line

            values = line.split()
            if len(values) < 4:  # Check for enough columns
                continue

            wavelength_str = values[2]
            fosc_str = values[3]

            if 'au**2' in wavelength_str or 'au**2' in fosc_str:
                continue  # Skip lines with non-numeric values

            wavelengths.append(float(wavelength_str))
            fosc_values.append(float(fosc_str))

    if not wavelengths or not fosc_values:
        print("Error: Absorption spectrum data not found in the ORCA output.")
        return None

    return wavelengths, fosc_values

def gaussian_broadening(x, y, sigma):
    gE = []
    for xi in x:
        tot = 0
        for xj, yj in zip(x, y):
            tot += yj * np.exp(-(((xj - xi) / sigma) ** 2))
            #tot += yj * np.exp(-np.log(2)*(((xj - xi) / sigma) ** 2))
        gE.append(tot)
    return gE

def plot_uv_vis_spectrum(wavelengths, fosc_values, output_file, fwhm=60):
    # Increase the number of points for a smoother overlay
    x_values = np.linspace(min(wavelengths), max(wavelengths), 70)

    plt.figure(figsize=(10, 6))

    # Original data
    plt.bar(wavelengths, fosc_values, color='black', alpha=0.7, width=2, align='edge', label='Original Data')

    # Apply Gaussian broadening
    sigma = fwhm / (2. * np.sqrt(2. * np.log(2)))
    fosc_convolved = gaussian_broadening(wavelengths, fosc_values, sigma)

    # Plot a smoother overlay
    gb = gaussian_broadening(x_values, fosc_values, sigma)
    plt.plot(x_values, gb, color='grey')

    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Oscillator Strength (fosc)')
    #plt.title('Oscillator Strength vs Wavelength')

    #plt.gca().invert_xaxis()  # Invert x-axis for energy vs wavelength
    #plt.legend()

    plt.savefig(output_file)
    print(f"Figure saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 script.py <path_to_orca_output_file> <output_image_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    output_file = sys.argv[2]
    spectrum_data = parse_orca_output(file_path)

    if spectrum_data:
        wavelengths, fosc_values = spectrum_data
        plot_uv_vis_spectrum(wavelengths, fosc_values, output_file)
