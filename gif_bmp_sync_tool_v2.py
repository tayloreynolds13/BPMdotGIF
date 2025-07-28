# Add squad_mode to the global state variables
slots = [GifSlot(i) for i in range(MAX_SLOTS)]
active_slot = 0
window_width = MIN_WINDOW_WIDTH
window_height = MIN_WINDOW_HEIGHT
bpm = 0
zoom_level = 1.0
paused = False
tap_times = []
last_tap_time = 0
squad_mode = False
squad_spacing = 0.5  # 0-1 range: 0=directly behind, 1=3x gif width spacing
squad_size = 80  # 0-100 range: 0=25% size, 100=100% size

def create_ui():
    global manager, window_width, window_height
    manager = pygame_gui.UIManager((window_width, window_height))
    
    # Main controls - now positioned above the thumbnail strip
    y_start = window_height - UI_HEIGHT - THUMBNAIL_HEIGHT
    
    # BPM controls
    pygame_gui.elements.UILabel(pygame.Rect(10, y_start + 5, 140, 20), "BPM:", manager=manager)
    bpm_input = pygame_gui.elements.UITextEntryLine(pygame.Rect(150, y_start + 5, 100, 30), manager=manager)
    bpm_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(150, y_start + 40, 200, 30), 
                                                       start_value=0, value_range=(30, MAX_BPM), manager=manager)
    
    # Speed controls
    half_button = pygame_gui.elements.UIButton(pygame.Rect(370, y_start + 5, 80, 30), text="/2", manager=manager)
    double_button = pygame_gui.elements.UIButton(pygame.Rect(460, y_start + 5, 80, 30), text="x2", manager=manager)
    
    # Beat controls for active slot
    pygame_gui.elements.UILabel(pygame.Rect(10, y_start + 80, 140, 20), "Beats in GIF:", manager=manager)
    beats_input = pygame_gui.elements.UITextEntryLine(pygame.Rect(150, y_start + 80, 100, 30), manager=manager)
    beats_input.set_text(str(slots[active_slot].beats))
    
    # File controls
    upload_button = pygame_gui.elements.UIButton(pygame.Rect(10, y_start + 120, 150, 30), 
                                               text="Upload GIF", manager=manager)
    export_button = pygame_gui.elements.UIButton(pygame.Rect(180, y_start + 120, 150, 30), 
                                               text="Export Active GIF", manager=manager)
    
    # Squad Mode button
    squad_button = pygame_gui.elements.UIButton(pygame.Rect(350, y_start + 120, 120, 30), 
                                              text="Squad Mode", manager=manager)
    
    # Zoom control
    pygame_gui.elements.UILabel(pygame.Rect(10, y_start + 160, 140, 20), "Zoom:", manager=manager)
    zoom_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(150, y_start + 160, 200, 30), 
                                                       start_value=1.0, value_range=(0.1, 3.0), manager=manager)

    # Squad spacing control
    pygame_gui.elements.UILabel(pygame.Rect(10, y_start + 200, 140, 20), "Squad Spacing:", manager=manager)
    squad_spacing_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect(150, y_start + 200, 200, 30), 
                                                                start_value=squad_spacing, value_range=(0.0, 1.0), manager=manager)

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
        'squad_spacing_slider': squad_spacing_slider
    }

def draw_main_stage():
    # Calculate main stage area
    stage_height = window_height - UI_HEIGHT - THUMBNAIL_HEIGHT
    stage_rect = pygame.Rect(0, 0, window_width, stage_height)
    
    # Draw stage background
    pygame.draw.rect(screen, (20, 20, 20), stage_rect)
    
    # Draw active GIF if loaded
    slot = slots[active_slot]
    if slot.is_loaded:
        if squad_mode:
            # Squad mode: draw backup dancers first (behind), then main dancer
            
            # Calculate main GIF dimensions
            main_scale = min(stage_rect.width / slot.width, stage_rect.height / slot.height) * zoom_level
            main_width = int(slot.width * main_scale)
            main_height = int(slot.height * main_scale)
            
            # Calculate backup dancer dimensions (80% of main)
            backup_scale = main_scale * 0.8
            backup_width = int(slot.width * backup_scale)
            backup_height = int(slot.height * backup_scale)
            
            # Calculate positions
            main_x = (stage_rect.width - main_width) // 2
            main_y = (stage_rect.height - main_height) // 2
            
            # Calculate spacing based on slider value
            # Simple linear spacing: 0 = centered, 1.0 = 0.5x gif width out for fine control
            max_spacing_multiplier = 0.5  # Even smaller for very fine control
            actual_spacing = squad_spacing * main_width * max_spacing_multiplier
            
            # Calculate backup dancer positions
            main_center_x = main_x + main_width // 2
            backup_center_x_left = main_center_x - actual_spacing
            backup_center_x_right = main_center_x + actual_spacing
            
            # Convert center positions to top-left positions for blitting
            left_x = backup_center_x_left - backup_width // 2
            right_x = backup_center_x_right - backup_width // 2
            
            backup_y = main_y + (main_height - backup_height) // 2  # Center vertically with main
            
            # Draw left backup dancer
            current_frame = slot.frames[slot.frame_idx]
            left_backup = pygame.transform.smoothscale(current_frame, (backup_width, backup_height))
            screen.blit(left_backup, (left_x, backup_y))
            
            # Draw right backup dancer  
            right_backup = pygame.transform.smoothscale(current_frame, (backup_width, backup_height))
            screen.blit(right_backup, (right_x, backup_y))
            
            # Draw main dancer (on top)
            main_frame = pygame.transform.smoothscale(current_frame, (main_width, main_height))
            screen.blit(main_frame, (main_x, main_y))
            
        else:
            # Normal mode: single GIF centered
            scale = min(stage_rect.width / slot.width, stage_rect.height / slot.height) * zoom_level
            scaled_width = int(slot.width * scale)
            scaled_height = int(slot.height * scale)
            
            # Center the GIF in the stage
            x = (stage_rect.width - scaled_width) // 2
            y = (stage_rect.height - scaled_height) // 2
            
            # Scale and draw the current frame
            current_frame = slot.frames[slot.frame_idx]
            scaled_frame = pygame.transform.smoothscale(current_frame, (scaled_width, scaled_height))
            screen.blit(scaled_frame, (x, y))

# And add the squad button event handling in the main loop:
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
                ui_elements['bpm_input'].set_text(str(bmp))
                ui_elements['bpm_slider'].set_current_value(bmp)
            elif event.ui_element == ui_elements['double_button']:
                bpm = min(MAX_BPM, bpm * 2)
                ui_elements['bpm_input'].set_text(str(bpm))
                ui_elements['bpm_slider'].set_current_value(bpm)
            elif event.ui_element == ui_elements['squad_button']:
                squad_mode = not squad_mode
                # Update button text to show current state
                ui_elements['squad_button'].set_text("Squad: ON" if squad_mode else "Squad Mode")
            elif event.ui_element == ui_elements['squad_spacing_slider']:
                squad_spacing = event.value  # Keep as float for 0-1 range 