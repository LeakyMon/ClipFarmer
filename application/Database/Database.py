import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
from backend.firebase import (
    get_videos_from_folder, delete_video_from_firebase,
    check_if_title_exists, check_if_song_exists, add_video_metadata, upload_file_to_storage,
    delete_song_from_firebase, add_song_metadata
)

class ModifyDatabase(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Access the main controller (App)

        self.label = ctk.CTkLabel(self, text="Modify Database", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Create the navigation bar at the top
        self.navbar = ctk.CTkFrame(self)
        self.navbar.pack(fill="x", padx=10, pady=10)

        # Add navigation buttons
        self.folders_button = ctk.CTkButton(self.navbar, text="Folders", command=self.show_folders)
        self.folders_button.pack(side="left", padx=5)

        self.videos_button = ctk.CTkButton(self.navbar, text="Videos", command=self.show_videos)
        self.videos_button.pack(side="left", padx=5)

        self.songs_button = ctk.CTkButton(self.navbar, text="Songs", command=self.show_songs)
        self.songs_button.pack(side="left", padx=5)

        self.thumbnails_button = ctk.CTkButton(self.navbar, text="Thumbnails", command=self.show_thumbnails)
        self.thumbnails_button.pack(side="left", padx=5)

        self.summary_button = ctk.CTkButton(self.navbar, text="Summary", command=self.show_summary)
        self.summary_button.pack(side="left", padx=5)

        # Main content area (below the navigation bar)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.folder_list = []

    ### --- Functions to Update the Main Frame Content --- ###
    
    def clear_main_frame(self):
        """Clear the contents of the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_folders(self):
        """Display folder management options with styled folder icons and video count."""
        self.clear_main_frame()

        # Create column headers
        headers_frame = ctk.CTkFrame(self.main_frame)
        headers_frame.pack(fill="x", padx=20, pady=10)

        # Folder column title
        ctk.CTkLabel(headers_frame, text="Folder", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Gap for spacing between the Folder and Number of Videos columns
        ctk.CTkLabel(headers_frame, text="").grid(row=0, column=1, padx=200)  # Adjust the width of the gap as needed

        # Number of Videos column title
        ctk.CTkLabel(headers_frame, text="Number of Videos", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Load and prepare the folder image
        image_path = os.path.join("..", "images", "folder.jpg")
        self.folder_image = Image.open(image_path)
        self.folder_image_resized = self.folder_image.resize((50, 50))  # Resize the folder image to fit the buttons
        self.folder_photo = ImageTk.PhotoImage(self.folder_image_resized)

        # Access the folders from the controller (main app)
        self.folder_list = self.controller.folders

        # Create a frame inside main_frame for organizing folder entries
        folder_frame = ctk.CTkFrame(self.main_frame)
        folder_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Display each folder in the main_frame with the folder icon and the number of videos
        for idx, folder in enumerate(self.folder_list):
            folder_container = ctk.CTkFrame(folder_frame)
            folder_container.pack(fill="x", pady=5)

            # Add folder icon
            folder_icon = tk.Label(folder_container, image=self.folder_photo)
            folder_icon.pack(side="left", padx=10)

            # Add folder name next to the icon
            folder_name_label = ctk.CTkLabel(folder_container, text=folder, font=ctk.CTkFont(size=14))
            folder_name_label.pack(side="left", padx=10)

            # Add a gap between the folder name and number of videos
            ctk.CTkLabel(folder_container, text="").pack(side="left", padx=200)  # Adjust gap width as needed

            # Number of videos for this folder (you can customize how this is calculated)
            #num_videos = len([video for video in self.controller.videos if video['folder'] == folder])  # Example
            #num_videos_label = ctk.CTkLabel(folder_container, text=str(num_videos), font=ctk.CTkFont(size=14))
            #num_videos_label.pack(side="left", padx=10)



    def show_videos(self):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Video Management").pack(pady=10)

        # Access the folders from the controller (main app) instead of making redundant calls
        self.video_list = self.controller.videos

        # Display each folder in the main_frame
        for video in self.video_list:
            ctk.CTkLabel(self.main_frame, text=video['title']).pack(pady=5)

        self.add_video_button = ctk.CTkButton(self.main_frame, text="Add Video", command=self.add_video)
        self.add_video_button.pack(padx=5, pady=5)

        self.delete_video_button = ctk.CTkButton(self.main_frame, text="Delete Video", command=self.delete_video)
        self.delete_video_button.pack(padx=5, pady=5)

        

    def show_songs(self):
        """Display song management options."""
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Song Management").pack(pady=10)

        # Access the songs from the controller (main app)
        self.songs_list = self.controller.songs

        for song in self.songs_list:
            ctk.CTkLabel(self.main_frame, text=song['title']).pack(pady=5)

        # Display song management options
        #self.view_music_button = ctk.CTkButton(self.main_frame, text="View Songs", command=self.view_music)
        #self.view_music_button.pack(padx=5, pady=5)

        self.add_music_button = ctk.CTkButton(self.main_frame, text="Add Song", command=self.add_music)
        self.add_music_button.pack(padx=5, pady=5)

        self.delete_music_button = ctk.CTkButton(self.main_frame, text="Delete Song", command=self.delete_music)
        self.delete_music_button.pack(padx=5, pady=5)

        

    def show_thumbnails(self):
        self.clear_main_frame()

        self.display_thumbnail_list(self.controller.thumbnails)

        self.add_thumbnail = ctk.CTkButton(self.main_frame, text="Add Thumbnail", command=self.add_thumbnail_1)
        self.add_thumbnail.pack(padx=5, pady=5)

        self.delete_thumbnail = ctk.CTkButton(self.main_frame, text="Delete Thumbnail", command=self.delete_thumbnail_1)
        self.delete_thumbnail.pack(padx=5, pady=5)

    def add_thumbnail_1(self):
        print("adding thumbnail")
    def delete_thumbnail_1(self):
        print("deleting thumbnail")
    # Function to View Videos
    def view_videos(self):
        self.display_list(self.controller.videos)

    # Function to View Songs
    def view_music(self):
        self.display_list(self.controller.songs)

    def show_summary(self):
        self.clear_main_frame()
        self.show_folders()
        self.show_videos()
        self.show_songs()
        self.show_thumbnails()


    # Function to Display List (either Videos or Music)
    def display_list(self, items):
        list_window = ctk.CTkToplevel(self)
        list_window.title("List of Items")
        
        listbox = tk.Listbox(list_window, width=50, height=20)
        listbox.pack(pady=20)
        
        for item in items:
            listbox.insert(tk.END, f"Title: {item['title']}, URL: {item['url']}")

    def display_thumbnail_list(self,thumbnails):
        self.clear_main_frame()

        ctk.CTkLabel(self.main_frame, text="Thumbnail Management").pack(pady=10)

        # Access the folders from the controller (main app) instead of making redundant calls
        self.thumbnail_list = self.controller.thumbnails

        # Display each folder in the main_frame
        for thumbnail in self.thumbnail_list:
            ctk.CTkLabel(self.main_frame, text=thumbnail).pack(pady=5)

    def add_video(self, video):
        print("add video")
    def delete_video(self, video):
        print("del video")
    def add_music(self, music):
        print("add music")
    def delete_music(self, music):
        print("del music")