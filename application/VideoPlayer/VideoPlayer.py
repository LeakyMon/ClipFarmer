import customtkinter as ctk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import os
import cv2
import pygame

class VideoPlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.video_file = None  # To store the selected video file
        self.cap = None  # To store the OpenCV video capture object
        self.is_playing = False
        self.audio_file = None  # To store the extracted audio file

        # Initialize pygame for audio playback
        pygame.mixer.init()

        # Create the title label
        self.title_label = ctk.CTkLabel(self, text="Video Player", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Create a frame to display the video
        self.video_frame = ctk.CTkFrame(self, width=640, height=360, fg_color="black")
        self.video_frame.pack(pady=20)

        # Create a canvas to display the video frames
        self.video_canvas = ctk.CTkCanvas(self.video_frame, width=640, height=360, bg="black")
        self.video_canvas.pack()

        # Create a frame for the control buttons (play, pause, etc.)
        self.control_frame = ctk.CTkFrame(self)  # New frame for buttons
        self.control_frame.pack(pady=10)  # Place the control frame below the video

        # Create buttons for control
        self.play_button = ctk.CTkButton(self.control_frame, text="Play", command=self.play_video)
        self.play_button.grid(row=0, column=0, padx=10)

        self.pause_button = ctk.CTkButton(self.control_frame, text="Pause", command=self.pause_video)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.restart_button = ctk.CTkButton(self.control_frame, text="Restart", command=self.restart_video)
        self.restart_button.grid(row=0, column=2, padx=10)

        self.open_button = ctk.CTkButton(self.control_frame, text="Open Video", command=self.open_video_file)
        self.open_button.grid(row=0, column=3, padx=10)

        # Create a volume slider
        self.volume_slider = ctk.CTkSlider(self, from_=0, to=1, number_of_steps=100, command=self.set_volume)
        self.volume_slider.set(1)  # Set default volume to 100%
        self.volume_slider.pack(pady=10)

    def open_video_file(self):
        """Open a file dialog to choose a video file."""
        video_file = filedialog.askopenfilename(
            title="Select Video",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if video_file:
            self.video_file = video_file
            self.load_video(self.video_file)

    def load_video(self, filepath):
        """Load the selected video, extract audio, and display the video."""
        self.video_file = filepath  # Use the provided filepath
        self.cap = cv2.VideoCapture(self.video_file)  # Open the video file

        # Extract and save audio from the video file
        self.extract_audio()

        self.is_playing = True
        self.play_video()  # Start playing the video

    def extract_audio(self):
        """Extract audio from the video file and save it as a temporary .wav file."""
        if self.video_file:
            # Extract the audio using moviepy
            video_clip = VideoFileClip(self.video_file)
            audio = video_clip.audio
            self.audio_file = "temp_audio.wav"  # Save audio as a temporary wav file
            audio.write_audiofile(self.audio_file)

            # Load the extracted audio into pygame
            pygame.mixer.music.load(self.audio_file)  # Load the extracted audio
            pygame.mixer.music.set_volume(1)  # Set default volume to 100%

    def play_video(self):
        """Play the video and start audio playback."""
        if self.cap and self.is_playing:
            # Play audio if it's not already playing
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()  # Play the audio

            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 360))
                frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_image)
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_canvas.create_image(0, 0, anchor="nw", image=img_tk)
                self.video_canvas.image = img_tk  # Keep reference to avoid garbage collection

                # Continue playing after a delay
                self.after(30, self.play_video)
            else:
                self.is_playing = False
                pygame.mixer.music.stop()  # Stop the audio when the video ends

    def pause_video(self):
        """Pause the video and audio playback."""
        self.is_playing = False
        pygame.mixer.music.pause()  # Pause the audio

    def restart_video(self):
        """Restart the video and audio from the beginning."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            pygame.mixer.music.rewind()  # Restart the audio
            self.is_playing = True
            self.play_video()

    def set_volume(self, volume):
        """Adjust the audio volume."""
        pygame.mixer.music.set_volume(float(volume))  # Set the volume based on slider position

    def on_closing(self):
        """Release video capture and stop audio when the window is closed."""
        if self.cap:
            self.cap.release()
        pygame.mixer.music.stop()  # Stop the audio
        if self.audio_file and os.path.exists(self.audio_file):
            os.remove(self.audio_file)  # Clean up the temporary audio file
