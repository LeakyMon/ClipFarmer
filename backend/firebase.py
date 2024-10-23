import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# Path to your Firebase credentials JSON file (relative to the current file)
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), "../firebase_credentials.json"))

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'storageBucket': 'clipfarmer-f8a79.appspot.com'
})

# Initialize Firestore and Firebase Storage
db = firestore.client()
bucket = storage.bucket()

def upload_file_to_storage(file_path, file_name, folder_type, file_type):
    """Uploads a file to Firebase Storage (video or thumbnail) and returns its public URL."""
    blob = bucket.blob(f'{folder_type}/{file_type}/{file_name}')
    blob.upload_from_filename(file_path)
    blob.make_public()
    print(f"{file_type.capitalize()} uploaded to: {blob.public_url}")
    return blob.public_url

def add_video_metadata(title, video_url, thumbnail_url, folder_type):
    """Adds a new video document to the 'videos' collection in Firestore."""
    
    # Generate a unique ID for the document
    video_id = db.collection('videos').document().id

    # Define the video data
    video_data = {
        'title': title,
        'url': video_url,
        'thumbnail': thumbnail_url,
        'folder': folder_type,
        'id': video_id
    }

    # Add the document to Firestore
    db.collection('videos').document(video_id).set(video_data)
    print(f"Metadata for '{title}' saved in Firestore with ID: {video_id}")
