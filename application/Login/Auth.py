import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter
import customtkinter
from customtkinter import CTkImage
import sys
from tkinter import PhotoImage
import os

from backend.firebase import get_auth

class Authentication():

    def __init__(self):
            super().__init__()
            
            self.auth = get_auth()
            self.user = None 

    
    def sign_in(self, email, password):
        try:
            self.user = self.auth.sign_in_with_email_and_password(email, password)
            print("User signed in successfully.")
            return self.user
        except Exception as e:
            print("Error signing in:", e)
            return None

    def signUp(self, email,password):
        try:
            self.user = self.auth.create_user_with_email_and_password(email, password)
            print("User created successfully.")
            return self.user
        except Exception as e:
            print("Error creating user:", e)
            return None
    def isUserSignedIn(self):
        if self.user:
            try:
                self.auth.get_account_info(self.user['id_token'])
                return self.user
            except:
                print("User token expired/invalid")
                return self.user
        return self.user