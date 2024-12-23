import customtkinter
import os
from PIL import Image, ImageTk
from CreateVideo.VideoEditor import CreateVideoPage
from UploadVideo.Upload import UploadFrame
from Library.Library import LibraryFrame
from VideoPlayer.VideoPlayer import VideoPlayerFrame
from HomeFrame.HomeFrame import HomeFrame  # Import the new HomeFrame class
from WebUpload.WebUpload import UploadToWeb
from Database.Database import ModifyDatabase
from Reddit.Reddit import RedditScraper
from Chalkboard.Chalkboard import Chalkboard
from backend.firebase import (
    list_folders_in_bucket,get_videos_from_folder
)
from Login.Login import AuthPage  # Import the AuthPage class


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("dark")  # This sets dark mode on startup

        self.title("ClipFarmer.py")
        self.geometry("1250x750+100+50")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join("..", "CustomTkinter", "examples", "test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.create_video_img = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                       dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(10, weight=1)
        self.navigation_frame.grid_forget()  # Hide navigation frame initially

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Image Example", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Create Video",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.create_video_img, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Upload",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.library_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Library",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.library_button_event)
        self.library_button.grid(row=4, column=0, sticky="ew")

        self.videoplayer_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Video Player",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, anchor="w", command=self.videoplayer_button_event)
        self.videoplayer_button.grid(row=5, column=0, sticky="ew")

        self.upload_to_web_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Web Upload",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, anchor="w", command=self.upload_to_web_button_event)
        self.upload_to_web_button.grid(row=6, column=0, sticky="ew")

        self.modify_database_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Database",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, anchor="w", command=self.modify_database_button_event)
        self.modify_database_button.grid(row=7, column=0, sticky="ew")
        
        self.reddit_scraper_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Scrape Reddit",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, anchor="w", command=self.reddit_scraper_button_event)
        self.reddit_scraper_button.grid(row=8, column=0, sticky="ew")


        self.chalkboard_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Chalkboard",
                                                        fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                        image=self.add_user_image, anchor="w", command=self.chalkboard_button_event)
        self.chalkboard_button.grid(row=9, column=0,sticky="ew")


        self.vertical_separator = customtkinter.CTkFrame(self.navigation_frame, width=2, fg_color="white")
        self.vertical_separator.grid(row=0, column=1, rowspan=9, sticky="ns")  # Span all rows vertically

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=10, column=0, padx=20, pady=20, sticky="s")


        self.auth_frame = AuthPage(self, controller=self)  # Login screen frame

    

        self.initialize_frames()


        self.folders = []
        self.videos = []
        self.songs = []
        self.thumbnails = []

        self.load_data()

        # select default frame
        #self.select_frame_by_name("home")
        self.auth_frame.grid(row=0, column=1, sticky="nsew")

    def initialize_frames(self):
        """Initialize all content frames but keep them hidden until login."""
        self.home_frame = HomeFrame(self, controller=self)
        self.second_frame = CreateVideoPage(self, controller=self)
        self.third_frame = UploadFrame(self, controller=self)
        self.library_frame = LibraryFrame(self, controller=self)
        self.videoplayer_frame = VideoPlayerFrame(self, controller=self)
        self.upload_to_web_frame = UploadToWeb(self, controller=self)
        self.database_frame = ModifyDatabase(self, controller=self)
        self.reddit_scraper_frame = RedditScraper(self, controller=self)
        self.chalkboard_frame = Chalkboard(self,controller=self)

    def show_home_page(self):
        """Displays the home page after successful login."""
        self.auth_frame.grid_forget()  # Hide the login frame
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")  # Show navigation frame
        self.select_frame_by_name("home")  # Show the home frame



    def load_data(self):
        folder_list = list_folders_in_bucket()  # Fetch the folders list
        self.thumbnails = []  # Initialize the list for thumbnails
        
        for folder in folder_list:
            self.folders.append(folder)
            if folder != "Music" and folder != "Scripts":
                videos_in_folder = get_videos_from_folder(folder)
                self.videos += videos_in_folder
                # Append the thumbnail for each video
                for video in videos_in_folder:
                    self.thumbnails.append(video['thumbnail'])
            else:
                self.songs += get_videos_from_folder(folder)
        """
        print("Folders:", self.folders)
        print("Videos:", self.videos)
        print("Songs:", self.songs)
        print("Thumbnails:", self.thumbnails)  # Print to verify thumbnail retrieval
        """


        

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "Create Video" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "Upload" else "transparent")
        self.library_button.configure(fg_color=("gray75", "gray25") if name == "Library" else "transparent")
        self.videoplayer_button.configure(fg_color=("gray75", "gray25") if name == "Video Player" else "transparent")
        self.upload_to_web_button.configure(fg_color=("gray75", "gray25") if name == "Web Upload" else "transparent")
        self.modify_database_button.configure(fg_color=("gray75", "gray25") if name == "Database" else "transparent")
        self.reddit_scraper_button.configure(fg_color=("gray75", "gray25") if name == "Reddit Scraper" else "transparent")
        self.chalkboard_button.configure(fg_color=("gray75", "gray25") if name == "Chalkboard" else "transparent")
        # show selected frame
        # Replace the use of pack for home_frame with grid
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "Create Video":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "Upload":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()
        if name == "Library":
            self.library_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.library_frame.grid_forget()
        if name == "Video Player":
            self.videoplayer_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.videoplayer_frame.grid_forget()
        if name == "Web Upload":
            self.upload_to_web_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.upload_to_web_frame.grid_forget()
        if name == "Database":
            self.database_frame.grid(row=0,column=1, sticky="nsew")
        else:
            self.database_frame.grid_forget()
        if name == "Reddit Scraper":
            self.reddit_scraper_frame.grid(row=0,column=1,sticky="nsew")
        else:
            self.reddit_scraper_frame.grid_forget()
            
        if name == "Chalkboard":
            self.chalkboard_frame.grid(row=0,column=1,sticky="nsew")
        else:
            self.chalkboard_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("Create Video")

    def frame_3_button_event(self):
        self.select_frame_by_name("Upload")

    def library_button_event(self):
        self.select_frame_by_name("Library")

    def videoplayer_button_event(self):
        self.select_frame_by_name("Video Player")

    def upload_to_web_button_event(self):
        self.select_frame_by_name("Web Upload")

    def modify_database_button_event(self):
        self.select_frame_by_name("Database")

    def reddit_scraper_button_event(self):
        self.select_frame_by_name("Reddit Scraper")

    def chalkboard_button_event(self):
        self.select_frame_by_name("Chalkboard")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
