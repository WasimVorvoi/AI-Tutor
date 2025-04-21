import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import *
import openai
import time
FONT_PATH = "arial.ttf"
HAND_IMG = "hand.png"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
openai.api_key = "OPENAI_API_KEY"
def generate_ai_script(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Explain {prompt} like Khan Academy on a whiteboard."}]
    )
    return response['choices'][0]['message']['content']
def generate_handwriting_frames(text, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.truetype(FONT_PATH, 36)
    hand = Image.open(HAND_IMG).resize((50, 50))
    x, y = 100, 100
    line_height = 50
    frames = []

    current_text = ""
    for i, char in enumerate(text):
        if char == '\n':
            current_text += char
            y += line_height
            x = 100
        else:
            current_text += char

        img = Image.new("RGB", (1280, 720), "white")
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), current_text, font=font, fill="black")
        try:
            text_width, _ = font.getsize(current_text.strip())
        except:
            bbox = font.getbbox(current_text.strip())
            text_width = bbox[2] - bbox[0]
        hand_x = 100 + text_width + 10
        hand_y = y - 10
        img.paste(hand, (hand_x, hand_y), hand if hand.mode == 'RGBA' else None)

        frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
        img.save(frame_path)
        frames.append(frame_path)
    return frames
def generate_audio(text, output_path):
    tts = gTTS(text=text)
    tts.save(output_path)
def generate_whiteboard_video(topic):
    print("Generating script...")
    script = generate_ai_script(topic)
    print("Script generated.")

    frames_dir = os.path.join(OUTPUT_DIR, "frames")
    audio_path = os.path.join(OUTPUT_DIR, "audio.mp3")
    video_path = os.path.join(OUTPUT_DIR, "whiteboard_video.mp4")

    print("Creating frames...")
    frames = generate_handwriting_frames(script, frames_dir)

    print("Creating audio...")
    generate_audio(script, audio_path)

    print("Combining into video...")
    clips = [ImageClip(m).set_duration(0.1) for m in frames]
    video = concatenate_videoclips(clips, method="compose")

    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    video.write_videofile(video_path, fps=10)
    print("Video saved at", video_path)
def on_generate():
    topic = entry.get().strip()
    if not topic:
        messagebox.showerror("Error", "Enter a topic.")
        return
    try:
        generate_whiteboard_video(topic)
        messagebox.showinfo("Done", "Video generated successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("AI Whiteboard Tutor")
root.geometry("400x200")
label = tk.Label(root, text="Enter a topic to explain:")
label.pack(pady=10)
entry = tk.Entry(root, width=40)
entry.pack(pady=5)
btn = tk.Button(root, text="Generate Video", command=on_generate)
btn.pack(pady=20)
root.mainloop()
