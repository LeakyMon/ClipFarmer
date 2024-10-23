import customtkinter as ctk
import os
from PIL import Image, ImageTk
from backend.firebase import get_videos_from_folder, delete_video_from_firebase  # Import the new delete function
import requests

class LibraryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_video = None  # Track the selected video
        self.create_folder_view()

    def create_folder_view(self):
        """Creates the folder view showing Background and Overlay folders."""
        # Clear current frame content
        for widget in self.winfo_children():
            widget.destroy()

        # Title
        self.title_label = ctk.CTkLabel(self, text="My Videos", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Create folder buttons
        self.background_button = ctk.CTkButton(self, text="Background", command=lambda: self.display_folder_content("Background"))
        self.background_button.pack(pady=20)

        self.overlay_button = ctk.CTkButton(self, text="Overlay", command=lambda: self.display_folder_content("Overlay"))
        self.overlay_button.pack(pady=20)

        # Footer for back button
        self.create_footer()

    def create_footer(self):
        """Creates a footer with a Back button."""
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(side="bottom", pady=20)

        self.back_button = ctk.CTkButton(self.footer_frame, text="Back", command=self.create_folder_view)
        self.back_button.pack()

    def display_folder_content(self, folder_name):
        """Displays the thumbnails and titles of the videos in the selected folder."""
        # Clear current frame content
        for widget in self.winfo_children():
            widget.destroy()

        # Title
        self.title_label = ctk.CTkLabel(self, text=f"{folder_name} Videos", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Fetch video data from Firestore
        video_data = self.fetch_videos_from_folder(folder_name)

        # Display video thumbnails and titles
        for index, video in enumerate(video_data):
            video_frame = ctk.CTkFrame(self)
            video_frame.pack(pady=10)

            # Fetch the thumbnail image from the URL
            thumbnail_image = Image.open(requests.get(video['thumbnail'], stream=True).raw)
            thumbnail_resized = thumbnail_image.resize((100, 100))
            thumbnail = ImageTk.PhotoImage(thumbnail_resized)

            thumbnail_label = ctk.CTkLabel(video_frame, image=thumbnail, text="")
            thumbnail_label.image = thumbnail  # Keep a reference to avoid garbage collection
            thumbnail_label.grid(row=0, column=0, padx=10)

            title_label = ctk.CTkLabel(video_frame, text=video['title'], font=("Arial", 14))
            title_label.grid(row=0, column=1, padx=10)

            # Select Video Button
            select_button = ctk.CTkButton(video_frame, text="Select", command=lambda v=video: self.select_video(v, folder_name))
            select_button.grid(row=0, column=2, padx=10)

        # Footer for back button
        self.create_footer()

    def select_video(self, video, folder_name):
        """Selects a video and shows the option to delete it."""
        # Clear current frame content
        for widget in self.winfo_children():
            widget.destroy()

        self.selected_video = video

        # Title
        self.title_label = ctk.CTkLabel(self, text=f"Selected Video: {video['title']}", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Display thumbnail and title
        thumbnail_image = Image.open(requests.get(video['thumbnail'], stream=True).raw)
        thumbnail_resized = thumbnail_image.resize((150, 150))
        thumbnail = ImageTk.PhotoImage(thumbnail_resized)

        thumbnail_label = ctk.CTkLabel(self, image=thumbnail, text="")
        thumbnail_label.image = thumbnail  # Keep a reference to avoid garbage collection
        thumbnail_label.pack(pady=10)

        title_label = ctk.CTkLabel(self, text=video['title'], font=("Arial", 18))
        title_label.pack(pady=10)

        # Delete Button
        delete_button = ctk.CTkButton(self, text="Delete Video", fg_color="red", command=lambda: self.delete_video(video, folder_name))
        delete_button.pack(pady=10)

        # Footer for back button
        self.create_footer()

    def delete_video(self, video, folder_name):
        """Deletes the selected video from Firestore and Firebase Storage."""
        # Call the delete function from firebase.py
        file_name = f"{video['title']}.mp4"  # Assuming the video file is named with its title
        thumbnail_name = f"{video['title']}.mp4_thumbnail.jpg"  # Updated to match the actual thumbnail naming

        delete_video_from_firebase(video['id'], folder_name, file_name, thumbnail_name)

        # After deletion, return to the folder view
        self.create_folder_view()


    def fetch_videos_from_folder(self, folder_name):
        """Fetches videos from the folder by querying Firestore."""
        return get_videos_from_folder(folder_name)
