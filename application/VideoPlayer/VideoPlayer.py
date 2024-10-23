import customtkinter as ctk
from tkinter import filedialog
from moviepy.editor import VideoFileClip
from PIL import Image, ImageTk
import os
import cv2

class VideoPlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.video_file = None  # To store the selected video file
        self.cap = None  # To store the OpenCV video capture object
        self.is_playing = False

        # Create the title label
        self.title_label = ctk.CTkLabel(self, text="Video Player", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Create a frame to display the video
        self.video_frame = ctk.CTkFrame(self, width=640, height=360, fg_color="black")
        self.video_frame.pack(pady=20)

        # Create a canvas to display the video frames
        self.video_canvas = ctk.CTkCanvas(self.video_frame, width=640, height=360, bg="black")
        self.video_canvas.pack()

        # Create buttons for control
        self.play_button = ctk.CTkButton(self, text="Play", command=self.play_video)
        self.play_button.pack(side="left", padx=10)

        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause_video)
        self.pause_button.pack(side="left", padx=10)

        self.restart_button = ctk.CTkButton(self, text="Restart", command=self.restart_video)
        self.restart_button.pack(side="left", padx=10)

        # Open video button to select a file
        self.open_button = ctk.CTkButton(self, text="Open Video", command=self.open_video_file)
        self.open_button.pack(side="left", padx=10)

    def open_video_file(self):
        """Open a file dialog to choose a video file."""
        video_file = filedialog.askopenfilename(
            title="Select Video",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if video_file:
            self.video_file = video_file
            self.load_video()

    def load_video(self):
        """Load the selected video and display it."""
        self.cap = cv2.VideoCapture(self.video_file)
        self.is_playing = True
        self.play_video()

    def play_video(self):
        """Play the video in the canvas frame."""
        if self.cap and self.is_playing:
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

    def pause_video(self):
        """Pause the video playback."""
        self.is_playing = False

    def restart_video(self):
        """Restart the video from the beginning."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.is_playing = True
            self.play_video()

    def on_closing(self):
        """Release video capture when the window is closed."""
        if self.cap:
            self.cap.release()
