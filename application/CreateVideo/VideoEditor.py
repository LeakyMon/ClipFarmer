import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import requests
import sys
from .VideoGenerator import VideoGenerator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.firebase import get_videos_from_folder  # Import function to fetch videos
### --- BOTTOM AUDIO IS SECOND CLIP --- ###
from CreateVideo.VideoGenerator import VideoGenerator  # Import the VideoGenerator class

class CreateVideoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Variables to store selected video data and thumbnails
        self.first_video_data = None
        self.second_video_data = None
        self.first_thumbnail = None
        self.second_thumbnail = None
        self.script_selection = None
        self.music_selection = None
        self.script = None

        self.modifications = {
            "subtitles_top": True,
            "subtitles_second_clip": False,
            "audio_top": False,
            "audio_second_clip": False,
            "caption": '',
            "duration":'',
            "length":0,
            "title":'',
            "single_video": False,
            "letterbox": False,
            "script_text": None
        }
        self.emoji = False
        # Title for Create Video page (centered)
        self.label = ctk.CTkLabel(self, text="Create Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=10)

        # Main container for canvas and modifications
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=15)

        # Video canvas (centered middle)
        self.video_canvas = ctk.CTkCanvas(self.main_frame, width=270, height=480, bg="black")  # Scaled down by a factor of 4
        self.video_canvas.grid(row=0, column=0, padx=20)

        # Modifications frame (to the right of video canvas)
        # Define the modifications frame
        self.modifications_frame = ctk.CTkFrame(self.main_frame)
        self.modifications_frame.grid(row=0, column=2, padx=20, pady=20, sticky="n")

        self.submit_frame = ctk.CTkFrame(self.main_frame)
        self.submit_frame.grid(row=0, column=8, padx=20, pady=20,sticky="w")

        #self.submit_button = ctk.CTkButton(self.submit_frame)
        #self.submit_button.pack( fill="both", expand=True, padx=10, pady=10)


        image_path = os.path.join("..", "images", "folder.jpg")
        self.script_path = os.path.join("..", "images", "script.png")

        self.folder_image = Image.open(image_path)
        self.folder_image_resized = self.folder_image.resize((50, 50))  # Resize the folder image to fit the buttons
        self.folder_photo = ImageTk.PhotoImage(self.folder_image_resized)


        # Scrollable frame for folder selection (below canvas and modifications)
       # Scrollable frame for folder selection (left side for videos)
        # Container frame for both scrollable frames (for videos and music)
        self.scrollable_container = ctk.CTkFrame(self)
        self.scrollable_container.pack(fill="both", expand=True, padx=20, pady=15)

        # Scrollable frame for folder selection (left side for videos)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.scrollable_container, width=400, height=200)
        self.scrollable_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Scrollable frame for music selection (right side for music)
        self.scrollable_frame_music = ctk.CTkScrollableFrame(self.scrollable_container, width=400, height=200)
        self.scrollable_frame_music.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        # Create two folders: Background and Overlay for videos
        self.create_folder_button("Background", self.folder_photo)
        self.create_folder_button("Overlay", self.folder_photo)

        # Add music-related content in the second scrollable frame
        self.create_music_folder_button("Music", self.folder_photo, self.scrollable_frame_music)
        self.create_scripts_button("Scripts", self.folder_photo, self.scrollable_frame_music)


        self.create_mods()

    def create_folder_button(self, name, image):
        """Creates a button for each folder."""
        folder_button = ctk.CTkButton(self.scrollable_frame, image=image, text=name, compound="left", command=lambda: self.open_folder(name))
        folder_button.pack(pady=10, padx=10, anchor="w")
    def create_music_folder_button(self, name, image):
        """Creates a button for each folder."""
        folder_button = ctk.CTkButton(self.scrollable_frame_music, image=image, text=name, compound="right", command=lambda: self.open_folder(name))
        folder_button.pack(pady=10, padx=10, anchor="w")
    

    def open_folder(self, folder_name):
        """Opens the selected folder and displays its videos."""
        self.current_folder = folder_name
        print(f"Opening {folder_name} folder...")

        # Clear current frame content
        if folder_name == "Background" or folder_name == "Overlay":
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
        elif folder_name == "Scripts":
            self.open_scripts_folder(folder_name)
        else:
            self.open_music_folder
            

    def create_mods(self):
        # Add the subtitle switch to the modifications frame
        self.subtitle_var1 = ctk.BooleanVar(value=False)
        self.subtitle_var_top = ctk.CTkSwitch(master=self.modifications_frame, text="Subtitles Vid 1", variable=self.subtitle_var1)
        self.subtitle_var_top.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        self.subtitle_var2 = ctk.BooleanVar(value=False)
        self.subtitle_var_bottom = ctk.CTkSwitch(master=self.modifications_frame, text="Subtitles Vid 2", variable=self.subtitle_var2)
        self.subtitle_var_bottom.grid(row=1, column=0, pady=10, padx=20, sticky="w")

        self.audio_var_top = ctk.BooleanVar(value=False)
        self.audio_top = ctk.CTkSwitch(master=self.modifications_frame, text="Audio 1", variable=self.audio_var_top)
        self.audio_top.grid(row=2, column=0, pady=10, padx=20, sticky="w")

        self.audio_var_bottom = ctk.BooleanVar(value=False)
        self.audio_bottom = ctk.CTkSwitch(master=self.modifications_frame, text="Audio 2", variable=self.audio_var_bottom)
        self.audio_bottom.grid(row=3, column=0, pady=10, padx=20, sticky="w")

        self.letterbox_var = ctk.BooleanVar(value=False)
        self.letterbox = ctk.CTkSwitch(master=self.modifications_frame, text="Letterbox", variable=self.letterbox_var)
        self.letterbox.grid(row=4, column=0, pady=10, padx=20, sticky="w")

        self.caption_var = ctk.CTkEntry(self.modifications_frame, placeholder_text="Enter Caption")
        self.caption_var.grid(row=5, column=0, pady=10, padx=20, sticky="w")

        self.duration_entry = ctk.CTkEntry(self.modifications_frame, placeholder_text="Enter Duration")
        self.duration_entry.grid(row=6, column=0, padx=(20, 0), pady=(10, 10), sticky="w")

        self.length_entry = ctk.CTkEntry(self.modifications_frame, placeholder_text="Enter Length")
        self.length_entry.grid(row=7, column=0, padx=(20, 0), pady=(10, 10), sticky="w")

        self.title_entry = ctk.CTkEntry(self.modifications_frame, placeholder_text="Enter Title")
        self.title_entry.grid(row=8, column=0, padx=(20, 0), pady=(10, 10), sticky="w")


        self.script_textbox = ctk.CTkTextbox(self.submit_frame, width=200, height=200)
        self.script_textbox.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        # Move the buttons to the bottom-right of the frame
        self.undo_button = ctk.CTkButton(self.submit_frame, text="Undo", fg_color="orange", command=self.undo_last_video)
        self.undo_button.grid(row=1, column=0, pady=10, padx=20, sticky="w")

        self.emoji_button = ctk.CTkButton(self.submit_frame, text="Add Emoji", fg_color="blue", command=self.add_emoji)
        self.emoji_button.grid(row=2, column=0, pady=10, padx=20, sticky="w")

        self.submit_button = ctk.CTkButton(self.submit_frame, text="Submit", fg_color="blue", command=self.submit)
        self.submit_button.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        
    def add_emoji(self):
        print("adding emoji")
        self.emoji = True
        if self.emoji == True:
            emoji_window = tk.Toplevel(self)
            emoji_window.title("Select Emoji")
            self.modifications["emoji"] = True
            emojis = ["😂", "😊", "👍", "🔥", "❤️", "🎉", "😎"]
            for emoji in emojis:
                emoji_button = ctk.CTkButton(emoji_window, text=emoji, command=lambda e=emoji: self.add_emoji_to_caption(e))
                emoji_button.pack(pady=5, padx=10)

    def add_emoji_to_caption(self, emoji):
        """Adds the selected emoji to the caption entry."""
        current_caption = self.caption_var.get()
        self.caption_var.delete(0, tk.END)
        self.caption_var.insert(0, current_caption + emoji)

    def update_modifications(self):
    # Check if the title is provided
        if not self.title_entry.get():
            print("Add title")
            return False  # Stop further execution if the title is missing

        # Check if both length and duration are missing
        if not self.duration_entry.get() and not self.length_entry.get():
            print("Add length or duration")
            return False # Stop further execution if both are missing

        # Proceed with updating the modifications if all checks pass
        self.modifications["subtitles_top"] = self.subtitle_var1.get()
        self.modifications["subtitles_second_clip"] = self.subtitle_var2.get()
        self.modifications["audio_top"] = self.audio_var_top.get()
        self.modifications["audio_second_clip"] = self.audio_var_bottom.get()
        self.modifications["caption"] = self.caption_var.get()
        self.modifications["duration"] = self.duration_entry.get()  # Will be empty if not provided
        self.modifications["length"] = int(self.length_entry.get()) if self.length_entry.get() else None
        self.modifications["title"] = self.title_entry.get()
        self.modifications["letterbox"] = self.letterbox_var.get()
        self.modifications["script_text"] = self.script

        # Check if there's a second video
        if self.first_video_data is None and self.second_video_data is None:
            print("Select a video")
            return False
        elif self.second_video_data is None:
            print("One video", self.first_video_data)
            self.modifications["single_video"] = True
        else:
            print("TWo video", self.first_video_data, self.second_video_data)
            self.modifications["single_video"] = False

        print(self.modifications)
        return True

    def fetch_videos_from_folder(self, folder_name):
        """Fetches videos from a local folder (or returns a hard-coded video for 'Overlay')."""

        return get_videos_from_folder(folder_name)
    """
        video_list = []

        if folder_name == "Overlay":
            # Hardcoded video and thumbnail for the "Overlay" folder
            video_list.append({
                'title': 'WorldOfTshirts',
                'thumbnail': 'https://firebasestorage.googleapis.com/v0/b/clipfarmer-f8a79.appspot.com/o/Overlay%2Fthumbnails%2FWorldOfTshirts.mp4_thumbnail.jpg?alt=media&token=5f427b45-ce7a-40fc-b6b9-4ecf51f564dc',
                'url': 'https://firebasestorage.googleapis.com/v0/b/clipfarmer-f8a79.appspot.com/o/Overlay%2Fvideos%2FWorldOfTshirts.mp4?alt=media&token=997f3735-a151-457a-8863-098f046c4c95'
            })
        if folder_name == "Background":
            video_list.append({
                'title': 'Minecraft',
                'thumbnail': "https://storage.googleapis.com/clipfarmer-f8a79.appspot.com/Background/thumbnails/Minecraft.mp4_thumbnail.jpg",
                'url': "https://storage.googleapis.com/clipfarmer-f8a79.appspot.com/Background/videos/Minecraft.mp4"
            })
        return video_list


    """

    """
    def fetch_videos_from_folder(self, folder_name):
        
        
    """

    def create_folder_view(self):
        """Restores the folder view."""
        # Clear current frame content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create folder buttons again
        self.create_folder_button("Background", self.folder_photo)
        self.create_folder_button("Overlay", self.folder_photo)
    def create_music_view(self):
        """Restores the folder view."""
        # Clear current frame content
        for widget in self.scrollable_frame_music.winfo_children():
            widget.destroy()

        # Create folder buttons again
        self.create_music_folder_button("Music", self.folder_photo, self.scrollable_frame_music)
        self.create_scripts_button("Script", self.folder_photo,self.scrollable_frame_music)

    def select_video(self, video):
        """When a video is selected, display it on the canvas."""
        print(f"Selected video: {video['title']}")

        # Load the thumbnail image
        thumbnail_image = Image.open(requests.get(video['thumbnail'], stream=True).raw)
        thumbnail_resized = thumbnail_image.resize((270, 240))  # Resize to fit half the canvas

        if self.first_video_data is None:
            # Set as first video
            print("Selected first video", video)
            self.first_video_data = video
            self.first_thumbnail = ImageTk.PhotoImage(thumbnail_image.resize((270, 480)))  # Full canvas size initially
            self.display_on_canvas()

        elif self.second_video_data is None:
            # Set as second video
            print("Selected second video", video)

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

    def submit(self):
        print("submitting with current mods")
        complete = self.update_modifications()
        if complete:
            video_generator = VideoGenerator(
            modifications=self.modifications,        # Pass modifications dictionary
            first_video_data=self.first_video_data,  # Pass the first selected video data
            second_video_data=self.second_video_data # Pass the second selected video data (or None if single video)
            )
        
        # After the video generation process is completed
            print(f"Video generated and saved to: {video_generator.filepath}")
            self.reset()
            video_generator.cleanup_temp_files()
            self.controller.videoplayer_frame.load_video(video_generator.getFilepath())
            self.controller.select_frame_by_name("Video Player")
        else:
            return
        ### --- HERE IS WHERE WE NEED TO RENDER THE VIDEO ACCORDING TO THE MODIFICATIONS --- ###

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

    def create_scripts_button(self,name,image,frame):
        music_button = ctk.CTkButton(frame, image=image, text=name, compound="left", command=lambda: self.open_scripts_folder(name))
        music_button.pack(pady=10, padx=10, anchor="w")


    def open_music_folder(self,name):
        print("POpne")
    def open_scripts_folder(self,name):
        self.current_folder = name
        print(f"Opening {name} folder...")

        # Clear current frame content
        for widget in self.scrollable_frame_music.winfo_children():
            widget.destroy()

        # Fetch video data from Firestore
        script_data = self.fetch_videos_from_folder(name)

        # Display video thumbnails and titles
        for script in script_data:
            script_frame = ctk.CTkFrame(self.scrollable_frame_music)
            script_frame.pack(pady=10, padx=10, anchor="w")

            # Fetch the thumbnail image from the URL
            self.script_image = Image.open(self.script_path)
            self.script_image_resized = self.script_image.resize((50, 50))  # Resize the folder image to fit the buttons
            self.script_photo = ImageTk.PhotoImage(self.script_image_resized)

            script_label = ctk.CTkLabel(script_frame, image=self.script_photo, text="")
            script_label.image = self.script_photo  # Keep a reference to avoid garbage collection
            script_label.grid(row=0, column=0, padx=10)

            title_label = ctk.CTkLabel(script_frame, text=script['title'], font=("Arial", 14))
            title_label.grid(row=0, column=1, padx=10)

            select_button = ctk.CTkButton(script_frame, text="Select", command=lambda v=script: self.select_script(v))
            select_button.grid(row=0, column=2, padx=10)

        # Add Back Button
        music_back_button = ctk.CTkButton(self.scrollable_frame_music, text="Back", command=self.create_music_view)
        music_back_button.pack(pady=10, padx=10, anchor="w")

    def select_script(self, script):
        print(f"Selected script: {script['title']}")
    
    # Clear any existing text in the textbox
        self.script_textbox.delete("1.0", tk.END)  # Clear the textbox content
    
    # Insert the selected script's text
        self.script_textbox.insert(tk.END, script['text'])  # Insert the script text into the textbox
        self.script = script['text']
    def reset(self):
        print("Resetting")
        
        # Reset video data and thumbnails
        self.first_video_data = None
        self.second_video_data = None
        self.first_thumbnail = None
        self.second_thumbnail = None
        
        # Reset modifications dictionary
        self.modifications = {
            "subtitles_top": False,
            "subtitles_second_clip": False,
            "audio_top": False,
            "audio_second_clip": False,
            "caption": '',
            "duration": '',
            "length": 0,
            "title": '',
            "single_video": False,
            "letterbox":False,
            "script_text":None
        }

        # Reset the canvas (remove displayed videos)
        self.video_canvas.delete("all")
        
        # Reset switches to their default values (False or unchecked)
        self.subtitle_var1.set(False)  # Reset the "Subtitles Top" switch
        self.subtitle_var2.set(False)  # Reset the "Subtitles Bottom" switch
        self.audio_var_top.set(False)  # Reset the "Top Audio" switch
        self.audio_var_bottom.set(False)  # Reset the "Bottom Audio" switch
        self.letterbox_var.set(False)
        # Clear text input fields
        self.caption_var.delete(0, tk.END)  # Clear the caption entry
        self.duration_entry.delete(0, tk.END)  # Clear the duration entry
        self.length_entry.delete(0, tk.END)  # Clear the length entry
        self.title_entry.delete(0, tk.END)  # Clear the title entry
        self.script_textbox.delete("1.0", tk.END)  # Clear the textbox content
        self.script_text = None
        

