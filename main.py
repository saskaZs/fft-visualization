import pyaudio
import numpy as np
import pygame
import colorsys
import math
import sys

# --- CONFIGURATION ---
# Buffer size: 512 is selected to balance performance with the custom FFT implementation
CHUNK = 512        
RATE = 44100
SYMMETRY = 12      # Number of angular segments for the radial projection
SCALE = 3          # Zoom factor for the visualization

# --- CUSTOM RECURSIVE FFT IMPLEMENTATION ---
# Implementation of the Cooley-Tukey algorithm.
# This function demonstrates the "Divide and Conquer" approach to computing the DFT.
def my_recursive_fft(x):
    """
    Computes the Discrete Fourier Transform (DFT) of the input sequence x 
    using the recursive Cooley-Tukey Fast Fourier Transform (FFT) algorithm.
    
    Args:
        x (list or np.array): Input sequence of complex or real numbers.
        
    Returns:
        list: The frequency spectrum of the input.
    """
    N = len(x)
    # Base case: A signal of length 1 is its own DFT
    if N <= 1: return x
    
    # Recursive step: Divide the signal into even and odd indexed parts
    even = my_recursive_fft(x[0::2])
    odd =  my_recursive_fft(x[1::2])
    
    # Combine step: Apply the "Butterfly" operations using twiddle factors
    # T[k] = exp(-2j * pi * k / N) * odd[k]
    T = [np.exp(-2j * np.pi * k / N) * odd[k] for k in range(N // 2)]
    
    # Return the combined spectrum
    return [even[k] + T[k] for k in range(N // 2)] + \
           [even[k] - T[k] for k in range(N // 2)]

# --- INITIALIZATION ---
pygame.init()

# Setup Display
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Initialize Fullscreen with Double Buffering for rendering optimization
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.display.set_caption("Real-Time FFT Audio Visualizer")
pygame.mouse.set_visible(False) 

clock = pygame.time.Clock()

# Audio Input Setup (PyAudio)
p = pyaudio.PyAudio()

try:
    # Open input stream
    stream = p.open(format=pyaudio.paInt16, 
                    channels=1, 
                    rate=RATE, 
                    input=True, 
                    frames_per_buffer=CHUNK)
except Exception as e:
    print(f"Error: Failed to initialize audio stream. {e}")
    sys.exit()

def get_audio_spectrum():
    """
    Captures audio data, applies a window function, and computes the frequency spectrum.
    
    Returns:
        np.array: Logarithmic magnitude spectrum of the audio signal.
    """
    try:
        # 1. Read raw binary data from buffer
        data = stream.read(CHUNK, exception_on_overflow=False)
        data_int = np.frombuffer(data, dtype=np.int16)
        
        # 2. Apply Hanning Window to reduce spectral leakage caused by discontinuities at buffer edges
        window = np.hanning(len(data_int))
        windowed_data = data_int * window
        
        # 3. Compute FFT using custom implementation
        complex_spectrum = my_recursive_fft(windowed_data)
        
        # 4. Calculate Magnitude and convert to Decibels (Logarithmic scale)
        half_n = len(complex_spectrum) // 2
        magnitude = np.abs(complex_spectrum[:half_n])
        
        # Add 1 to avoid log(0) undefined errors
        return np.log10(magnitude + 1) * 20
    except Exception:
        # Fallback for read errors
        return np.zeros(CHUNK // 2)

# Global state variables for temporal dynamics
global_hue = 0
rotation_speed = 0.005

def render_visualization(fft_data, rotation):
    """
    Renders the spectral data as a geometric radial pattern.
    """
    global global_hue, rotation_speed
    
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # --- 1. VISUAL PERSISTENCE (Motion Blur) ---
    # Instead of clearing the screen, overlay a semi-transparent black surface.
    # This creates a fading trail effect, representing temporal history.
    trail_surface = pygame.Surface((WIDTH, HEIGHT))
    trail_surface.set_alpha(15) # Low alpha value increases trail longevity
    trail_surface.fill((0, 0, 0))
    screen.blit(trail_surface, (0, 0))

    if len(fft_data) == 0: return

    # Calculate average amplitude for dynamic reactivity
    avg_amp = np.mean(fft_data)
    
    # Dynamic parameter adjustment based on signal amplitude (Beat Detection)
    if avg_amp > 45:
        global_hue += 0.05
        rotation_speed = 0.02
    else:
        global_hue += 0.002
        rotation_speed = max(0.002, rotation_speed * 0.95) # Damping factor

    # Limit processing to lower frequencies (Bass/Low-Mid) for visual clarity
    max_idx = min(len(fft_data), 80) 

    # --- 2. GEOMETRIC PROJECTION ---
    for i in range(2, max_idx):
        val = fft_data[i]
        if val < 10: continue # Noise gate threshold

        # Determine color using HSV model based on frequency index and time
        hue = (i * 0.02 + global_hue) % 1.0
        # Map amplitude to saturation/value
        rgb = colorsys.hsv_to_rgb(hue, 0.9, min(1.0, val / 60))
        color = tuple(int(c * 255) for c in rgb)

        # Calculate radial distance with non-linear scaling for dramatic effect on high amplitudes
        base_radius = i * (5 if WIDTH > 1500 else 3) 
        radius = base_radius + (val ** 1.8) * 0.1 

        angle_offset = i * 0.1
        
        # --- 3. SYMMETRY RENDERING ---
        # Project the calculated point across multiple angular segments
        for j in range(SYMMETRY):
            angle = math.radians((360 / SYMMETRY) * j) + rotation + angle_offset
            
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            size = val * 0.15
            
            # Render data point
            pygame.draw.circle(screen, color, (int(x), int(y)), int(size))
            
            # Render connective lines for high-energy points (Visual feedback)
            if val > 50:
                 line_end_x = center_x + math.cos(angle - 0.2) * (radius * 0.5)
                 line_end_y = center_y + math.sin(angle - 0.2) * (radius * 0.5)
                 pygame.draw.line(screen, color, (x,y), (line_end_x, line_end_y), 1)

# --- MAIN EVENT LOOP ---
running = True
rotation = 0

print("System initialized. Press ESC to exit.")

while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 1. Data Acquisition
    spectrum = get_audio_spectrum()

    # 2. Rendering
    render_visualization(spectrum, rotation)
    
    # 3. Display Update
    pygame.display.flip()
    
    # 4. State Update
    rotation += rotation_speed
    clock.tick(60)

# Resource Cleanup
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()