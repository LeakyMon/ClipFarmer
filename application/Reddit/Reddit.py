import customtkinter as ctk
import tkinter as tk
import praw
import json
import os
from threading import Thread
from time import time
from itertools import cycle
from sys import stdout
from time import sleep


class RedditScraper(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=15)

        # Title label
        self.title_label = ctk.CTkLabel(self.main_frame, text="Reddit Scraper", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)

        # Start Button
        self.subreddit_entry = ctk.CTkEntry(self.main_frame, placeholder_text= "Enter a subreddit")
        self.subreddit_entry.pack(pady=10)
        
        self.scrape_button = ctk.CTkButton(self.main_frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.pack(pady=20)

        # Output box for logs
        self.output_text = ctk.CTkTextbox(self.main_frame, width=400, height=200)
        self.output_text.pack(pady=20)

        # Initialize threading variables
        self.error = False
        self.done = False
        self.start_time = 0
        self.subreddit = None

    def log_message(self, message):
        """Helper function to append messages to the output box."""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)

    def animate(self, message):
        for c in cycle([f'⡿ {message}', f'⣟ {message}', f'⣯ {message}', f'⣷ {message}', f'⣾ {message}', f'⣽ {message}', f'⣻ {message}', f'⢿ {message}']):
            if self.error:
                self.log_message(f'Error occurred.')
                break
            if self.done:
                duration = round(time() - self.start_time, 2)
                self.log_message(f"✔️  Reddit Scraping Completed in {duration} seconds")
                break
            stdout.write('\r' + c)
            stdout.flush()
            sleep(0.06)

    def start_scraping(self):
        if self.subreddit_entry.get() == None:
            print("scarystories subreddit")
        self.subreddit = "scarystories"
        self.start_time = time()
        self.done = False
        self.error = False
        self.output_text.delete(1.0, tk.END)

        # Start animation and scraping in a separate thread
        Thread(target=self.animate, args=("Scraping Reddit Data",)).start()
        Thread(target=self.scrape_reddit).start()

    def scrape_reddit(self):
        try:
            reddit = praw.Reddit(client_id='sLELtGZgxpACY3CRqSB8kA',
                                 client_secret='LzOlUDo625PEteH3vxL-yCTOeRxm2g',
                                 user_agent='VideoGenerator/1.0 by Tiny-Swimming-3547')

            scraped_data = {"title": [], "body": [], "author": []}
            hot_posts = reddit.subreddit(self.subreddit).hot(limit=10)

            for post in hot_posts:
                scraped_data["body"].append(str(post.selftext))
                scraped_data["title"].append(str(post.title))
                scraped_data["author"].append(str(post.author))

            json_data = json.dumps(scraped_data, indent=4)

            try:
                os.mkdir('Stories')
            except FileExistsError:
                pass

            with open("Stories/Stories.json", "w") as file:
                file.write(json_data)

            self.done = True
        except Exception as e:
            self.error = True
            self.log_message(f"Error: {str(e)}")


