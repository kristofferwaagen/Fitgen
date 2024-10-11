import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from rembg import remove
import os
import random
import json
import hashlib
import time

# Categories for clothing
categories = ["tops", "bottoms", "shoes"]
base_dir = "clothing_items"
favorites_file = os.path.join(base_dir, "favorites.json")
last_randomization_time = 0  # Tracks the time of the last randomization
randomization_delay = 1.0  # 1 second delay between randomizations

# Create directories for storing clothing items and metadata if they don't exist
for category in categories:
    os.makedirs(os.path.join(base_dir, category), exist_ok=True)
    os.makedirs(os.path.join(base_dir, f"{category}_metadata"), exist_ok=True)

# Load existing hashes to prevent duplicate uploads
def load_existing_hashes():
    all_hashes = set()
    for category in categories:
        metadata_dir = os.path.join(base_dir, f"{category}_metadata")
        for metadata_file in os.listdir(metadata_dir):
            metadata_path = os.path.join(metadata_dir, metadata_file)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                all_hashes.add(metadata.get('hash'))
    return all_hashes

# Set of all existing image hashes
existing_hashes = load_existing_hashes()

# Load favorites from file
def load_favorites():
    if os.path.exists(favorites_file):
        try:
            with open(favorites_file, 'r') as f:
                data = f.read().strip()
                if not data:  # Handle empty file case
                    return []
                return json.loads(data)
        except (json.JSONDecodeError, FileNotFoundError):
            # If the file is empty, corrupted, or missing, return an empty list
            return []
    return []

# Save favorites to file
def save_favorites(favorites):
    if isinstance(favorites, list):
        with open(favorites_file, 'w') as f:
            json.dump(favorites, f, indent=4)

# Calculate the hash of an image
def calculate_image_hash(image):
    hasher = hashlib.md5()
    with open(image, 'rb') as img_file:
        buf = img_file.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Check if an image hash exists in the global set of hashes
def is_duplicate_image(image_hash):
    return image_hash in existing_hashes

# Downscale the image before processing to reduce memory usage and improve performance
def downscale_image(image, max_size=(800, 800)):
    """
    Rescale the image so that its longest side is max_size.
    This reduces image size to optimize performance on mobile devices.
    """
    image.thumbnail(max_size)
    return image

# Clear previous images and status messages
def clear_previous():
    output_image_label.config(image='')
    top_label.config(image='')
    bottom_label.config(image='')
    shoes_label.config(image='')
    top_name_label.config(text='')
    bottom_name_label.config(text='')
    shoes_name_label.config(text='')
    status_label.config(text='')

# Upload an image
def upload_image():
    clear_previous()
    file_path = filedialog.askopenfilename()
    if file_path:
        image_hash = calculate_image_hash(file_path)

        # Check if the image is a duplicate
        if is_duplicate_image(image_hash):
            status_label.config(text="Duplicate image detected. Image not uploaded.")
            return

        # Ask the user to define the category
        category = simpledialog.askstring("Input", f"Define the category for this item (choose from: {', '.join(categories)}):", parent=root)
        if category and category.lower() in categories:
            base_name = os.path.basename(file_path).rsplit('.', 1)[0]
            output_path = os.path.join(base_dir, category.lower(), f"{base_name}_no_bg.png")
            metadata_path = os.path.join(base_dir, f"{category.lower()}_metadata", f"{base_name}.json")

            # If the image has been processed before, skip processing
            if os.path.exists(output_path):
                status_label.config(text="Image already processed. Using the existing image.")
                return

            input_image = Image.open(file_path)

            # Downscale the image to reduce memory usage
            input_image = downscale_image(input_image)

            # Remove the background using rembg
            output_image = remove(input_image)

            # Display the output image (further downscale for display purposes)
            output_image.thumbnail((400, 400))
            output_image_tk = ImageTk.PhotoImage(output_image)
            output_image_label.config(image=output_image_tk)
            output_image_label.image = output_image_tk

            # Ask the user to name the item and save it
            item_name = simpledialog.askstring("Input", "Name the item:", parent=root)
            if item_name:
                # Save the image and metadata
                output_image.save(output_path)
                with open(metadata_path, 'w') as f:
                    json.dump({'name': item_name, 'hash': image_hash}, f)

                # Add the new hash to the global set of hashes
                existing_hashes.add(image_hash)

                status_label.config(text=f"Saved output image to: {output_path}")
            else:
                status_label.config(text="Item name not provided. Please try again.")
        else:
            status_label.config(text="Invalid category. Please try again.")

# Randomize the outfit, with throttling to avoid excessive CPU usage
def randomize_outfit():
    global last_randomization_time, current_outfit  # Define current_outfit as global here

    # Check if enough time has passed since the last randomization
    current_time = time.time()
    if current_time - last_randomization_time < randomization_delay:
        status_label.config(text="Please wait before randomizing again.")
        return

    clear_previous()
    outfit = {}
    names = {}
    missing_categories = []
    for category in categories:
        items = os.listdir(os.path.join(base_dir, category))
        if items:
            selected_item = random.choice(items)
            outfit[category] = selected_item
            # Load the metadata
            base_name = selected_item.rsplit('_no_bg.png', 1)[0]
            metadata_path = os.path.join(base_dir, f"{category}_metadata", f"{base_name}.json")
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                names[category] = metadata['name']
        else:
            outfit[category] = None
            names[category] = None
            missing_categories.append(category)

    if missing_categories:
        status_label.config(text=f"Cannot create outfit. Missing items in: {', '.join(missing_categories)}")
    else:
        # Load images and display them (further downscaling for mobile efficiency)
        top_image = Image.open(os.path.join(base_dir, 'tops', outfit['tops']))
        bottom_image = Image.open(os.path.join(base_dir, 'bottoms', outfit['bottoms']))
        shoes_image = Image.open(os.path.join(base_dir, 'shoes', outfit['shoes']))

        top_image.thumbnail((200, 200))
        bottom_image.thumbnail((200, 200))
        shoes_image.thumbnail((200, 200))

        top_image_tk = ImageTk.PhotoImage(top_image)
        bottom_image_tk = ImageTk.PhotoImage(bottom_image)
        shoes_image_tk = ImageTk.PhotoImage(shoes_image)

        top_label.config(image=top_image_tk)
        top_label.image = top_image_tk
        bottom_label.config(image=bottom_image_tk)
        bottom_label.image = bottom_image_tk
        shoes_label.config(image=shoes_image_tk)
        shoes_label.image = shoes_image_tk

        top_name_label.config(text=names['tops'])
        bottom_name_label.config(text=names['bottoms'])
        shoes_name_label.config(text=names['shoes'])

        favorite_button.config(state=tk.NORMAL)

        # Store the current outfit in the global variable for favoriting
        current_outfit = {
            'top': outfit['tops'],
            'bottom': outfit['bottoms'],
            'shoes': outfit['shoes'],
            'top_name': names['tops'],
            'bottom_name': names['bottoms'],
            'shoes_name': names['shoes']
        }

    # Update the time of the last randomization
    last_randomization_time = current_time

# Favorite the current outfit
def favorite_outfit():
    favorites = load_favorites()

    # Check if current_outfit exists before adding to favorites
    if 'current_outfit' in globals():
        favorites.append(current_outfit)
        save_favorites(favorites)
        status_label.config(text="Outfit added to favorites.")
    else:
        status_label.config(text="No outfit to favorite. Randomize an outfit first.")

# View and delete uploaded images
def view_uploaded_images():
    def on_image_click(event, img_path, metadata_path):
        if messagebox.askyesno("Delete Image", "Are you sure you want to delete this image?"):
            # Load the metadata to get the hash
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                image_hash = metadata.get('hash')

            # Remove the hash from the global set of hashes
            if image_hash in existing_hashes:
                existing_hashes.remove(image_hash)

            # Remove the image and metadata files
            os.remove(img_path)
            os.remove(metadata_path)

            refresh_images()

    def refresh_images():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        row = 0
        for category in categories:
            # Label for the category
            category_label = tk.Label(scrollable_frame, text=category.capitalize(), font=("Helvetica", 16, "bold"))
            category_label.grid(row=row, column=0, columnspan=4, pady=10)
            row += 1
            category_dir = os.path.join(base_dir, category)
            col = 0
            for filename in os.listdir(category_dir):
                img_path = os.path.join(category_dir, filename)
                base_name = filename.rsplit('_no_bg.png', 1)[0]
                metadata_path = os.path.join(base_dir, f"{category}_metadata", f"{base_name}.json")
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(img)

                img_label = tk.Label(scrollable_frame, image=img_tk)
                img_label.image = img_tk
                img_label.grid(row=row, column=col, padx=5, pady=5)
                img_label.bind("<Button-1>", lambda e, img_path=img_path, metadata_path=metadata_path: on_image_click(e, img_path, metadata_path))

                col += 1
                if col == 4:
                    col = 0
                    row += 1
            row += 1

    # Window to show all images
    view_window = tk.Toplevel(root)
    view_window.title("Uploaded Images")
    view_window.geometry("800x800")
    canvas = tk.Canvas(view_window)
    scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    refresh_images()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# View and delete favorite outfits
def view_favorites():
    def on_favorite_click(event, favorite):
        if messagebox.askyesno("Delete Favorite", f"Are you sure you want to delete this favorite outfit: {favorite['top_name']}, {favorite['bottom_name']}, {favorite['shoes_name']}?"):
            favorites.remove(favorite)  # Remove the favorite from the list
            save_favorites(favorites)  # Save the updated favorites list
            refresh_favorites()  # Refresh the display after deletion

    def refresh_favorites():
        # Clear previous widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Populate the favorite outfits in a grid
        row = 0
        for favorite in favorites:
            # Create a frame for the outfit
            outfit_frame = tk.Frame(scrollable_frame)
            outfit_frame.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            row += 1

            # Load images for the outfit
            top_img_path = os.path.join(base_dir, 'tops', favorite['top'])
            bottom_img_path = os.path.join(base_dir, 'bottoms', favorite['bottom'])
            shoes_img_path = os.path.join(base_dir, 'shoes', favorite['shoes'])

            top_img = Image.open(top_img_path)
            bottom_img = Image.open(bottom_img_path)
            shoes_img = Image.open(shoes_img_path)

            # Thumbnail the images
            top_img.thumbnail((100, 100))
            bottom_img.thumbnail((100, 100))
            shoes_img.thumbnail((100, 100))

            top_img_tk = ImageTk.PhotoImage(top_img)
            bottom_img_tk = ImageTk.PhotoImage(bottom_img)
            shoes_img_tk = ImageTk.PhotoImage(shoes_img)

            # Display the images and outfit details
            top_label = tk.Label(outfit_frame, image=top_img_tk)
            top_label.image = top_img_tk
            top_label.grid(row=0, column=0)

            bottom_label = tk.Label(outfit_frame, image=bottom_img_tk)
            bottom_label.image = bottom_img_tk
            bottom_label.grid(row=0, column=1)

            shoes_label = tk.Label(outfit_frame, image=shoes_img_tk)
            shoes_label.image = shoes_img_tk
            shoes_label.grid(row=0, column=2)

            # Display the names of the outfit components
            favorite_label = tk.Label(outfit_frame, text=f"{favorite['top_name']}, {favorite['bottom_name']}, {favorite['shoes_name']}")
            favorite_label.grid(row=0, column=3, padx=10)

            # Bind the click event to the images and label for deleting
            top_label.bind("<Button-1>", lambda e, fav=favorite: on_favorite_click(e, fav))
            bottom_label.bind("<Button-1>", lambda e, fav=favorite: on_favorite_click(e, fav))
            shoes_label.bind("<Button-1>", lambda e, fav=favorite: on_favorite_click(e, fav))
            favorite_label.bind("<Button-1>", lambda e, fav=favorite: on_favorite_click(e, fav))

    # Load the favorites from the JSON file
    favorites = load_favorites()

    # Window to show all favorites
    view_window = tk.Toplevel(root)
    view_window.title("Favorite Outfits")
    view_window.geometry("800x800")
    canvas = tk.Canvas(view_window)
    scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Populate the favorites list
    refresh_favorites()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Main window
root = tk.Tk()
root.title("Fitgen")
root.geometry("1000x1000")

# Upload button
upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=10)

# Labels to display the images
output_image_label = tk.Label(root)
output_image_label.pack(pady=10)

# Labels for displaying the randomized outfit
top_label = tk.Label(root)
top_label.pack(pady=5)
top_name_label = tk.Label(root, text="")
top_name_label.pack(pady=5)
bottom_label = tk.Label(root)
bottom_label.pack(pady=5)
bottom_name_label = tk.Label(root, text="")
bottom_name_label.pack(pady=5)
shoes_label = tk.Label(root)
shoes_label.pack(pady=5)
shoes_name_label = tk.Label(root, text="")
shoes_name_label.pack(pady=5)

# Label to display status
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# Randomize the outfit
randomize_button = tk.Button(root, text="Randomize Outfit", command=randomize_outfit)
randomize_button.pack(pady=5)

# Favorite the outfit
favorite_button = tk.Button(root, text="Favorite Outfit", command=favorite_outfit, state=tk.DISABLED)
favorite_button.pack(pady=5)

# View uploaded images
view_button = tk.Button(root, text="View Uploaded Images", command=view_uploaded_images)
view_button.pack(pady=5)

# View favorite outfits
view_favorites_button = tk.Button(root, text="View Favorite Outfits", command=view_favorites)
view_favorites_button.pack(pady=5)

# GUI loop
root.mainloop()
