<h1 align="center">
  🌡️ AutoCalibrate PT100 Node R1
</h1>

<p align="center">
  <em>A robust, open-source mechanical foundation for automated RTD temperature sensor calibration.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Hardware-Open_Source-brightgreen?style=for-the-badge&logo=open-source-initiative" alt="Open Source Hardware" />
  <img src="https://img.shields.io/badge/CAD-STEP-blue?style=for-the-badge" alt="STEP Files" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</p>

This repository contains the hardware design and CAD files for the **AutoCalibrate PT100 Node (Revision 1)**. Designed for precision and ease of assembly, this project provides the structural housing required to securely mount and calibrate lab-grade PT100 (RTD) sensors alongside their driving electronics.

## ✨ Features

*   **Modular Carrier System**: The internal carrier isolates the PCB and sensor for easy maintenance.
*   **Universal Compatibility**: Provided in `.step` format to ensure compatibility across SolidWorks, Fusion 360, FreeCAD, and others.
*   **Thermal Considerations**: Optimized airflow and structural rigidity for high-accuracy thermal calibration environments.

## 📦 Repository Contents

All CAD files are provided in standard `STEP` format for seamless cross-platform import.

*   `AutoCalibrate_PT100_Node_R1_assembly.step` — The master assembly file. Use this to view the complete system architecture and mechanical fits.
*   `R1_carrier.step` — The internal mounting chassis for the RTD sensor and calibration PCB.
*   `R1_lower_housing.step` — The rugged base enclosure providing external structural support and mounting points.

## 🛠️ Hardware Requirements

To physically build this calibration node, you will need the following components:

*   **Manufacturing**: 3D Printer (FDM/SLA) or CNC Router. 
    *   *Recommended Materials*: PETG, ABS, or ASA for superior thermal resistance compared to standard PLA.
*   **Sensor**: Standard industrial or lab-grade PT100 probe.
*   **Fasteners**: M3 threaded inserts and M3x10mm socket head cap screws for securing the carrier.
*   **Electronics**: Custom calibration PCB or microcontroller designed to interface with the carrier slot.

## ⚙️ Assembly Instructions

1.  **Fabrication**: Manufacture the `R1_carrier` and `R1_lower_housing` using your preferred method. If 3D printing, ensure a minimum of 3 perimeters for structural rigidity.
2.  **Inserts**: Press the M3 threaded inserts into the designated boss holes in the `R1_lower_housing` using a soldering iron.
3.  **Component Mounting**: Slot the calibration PCB and the PT100 sensor securely into the `R1_carrier`.
4.  **Final Integration**: Seat the assembled carrier into the lower housing and fasten using the M3 screws. Reference the `assembly.step` file for precise alignment.

## 🚀 Usage

Once assembled, connect your PT100 probe leads to the internal PCB. The node is designed to interface with your wider calibration network. 

*(Note: Provide specific software flashing instructions, pinouts, or network integration steps for your exact electronics here.)*

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any mechanical improvements or feature requests are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
