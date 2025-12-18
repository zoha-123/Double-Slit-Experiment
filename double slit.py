"""
Double-Slit Experiment Simulation (ROYGBIV)

An educational Python simulation demonstrating wave interference
using Young’s double-slit experiment.

Author: Zoha
"""
import pygame
import numpy as np
import math
import sys

# Constants
WIDTH, HEIGHT = 1200, 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

# ROYGBIV Wavelengths in nm with accurate RGB values
WAVELENGTHS = {
    'red': {'lambda': 700, 'rgb': (255, 0, 0), 'name': 'Red'},
    'orange': {'lambda': 620, 'rgb': (255, 165, 0), 'name': 'Orange'},
    'yellow': {'lambda': 580, 'rgb': (255, 255, 0), 'name': 'Yellow'},
    'green': {'lambda': 530, 'rgb': (0, 255, 0), 'name': 'Green'},
    'blue': {'lambda': 470, 'rgb': (0, 0, 255), 'name': 'Blue'},
    'indigo': {'lambda': 445, 'rgb': (75, 0, 130), 'name': 'Indigo'},
    'violet': {'lambda': 400, 'rgb': (148, 0, 211), 'name': 'Violet'}
}

# Scale factor to convert nm to pixels (for visualization)
SCALE_FACTOR = 0.15

# Initial slit separation (in pixels)
INITIAL_SLIT_SEPARATION = 100
MIN_SLIT_SEPARATION = 50
MAX_SLIT_SEPARATION = 300
SLIT_SEPARATION_STEP = 5

# Positions
SOURCE_X = 100
SLIT_X = 400
SCREEN_X = 900
SLIT_WIDTH = 5
SLIT_HEIGHT = 100
SCREEN_THICKNESS = 20

# Distance from slits to screen (in pixels)
L = SCREEN_X - SLIT_X

# Conversion factor: 1 pixel = 0.001 mm
PIXEL_TO_MM = 0.001

# Wave animation
WAVE_SPEED = 2
WAVE_PARTICLE_SIZE = 3
WAVE_PARTICLE_LIFETIME = 200  # frames
MAX_WAVE_PARTICLES = 500

class DoubleSlitSimulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Double-Slit Experiment Simulation - ROYGBIV Spectrum")
        self.clock = pygame.time.Clock()
        
        # Initialize font with fallback options
        try:
            self.font = pygame.font.SysFont('Arial', 18)
            self.small_font = pygame.font.SysFont('Arial', 14)
        except:
            try:
                self.font = pygame.font.SysFont('Times New Roman', 18)
                self.small_font = pygame.font.SysFont('Times New Roman', 14)
            except:
                try:
                    self.font = pygame.font.SysFont('Courier New', 18)
                    self.small_font = pygame.font.SysFont('Courier New', 14)
                except:
                    # Use default font if all else fails
                    self.font = pygame.font.Font(None, 18)
                    self.small_font = pygame.font.Font(None, 14)
        
        # Simulation parameters
        self.slit_separation = INITIAL_SLIT_SEPARATION
        self.running = True
        self.paused = False
        
        # Wave particles
        self.wave_particles = []
        self.frame_count = 0
        
        # Screen intensity array
        self.screen_height = HEIGHT
        self.screen_intensity = np.zeros((self.screen_height, 3))  # RGB intensities
        
        # Color toggles for each wavelength
        self.color_toggles = {color: True for color in WAVELENGTHS}  # Start with all colors active
        self.mono_color = None  # None means polychromatic
        
        # Pattern needs recalculation
        self.pattern_needs_update = True
        
    def toggle_all_colors(self):
        """Toggle all colors on or off"""
        self.mono_color = None
        all_active = all(self.color_toggles.values())
        for color in self.color_toggles:
            self.color_toggles[color] = not all_active
        self.pattern_needs_update = True
        
    def draw_light_source(self):
        # Draw light source
        pygame.draw.rect(self.screen, WHITE, (SOURCE_X - 20, HEIGHT//2 - 50, 40, 100))
        
        # Draw light beam - color depends on mode
        beam_start_x = SOURCE_X + 20
        beam_end_x = SLIT_X - 5
        beam_width = beam_end_x - beam_start_x
        beam_height = 80
        beam_y = HEIGHT//2 - beam_height//2
        
        # Determine beam color based on mode
        if self.mono_color:
            beam_color = WAVELENGTHS[self.mono_color]['rgb']
        else:
            beam_color = WHITE
        
        # Draw solid beam with selected color
        pygame.draw.rect(self.screen, beam_color, (beam_start_x, beam_y, beam_width, beam_height))
        
        # Add some glow effect to make it look more like light
        for i in range(3):
            glow_alpha = 100 - i * 30
            glow_height = beam_height + i * 10
            glow_y = beam_y - i * 5
            
            # Create a surface for the glow
            glow_surf = pygame.Surface((beam_width, glow_height), pygame.SRCALPHA)
            
            # Use the beam color with alpha for the glow
            glow_color = (*beam_color, glow_alpha)
            glow_surf.fill(glow_color)
            
            # Blit the glow surface
            self.screen.blit(glow_surf, (beam_start_x, glow_y))
    
    def draw_slits(self):
        # Draw barrier with slits
        pygame.draw.rect(self.screen, GRAY, (SLIT_X - 5, 0, 10, HEIGHT))
        
        # Calculate slit positions
        slit1_y = HEIGHT // 2 - self.slit_separation // 2
        slit2_y = HEIGHT // 2 + self.slit_separation // 2
        
        # Draw slits (gaps in the barrier)
        pygame.draw.rect(self.screen, BLACK, (SLIT_X - 5, slit1_y - SLIT_HEIGHT//2, 10, SLIT_HEIGHT))
        pygame.draw.rect(self.screen, BLACK, (SLIT_X - 5, slit2_y - SLIT_HEIGHT//2, 10, SLIT_HEIGHT))
        
        return slit1_y, slit2_y
    
    def calculate_interference_pattern(self):
        """Calculate the interference pattern mathematically for all wavelengths"""
        # Reset screen intensity
        self.screen_intensity = np.zeros((self.screen_height, 3))
        
        # Calculate pattern for each active wavelength
        for color_name, props in WAVELENGTHS.items():
            if not self.color_toggles[color_name]:
                continue
                
            wavelength = props['lambda'] * SCALE_FACTOR  # Convert to pixels
            rgb = props['rgb']
            
            # Calculate intensity for each point on the screen
            for y in range(self.screen_height):
                # Distance from center of screen
                y_rel = y - HEIGHT / 2
                
                # Small angle approximation: sinθ ≈ tanθ ≈ y_rel / L
                sin_theta = y_rel / L
                
                # Path difference between waves from the two slits
                path_diff = self.slit_separation * sin_theta
                
                # Phase difference
                phase_diff = 2 * math.pi * path_diff / wavelength
                
                # Intensity using interference formula: I = I0 * cos²(φ/2)
                intensity = (math.cos(phase_diff / 2)) ** 2
                
                # Add contribution to screen intensity
                self.screen_intensity[y][0] += intensity * rgb[0] / 255
                self.screen_intensity[y][1] += intensity * rgb[1] / 255
                self.screen_intensity[y][2] += intensity * rgb[2] / 255
        
        # Normalize intensities to prevent overflow
        max_intensity = np.max(self.screen_intensity)
        if max_intensity > 0:
            self.screen_intensity /= max_intensity
    
    def update_screen_intensity(self, particle, slit1_y, slit2_y):
        """Update screen intensity based on particle position"""
        # Calculate the path difference and phase
        y = particle['y']
        
        # Distance from each slit to the point on the screen
        d1 = math.sqrt((SCREEN_X - SLIT_X)**2 + (y - slit1_y)**2)
        d2 = math.sqrt((SCREEN_X - SLIT_X)**2 + (y - slit2_y)**2)
        
        # Path difference
        path_diff = abs(d1 - d2)
        
        # For each active wavelength, calculate its contribution
        for color_name, props in WAVELENGTHS.items():
            if not self.color_toggles[color_name]:
                continue
                
            wavelength = props['lambda'] * SCALE_FACTOR  # Convert to pixels
            rgb = props['rgb']
            
            # Phase difference (in radians)
            phase_diff = 2 * math.pi * path_diff / wavelength
            
            # Calculate intensity based on interference
            # Using the formula: I = I1 + I2 + 2*sqrt(I1*I2)*cos(phase_diff)
            # Assuming I1 = I2 = 1 for simplicity
            intensity = 2 + 2 * math.cos(phase_diff)
            intensity = intensity / 4  # Normalize to 0-1
            
            # Update screen intensity based on wavelength color
            screen_y = int(y)
            if 0 <= screen_y < self.screen_height:
                self.screen_intensity[screen_y][0] += intensity * rgb[0] / 255 * 0.05
                self.screen_intensity[screen_y][1] += intensity * rgb[1] / 255 * 0.05
                self.screen_intensity[screen_y][2] += intensity * rgb[2] / 255 * 0.05
    
    def draw_screen(self):
        # Draw the screen
        pygame.draw.rect(self.screen, LIGHT_GRAY, (SCREEN_X, 0, SCREEN_THICKNESS, HEIGHT))
        
        # Draw the intensity pattern
        for y in range(self.screen_height):
            intensity = self.screen_intensity[y]
            # Scale intensity to RGB values
            r = min(255, int(intensity[0] * 255))
            g = min(255, int(intensity[1] * 255))
            b = min(255, int(intensity[2] * 255))
            
            # Only draw if there's some intensity
            if r > 0 or g > 0 or b > 0:
                color = (r, g, b)
                pygame.draw.rect(self.screen, color, 
                                (SCREEN_X + SCREEN_THICKNESS, y, 50, 1))
    
    def emit_wave_particles(self, slit1_y, slit2_y):
        # Emit wave particles from slits at regular intervals
        if self.frame_count % 5 == 0:
            if self.mono_color:
                # Monochromatic mode - emit particles of the selected color
                color = WAVELENGTHS[self.mono_color]['rgb']
                
                # Emit from slit 1
                self.wave_particles.append({
                    'x': SLIT_X,
                    'y': slit1_y,
                    'color': color,
                    'wavelength': WAVELENGTHS[self.mono_color]['lambda'] * SCALE_FACTOR,
                    'lifetime': 0,
                    'source': 1,
                    'color_name': self.mono_color
                })
                
                # Emit from slit 2
                self.wave_particles.append({
                    'x': SLIT_X,
                    'y': slit2_y,
                    'color': color,
                    'wavelength': WAVELENGTHS[self.mono_color]['lambda'] * SCALE_FACTOR,
                    'lifetime': 0,
                    'source': 2,
                    'color_name': self.mono_color
                })
            else:
                # Polychromatic mode - emit white particles
                # Emit from slit 1
                self.wave_particles.append({
                    'x': SLIT_X,
                    'y': slit1_y,
                    'color': WHITE,
                    'lifetime': 0,
                    'source': 1
                })
                
                # Emit from slit 2
                self.wave_particles.append({
                    'x': SLIT_X,
                    'y': slit2_y,
                    'color': WHITE,
                    'lifetime': 0,
                    'source': 2
                })
    
    def update_wave_particles(self):
        # Update wave particles
        new_particles = []
        slit1_y = HEIGHT // 2 - self.slit_separation // 2
        slit2_y = HEIGHT // 2 + self.slit_separation // 2
        
        for particle in self.wave_particles:
            # Update position
            particle['x'] += WAVE_SPEED
            particle['lifetime'] += 1
            
            # Check if particle reached the screen
            if particle['x'] >= SCREEN_X:
                # Calculate interference pattern contribution
                self.update_screen_intensity(particle, slit1_y, slit2_y)
            # Keep particle if it's still within bounds and lifetime
            elif particle['x'] < WIDTH and particle['lifetime'] < WAVE_PARTICLE_LIFETIME:
                new_particles.append(particle)
        
        self.wave_particles = new_particles
    
    def draw_wave_particles(self):
        # Draw wave particles
        for particle in self.wave_particles:
            # Calculate alpha based on lifetime
            alpha = 255 * (1 - particle['lifetime'] / WAVE_PARTICLE_LIFETIME)
            
            # Draw particle with glow effect
            radius = WAVE_PARTICLE_SIZE
            color = particle['color']
            
            # Create a surface for the glowing particle
            glow_surf = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
            
            # Draw multiple circles with decreasing alpha for glow effect
            for i in range(3):
                glow_radius = radius + i
                glow_alpha = max(0, int(alpha // (i + 1)))
                glow_color = (*color, glow_alpha)
                pygame.draw.circle(glow_surf, glow_color, (radius*2, radius*2), glow_radius)
            
            # Blit the glow surface onto the screen
            self.screen.blit(glow_surf, (particle['x'] - radius*2, particle['y'] - radius*2))
            
            # Draw expanding wavefront circles (Huygens' principle)
            if particle['lifetime'] % 10 == 0:
                wavefront_radius = (particle['x'] - SLIT_X) * 0.5
                if wavefront_radius > 0 and wavefront_radius < 200:
                    wavefront_alpha = max(0, 100 - int(wavefront_radius // 2))
                    wavefront_color = (*color, wavefront_alpha)
                    
                    # Create a surface for the wavefront circle
                    circle_surf = pygame.Surface((int(wavefront_radius*2+2), int(wavefront_radius*2+2)), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surf, wavefront_color, 
                                     (int(wavefront_radius+1), int(wavefront_radius+1)), 
                                     int(wavefront_radius), 1)
                    
                    # Blit the circle surface onto the screen
                    self.screen.blit(circle_surf, 
                                    (int(particle['x'] - wavefront_radius - 1), 
                                     int(particle['y'] - wavefront_radius - 1)))
    
    def draw_wavelength_legend(self):
        """Draw a legend showing the wavelengths for each color"""
        legend_x = WIDTH - 200
        legend_y = 20
        
        # Draw legend background
        pygame.draw.rect(self.screen, (50, 50, 50), (legend_x - 10, legend_y - 10, 190, 200))
        pygame.draw.rect(self.screen, WHITE, (legend_x - 10, legend_y - 10, 190, 200), 2)
        
        # Draw title
        title = self.small_font.render("ROYGBIV Spectrum", True, WHITE)
        self.screen.blit(title, (legend_x, legend_y))
        
        # Draw each color with its wavelength
        y_offset = 30
        for i, (color_name, props) in enumerate(WAVELENGTHS.items()):
            color = props['rgb']
            wavelength = props['lambda']
            name = props['name']
            
            # Draw color box
            pygame.draw.rect(self.screen, color, (legend_x, legend_y + y_offset + i * 25, 20, 20))
            
            # Draw text
            text = f"{name}: {wavelength} nm"
            text_surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(text_surface, (legend_x + 30, legend_y + y_offset + i * 25))
            
            # Draw key number
            key_text = f"[{i+1}]"
            key_surface = self.small_font.render(key_text, True, WHITE)
            self.screen.blit(key_surface, (legend_x + 150, legend_y + y_offset + i * 25))
    
    def draw_info(self):
        # Draw slit separation info
        slit_separation_mm = self.slit_separation * PIXEL_TO_MM
        slit_text = f"Slit Separation: {self.slit_separation} px ({slit_separation_mm:.3f} mm)"
        text_surface = self.font.render(slit_text, True, WHITE)
        self.screen.blit(text_surface, (20, 20))
        
        # Draw screen distance
        screen_distance_mm = L * PIXEL_TO_MM
        distance_text = f"Screen Distance: {L} px ({screen_distance_mm:.1f} mm)"
        text_surface = self.font.render(distance_text, True, WHITE)
        self.screen.blit(text_surface, (20, 50))
        
        # Draw current mode and wavelength info
        if self.mono_color:
            mode_text = f"Mode: Monochromatic ({WAVELENGTHS[self.mono_color]['name']})"
            wavelength_text = f"Wavelength: {WAVELENGTHS[self.mono_color]['lambda']} nm"
            
            # Calculate fringe spacing for this wavelength
            wavelength = WAVELENGTHS[self.mono_color]['lambda'] * SCALE_FACTOR
            fringe_spacing_px = (wavelength * L) / self.slit_separation
            fringe_spacing_mm = fringe_spacing_px * PIXEL_TO_MM
            fringe_text = f"Fringe Spacing: {fringe_spacing_px:.1f} px ({fringe_spacing_mm:.3f} mm)"
        else:
            mode_text = "Mode: Polychromatic (ROYGBIV)"
            wavelength_text = "Wavelength: Full visible spectrum"
            
            # Calculate fringe spacing for red and violet
            red_wavelength = WAVELENGTHS['red']['lambda'] * SCALE_FACTOR
            violet_wavelength = WAVELENGTHS['violet']['lambda'] * SCALE_FACTOR
            
            red_spacing_px = (red_wavelength * L) / self.slit_separation
            violet_spacing_px = (violet_wavelength * L) / self.slit_separation
            
            red_spacing_mm = red_spacing_px * PIXEL_TO_MM
            violet_spacing_mm = violet_spacing_px * PIXEL_TO_MM
            
            fringe_text = f"Fringe Spacing - Red: {red_spacing_px:.1f} px ({red_spacing_mm:.3f} mm), "
            fringe_text += f"Violet: {violet_spacing_px:.1f} px ({violet_spacing_mm:.3f} mm)"
        
        mode_surface = self.font.render(mode_text, True, WHITE)
        self.screen.blit(mode_surface, (20, 80))
        
        wavelength_surface = self.font.render(wavelength_text, True, WHITE)
        self.screen.blit(wavelength_surface, (20, 110))
        
        fringe_surface = self.font.render(fringe_text, True, WHITE)
        self.screen.blit(fringe_surface, (20, 140))
        
        # Draw instructions
        instructions = [
            "Left/Right Arrows: Adjust slit separation",
            "1-7: Select monochromatic light (ROYGBIV)",
            "A: Toggle all colors (polychromatic)",
            "Space: Pause/Resume",
            "C: Clear screen",
            "ESC: Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text_surface, (20, HEIGHT - 120 + i * 18))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_c:
                    # Clear screen intensity
                    self.screen_intensity = np.zeros((self.screen_height, 3))
                    self.pattern_needs_update = True
                elif event.key == pygame.K_a:
                    # Toggle polychromatic mode
                    self.toggle_all_colors()
                # Number keys for monochromatic light
                elif event.key == pygame.K_1:
                    self.set_monochromatic('red')
                elif event.key == pygame.K_2:
                    self.set_monochromatic('orange')
                elif event.key == pygame.K_3:
                    self.set_monochromatic('yellow')
                elif event.key == pygame.K_4:
                    self.set_monochromatic('green')
                elif event.key == pygame.K_5:
                    self.set_monochromatic('blue')
                elif event.key == pygame.K_6:
                    self.set_monochromatic('indigo')
                elif event.key == pygame.K_7:
                    self.set_monochromatic('violet')
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        old_slit_separation = self.slit_separation
        if keys[pygame.K_LEFT]:
            self.slit_separation = max(MIN_SLIT_SEPARATION, self.slit_separation - SLIT_SEPARATION_STEP)
        if keys[pygame.K_RIGHT]:
            self.slit_separation = min(MAX_SLIT_SEPARATION, self.slit_separation + SLIT_SEPARATION_STEP)
        
        # If slit separation changed, update pattern
        if old_slit_separation != self.slit_separation:
            self.pattern_needs_update = True
    
    def set_monochromatic(self, color_name):
        """Set the simulation to monochromatic mode with the specified color"""
        self.mono_color = color_name
        # Turn off all colors
        for color in self.color_toggles:
            self.color_toggles[color] = False
        # Turn on the selected color
        self.color_toggles[color_name] = True
        self.pattern_needs_update = True

    
    def run(self):
        while self.running:
            self.handle_events()
            
            if not self.paused:
                # Clear screen
                self.screen.fill(BLACK)
                
                # Update pattern if needed
                if self.pattern_needs_update:
                    self.calculate_interference_pattern()
                    self.pattern_needs_update = False
                
                # Draw components
                self.draw_light_source()
                slit1_y, slit2_y = self.draw_slits()
                self.draw_screen()
                
                # Emit and update wave particles
                self.emit_wave_particles(slit1_y, slit2_y)
                self.update_wave_particles()
                self.draw_wave_particles()
                
                # Draw information
                self.draw_info()
                
                
                # Update display
                pygame.display.flip()
                
                # Increment frame count
                self.frame_count += 1
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    simulation = DoubleSlitSimulation()
    simulation.run()