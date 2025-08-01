import pygame
import pygame_gui
from PIL import Image, ImageSequence
import time
import os
import tkinter as tk
from tkinter import filedialog

# CONFIG
DEFAULT_BEATS = 2
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 300  # Much smaller minimum height
# Dynamic UI height - will be calculated based on actual content
UI_HEIGHT = 0  # Will be calculated dynamically
THUMBNAIL_HEIGHT = 100
MAX_SLOTS = 10
MAX_BPM = 600
STAGE_HEIGHT_RATIO = 0.85  # 85% of available height for stage (0.1 to 0.9)

# Pop-out window settings
POPOUT_WIDTH = 800
POPOUT_HEIGHT = 600
popout_window = None
popout_screen = None
popout_active = False
current_window = "main"  # "main" or "stage"
stage_background_color = (20, 20, 20)  # Default dark gray
stage_background_image = None
stage_background_image_surface = None

# INIT
tk.Tk().withdraw()
pygame.init()
pygame.display.set_caption("GIF BPM Sync Tool v3")

class GifSlot:
    def __init__(self, index):
        self.index = index
        self.frames = [pygame.Surface((300, 300))]
        self.frames[0].fill((30, 30, 30))
        self.durations = [100]
        self.frames_pil = [Image.new("RGBA", (300, 300), (0, 0, 0, 255))]
        self.width = 300
        self.height = 300
        self.beats = DEFAULT_BEATS
        self.frame_idx = 0
        self.original_loop_duration = sum(self.durations)
        self.is_loaded = False
        self.original_size = (300, 300)

# Global State
slots = [GifSlot(i) for i in range(MAX_SLOTS)]
active_slot = 0
window_width = MIN_WINDOW_WIDTH
window_height = 800  # Start with a taller default height
bpm = 120  # Set a default BPM instead of 0
zoom_level = 1.0
paused = False
tap_times = []
last_tap_time = 0
squad_mode = False
squad_spacing = 0.5  # 0-1 range: 0=directly behind, 1=3x gif width spacing
squad_size = 80  # 0-100 range: 0=25% size, 100=100% size
horizontal_flip = False  # Whether to flip the GIF horizontally
stage_height_ratio = STAGE_HEIGHT_RATIO  # Configurable stage height ratio

# Setup
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
manager = pygame_gui.UIManager((window_width, window_height))

def create_popout_window():
    """Create the pop-out window for streaming/OBS"""
    global popout_window, popout_screen, popout_active, current_window
    if popout_window is None:
        # Create a separate window for the stage
        popout_window = pygame.display.set_mode((POPOUT_WIDTH, POPOUT_HEIGHT), pygame.RESIZABLE)
        popout_screen = popout_window
        popout_active = True
        current_window = "stage"
        pygame.display.set_caption("BPMdotGIF - Stage Window")
        print("Stage window created!")
        print("For OBS: Use 'Window Capture' and select 'BPMdotGIF - Stage Window'")
        print("Press ESC to return to main window")

def close_popout_window():
    """Close the pop-out window"""
    global popout_window, popout_screen, popout_active, current_window
    if popout_window is not None:
        # Restore the main window
        pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
        pygame.display.set_caption("GIF BPM Sync Tool v3")
        popout_window = None
        popout_screen = None
        popout_active = False
        current_window = "main"
        print("Stage window closed.")

def set_stage_background_color(color):
    """Set the stage background color"""
    global stage_background_color
    stage_background_color = color

def set_stage_background_image(image_path):
    """Set a custom background image for the stage"""
    global stage_background_image, stage_background_image_surface
    try:
        if image_path and os.path.exists(image_path):
            # Load and scale the background image
            bg_image = pygame.image.load(image_path)
            # Convert to ensure compatibility
            bg_image = bg_image.convert_alpha()
            stage_background_image = image_path
            stage_background_image_surface = bg_image
            print(f"Background image loaded: {image_path}")
        else:
            stage_background_image = None
            stage_background_image_surface = None
            print("No image file selected or file doesn't exist.")
    except pygame.error as e:
        print(f"Pygame error loading background image: {e}")
        stage_background_image = None
        stage_background_image_surface = None
    except Exception as e:
        print(f"Error loading background image: {e}")
        stage_background_image = None
        stage_background_image_surface = None

def clear_stage_background():
    """Clear the stage background image"""
    global stage_background_image, stage_background_image_surface
    stage_background_image = None
    stage_background_image_surface = None
    print("Background image cleared")

def draw_stage_background(target_screen, stage_rect):
    """Draw the stage background (color or image)"""
    if stage_background_image_surface is not None:
        # Scale background image to fit the stage
        scaled_bg = pygame.transform.smoothscale(stage_background_image_surface, 
                                               (stage_rect.width, stage_rect.height))
        target_screen.blit(scaled_bg, (stage_rect.x, stage_rect.y))
    else:
        # Draw solid color background
        pygame.draw.rect(target_screen, stage_background_color, stage_rect)

def draw_gif_on_stage(target_screen, stage_rect, slot, zoom_level, squad_mode, squad_size, horizontal_flip):
    """Draw the GIF on the stage (extracted from draw_main_stage for reuse)"""
    if not slot.is_loaded:
        return
        
    if squad_mode:
        # Squad mode: draw backup dancers first (behind), then main dancer
        
        # Calculate main GIF dimensions
        main_scale = min(stage_rect.width / slot.width, stage_rect.height / slot.height) * zoom_level
        main_width = int(slot.width * main_scale)
        main_height = int(slot.height * main_scale)
        
        # Calculate backup dancer dimensions based on squad size slider
        size_multiplier = 0.25 + (squad_size / 100.0) * 0.75
        backup_scale = main_scale * size_multiplier
        backup_width = int(slot.width * backup_scale)
        backup_height = int(slot.height * backup_scale)
        
        # Calculate main GIF's top-left position
        main_x = stage_rect.x + (stage_rect.width - main_width) // 2
        main_y = stage_rect.y + (stage_rect.height - main_height) // 2
        
        # Calculate spacing based on slider value
        effective_slider_value = squad_spacing ** 2
        actual_offset = effective_slider_value * main_width
        
        # Calculate backup dancer center X positions
        main_center_x = main_x + main_width / 2.0
        
        backup_center_x_left = main_center_x - actual_offset
        backup_center_x_right = main_center_x + actual_offset
        
        # Convert backup dancer center positions to top-left blit positions
        left_x = backup_center_x_left - backup_width / 2.0
        right_x = backup_center_x_right - backup_width / 2.0
        
        # Vertical position for backup dancers
        backup_y = main_y + (main_height - backup_height) / 2.0
        
        # Draw left backup dancer
        current_frame = slot.frames[slot.frame_idx]
        if horizontal_flip:
            current_frame = pygame.transform.flip(current_frame, True, False)
        left_backup = pygame.transform.smoothscale(current_frame, (backup_width, backup_height))
        target_screen.blit(left_backup, (int(left_x), int(backup_y)))
        
        # Draw right backup dancer  
        right_backup = pygame.transform.smoothscale(current_frame, (backup_width, backup_height))
        target_screen.blit(right_backup, (int(right_x), int(backup_y)))
        
        # Draw main dancer (on top)
        main_frame = pygame.transform.smoothscale(current_frame, (main_width, main_height))
        target_screen.blit(main_frame, (main_x, main_y))
        
    else:
        # Normal mode: single GIF centered
        scale = min(stage_rect.width / slot.width, stage_rect.height / slot.height) * zoom_level
        scaled_width = int(slot.width * scale)
        scaled_height = int(slot.height * scale)
        
        # Center the GIF in the stage
        x = stage_rect.x + (stage_rect.width - scaled_width) // 2
        y = stage_rect.y + (stage_rect.height - scaled_height) // 2
        
        # Scale and draw the current frame
        current_frame = slot.frames[slot.frame_idx]
        if horizontal_flip:
            current_frame = pygame.transform.flip(current_frame, True, False)
        scaled_frame = pygame.transform.smoothscale(current_frame, (scaled_width, scaled_height))
        target_screen.blit(scaled_frame, (x, y))

def draw_popout_stage():
    """Draw the stage in the pop-out window"""
    if not popout_active or popout_screen is None:
        return
        
    # Clear the popout screen
    popout_screen.fill((0, 0, 0))
    
    # Calculate stage area (full window for popout)
    stage_rect = pygame.Rect(0, 0, POPOUT_WIDTH, POPOUT_HEIGHT)
    
    # Draw stage background
    draw_stage_background(popout_screen, stage_rect)
    
    # Draw active GIF
    slot = slots[active_slot]
    draw_gif_on_stage(popout_screen, stage_rect, slot, zoom_level, squad_mode, squad_size, horizontal_flip)
    
    # Update the stage window display
    pygame.display.flip()

def create_ui():
    global manager, window_width, window_height, UI_HEIGHT
    manager = pygame_gui.UIManager((window_width, window_height))
    
    # Calculate dynamic UI height and positioning
    row_height = 30
    row_spacing = 5
    padding = 10
    controls_height = (4 * row_height) + (3 * row_spacing) + (2 * padding)  # 4 rows
    UI_HEIGHT = controls_height
    
    # Position controls at bottom, above thumbnails
    y_start = window_height - UI_HEIGHT - THUMBNAIL_HEIGHT
    
    # Calculate horizontal spacing to fill full width
    available_width = window_width - (2 * padding)  # Total width minus padding
    
    # Row 1: BPM and Speed controls (distributed across full width)
    row1_elements = 7  # BPM label, input, slider, /2, x2, Beats label, input
    element_width = available_width // row1_elements
    spacing = (available_width % row1_elements) // (row1_elements - 1)  # Distribute remainder
    
    x_offset = padding
    pygame_gui.elements.UILabel(pygame.Rect(x_offset, y_start + padding, element_width, 20), "BPM:", manager=manager)
    x_offset += element_width + spacing
    bpm_input = pygame_gui.elements.UITextEntryLine(pygame.Rect(x_offset, y_start + padding, element_width, 25), manager=manager)
    x_offset += element_width + spacing
    bpm_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x_offset, y_start + padding, element_width, 25), 
                                                       start_value=0, value_range=(30, MAX_BPM), manager=manager)
    x_offset += element_width + spacing
    half_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding, element_width, 25), text="/2", manager=manager)
    x_offset += element_width + spacing
    double_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding, element_width, 25), text="x2", manager=manager)
    x_offset += element_width + spacing
    pygame_gui.elements.UILabel(pygame.Rect(x_offset, y_start + padding, element_width, 20), "Beats:", manager=manager)
    x_offset += element_width + spacing
    beats_input = pygame_gui.elements.UITextEntryLine(pygame.Rect(x_offset, y_start + padding, element_width, 25), manager=manager)
    beats_input.set_text(str(slots[active_slot].beats))
    
    # Row 2: File and Mode controls (distributed across full width)
    row2_elements = 5  # Upload, Export, Squad, Flip, Stage
    element_width = available_width // row2_elements
    spacing = (available_width % row2_elements) // (row2_elements - 1)
    
    x_offset = padding
    upload_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + row_height + row_spacing, element_width, 25), 
                                               text="Upload", manager=manager)
    x_offset += element_width + spacing
    export_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + row_height + row_spacing, element_width, 25), 
                                               text="Export", manager=manager)
    x_offset += element_width + spacing
    squad_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + row_height + row_spacing, element_width, 25), 
                                              text="Squad", manager=manager)
    x_offset += element_width + spacing
    flip_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + row_height + row_spacing, element_width, 25), 
                                             text="Flip", manager=manager)
    x_offset += element_width + spacing
    popout_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + row_height + row_spacing, element_width, 25), 
                                               text="Stage", manager=manager)
    
    # Row 3: Sliders (labels are narrow, sliders are wide)
    label_width = max(60, available_width // 20)  # Narrow labels
    spacing = 20  # Fixed spacing between elements
    
    # Calculate slider width more conservatively
    # Total elements: 3 labels + 3 sliders + 4 spacings (between each element)
    total_elements = 6  # 3 labels + 3 sliders
    total_spacings = 5  # 4 spacings between elements + 1 extra for safety
    slider_width = (available_width - (3 * label_width) - (total_spacings * spacing)) // 3
    
    x_offset = padding
    pygame_gui.elements.UILabel(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), label_width, 20), "Zoom:", manager=manager)
    x_offset += label_width + spacing
    zoom_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), slider_width, 25), 
                                                       start_value=1.0, value_range=(0.1, 3.0), manager=manager)
    x_offset += slider_width + spacing
    pygame_gui.elements.UILabel(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), label_width, 20), "Spacing:", manager=manager)
    x_offset += label_width + spacing
    squad_spacing_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), slider_width, 25), 
                                                                start_value=squad_spacing, value_range=(0, 1), manager=manager)
    x_offset += slider_width + spacing
    pygame_gui.elements.UILabel(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), label_width, 20), "Size:", manager=manager)
    x_offset += label_width + spacing
    squad_size_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(x_offset, y_start + padding + 2*(row_height + row_spacing), slider_width, 25), 
                                                             start_value=squad_size, value_range=(0, 100), manager=manager)
    
    # Row 4: Background controls (distributed across full width)
    row4_elements = 3  # BG Color, BG Image, Clear BG
    element_width = available_width // row4_elements
    spacing = (available_width % row4_elements) // (row4_elements - 1)
    
    x_offset = padding
    bg_color_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + 3*(row_height + row_spacing), element_width, 25), 
                                                 text="BG Color", manager=manager)
    x_offset += element_width + spacing
    bg_image_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + 3*(row_height + row_spacing), element_width, 25), 
                                                 text="BG Image", manager=manager)
    x_offset += element_width + spacing
    clear_bg_button = pygame_gui.elements.UIButton(pygame.Rect(x_offset, y_start + padding + 3*(row_height + row_spacing), element_width, 25), 
                                                 text="Clear BG", manager=manager)
    
    return {
        'bpm_input': bpm_input,
        'bpm_slider': bpm_slider,
        'beats_input': beats_input,
        'zoom_slider': zoom_slider,
        'upload_button': upload_button,
        'export_button': export_button,
        'half_button': half_button,
        'double_button': double_button,
        'squad_button': squad_button,
        'squad_spacing_slider': squad_spacing_slider,
        'squad_size_slider': squad_size_slider,
        'flip_button': flip_button,

        'popout_button': popout_button,
        'bg_color_button': bg_color_button,
        'bg_image_button': bg_image_button,
        'clear_bg_button': clear_bg_button
    }

ui_elements = create_ui()

def extract_beats_from_filename(filepath):
    """Extract number of beats from filename pattern _XB.gif where X is a number"""
    filename = os.path.basename(filepath)
    import re
    match = re.search(r'_(\d+)B\.gif$', filename, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return DEFAULT_BEATS

def load_gif(gif_path, slot_index):
    slot = slots[slot_index]
    
    # Extract beats from filename
    slot.beats = extract_beats_from_filename(gif_path)
    ui_elements['beats_input'].set_text(str(slot.beats))
    
    pil_img = Image.open(gif_path)
    frames_out = []
    durations_out = []
    pil_out = []
    
    # Store original size
    slot.original_size = pil_img.size
    
    for frame in ImageSequence.Iterator(pil_img):
        frame_rgba = frame.convert("RGBA")
        pil_out.append(frame_rgba.copy())
        duration = frame.info.get("duration", 100)
        durations_out.append(duration)
        mode = frame_rgba.mode
        size = frame_rgba.size
        data = frame_rgba.tobytes()
        frames_out.append(pygame.image.frombuffer(data, size, mode))
    
    slot.frames = frames_out
    slot.durations = durations_out
    slot.frames_pil = pil_out
    slot.width, slot.height = size
    slot.original_loop_duration = sum(durations_out)
    slot.frame_idx = 0
    slot.is_loaded = True

def export_adjusted_gif(slot, speed_mult):
    path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
    if path:
        # Convert frames to RGBA and ensure proper disposal while maintaining transparency
        frames_pil = []
        for frame in slot.frames_pil:
            # Convert to RGBA to ensure transparency is preserved
            frame_rgba = frame.convert('RGBA')
            frames_pil.append(frame_rgba)

        new_durs = [max(20, int(d / speed_mult)) for d in slot.durations]
        
        frames_pil[0].save(
            path,
            save_all=True,
            append_images=frames_pil[1:],
            duration=new_durs,
            loop=0,
            disposal=2,  # Clear the frame before rendering the next one
            transparency=0,  # Use index 0 for transparency
            optimize=False
        )

def draw_main_stage():
    # Calculate main stage area - extend all the way to controls
    controls_y = window_height - UI_HEIGHT - THUMBNAIL_HEIGHT
    stage_height = controls_y  # Stage fills from top to controls
    stage_rect = pygame.Rect(0, 0, window_width, stage_height)
    
    # Draw stage background
    draw_stage_background(screen, stage_rect)
    
    # Draw active GIF if loaded
    slot = slots[active_slot]
    draw_gif_on_stage(screen, stage_rect, slot, zoom_level, squad_mode, squad_size, horizontal_flip)

def draw_thumbnail_strip():
    # Calculate thumbnail strip area
    strip_y = window_height - THUMBNAIL_HEIGHT
    thumbnail_width = window_width // MAX_SLOTS
    
    # Draw strip background
    pygame.draw.rect(screen, (40, 40, 40), (0, strip_y, window_width, THUMBNAIL_HEIGHT))
    
    # Draw thumbnails
    for i, slot in enumerate(slots):
        x = i * thumbnail_width
        y = strip_y
        
        # Draw slot background (highlighted if active)
        bg_color = (60, 60, 60) if i == active_slot else (40, 40, 40)
        pygame.draw.rect(screen, bg_color, (x, y, thumbnail_width, THUMBNAIL_HEIGHT))
        
        if slot.is_loaded:
            # Calculate thumbnail dimensions
            thumb_scale = min((thumbnail_width - 10) / slot.width, 
                            (THUMBNAIL_HEIGHT - 20) / slot.height)
            thumb_width = int(slot.width * thumb_scale)
            thumb_height = int(slot.height * thumb_scale)
            
            # Center thumbnail in its slot
            thumb_x = x + (thumbnail_width - thumb_width) // 2
            thumb_y = y + (THUMBNAIL_HEIGHT - thumb_height) // 2
            
            # Draw thumbnail
            current_frame = slot.frames[slot.frame_idx]
            if horizontal_flip:
                current_frame = pygame.transform.flip(current_frame, True, False)
            thumbnail = pygame.transform.smoothscale(current_frame, (thumb_width, thumb_height))
            screen.blit(thumbnail, (thumb_x, thumb_y))
        
        # Draw slot number
        font = pygame.font.SysFont(None, 24)
        number_text = font.render(str(i + 1), True, (200, 200, 200))
        screen.blit(number_text, (x + 5, y + 5))

def handle_tap():
    global last_tap_time, bpm, tap_times
    now = time.time()
    if last_tap_time:
        tap_times.append(now - last_tap_time)
        if len(tap_times) > 5:
            tap_times.pop(0)
        if len(tap_times) >= 2:
            avg = sum(tap_times) / len(tap_times)
            new_bpm = max(30, min(int(60 / avg), MAX_BPM))
            bpm = new_bpm
            ui_elements['bpm_input'].set_text(str(bpm))
            ui_elements['bpm_slider'].set_current_value(bpm)
    last_tap_time = now

# Main Loop
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.VIDEORESIZE:
            window_width = max(MIN_WINDOW_WIDTH, event.w)
            # Allow smaller heights - calculate minimum based on UI requirements
            row_height = 30
            row_spacing = 5
            padding = 10
            controls_height = (4 * row_height) + (3 * row_spacing) + (2 * padding)
            min_required_height = controls_height + THUMBNAIL_HEIGHT + 50  # 50px for stage minimum
            window_height = max(min_required_height, event.h)
            screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
            ui_elements = create_ui()
            if bpm > 0:
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
        
        # Add tap input handling
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Calculate stage area
            stage_height = window_height - UI_HEIGHT - THUMBNAIL_HEIGHT
            if event.pos[1] <= stage_height:
                handle_tap()
        
        if event.type == pygame.KEYDOWN:
            # ESC key to switch between windows
            if event.key == pygame.K_ESCAPE:
                if current_window == "stage":
                    close_popout_window()
                elif current_window == "main" and popout_active:
                    create_popout_window()
            
            # Check if any text entry field is focused to prevent hotkey conflicts
            text_field_focused = (ui_elements['bpm_input'].is_focused or 
                                ui_elements['beats_input'].is_focused)
            
            if event.key == pygame.K_SPACE:
                paused = not paused
            # Only process number key hotkeys if no text field is focused
            elif not text_field_focused:
                if event.key in range(pygame.K_1, pygame.K_9 + 1):
                    active_slot = event.key - pygame.K_1
                    ui_elements['beats_input'].set_text(str(slots[active_slot].beats))
                elif event.key == pygame.K_0:
                    active_slot = 9
                    ui_elements['beats_input'].set_text(str(slots[active_slot].beats))
            
            # Arrow keys always work regardless of focus
            if event.key == pygame.K_RIGHT:
                bpm = min(MAX_BPM, bpm * 2)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.key == pygame.K_LEFT:
                bpm = max(30, bpm // 2)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.key == pygame.K_UP:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    bpm = min(MAX_BPM, bpm + 10)
                else:
                    bpm = min(MAX_BPM, bpm + 1)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.key == pygame.K_DOWN:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    bpm = max(30, bpm - 10)
                else:
                    bpm = max(30, bpm - 1)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == ui_elements['upload_button']:
                path = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
                if path:
                    load_gif(path, active_slot)
            elif event.ui_element == ui_elements['export_button']:
                if slots[active_slot].is_loaded:
                    if bpm > 0:
                        target_duration = (slots[active_slot].beats / bpm) * 60000
                        effective_speed_multiplier = slots[active_slot].original_loop_duration / target_duration
                        export_adjusted_gif(slots[active_slot], effective_speed_multiplier)
            elif event.ui_element == ui_elements['half_button']:
                bpm = max(30, bpm // 2)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.ui_element == ui_elements['double_button']:
                bpm = min(MAX_BPM, bpm * 2)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.ui_element == ui_elements['squad_button']:
                squad_mode = not squad_mode
            elif event.ui_element == ui_elements['flip_button']:
                horizontal_flip = not horizontal_flip
            elif event.ui_element == ui_elements['popout_button']:
                create_popout_window()

            elif event.ui_element == ui_elements['bg_color_button']:
                # Simple color picker - cycle through some preset colors
                colors = [(20, 20, 20), (0, 0, 0), (50, 50, 50), (100, 0, 100), (0, 100, 100)]
                current_index = colors.index(stage_background_color) if stage_background_color in colors else 0
                next_index = (current_index + 1) % len(colors)
                set_stage_background_color(colors[next_index])
            elif event.ui_element == ui_elements['bg_image_button']:
                # Open file dialog for background image
                bg_path = filedialog.askopenfilename(
                    title="Select Background Image",
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
                )
                if bg_path:
                    set_stage_background_image(bg_path)
            elif event.ui_element == ui_elements['clear_bg_button']:
                # Clear the background image
                clear_stage_background()
        
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == ui_elements['bpm_input']:
                try:
                    new_bpm = int(event.text)
                    bpm = max(30, min(new_bpm, MAX_BPM))
                    ui_elements['bpm_slider'].set_current_value(bpm)
                except ValueError:
                    pass
            elif event.ui_element == ui_elements['beats_input']:
                try:
                    # Auto-update beats when user finishes typing
                    slots[active_slot].beats = float(event.text)
                except ValueError:
                    # If invalid, reset to current value
                    ui_elements['beats_input'].set_text(str(slots[active_slot].beats))
        
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == ui_elements['bpm_slider']:
                bpm = int(event.value)
                ui_elements['bpm_input'].set_text(str(bpm))
            elif event.ui_element == ui_elements['zoom_slider']:
                zoom_level = event.value
            elif event.ui_element == ui_elements['squad_spacing_slider']:
                squad_spacing = event.value
            elif event.ui_element == ui_elements['squad_size_slider']:
                squad_size = int(event.value)

        
        # Only process UI events when in main window
        if current_window == "main":
            manager.process_events(event)
    
    # Only update UI when in main window
    if current_window == "main":
        manager.update(time_delta)
    
    # Update GIF frames
    if not paused:
        for slot in slots:
            if slot.is_loaded:
                if bpm > 0:
                    target_duration = (slot.beats / bpm) * 60000
                    effective_speed_multiplier = slot.original_loop_duration / target_duration
                    current_duration = slot.durations[slot.frame_idx] / effective_speed_multiplier
                else:
                    current_duration = slot.durations[slot.frame_idx]
                
                if pygame.time.get_ticks() % int(current_duration) < 17:  # 17ms is roughly 1 frame at 60fps
                    slot.frame_idx = (slot.frame_idx + 1) % len(slot.frames)
    
    # Draw based on current window
    if current_window == "main":
        # Draw main window
        screen.fill((30, 30, 30))
        draw_main_stage()
        draw_thumbnail_strip()
        manager.draw_ui(screen)
        pygame.display.flip()
    elif current_window == "stage":
        # Draw stage window
        draw_popout_stage()

pygame.quit()
