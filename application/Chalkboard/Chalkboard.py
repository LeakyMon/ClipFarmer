import tkinter as tk
from tkinter import *
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk


class Chalkboard(customtkinter.CTkFrame):
        def __init__(self, parent, controller):
            print("chalk")