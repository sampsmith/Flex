# Flex001 - Industrial Vision Inspection System

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)](https://opencv.org/)

A rule based vison application to detect misaligned boards on a pallet production line. 

## Images


<img width="2565" height="1437" alt="Screenshot 2025-05-29 205029" src="https://github.com/user-attachments/assets/fac8b58c-f171-400c-b463-78ce71b82e3f" />

![Stringer-topboard-alignemnt-measurement](https://github.com/user-attachments/assets/8592765d-579f-416f-827c-a2ad25763a94)

![Nails_image](https://github.com/user-attachments/assets/832c1e77-1654-4d2c-9a8d-1a762efa27ea)

![stringers](https://github.com/user-attachments/assets/c0bd9901-654e-4f51-b6ba-886c0ea3be1b)


## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/sampsmith/Flex.git
cd Flex001

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📋 Prerequisites

- **Python 3.8+**
- **CUDA-capable GPU** (recommended for optimal performance)
- **Basler cameras** with Pylon SDK
- **Relay module** for hardware control

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sampsmith/Flex.git
   cd Flex001
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Basler Pylon SDK** (commercial license required)
   - Download from [Basler AG](https://www.baslerweb.com/)
   - Follow installation instructions for your platform

4. **Configure your hardware**
   - Connect Basler cameras
   - Set up relay module on COM port
   - Configure model paths in settings

5. **Run the application**
   ```bash
   python main.py
   ```


## Key Features

- **Dual Detection**: Handles both nail detection and board alignment simultaneously
- **Industrial Cameras**: Works with Basler cameras - both hardware-triggered and timed modes
- **Real-time Processing**: Uses GPU acceleration for speedy YOLO inference
- **Fault Logging**: Keeps track of all defects in a SQLite database
- **Hardware Control**: Automatically triggers relays when defects are found
- **Clean Code**: Modular architecture that's easy to maintain and extend
- **User-friendly Interface**: PySide6 GUI with real-time visualisation

## What You'll Need

### Hardware
- Basler cameras (compatible with Basler Pylon SDK)
- Relay module for hardware control
- CUDA-capable GPU (recommended, but CPU-only mode works too)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
Flex001/
├── main.py                          # Main entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── config/
│   └── settings.py                 # Application configuration
├── utils/
│   ├── logger.py                   # Logging utilities
│   └── image_utils.py              # Image processing utilities
├── hardware/
│   └── relay_controller.py         # Relay hardware communication
├── database/
│   └── fault_database.py           # Database operations
├── models/
│   └── model_manager.py            # YOLO model management
├── camera/
│   ├── camera_manager.py           # Camera initialisation
│   └── camera_workers.py           # Camera worker threads
├── detection/
│   └── detection_worker.py         # YOLO inference workers
└── gui/
    ├── main_window.py              # Main GUI window
    └── dialogs.py                  # Settings and fault history dialogs
```

## Configuration

The application uses a settings dialog to configure:
- Model paths for nail and board detection
- Pixel to millimetre conversion ratios
- Target measurements and tolerances
- Confidence thresholds
- Relay communication settings

## Usage

1. Start the application
2. Configure your models and settings via the Settings dialog
3. Select cameras for nail and board detection
4. Start the detection process
5. Monitor results and fault history

## Fault Management

The system automatically logs all detected faults to a SQLite database, including:
- Timestamp of detection
- Type of fault (nail or board alignment)
- Image index
- Detailed information
- Measurement data (for board alignment)

## Hardware Integration

### Cameras
- Supports Basler cameras with Pylon SDK
- Hardware-triggered mode for board alignment
- Timed capture mode for nail detection

### Relay Control
- Automatic relay triggering on defect detection
- Configurable COM port and baud rate
- Custom relay commands for your hardware

## Troubleshooting

### Common Issues
- **Camera not detected**: Ensure Pylon SDK is properly installed
- **Model loading errors**: Check model file paths in settings
- **Relay communication**: Verify COM port and baud rate settings

### Logs
Check the `logs/` directory for detailed application logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the [LICENSE](LICENSE) file for details.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Third-Party Licenses and Notices

This software uses the following third-party libraries and components:

### Free for Commercial Use
- **PySide6** (LGPL v3) - GUI framework
- **OpenCV** (Apache 2.0) - Computer vision library
- **NumPy** (BSD) - Numerical computing
- **Pillow** (HPND) - Image processing
- **PySerial** (BSD) - Serial communication
- **SQLite3** (Public Domain) - Database engine

### BSD License (Requires License Notice)
- **PyTorch** (BSD) - Deep learning framework
- **TorchVision** (BSD) - Computer vision for PyTorch

Copyright (c) 2016-2024, Facebook, Inc. All rights reserved.
Copyright (c) 2016-2024, PyTorch Contributors. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

### AGPL v3 License (Source Code Disclosure Required)
- **Ultralytics** (AGPL v3) - YOLO implementation

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

**Important**: If you distribute this software, you must provide access to the source code under the same license terms.

### Commercial License Required
- **PyPylon/Basler Pylon SDK** - Camera interface library

The Basler Pylon SDK requires a separate commercial license from Basler AG for commercial use. Please contact Basler AG for licensing information.

## Commercial Use Considerations

⚠️ **Important Commercial Use Notice**:

1. **Basler Pylon SDK**: Requires a commercial license from Basler AG for commercial deployment
2. **Ultralytics**: AGPL v3 license requires source code disclosure if you distribute the software
3. **PyTorch/TorchVision**: BSD license requires license notice inclusion

For commercial deployment, consider:
- Replacing PyPylon with an open-source camera interface
- Using ONNX runtime instead of Ultralytics for YOLO inference
- Ensuring all license notices are properly included

## Thanks

- [Ultralytics](https://github.com/ultralytics/ultralytics) for the YOLO implementation
- [PySide6](https://doc.qt.io/qtforpython/) for the GUI framework
- [Basler](https://www.baslerweb.com/) for the camera SDK
- [OpenCV](https://opencv.org/) for the computer vision utilities
- [PyTorch](https://pytorch.org/) for the deep learning framework

## Getting Help

If you run into any issues:
Contact: Sam Smith - 07948607918


---

**Important Note**: This system is designed for industrial use. Please ensure you follow proper safety protocols when integrating with production equipment. 
