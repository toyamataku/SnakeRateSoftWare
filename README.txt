# SnakeRateSoftWare

This project employs [Cython](https://cython.org/) to compile part of its functionality into binary (`.pyd`) files for performance and code confidentiality.  
**The uncompiled `.pyx` source code is not disclosed**, and only the resulting binaries are provided in this repository.

---

## Overview

This project provides the following features:

- **Livewire Segmentation**: `my_process_image_livewire.cp312-win_amd64.pyd`  
- **Multiplier Settings**: `my_select_multipliers.cp312-win_amd64.pyd`  
- **Image Analysis (3-code processing, etc.)**: `my_process_image_3code.cp312-win_amd64.pyd`  
- **Circular Intersection Analysis**: `my_process_circle_intersections.cp312-win_amd64.pyd`  

These files are compiled for **Python 3.12 on Windows 64-bit**.

---

## How to Use

1. **Setup**  
   - Make sure you have **Python 3.12 (Windows 64-bit)** installed.
   - Install the required packages by running:
     ```bash
     pip install -r requirements.txt
     ```
   - The `requirements.txt` looks like this:
     ```txt
     Cython==3.0.11
     numpy==2.1.1
     pandas==2.2.3
     opencv-python==4.10.0.84
     scikit-image==0.24.0
     scipy==1.14.1
     networkx==3.3
     ```

2. **Execution**  
   - Run `main_script.py` to launch the GUI or command-line interface for image processing.
   - Example usage:
     ```bash
     python main_script.py
     ```
   - Make sure the compiled `.pyd` files (e.g., `my_process_image_livewire.cp312-win_amd64.pyd`) are in the same directory as `main_script.py`.

3. **Notes**  
   - This repository only provides **Windows 64-bit binaries** for **Python 3.12**.
   - Compatibility on other operating systems or Python versions is not guaranteed.

---

## About Cython and Licensing

- We utilize [Cython](https://cython.org/) to compile some modules for performance and to protect the uncompiled source.
- Our custom `.pyx` code is **not published**, only the compiled `.pyd` binaries are included.
- Refer to [Cython’s license](https://github.com/cython/cython/blob/main/LICENSE.txt) for details on Cython itself.

---

## Dependencies / Requirements

- **Python 3.12 (Windows 64-bit)**
- **Required packages** in `requirements.txt` (exact versions):
  - `Cython==3.0.11`
  - `numpy==2.1.1`
  - `pandas==2.2.3`
  - `opencv-python==4.10.0.84`
  - `scikit-image==0.24.0`
  - `scipy==1.14.1`
  - `networkx==3.3`

These versions have been tested and are recommended.

---

## License

- The compiled binaries and script files in this repository follow the license specified within this project (e.g., MIT, BSD, etc.).
- Various open-source libraries (e.g., Cython, NumPy, etc.) are used under their respective licenses.
- Check the `LICENSE` file and official websites for each third-party library for more details.

---

## Disclaimer

- This software is provided **"as is,"** without any express or implied warranties.
- The author shall not be held liable for any direct or indirect damages arising from its use.

---

## Additional Usage Details

### 1. Image Selection
- When you run `main_script.py`, a file dialog appears, prompting you to choose an image (e.g., a fundus or retinal image).
- After selection, the program asks you to specify two points on the optic disc edge.  
  - The distance between these points is used to set a baseline for drawing circles (multipliers).
  - You will see a small dialog where you can select integer multipliers (e.g., 2x, 3x).
  - Click **OK** to confirm.

### 2. Measuring the Optic Disc Diameter
- About 1 second after choosing the multipliers, the Livewire segmentation window opens automatically.
- In this Livewire window, you can semi-automatically trace the blood vessel by clicking along its path.
- The software attempts to snap to vessel edges to assist in segmentation.

### 3. Livewire Segmentation for Vascular Tracing
- Continue clicking along the vessel to define its path.
- **Press `Z` (zoom)** to toggle the zoom level:
  - Each press cycles **1.0× → 1.5× → 2.0× → back to 1.0×**, repeatedly.
- **Press `r` (reverse)** to remove the most recently traced line if you need to correct a mistake.
- **Press `q` (quit)** to finalize the tracing and exit Livewire segmentation.

### 4. Result Files
- Upon pressing **q**, the software calculates the vessel’s “meandering” or tortuosity angles (bends), as well as intersections with any circles drawn.
- The following output files are generated in the **same folder** as your input image:
  1. **`_1_bends.png`**  
     - A visualization showing the traced vessel, bends, and intersections with the circles (multiplied optic disc diameters).
     - The filename matches your original image’s basename, plus `"_1_bends.png"`.
  2. **`result.xlsx`**  
     - An Excel file containing bend details and the total meandering angle.
     - The column **“Total Meandering Angle at All Bends”** contains the sum of all bend angles measured.

These outputs provide a quantitative measure of the vessel’s tortuosity (snake-like meandering) and allow for assessment of how the vessel intersects the optic disc’s circular boundaries.
