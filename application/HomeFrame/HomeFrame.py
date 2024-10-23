import tkinter as tk
from tkinter import *
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk

class HomeFrame(customtkinter.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0)
        self.controller = controller

        # Configure the grid to center the frame's content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Create a wrapper frame to center the content
        self.wrapper_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.wrapper_frame.grid(row=1, column=1, sticky="nsew")

        # Add the label and other elements to the wrapper frame
        label = customtkinter.CTkLabel(self.wrapper_frame, wraplength=600, text="VideoMerge AI", font=('Arial', 44))
        label.grid(row=0, column=0, pady=20)

        self.createHomeFrame()

    def createHomeFrame(self):
        # Load and resize image
        self.image = Image.open("C:/Users/hecto/Desktop/Video Editor/video_editor/GUI/images/logo1.png")
        self.resized_image = self.image.resize((150, 150))
        self.myIMG = ImageTk.PhotoImage(self.resized_image)

        # Display image in the wrapper frame
        self.label_with_image = customtkinter.CTkLabel(self.wrapper_frame, image=self.myIMG, text="")
        self.label_with_image.grid(row=1, column=0, padx=20, pady=(10, 5))

        # Add text labels to the wrapper frame
        label_1 = customtkinter.CTkLabel(self.wrapper_frame, wraplength=500, text="Dashboard", font=('Arial', 25))
        label_1.grid(row=2, column=0, pady=5)

        label_2 = customtkinter.CTkLabel(self.wrapper_frame, text="Analyze subtitles and recommend B roll footage based on context", font=('Arial', 14))
        label_2.grid(row=3, column=0, pady=5)

        label_3 = customtkinter.CTkLabel(self.wrapper_frame, text="Add Title instead of subtitles to Clips", font=('Arial', 14))
        label_3.grid(row=4, column=0, pady=5)

        label_4 = customtkinter.CTkLabel(self.wrapper_frame, text="Video Templates", font=('Arial', 14))
        label_4.grid(row=5, column=0, pady=5)

        label_5 = customtkinter.CTkLabel(self.wrapper_frame, text="1 step post to Youtube, Tik Tok, IG", font=('Arial', 14))
        label_5.grid(row=6, column=0, pady=5)

        label_6 = customtkinter.CTkLabel(self.wrapper_frame, text="Create better aspect ratio, blur top and bottom", font=('Arial', 14))
        label_6.grid(row=7, column=0, pady=5)

        label_7 = customtkinter.CTkLabel(self.wrapper_frame, text="Trending Page", font=('Arial', 14))
        label_7.grid(row=8, column=0, pady=5)
