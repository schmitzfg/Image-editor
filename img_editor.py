from PIL import ImageFilter, ImageOps, ImageEnhance, ImageTk, ImageChops
import PIL.Image as PILImage


import random
import os
import customtkinter as ctk
from tkinter.filedialog import askopenfile, asksaveasfilename

BTN_COLOR = "#007bff"
TEXT_COLOR = "#eaeaea"
current_image = None
original_image = None
tk_image = None
history = []
brightness_value = 1
contrast_value = 1
saturation_value = 1
sharpness_value = 1
blur_value = 0
grayscale_value = False
sepia_value = False
filter_value = False
posterize_bits = 4
resize_enabled = False
resize_width = 0
resize_height = 0
vignette_value = 0
emboss_value = False
vintage_value = 0
noise_value = False
pixelate_value = 1
bloom_value = 0
kernel_sharpen_value = 0
gaussian_noise_value = 0
temperature_value = 0
edge_detect_value = False


def display_image(image):
    global tk_image

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    resized = image.copy()

    # FILL CANVAS
    if fullscreen_var.get():
        resized = resized.resize((canvas_width, canvas_height))
    # KEEP ASPECT RATIO
    else:
        resized.thumbnail((canvas_width, canvas_height))

    tk_image = ImageTk.PhotoImage(resized)

    canvas.delete("all")

    # for canvas
    x = (canvas_width - resized.width) // 2
    y = (canvas_height - resized.height) // 2
    # show on display
    canvas.create_image(x, y, anchor="nw", image=tk_image)




def open_image():
    global current_image, original_image

    button_text.set("loading...")
    file = askopenfile(parent=root, mode='rb', title='Choose a image', filetypes=[("Image extensions", (".jpg", ".jpeg", ".png"))])
    if file:
        file_name_label.configure(text=os.path.basename(file.name))   # name of file
        
        # open image
        image = PILImage.open(file.name)
        current_image = image
        original_image = image.copy()
        display_image(current_image)

    button_text.set("Browse")



def save_image():
    global current_image

    if current_image is None:
        return

    file_path = asksaveasfilename(defaultextension=".jpg",
                                    filetypes=[("JPEG", "*.jpg"),
                                                ("PNG", "*.png"),
                                                ("All Files", "*.*")])
    if file_path:
        # JPG
        if file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
            # compression_high_label.configure(text="JPEG Quality")
            # compression ON
            if compression_enabled.get():
                quality = int(compression_slider.get())
                current_image.save(file_path,
                                    optimize=True,
                                    quality=quality)
            # compression OFF
            else:
                current_image.save(file_path)
        elif file_path.endswith(".png"):
            # compression_high_label.configure(text="PNG Compression")
            if compression_enabled.get():
                compression = int(compression_slider.get() / 11)
                current_image.save(file_path, optimize=True, compress_level=compression)
            else:
                current_image.save(file_path)
        # PNG
        else:
            current_image.save(file_path)



def flip_image(transpose_type):
    """Used for left_right_button and rotate_button"""
    global original_image
    if original_image is None:
        return
    original_image = original_image.transpose(transpose_type)
    apply_adjustments()


def update_blur(value):
    """For blur Slider"""
    global blur_value
    blur_value = value

    apply_adjustments()


##========================================================================================
def apply_adjustments():
    global current_image
    if original_image is None:
        return

    image = original_image.copy().convert("RGB")

    # BRIGHTNESS
    image = ImageEnhance.Brightness(image).enhance(brightness_value)

    # CONTRAST
    image = ImageEnhance.Contrast(image).enhance(contrast_value)

    # SATURATION
    image = ImageEnhance.Color(image).enhance(saturation_value)


    ## COLOR TEMPERATURE
    if temperature_value != 0:

        pixels = image.load()
        width, height = image.size

        for x in range(width):
            for y in range(height):

                r,g,b = pixels[x,y]

                # warm
                if temperature_value > 0:
                    r += temperature_value * 0.6
                    b -= temperature_value * 0.4

                # cool
                else:
                    r += temperature_value * 0.4
                    b -= temperature_value * 0.6

                r = max(0,min(255,int(r)))
                g = max(0,min(255,int(g)))
                b = max(0,min(255,int(b)))

                pixels[x,y]=(r,g,b)


    # SHARPNESS
    image = ImageEnhance.Sharpness(image).enhance(sharpness_value)

    # BLUR
    if blur_value > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_value))

    # GRAYSCALE
    if grayscale_value:
        image = ImageOps.grayscale(image)
        image = image.convert("RGB")

    # SEPIA
    if sepia_value:
        sepia = []

        for r in range(256):
            tr = int(r * 0.393 + r * 0.769 + r * 0.189)
            tg = int(r * 0.349 + r * 0.686 + r * 0.168)
            tb = int(r * 0.272 + r * 0.534 + r * 0.131)

            sepia.extend((
                min(255, tr),
                min(255, tg),
                min(255, tb)))

        image = image.convert("L")
        image.putpalette(sepia)
        image = image.convert("RGB")


    ## Filter
    if filter_value:
        image = image.convert("RGB")
        image = ImageOps.grayscale(image)
        image = ImageOps.invert(image)
        image = image.convert("RGB")
        image = ImageOps.posterize(image, bits=posterize_bits)


    ## resise
    if resize_enabled:
        if resize_width > 0 and resize_height > 0:
            image = image.resize((resize_width, resize_height))

    # EMBOSS
    if emboss_value:
        image = image.filter(ImageFilter.EMBOSS)


    # VIGNETTE
    if vignette_value > 0:
        width, height = image.size
        mask = PILImage.new("L", (width, height), 255)

        center_x = width / 2
        center_y = height / 2
        max_dist = (center_x**2 + center_y**2) ** 0.5

        for x in range(width):
            for y in range(height):

                dx = x - center_x
                dy = y - center_y
                dist = (dx*dx + dy*dy)**0.5

                fade = (dist / max_dist) ** 2

                intensity = int(
                    255 -
                    fade *
                    vignette_value *
                    80      # controla întunecarea
                )

                intensity = max(120, min(255, intensity))

                mask.putpixel((x,y), intensity)

        mask = mask.filter(ImageFilter.GaussianBlur(150))

        image.putalpha(mask)
        background = PILImage.new("RGB", image.size, (0,0,0))

        background.paste(image, mask=image.split()[-1])

        image = background


    ## VINTAGE
    if vintage_value > 0:
        image = image.convert("RGB")  # 🔥 important

        image = ImageEnhance.Color(image).enhance(1 - 0.5 * vintage_value)
        image = ImageEnhance.Contrast(image).enhance(1 - 0.2 * vintage_value)
        image = ImageEnhance.Brightness(image).enhance(1 + 0.05 * vintage_value)

        sepia = PILImage.new("RGB", image.size, (255, 220, 170))

        image = PILImage.blend(image, sepia, 0.15 * vintage_value)


    ## PIXELATE
    if pixelate_value > 1:
        width, height = image.size

        small = image.resize((max(1, width // pixelate_value),
                            max(1, height // pixelate_value)),
                            PILImage.Resampling.BILINEAR)

        image = small.resize((width, height), PILImage.Resampling.NEAREST)



    ## NOICE
    if noise_value:
        pixels = image.load()
        width,height = image.size
        for x in range(width):
            for y in range(height):

                r,g,b = pixels[x,y]

                noise = random.randint(-30,30)

                r = max(0,min(255,r+noise))
                g = max(0,min(255,g+noise))
                b = max(0,min(255,b+noise))

                pixels[x,y]=(r,g,b)

    ## GAUSSIAN NOISE
    if gaussian_noise_value > 0:

        pixels = image.load()
        width,height = image.size

        for x in range(width):
            for y in range(height):
                r,g,b = pixels[x,y]

                noise = int(random.gauss(0, gaussian_noise_value))

                r=max(0,min(255,r+noise))
                g=max(0,min(255,g+noise))
                b=max(0,min(255,b+noise))

                pixels[x,y]=(r,g,b)




    ## bloom
    if bloom_value > 0:
        blurred = image.filter(ImageFilter.GaussianBlur(radius=20))
        bright = ImageEnhance.Brightness(blurred).enhance(1.3 + bloom_value)
        image = ImageChops.blend(image, bright, 0.4 * bloom_value)


    ## EDGE DETECT
    if edge_detect_value:
        image = image.filter(ImageFilter.FIND_EDGES)
    image = image.convert("RGB")
    current_image = image

    display_image(current_image)

    



def update_brightness(value):
    global brightness_value
    brightness_value = value

    apply_adjustments()



def update_contrast(value):
    global contrast_value
    contrast_value = value

    apply_adjustments()



def update_saturation(value):
    global saturation_value
    saturation_value = value

    apply_adjustments()




def update_sharpness(value):
    global sharpness_value
    sharpness_value = value

    apply_adjustments()




def toggle_grayscale():
    global grayscale_value
    grayscale_value = grayscale_checkbox.get()

    apply_adjustments()



def toggle_sepia():
    global sepia_value
    sepia_value = sepia_checkbox.get()

    apply_adjustments()



def toggle_filter():
    global filter_value
    filter_value = filter_checkbox.get()
    if filter_value:
        posterize_slider.configure(state="normal")
    else:
        posterize_slider.configure(state="disabled")

    apply_adjustments()


def update_posterize(value):
    global posterize_bits
    posterize_bits = int(value)

    apply_adjustments()



def toggle_resize():
    global resize_enabled
    resize_enabled = resize_checkbox.get()
    if resize_enabled:
        width_entry.configure(state="normal")
        height_entry.configure(state="normal")
        keep_ratio_checkbox.configure(state="normal")
    else:
        width_entry.configure(state="disabled")
        height_entry.configure(state="disabled")
        keep_ratio_checkbox.configure(state="disabled")

    apply_adjustments()


def update_resize():
    global resize_width, resize_height
    try:
        w = width_entry.get()
        h = height_entry.get()
        original_w, original_h = original_image.size
        ratio = original_h / original_w

        # dacă Keep Ratio activ
        if keep_ratio.get():
            # user a scris Width
            if w:
                resize_width = int(w)
                resize_height = int(resize_width * ratio)
                height_entry.delete(0,"end")
                height_entry.insert(0,str(resize_height))

            # user a scris Height
            elif h:
                resize_height = int(h)
                resize_width = int(resize_height / ratio)

                width_entry.delete(0,"end")
                width_entry.insert(0,str(resize_width))
        else:
            resize_width = int(w)
            resize_height = int(h)

        apply_adjustments()
    except:
        pass



def toggle_emboss():
    global emboss_value
    emboss_value = emboss_checkbox.get()

    apply_adjustments()

def update_vintage(value):
    global vintage_value
    vintage_value = float(value)
    apply_adjustments()


def update_vignette(value):
    global vignette_value
    vignette_value = float(value)
    apply_adjustments()


def update_pixelate(value):
    global pixelate_value
    pixelate_value = max(1, int(value))
    apply_adjustments()


def toggle_noise():
    global noise_value
    noise_value = noise_checkbox.get()
    apply_adjustments()



def update_bloom(value):
    global bloom_value
    bloom_value = float(value)
    apply_adjustments()




def update_kernel(value):
    global kernel_sharpen_value

    kernel_sharpen_value = float(value)
    apply_adjustments()



def update_gaussian(value):
    global gaussian_noise_value
    gaussian_noise_value = float(value)

    apply_adjustments()



def update_temperature(value):
    global temperature_value
    temperature_value = float(value)

    apply_adjustments()


def toggle_edge():
    global edge_detect_value
    edge_detect_value = edge_checkbox.get()

    apply_adjustments()



def reset_all_values():
    global brightness_value, contrast_value, saturation_value
    global sharpness_value, blur_value
    global grayscale_value, sepia_value, filter_value
    global posterize_bits
    global resize_enabled, resize_width, resize_height
    global vignette_value, emboss_value, vintage_value
    global noise_value, pixelate_value, bloom_value
    global kernel_sharpen_value, gaussian_noise_value
    global temperature_value, edge_detect_value

    brightness_value = 1
    contrast_value = 1
    saturation_value = 1
    sharpness_value = 1
    blur_value = 0

    grayscale_value = False
    sepia_value = False
    filter_value = False

    posterize_bits = 4

    resize_enabled = False
    resize_width = 0
    resize_height = 0

    vignette_value = 0
    emboss_value = False
    vintage_value = 0

    noise_value = False
    pixelate_value = 1
    bloom_value = 0

    kernel_sharpen_value = 0
    gaussian_noise_value = 0
    temperature_value = 0
    edge_detect_value = False


    # RESET UI SAFE
    brightness_slider.set(1)
    contrast_slider.set(1)
    saturation_slider.set(1)
    sharpness_slider.set(1)
    blur_slider.set(0)

    vintage_slider.set(0)
    vignette_slider.set(0)
    pixelate_slider.set(1)
    bloom_slider.set(0)
    temperature_slider.set(0)

    grayscale_checkbox.deselect()
    sepia_checkbox.deselect()
    filter_checkbox.deselect()
    edge_checkbox.deselect()
    noise_checkbox.deselect()
    emboss_checkbox.deselect()

    # IMPORTANT
    apply_adjustments()


    ## reset GUI sliders/checkboxes
    brightness_slider.set(1)
    contrast_slider.set(1)
    saturation_slider.set(1)
    sharpness_slider.set(1)

    blur_slider.set(0)

    vintage_slider.set(0)
    vignette_slider.set(0)
    pixelate_slider.set(1)

    bloom_slider.set(0)
    temperature_slider.set(0)

    grayscale_checkbox.deselect()
    sepia_checkbox.deselect()
    filter_checkbox.deselect()
    edge_checkbox.deselect()
    noise_checkbox.deselect()
    emboss_checkbox.deselect()




def apply_preset(name):
    global brightness_value
    global contrast_value
    global saturation_value
    global bloom_value
    global vintage_value
    global vignette_value
    global temperature_value
    global grayscale_value
    global blur_value

    reset_all_values()

    if name == "Retro":
        vintage_value = 0.8
        vignette_value = 0.12
        saturation_value = 0.85
        temperature_value = 35
        contrast_value = 0.95

    elif name == "Cinema":
        contrast_value = 1.4
        saturation_value = 0.75
        vignette_value = 0.08
        bloom_value = 0.15
        temperature_value = -10

    elif name == "B&W":
        grayscale_value = True
        contrast_value = 1.3

    elif name == "Cold":
        temperature_value = -70
        contrast_value = 1.2

    elif name == "Warm":
        temperature_value = 60
        saturation_value = 1.2

    elif name == "Cyberpunk":
        temperature_value = -50
        bloom_value = 0.6
        contrast_value = 1.5
        saturation_value = 1.4

    elif name == "Dreamy":
        bloom_value = 0.8
        blur_value = 1
        brightness_value = 1.1

    apply_adjustments()







## button animation
def add_hover(button):
    button.bind("<Enter>", lambda e: button.configure(border_width=2,
                                                      text_color="lightgreen",
                                                      border_color="#4da6ff",
                                                      fg_color="#004488"))
    button.bind("<Leave>",lambda e: button.configure(border_width=0,
                                                     text_color=TEXT_COLOR,
                                                     fg_color=BTN_COLOR))



#### GUI ####
ctk.set_appearance_mode("dark")     # dark / light / system
# ctk.set_default_color_theme("green")


root = ctk.CTk()

root.title("Simple Image Editor")
root.after(0, lambda: root.state("zoomed"))


# -------- MAIN CONTAINER ----------
frame = ctk.CTkFrame(root)
frame.pack(fill="both", expand=True)



# -------- LEFT SIDE -----------
left_frame = ctk.CTkFrame(frame)
left_frame.pack(side="left", fill="both", expand=True)


left_right_button = ctk.CTkButton(left_frame,
                       text="Flip",
                       command=lambda: flip_image(PILImage.Transpose.FLIP_LEFT_RIGHT),
                       fg_color= BTN_COLOR,
                       font=("Comic Sans", 20, "bold"),
                       text_color= TEXT_COLOR,
                       hover_color="#7ed6d4")
left_right_button.pack(pady=10)
# add_hover(left_right_button)


rotate_button = ctk.CTkButton(left_frame,
                       text="Rotate 90°",
                       command=lambda: flip_image(PILImage.Transpose.ROTATE_90),
                       fg_color= BTN_COLOR,
                       font=("Comic Sans", 20, "bold"),
                       text_color= TEXT_COLOR,
                       hover_color="#7ed6d4")
rotate_button.pack(pady=10)
# add_hover(rotate_button)



##-----

resize_checkbox = ctk.CTkCheckBox(left_frame,
                                text="Enable Resize Image",
                                command=toggle_resize,
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
resize_checkbox.pack(pady=20)

keep_ratio = ctk.BooleanVar(value=True)
keep_ratio_checkbox = ctk.CTkCheckBox(left_frame,
                                    text="Keep Aspect Ratio",
                                    variable=keep_ratio,
                                    font=("Arial",16,"bold"),
                                    text_color=TEXT_COLOR,
                                    state="disable")
keep_ratio_checkbox.pack(pady=5)


width_label = ctk.CTkLabel(left_frame, text="Width", font=("Arial", 16, "bold"),
                                                    text_color= TEXT_COLOR)
width_label.pack()
width_entry = ctk.CTkEntry(left_frame, placeholder_text="1920", font=("Arial", 15), state="disabled")
width_entry.pack(pady=5)
##-----

height_label = ctk.CTkLabel(left_frame, text="Height", font=("Arial", 16, "bold"),
                                                    text_color= TEXT_COLOR)
height_label.pack()
height_entry = ctk.CTkEntry(left_frame, placeholder_text="1080", font=("Arial", 15), state="disabled")
height_entry.pack(pady=5)


##-----
width_entry.bind("<KeyRelease>", lambda e: update_resize())
height_entry.bind("<KeyRelease>", lambda e: update_resize())

##-----

def toggle_compression():
    """Toggle Enable Quality"""
    if compression_enabled.get():
        compression_slider.configure(state="normal")
        compression_slider.set(90)
    else:
        compression_slider.set(100)
        compression_slider.configure(state="disabled")


compression_enabled = ctk.BooleanVar(value=False)   # Default off compression
compression_checkbox = ctk.CTkCheckBox(left_frame,
                                        text="Enable Quality",
                                        variable=compression_enabled,
                                        command=lambda: toggle_compression(),
                                        text_color=TEXT_COLOR,
                                        font=("Arial", 16, "bold"))
compression_checkbox.pack(pady=35, side="bottom")
##---------


compression_low_label = ctk.CTkLabel(left_frame,
                                text="Low Quality",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
compression_low_label.pack(pady=0, side="bottom" )
##---------

compression_slider = ctk.CTkSlider(left_frame, from_=1, to=100, orientation="vertical", state="disabled")
compression_slider.set(100)
compression_slider.pack(pady=(5), side="bottom")

compression_high_label = ctk.CTkLabel(left_frame,
                                text="Normal Quality",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
compression_high_label.pack(pady=5, side="bottom" )






#######################################################################
##----------- MIDDLE FRAME ------------
middle_frame = ctk.CTkFrame(frame)
middle_frame.pack(side="left", fill="both", expand=True)
###

canvas = ctk.CTkCanvas(middle_frame,
                       height=860,
                       width=950,
                       bg="#F05F44")
canvas.pack(fill="both", expand=True)
###

## File name label
file_name_label = ctk.CTkLabel(middle_frame, 
                     text="", font=("Comic Sans", 20, "bold"),
                     text_color = TEXT_COLOR,)
file_name_label.pack(pady=5)
#######

button_text = ctk.StringVar(value="Browse")
button_browse = ctk.CTkButton(middle_frame,
                       textvariable=button_text,
                       command=open_image,
                       fg_color= BTN_COLOR,
                       font=("Comic Sans", 20, "bold"),
                       text_color= TEXT_COLOR,
                       hover_color="#7ed6d4")
button_browse.pack(pady=(5, 20), side="left", expand=True)


##############
save_button = ctk.CTkButton(middle_frame,
    text="SAVE",
    command=save_image,
    fg_color="#28a745",
    font=("Comic Sans", 20, "bold"),
    text_color= TEXT_COLOR,
    hover_color="#34d058")
save_button.pack(pady=(5, 20), side="right", expand=True)


####################################################################
# -------- RIGHT FRAME ----------
right_frame = ctk.CTkFrame(frame)
right_frame.pack(side="right", fill="both", expand=True)


#### --- TABS ----
tabview = ctk.CTkTabview(right_frame)
tabview.pack(fill="both", expand=True,padx=10, pady=10)
tabview._segmented_button.configure(
                        font=("Arial", 16, "bold"),
                        fg_color="#1f1f1f",
                        selected_color="#007bff",
                        selected_hover_color="#3399ff",
                        unselected_color="#2b2b2b",
                        unselected_hover_color="#444444",
                        text_color=TEXT_COLOR)
tabview.add("🏠 Default")
tabview.add("⚙️ Advanced")
tabview.add("🎨 Presets")
default_tab = tabview.tab("🏠 Default")
advanced_tab = tabview.tab("⚙️ Advanced")
presets_tab = tabview.tab("🎨 Presets")


############### DEFAULT TAB ################
## --------- Checkbox Fullscreen ---------
fullscreen_var = ctk.BooleanVar(value=True)
check_button = ctk.CTkCheckBox(default_tab,
                               text = "Full Screen",
                               variable = fullscreen_var,
                               font = ("Arial", 16, "bold"),
                               command=lambda: display_image(current_image) if current_image else None,
                               text_color= TEXT_COLOR)
check_button.pack(pady=20)


## ----- Brightness Slider Label ----
brightness_label = ctk.CTkLabel(default_tab,
                                text="Brightness",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
brightness_label.pack(pady=(20, 0))

## ----- Brightness Slider -----
brightness_slider = ctk.CTkSlider(default_tab,
                                from_=0,
                                to=3,
                                command=update_brightness)
brightness_slider.set(1)
brightness_slider.pack(pady=(5, 20))



## ----- Contrast Slider Label ----
brightness_label = ctk.CTkLabel(default_tab,
                                text="Contrast",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
brightness_label.pack(pady=(20, 0))

## ----- Contrast Slider -----
contrast_slider = ctk.CTkSlider(default_tab,
                                from_=0,
                                to=3,
                                command=update_contrast)

contrast_slider.set(1)
contrast_slider.pack(pady=(5,20))




## ----- Saturation Label ----
brightness_label = ctk.CTkLabel(default_tab,
                                text="Saturation",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
brightness_label.pack(pady=(20, 0))

## ---- Saturation ------
saturation_slider = ctk.CTkSlider(default_tab,
                                from_=0,
                                to=3,
                                command=update_saturation)
saturation_slider.set(1)
saturation_slider.pack(pady=(5,20))





## ----- Sharpness Label ----
sharpness_label = ctk.CTkLabel(default_tab,
                                text="Sharpness",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
sharpness_label.pack(pady=(20, 0))
## -----Sharpeness -----
sharpness_slider = ctk.CTkSlider(default_tab,
                                from_=0,
                                to=5,
                                command=update_sharpness)
sharpness_slider.set(1)
sharpness_slider.pack(pady=(5,20))



## ----- Blur Label ----
brightness_label = ctk.CTkLabel(default_tab,
                                text="Blur",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR)
brightness_label.pack(pady=(20, 0))
## -- Blur --
blur_slider = ctk.CTkSlider(default_tab,
                            from_=0,
                            to=10,
                            command=update_blur)
blur_slider.set(0)
blur_slider.pack(pady=(5,20))


## ----Grayscale ----
grayscale_checkbox = ctk.CTkCheckBox(default_tab,
                                    text="Grayscale",
                                    font=("Arial", 16, "bold"),
                                    text_color= TEXT_COLOR,
                                    command=toggle_grayscale)
grayscale_checkbox.pack(pady=10)



## ---- Sepia ----
sepia_checkbox = ctk.CTkCheckBox(default_tab,
                                text="Sepia",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR,
                                command=toggle_sepia)
sepia_checkbox.pack(pady=10)



## -------------- Filter ---------------
filter_checkbox = ctk.CTkCheckBox(default_tab,
                                text="Filter",
                                font=("Arial", 16, "bold"),
                                text_color= TEXT_COLOR,
                                command=toggle_filter)
filter_checkbox.pack(pady=10)



## ----------------------------
posterize_label = ctk.CTkLabel(default_tab,
                            text="Filter Posterize Bits",
                            font=("Arial", 16, "bold"),
                            text_color=TEXT_COLOR)
posterize_label.pack(pady=(10, 0))

posterize_slider = ctk.CTkSlider(default_tab,
                                from_=1,
                                to=8,
                                number_of_steps=7,
                                command=update_posterize,
                                state="disabled")
posterize_slider.set(4)
posterize_slider.pack(pady=(5, 20))



####################### Advanced Tab ############################
## emboss
emboss_checkbox = ctk.CTkCheckBox(advanced_tab,
                                text="Emboss",
                                command=toggle_emboss,
                                font=("Arial", 16, "bold"),
                                text_color=TEXT_COLOR)
emboss_checkbox.pack(pady=10)



## noice
noise_checkbox = ctk.CTkCheckBox(advanced_tab,
                                text="Noise",
                                command=toggle_noise,
                                font=("Arial", 16, "bold"),
                                text_color=TEXT_COLOR)
noise_checkbox.pack(pady=10)



edge_checkbox = ctk.CTkCheckBox(advanced_tab,
                                text="Edge Detect",
                                command=toggle_edge,
                                font=("Arial",15,"bold"),
                                text_color=TEXT_COLOR)
edge_checkbox.pack(pady=10)


## vignette
vignette_label = ctk.CTkLabel(advanced_tab,
                            text="Vignette",
                            font=("Arial", 16, "bold"),
                            text_color=TEXT_COLOR)
vignette_label.pack(pady=(5,0))

vignette_slider = ctk.CTkSlider(advanced_tab,
                                from_=0,
                                to=1,
                                command=update_vignette)
vignette_slider.set(0)
vignette_slider.pack(pady=(0,5))


# ## vintage
vintage_label = ctk.CTkLabel(advanced_tab,
                            text="Vintage",
                            font=("Arial", 16, "bold"),
                            text_color=TEXT_COLOR)
vintage_label.pack(pady=(5,0))

vintage_slider = ctk.CTkSlider(advanced_tab,
                            from_=0,
                            to=2,
                            command=update_vintage)
vintage_slider.set(0)
vintage_slider.pack(pady=(0,5))



## pixelate
pixelate_label = ctk.CTkLabel(advanced_tab,
                            text="Pixelate",
                            font=("Arial", 16, "bold"),
                            text_color=TEXT_COLOR)
pixelate_label.pack(pady=(5,0))

pixelate_slider = ctk.CTkSlider(advanced_tab,
                                from_=1,
                                to=30,
                                command=update_pixelate)
pixelate_slider.set(1)
pixelate_slider.pack(pady=(0,5))



## bloom
bloon_label = ctk.CTkLabel(advanced_tab,
                            text="Bloom",
                            font=("Arial", 16, "bold"),
                            text_color=TEXT_COLOR)
bloon_label.pack(pady=(5,0))

bloom_slider = ctk.CTkSlider(advanced_tab,
                            from_=0,
                            to=2,
                            command=update_bloom)
bloom_slider.set(0)
bloom_slider.pack(pady=(0,5))



## kernel
kernel_label = ctk.CTkLabel(advanced_tab,
                            text="Sharpen Kernel",
                            font=("Arial",16,"bold"),
                            text_color=TEXT_COLOR)
kernel_label.pack(pady=(5,0))

kernel_slider = ctk.CTkSlider(advanced_tab,
                            from_=0,
                            to=5,
                            command=update_kernel)
kernel_slider.set(0)
kernel_slider.pack(pady=(0,5))


## gaussian
gaussian_label = ctk.CTkLabel(advanced_tab,
                            text="Gaussian Noise",
                            font=("Arial",16,"bold"),
                            text_color=TEXT_COLOR)
gaussian_label.pack(pady=(5,0))

gaussian_slider = ctk.CTkSlider(advanced_tab,
                                from_=0,
                                to=50,
                                command=update_gaussian)
gaussian_slider.set(0)
gaussian_slider.pack(pady=(0,5))





## temperature
temperature_label = ctk.CTkLabel(advanced_tab,
                                text="Color Temperature",
                                font=("Arial",16,"bold"),
                                text_color=TEXT_COLOR)
temperature_label.pack(pady=(5,0))


temperature_slider = ctk.CTkSlider(advanced_tab,
                                from_=-100,
                                to=100,
                                command=update_temperature)
temperature_slider.set(0)
temperature_slider.pack(pady=(0,10))


#######################################
## Presets
preset_names = [
    "Retro",
    "Cinema",
    "B&W",
    "Cold",
    "Warm",
    "Cyberpunk",
    "Dreamy"]
for preset in preset_names:
    btn = ctk.CTkButton(presets_tab,
                        text=preset,
                        command=lambda p=preset: apply_preset(p),
                        fg_color=BTN_COLOR,
                        font=("Arial",16,"bold"),
                        hover_color="#7ed6d4")
    btn.pack(pady=20, padx=10, fill="x")
    add_hover(btn)



## Reset Button
reset_button = ctk.CTkButton(presets_tab,
                            text="RESET",
                            command=reset_all_values,
                            fg_color="#28a745",
                            font=("Comic Sans", 20, "bold"),
                            text_color= TEXT_COLOR,
                            hover_color="#34d058")
reset_button.pack(pady=(5, 20), side="bottom", fill="x")


# add_hover(reset_button)




root.mainloop()







# print("IMAGE FILE:", Image.__file__)
# print("HAS OPEN:", hasattr(Image, "open"))



# def crop_image(image, start_x, start_y, end_X, end_y):
#     return image.crop((start_x, start_y, end_X, end_y))



# Pot să-ți fac și:

# icon images reale (PNG/SVG în tab buttons)
# sidebar în loc de tabview (Lightroom style)



# def optimise_image(image):
#     # image = crop_image(image, 20, 20, 400, 400)     # crop it
#     # image = resize_image(image, 200, 200)           # resize
#     # image = flip_image(image)                       # flip it
#     # image = rotate_image(image, degrees=180)        # rotate, 
#     # image = compress_image(image, "image.png", 0)   # compress / quality
#     # image = blur_image(image)                       # blurr
#     # image = sharpen_image(image)
#     image = adjust_brightness(image, 1.2)             # 0-1 negativ, over 1 positiv
#     # image = adjust_contrast(image, 1.4)             # 0-1 negativ, over 1 positiv
#     # image = add_filters(image, bits=4)              # bits = 8 - original, 4 - posterizare vizibilă, 2 - foarte dur, 1 - black and white 
#     return image


# # im = Image.open("meee.png")
# # optimised_image = optimise_image(im)
# # optimised_image.save("image.png")