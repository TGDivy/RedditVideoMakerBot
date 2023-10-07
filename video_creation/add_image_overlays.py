
import os
import re

import ffmpeg
import spacy


def get_image_clips(number_of_clips: int, reddit_id: str, screenshot_width: int, opacity: float):
    image_clips = list()

    image_clips.insert(
        0,
        ffmpeg.input(f"assets/temp/{reddit_id}/png/title.png")["v"].filter(
            "scale", screenshot_width, -1
        ),
    )
    for i in range(0, number_of_clips):
        # Load the screenshot image
        image_clip = ffmpeg.input(f"assets/temp/{reddit_id}/png/comment_{i}.png")["v"].filter(
            "scale", screenshot_width, -1
        )

        # Apply the opacity filter
        image_clip = image_clip.filter("colorchannelmixer", aa=opacity)

        image_clips.append(
            image_clip,
        )

    return image_clips


# Function to split text into meaningful chunks
nlp = spacy.load("en_core_web_sm")
def split_text_into_chunks(text, max_words_per_chunk=3):
    # If the token is a pause or a punctuation mark, add it to the previous chunk and start a new chunk
    doc = nlp(text)
    chunks = []
    current_chunk = []
    for token in doc:
        if token.is_space:
            continue
        if not token.is_punct:
            current_chunk.append(token.text_with_ws)
        
        if token.is_sent_end or token.is_punct or token.is_space or re.match(r"\d", token.text_with_ws):
            if re.match(r"\d", token.text_with_ws):
                chunks.append(current_chunk)
                current_chunk = []
                continue
            if current_chunk:
                current_chunk.append(token.text_with_ws)
                chunks.append(current_chunk)
                current_chunk = []
            else:
                chunks[-1].append(token.text_with_ws)
        

        if len(current_chunk) >= max_words_per_chunk:
            chunks.append(current_chunk)
            current_chunk = []
    if current_chunk:
        chunks.append(current_chunk)

    chunks = ["".join(chunk).strip() for chunk in chunks]
    return chunks

def add_caption_to_video(caption, background_clip, total_duration, start_time):
    caption_fontsize = 36  # Adjust the font size as needed
    caption_color = 'white'  # Color of the text

    # We want to only show at max 2-3 words per spoken text
    # So we split the text into words and iteratively add the words to the background spacing them out evenly
    current_index = 0
    caption_chunks = split_text_into_chunks(caption, max_words_per_chunk=3)

    while current_index < len(caption_chunks):
        line = caption_chunks[current_index]
        end_time = start_time + (total_duration / len(caption_chunks))
        background_clip = background_clip.drawtext(
            text=line,
            enable=f"between(t,{start_time},{end_time})",
            # Positioning
            x="(w-text_w)/2",
            y="(h-text_h)*3/5",
            # Text properties
            fontsize=caption_fontsize,
            fontcolor=caption_color,
            fontfile=os.path.join("fonts", "Roboto-Regular.ttf"),
            # Background box
            box=1,
            boxcolor="black@0.7",
            boxborderw=10,
            # Shadow
            shadowcolor="black",
            shadowx=2,
            shadowy=2,
        )
        start_time = end_time
        current_index += 1
    
    return background_clip


def add_image_overlays(reddit_obj, background_clip, audio_clips_durations, number_of_clips, reddit_id, screenshot_width, opacity):
    image_clips = get_image_clips(number_of_clips, reddit_id, screenshot_width, opacity)
    title = reddit_obj["thread_title"]
    comments = [title]+ [comment["comment_body"] for comment in reddit_obj["comments"][:number_of_clips]]
    
    current_time = 0
    for i in range(0, number_of_clips+1):        
        # Add the image to the background
        background_clip = background_clip.overlay(
            image_clips[i],
            enable=f"between(t,{current_time},{current_time + audio_clips_durations[i]})",
            x="(main_w-overlay_w)/2",
            y="(main_h-overlay_h)/5",
        )
        background_clip = add_caption_to_video(comments[i], background_clip, audio_clips_durations[i], current_time)

        current_time += audio_clips_durations[i]
       
    
    return background_clip