import tkinter as tk
from tkinter import *
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk


class Chalkboard(ctk.CTkFrame):
         def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller

            self.label = ctk.CTkLabel(self, text="Chalkboard", font=ctk.CTkFont(size=24, weight="bold"))
            self.label.pack(pady=10)

            # Add a simple drawing canvas
            self.canvas = tk.Canvas(self, width=500, height=500, bg="white")
            self.canvas.pack(pady=10)