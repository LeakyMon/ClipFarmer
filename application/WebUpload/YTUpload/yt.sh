#!/bin/bash

# Video file path (adjust this to point to your video file)
VIDEO_FILE= "C:\Users\hecto\Desktop\ClipFarmer\application\combined_output_with_caption.mp4"

# Title, description, etc. for the video (modify as needed)
VIDEO_TITLE="Automated YouTube Upload 3"
VIDEO_DESCRIPTION="This video was generated and uploaded automatically."
VIDEO_KEYWORDS="python, automation, youtube"
VIDEO_CATEGORY="22"  # Default category ID for People & Blogs
PRIVACY_STATUS="unlisted"  # Privacy status options: public, private, unlisted

# Call yt.py with arguments
python yt.py \
    --file="$VIDEO_FILE" \
    --title="$VIDEO_TITLE" \
    --description="$VIDEO_DESCRIPTION" \
    --keywords="$VIDEO_KEYWORDS" \
    --category="$VIDEO_CATEGORY" \
    --privacyStatus="$PRIVACY_STATUS"