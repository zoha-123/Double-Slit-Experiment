# Double-Slit-Experiment
Double-Slit Experiment Simulation with ROYGBIV Spectrum and Dynamic Animation

This simulation demonstrates the wave nature of light through the double-slit experiment
using the full visible spectrum (ROYGBIV). It provides mathematical accuracy and
dynamic animations showing wave propagation and interference.

Physics:
The simulation uses the principle of wave superposition with the formula:
y_n = n * λ * L / d for the position of the nth bright fringe

Where:
y_n = distance from center to nth bright fringe
n = fringe order (0, 1, 2, ...)
λ = wavelength of light (nm)
d = slit separation (mm)
L = distance from slits to screen (mm)

Fringe spacing between adjacent bright fringes:
Δy = λ * L / d

ROYGBIV Spectrum:
- Red: 700 nm
- Orange: 620 nm
- Yellow: 580 nm
- Green: 530 nm
- Blue: 470 nm
- Indigo: 445 nm
- Violet: 400 nm

Instructions:
- Run the script using Python 3 with Pygame and NumPy installed.
- Use Left/Right arrow keys to adjust the slit separation.
- Press 1-7 to select monochromatic light (Red, Orange, Yellow, Green, Blue, Indigo, Violet)
- Press A to toggle all colors (polychromatic light)
- Press Space to pause/resume the simulation.
- Press C to clear the screen.
- Press ESC to quit.
"""
