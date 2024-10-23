import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import requests
import sys
class UploadToWeb(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Upload to Web", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # Main container for canvas and modifications
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20)

        # Paths for the button images
        ytpath = os.path.join("WebUpload","icons", "youtube.png")
        tiktokpath = os.path.join("WebUpload", "icons", "tiktok.png")
        instagrampath = os.path.join( "WebUpload","icons", "instagram.png")
        xpath = os.path.join("WebUpload","icons", "twitter.png")

        # Load images for the buttons
        youtube_img = self.load_image(ytpath)
        tiktok_img = self.load_image(tiktokpath)
        instagram_img = self.load_image(instagrampath)
        x_img = self.load_image(xpath)

        # Create buttons with images
        self.youtube_button = ctk.CTkButton(self.main_frame, text="",image=youtube_img, command=self.upload_to_youtube)
        self.tiktok_button = ctk.CTkButton(self.main_frame, text="",image=tiktok_img, command=self.upload_to_tiktok)
        self.instagram_button = ctk.CTkButton(self.main_frame, text="",image=instagram_img, command=self.upload_to_instagram)
        self.x_button = ctk.CTkButton(self.main_frame, text="",image=x_img, command=self.upload_to_x)

        # Grid layout for buttons
        self.youtube_button.grid(row=0, column=0, padx=10, pady=10)
        self.tiktok_button.grid(row=0, column=1, padx=10, pady=10)
        self.instagram_button.grid(row=0, column=2, padx=10, pady=10)
        self.x_button.grid(row=0, column=3, padx=10, pady=10)

    # Helper method to load images
    def load_image(self, image_path):
        # Load and resize image for the button
        image = Image.open(image_path)
        image = image.resize((50, 50))  # Resize the image to fit the button
        return ImageTk.PhotoImage(image)

    def upload_to_youtube(self):
        print("Uploading to YouTube...")

    def upload_to_tiktok(self):
        print("Uploading to TikTok...")

    def upload_to_instagram(self):
        print("Uploading to Instagram...")

    def upload_to_x(self):
        print("Uploading to X...")
