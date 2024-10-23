import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import requests
import sys


class YoutubeUpload(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Upload to Youtube", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)

        # Main container for canvas and modifications
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20)
