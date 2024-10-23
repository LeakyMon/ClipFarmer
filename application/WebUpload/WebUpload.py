import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import requests
import sys
from WebUpload.YTUpload.yt import upload_to_youtube  # Import the upload function

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
        ytpath = os.path.join("WebUpload", "icons", "youtube.png")
        tiktokpath = os.path.join("WebUpload", "icons", "tiktok.png")
        instagrampath = os.path.join("WebUpload", "icons", "instagram.png")
        xpath = os.path.join("WebUpload", "icons", "twitter.png")

        # Load images for the buttons
        youtube_img = self.load_image(ytpath)
        tiktok_img = self.load_image(tiktokpath)
        instagram_img = self.load_image(instagrampath)
        x_img = self.load_image(xpath)

        # Create buttons with images
        self.youtube_button = ctk.CTkButton(self.main_frame, text="", image=youtube_img, command=self.upload_to_youtube)
        self.tiktok_button = ctk.CTkButton(self.main_frame, text="", image=tiktok_img, command=self.upload_to_tiktok)
        self.instagram_button = ctk.CTkButton(self.main_frame, text="", image=instagram_img, command=self.upload_to_instagram)
        self.x_button = ctk.CTkButton(self.main_frame, text="", image=x_img, command=self.upload_to_x)

        # Grid layout for buttons
        self.youtube_button.grid(row=0, column=0, padx=10, pady=10)
        self.tiktok_button.grid(row=0, column=1, padx=10, pady=10)
        self.instagram_button.grid(row=0, column=2, padx=10, pady=10)
        self.x_button.grid(row=0, column=3, padx=10, pady=10)

        # Frame for upload information fields
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=20)

        self.videoToUpload = None

    def bringVideoToUpload(self, filename):
        print("here ", filename)
        self.videoToUpload = filename

    # Helper method to load images
    def load_image(self, image_path):
        # Load and resize image for the button
        image = Image.open(image_path)
        image = image.resize((50, 50))  # Resize the image to fit the button
        return ImageTk.PhotoImage(image)

    # Method to reset info frame before displaying platform-specific fields
    def reset_info_frame(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()

    def upload_to_youtube(self):
        self.reset_info_frame()
        print("Uploading to YouTube...")

        # YouTube specific prompts
        ctk.CTkLabel(self.info_frame, text="YouTube Video Name:").pack(pady=5)
        self.youtube_title_entry = ctk.CTkEntry(self.info_frame)
        self.youtube_title_entry.pack(pady=5)

        ctk.CTkLabel(self.info_frame, text="YouTube Description:").pack(pady=5)
        self.youtube_desc_entry = ctk.CTkEntry(self.info_frame)
        self.youtube_desc_entry.pack(pady=5)

        # Add an Upload button for YouTube
        self.youtube_upload_button = ctk.CTkButton(self.info_frame, text="Upload to YouTube", command=self.handle_youtube_upload)
        self.youtube_upload_button.pack(pady=10)

    def upload_to_tiktok(self):
        self.reset_info_frame()
        print("Uploading to TikTok...")

        # TikTok specific prompts
        ctk.CTkLabel(self.info_frame, text="TikTok Video Title:").pack(pady=5)
        self.tiktok_title_entry = ctk.CTkEntry(self.info_frame)
        self.tiktok_title_entry.pack(pady=5)

        ctk.CTkLabel(self.info_frame, text="TikTok Hashtags:").pack(pady=5)
        self.tiktok_hashtags_entry = ctk.CTkEntry(self.info_frame)
        self.tiktok_hashtags_entry.pack(pady=5)

        # Add an Upload button for TikTok
        self.tiktok_upload_button = ctk.CTkButton(self.info_frame, text="Upload to TikTok", command=self.handle_tiktok_upload)
        self.tiktok_upload_button.pack(pady=10)

    def upload_to_instagram(self):
        self.reset_info_frame()
        print("Uploading to Instagram...")

        # Instagram specific prompts
        ctk.CTkLabel(self.info_frame, text="Instagram Caption:").pack(pady=5)
        self.instagram_caption_entry = ctk.CTkEntry(self.info_frame)
        self.instagram_caption_entry.pack(pady=5)

        # Add an Upload button for Instagram
        self.instagram_upload_button = ctk.CTkButton(self.info_frame, text="Upload to Instagram", command=self.handle_instagram_upload)
        self.instagram_upload_button.pack(pady=10)

    def upload_to_x(self):
        self.reset_info_frame()
        print("Uploading to X...")

        # X (formerly Twitter) specific prompts
        ctk.CTkLabel(self.info_frame, text="X Post Text:").pack(pady=5)
        self.x_text_entry = ctk.CTkEntry(self.info_frame)
        self.x_text_entry.pack(pady=5)

        # Add an Upload button for X
        self.x_upload_button = ctk.CTkButton(self.info_frame, text="Upload to X", command=self.handle_x_upload)
        self.x_upload_button.pack(pady=10)

    # Upload handlers for each platform
    def handle_youtube_upload(self):
        title = self.youtube_title_entry.get()
        description = self.youtube_desc_entry.get()
        
        # Assuming self.videoToUpload contains the file path to the video
        video_file = self.videoToUpload

        if not video_file:
            print("No video file selected for upload.")
            return
        
        if not title or not description:
            print("Title or description cannot be empty.")
            return

        print(f"Uploading to YouTube with title: {title}, description: {description}")

        # Call the upload_to_youtube function from yt.py
        upload_to_youtube(
            file=video_file,
            title=title,
            description=description,
            category="22",  # You can let the user select a category in your GUI if needed
            keywords="python, automation, youtube",  # Adjust as needed or let the user input keywords
            privacy_status="unlisted"  # Let the user select privacy status if needed
        )

    def handle_tiktok_upload(self):
        title = self.tiktok_title_entry.get()
        hashtags = self.tiktok_hashtags_entry.get()
        print(f"Uploading to TikTok with title: {title}, hashtags: {hashtags}")
        # Add your TikTok upload logic here

    def handle_instagram_upload(self):
        caption = self.instagram_caption_entry.get()
        print(f"Uploading to Instagram with caption: {caption}")
        # Add your Instagram upload logic here

    def handle_x_upload(self):
        post_text = self.x_text_entry.get()
        print(f"Uploading to X with post text: {post_text}")
        # Add your X upload logic here
