import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import requests
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.firebase import get_videos_from_folder  # Import function to fetch videos


class CreateVideoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Variables to store selected video data and thumbnails
        self.first_video_data = None
        self.second_video_data = None
        self.first_thumbnail = None
        self.second_thumbnail = None

        self.modifications = {
            "subtitles": True,
            "caption": False,
            "subclips": False,
            "music": False,
            "upload_to_yt": False,
            "save_copy": False,
            "single_video": False
        }

        # Title for Create Video page (centered)
        self.label = ctk.CTkLabel(self, text="Create Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # Main container for canvas and modifications
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20)

        # Video canvas (centered middle)
        self.video_canvas = ctk.CTkCanvas(self.main_frame, width=270, height=480, bg="black")  # Scaled down by a factor of 4
        self.video_canvas.grid(row=0, column=0, padx=20)

        # Modifications frame (to the right of video canvas)
        # Define the modifications frame
        self.modifications_frame = ctk.CTkFrame(self.main_frame)
        self.modifications_frame.grid(row=0, column=2, padx=20, pady=20, sticky="n")


        image_path = os.path.join("..", "images", "folder.jpg")
        self.folder_image = Image.open(image_path)
        self.folder_image_resized = self.folder_image.resize((50, 50))  # Resize the folder image to fit the buttons
        self.folder_photo = ImageTk.PhotoImage(self.folder_image_resized)


        # Scrollable frame for folder selection (below canvas and modifications)
       # Scrollable frame for folder selection (left side for videos)
        # Container frame for both scrollable frames (for videos and music)
        self.scrollable_container = ctk.CTkFrame(self)
        self.scrollable_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Scrollable frame for folder selection (left side for videos)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.scrollable_container, width=400, height=200)
        self.scrollable_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Scrollable frame for music selection (right side for music)
        self.scrollable_frame_music = ctk.CTkScrollableFrame(self.scrollable_container, width=400, height=200)
        self.scrollable_frame_music.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create two folders: Background and Overlay for videos
        self.create_folder_button("Background", self.folder_photo)
        self.create_folder_button("Overlay", self.folder_photo)

        # Add music-related content in the second scrollable frame
        self.create_music_folder_button("Music", self.folder_photo, self.scrollable_frame_music)

        self.create_mods()

    def create_folder_button(self, name, image):
        """Creates a button for each folder."""
        folder_button = ctk.CTkButton(self.scrollable_frame, image=image, text=name, compound="left", command=lambda: self.open_folder(name))
        folder_button.pack(pady=10, padx=10, anchor="w")

    def open_folder(self, folder_name):
        """Opens the selected folder and displays its videos."""
        self.current_folder = folder_name
        print(f"Opening {folder_name} folder...")

        # Clear current frame content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Fetch video data from Firestore
        video_data = self.fetch_videos_from_folder(folder_name)

        # Display video thumbnails and titles
        for video in video_data:
            video_frame = ctk.CTkFrame(self.scrollable_frame)
            video_frame.pack(pady=10, padx=10, anchor="w")

            # Fetch the thumbnail image from the URL
            thumbnail_image = Image.open(requests.get(video['thumbnail'], stream=True).raw)
            thumbnail_resized = thumbnail_image.resize((100, 100))
            thumbnail = ImageTk.PhotoImage(thumbnail_resized)

            thumbnail_label = ctk.CTkLabel(video_frame, image=thumbnail, text="")
            thumbnail_label.image = thumbnail  # Keep a reference to avoid garbage collection
            thumbnail_label.grid(row=0, column=0, padx=10)

            title_label = ctk.CTkLabel(video_frame, text=video['title'], font=("Arial", 14))
            title_label.grid(row=0, column=1, padx=10)

            select_button = ctk.CTkButton(video_frame, text="Select", command=lambda v=video: self.select_video(v))
            select_button.grid(row=0, column=2, padx=10)

        # Add Back Button
        back_button = ctk.CTkButton(self.scrollable_frame, text="Back", command=self.create_folder_view)
        back_button.pack(pady=10, padx=10, anchor="w")

    def create_mods(self):
        # Add the subtitle switch to the modifications frame
        self.switch_var1 = ctk.BooleanVar(value=False)
        self.switch1 = ctk.CTkSwitch(master=self.modifications_frame, text="Subtitles", variable=self.switch_var1)
        self.switch1.grid(row=0, column=0, pady=10, padx=20, sticky="w")


        self.undo_button = ctk.CTkButton(self.modifications_frame, text="Undo", fg_color="orange",
                                 command=self.undo_last_video)
        
        self.undo_button.grid(row=1, column=0, pady=10, padx=20, sticky="w")
        #self.undo_button.pack_forget()  # Hide the undo button initially

    def fetch_videos_from_folder(self, folder_name):
        """Fetches videos from the folder by querying Firestore."""
        return get_videos_from_folder(folder_name)

    def create_folder_view(self):
        """Restores the folder view."""
        # Clear current frame content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create folder buttons again
        self.create_folder_button("Background", self.folder_photo)
        self.create_folder_button("Overlay", self.folder_photo)

    def select_video(self, video):
        """When a video is selected, display it on the canvas."""
        print(f"Selected video: {video['title']}")

        # Load the thumbnail image
        thumbnail_image = Image.open(requests.get(video['thumbnail'], stream=True).raw)
        thumbnail_resized = thumbnail_image.resize((270, 240))  # Resize to fit half the canvas

        if self.first_video_data is None:
            # Set as first video
            self.first_video_data = video
            self.first_thumbnail = ImageTk.PhotoImage(thumbnail_image.resize((270, 480)))  # Full canvas size initially
            self.display_on_canvas()

        elif self.second_video_data is None:
            # Set as second video
            self.second_video_data = video
            self.second_thumbnail = ImageTk.PhotoImage(thumbnail_resized)
            self.display_on_canvas(split=True)  # Now split the canvas when second video is added

        # Show the Undo button since we have at least one video
        #self.undo_button.grid(row=0,col=2,))
        self.create_folder_view()



    def display_on_canvas(self, split=False):
        """Displays the selected video thumbnails on the canvas."""
        self.video_canvas.delete("all")

        if split:
            # Split canvas: first video on bottom half, second video on top half
            if self.first_thumbnail:
                self.video_canvas.create_image(0, 240, anchor="nw", image=self.first_thumbnail)  # Bottom half
            if self.second_thumbnail:
                self.video_canvas.create_image(0, 0, anchor="nw", image=self.second_thumbnail)  # Top half
        else:
            # Only first video displayed fully
            if self.first_thumbnail:
                self.video_canvas.create_image(0, 0, anchor="nw", image=self.first_thumbnail)


    def undo_last_video(self):
        """Removes the last added video. If both videos are selected, remove the second; else remove the first."""
        if self.second_video_data is not None:
            # Remove second video
            self.second_video_data = None
            self.second_thumbnail = None
        elif self.first_video_data is not None:
            # Remove first video
            self.first_video_data = None
            self.first_thumbnail = None

        # Clear the canvas and update the display based on remaining videos
        self.video_canvas.delete("all")

        if self.first_thumbnail and not self.second_thumbnail:
            self.display_on_canvas()
        elif self.first_thumbnail and self.second_thumbnail:
            self.display_on_canvas(split=True)

        # Hide Undo button if both videos are removed
        if self.first_video_data is None and self.second_video_data is None:
            self.undo_button.pack_forget()


    def create_music_folder_button(self, name, image, frame):
        """Creates a button for each music folder in the specified frame."""
        music_button = ctk.CTkButton(frame, image=image, text=name, compound="left", command=lambda: self.open_music_folder(name))
        music_button.pack(pady=10, padx=10, anchor="w")

    def open_music_folder(self,name):
        print("POpne")
