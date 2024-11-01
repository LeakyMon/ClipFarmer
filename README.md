# ClipFarmer

**ClipFarmer** is a Python-based application using the `tkinter` library to streamline the process of creating and managing short-form videos, such as YouTube Shorts, TikToks, and Instagram Reels. This tool is designed to simplify video generation, uploading, and library management with a user-friendly graphical interface.

## Features

Upon launching ClipFarmer, the application opens a window displaying a homepage with a navigation sidebar. Each tab in the sidebar serves a unique purpose:

- **Create a Video**  
  Begin creating a new video with options for video length, format, and other customizations tailored to short-form content.

- **Upload a Video**  
  Upload your created videos to various platforms directly from the application, ensuring quick and efficient sharing.

- **Video Library**  
  Manage your collection of videos, including options for organizing, editing, and reviewing previously created content.

- **Video Player**  
  View your videos within the app before uploading to ensure quality and alignment with your goals.

- **Reddit Scraper**  
  Use this tool to gather inspiration or source content by scraping Reddit for popular or relevant posts that could enhance your videos.

- **Database**  
  Access and manage video-related data, which may include metadata, content tags, or other organizational elements.

- **Upload to Web**  
  Seamlessly upload your videos to various online platforms, complete with automated captions and descriptions.

## Installation

1. **Clone this repository**:
    ```bash
    git clone https://github.com/LeakyMon/ClipFarmer.git
    ```

2. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Setup Environment Variables**:
    - Create a `.env` file in the root directory of the project. This file will store your sensitive information securely and keep it hidden from the public repository.
    - Inside the `.env` file, add the following variables:

      ```plaintext
      # Firebase Credentials
      FIREBASE_CREDENTIALS_PATH=path/to/your/firebase_credentials.json
      FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket

      # Reddit API Credentials
      REDDIT_CLIENT_ID=your-reddit-client-id
      REDDIT_CLIENT_SECRET=your-reddit-client-secret
      REDDIT_USER_AGENT=your-reddit-user-agent
      ```

    - **Explanation of Variables**:
      - `FIREBASE_CREDENTIALS_PATH`: Path to your Firebase credentials JSON file.
      - `FIREBASE_STORAGE_BUCKET`: The Firebase storage bucket name for your project.
      - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT`: Your Reddit API credentials required for accessing Reddit data.

4. **Add .env to .gitignore**:
    - To keep your credentials secure, ensure `.env` is listed in your `.gitignore` file to prevent it from being tracked in the repository.

5. **Run the application**:
    ```bash
    python main.py
    ```

## Usage

Each tab in the application is designed to guide you through the video creation and management process, providing all the tools necessary to produce and upload high-quality short-form videos with ease.

## License

This project is licensed under the MIT License.
