# Real-Time FFT Audio Visualizer

![Project Banner](https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=1000&auto=format&fit=crop)
*(Note: The image above is a placeholder. Please replace it with a screenshot of your running application.)*

A Python-based application that performs real-time spectral analysis of audio signals and renders a reactive geometric visualization.

This project was developed to demonstrate the practical implementation of the **Cooley-Tukey Fast Fourier Transform (FFT)** algorithm and its application in digital signal processing (DSP) and computer graphics, without relying on external FFT libraries.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Theoretical Background](#-theoretical-background)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)

## 🔭 Overview
The application captures raw audio data from the microphone, processes it from the Time Domain to the Frequency Domain using a custom recursive FFT implementation, and maps the resulting frequency magnitudes to a polar coordinate system.

The result is a "digital mandala" that responds to music in real-time, visualizing bass, mid, and treble frequencies through radius, color, and motion.

## 🚀 Features
* **Custom Signal Processing:** Implements the recursive Cooley-Tukey algorithm (Radix-2) from scratch.
* **Real-Time Rendering:** Utilizes **Pygame** for high-performance 60 FPS graphics.
* **Spectral Leakage Reduction:** Applies a **Hanning Window** function to the input buffer.
* **Reactive Visuals:**
    * **Beat Detection:** Dynamic rotation and color shifts based on average signal amplitude.
    * **Visual Persistence:** Implements a trail effect using alpha blending to visualize signal decay.
    * **Radial Symmetry:** Maps frequency data to a 12-segment polar pattern.

## 🧠 Theoretical Background

### 1. The Fast Fourier Transform (FFT)
The core of this project is the transformation of discrete time-domain signals into the frequency domain. The **Discrete Fourier Transform (DFT)** is defined as:

$$X_k = \sum_{n=0}^{N-1} x_n \cdot e^{-i 2\pi k n / N}$$

Direct computation of the DFT has a time complexity of $O(N^2)$. To optimize this for real-time applications, this project implements the **Cooley-Tukey algorithm**, which utilizes a "Divide and Conquer" strategy to reduce complexity to $O(N \log N)$.

**Algorithm Steps:**
1.  **Divide:** Recursively split the input array of length $N$ into two sub-arrays of length $N/2$: one containing even-indexed elements ($x_{2m}$) and one containing odd-indexed elements ($x_{2m+1}$).
2.  **Conquer:** Compute the DFT of these sub-arrays recursively.
3.  **Combine:** Merge the results using the "Butterfly Operation":
    $$X_k = E_k + W_N^k \cdot O_k$$
    $$X_{k + N/2} = E_k - W_N^k \cdot O_k$$
    Where $W_N^k = e^{-i 2\pi k / N}$ is the "Twiddle Factor".

### 2. Windowing Function
Before processing, raw audio chunks are multiplied by a **Hanning Window**:

$$w(n) = 0.5 \left(1 - \cos\left(\frac{2\pi n}{N-1}\right)\right)$$

**Purpose:** This tapers the signal to zero at the edges of the sample window (512 samples), reducing discontinuities. This minimizes "spectral leakage" (noise) in the frequency analysis.

### 3. Visualization Mapping
The visualization maps the linear frequency array to a **Polar Coordinate System** ($r, \theta$):

* **Angle ($\theta$):** Determined by the symmetry index (12 segments) and a global rotation variable.
* **Radius ($r$):** Corresponds to the frequency bin index, scaled non-linearly by the amplitude ($A^{1.8}$) to emphasize strong beats.
* **Color (HSV):**
    * *Hue:* Determined by the frequency index (mapping pitch to color).
    * *Brightness (Value):* Driven by signal amplitude (louder = brighter).

## 🛠️ Installation & Setup

### Prerequisites
* **Python 3.8** or higher
* **PortAudio** library (Required for PyAudio to access the microphone)

### Step 1: Install System Dependencies (PortAudio)

* **Windows:**
    Usually not required (PyAudio binary wheels include PortAudio).
    
* **macOS:**
    ```bash
    brew install portaudio
    ```

* **Linux (Ubuntu/Debian):**
    ```bash
    sudo apt-get install python3-pyaudio portaudio19-dev
    ```

### Step 2: Set up Python Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```
(Ensure requirements.txt contains: pyaudio, numpy, pygame)

## 💻 Usage
Ensure your microphone is set as the default recording device in your OS settings.
Run the main script:

```bash
python main.py
```

The application will launch in fullscreen mode. Play some music or speak into the microphone to see the visualization.
**Controls:** Press ESC to exit the application.

## 📂 Project Structure
.
├── main.py # Entry point, custom FFT logic, and visualization loop
├── requirements.txt # Python dependencies
└── README.md # Documentation
