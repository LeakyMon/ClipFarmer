import customtkinter as ctk

class CreateVideoPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        # Title for Create Video page
        self.label = ctk.CTkLabel(self, text="Create Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=20)
        
        # Define mobile video aspect ratio (1080x1920, scaled down)
        self.video_canvas = ctk.CTkCanvas(self, width=270, height=480, bg="black")  # Scaled down by a factor of 4
        self.video_canvas.pack(pady=20)
        
        # Add a border around the video box (optional)
        self.video_canvas.create_rectangle(2, 2, 268, 478, outline="white", width=2)

        # Bottom section frame (to fit remaining area below the video)
        self.bottom_section = ctk.CTkFrame(self, fg_color="gray")  # Set the color of the frame
        self.bottom_section.pack(fill="both", expand=True, padx=20, pady=20)

        # Add padding to bottom section and more elements if needed
        self.bottom_label = ctk.CTkLabel(self.bottom_section, text="Additional Controls or Information", font=ctk.CTkFont(size=16))
        self.bottom_label.pack(pady=10)
