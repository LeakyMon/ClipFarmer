import customtkinter as ctk
from PIL import Image, ImageTk
import os

class CreateVideoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        # Title for Create Video page
        self.label = ctk.CTkLabel(self, text="Create Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)
        
        # Define mobile video aspect ratio (1080x1920, scaled down)
        self.video_canvas = ctk.CTkCanvas(self, width=270, height=480, bg="black")  # Scaled down by a factor of 4
        self.video_canvas.pack(pady=20)
        
        # Add a border around the video box (optional)
        self.video_canvas.create_rectangle(2, 2, 268, 478, outline="white", width=2)

        # Scrollable frame for additional controls
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=400, height=200)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Load folder image
        image_path = os.path.join("..", "images", "folder.jpg")
        self.folder_image = Image.open(image_path)
        self.folder_image_resized = self.folder_image.resize((50, 50))  # Resize the folder image to fit the buttons
        self.folder_photo = ImageTk.PhotoImage(self.folder_image_resized)

        # Create two folders: Background and Overlay
        self.create_folder_button("Background", self.folder_photo)
        self.create_folder_button("Overlay", self.folder_photo)

    def create_folder_button(self, name, image):
        # Create folder button in the scrollable frame
        folder_button = ctk.CTkButton(self.scrollable_frame, image=image, text=name, compound="left", command=lambda: self.open_folder(name))
        folder_button.pack(pady=10, padx=10, anchor="w")

    def open_folder(self, folder_name):
        print(f"Opening {folder_name} folder...")
        # You can add more functionality here (e.g., show files or open a new frame)
