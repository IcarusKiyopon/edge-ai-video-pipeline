import asyncio
import os
import random
import re
import subprocess
from dotenv import load_dotenv
from groq import Groq
import edge_tts
from moviepy.editor import AudioFileClip, VideoFileClip
from faster_whisper import WhisperModel
import srt
from datetime import timedelta

# Load secrets from .env file securely
load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile" 
VOICE = "en-US-AvaNeural"  

# Use absolute paths to prevent working-directory crashes
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
GAMEPLAY_FOLDER = os.path.join(BASE_DIR, "gameplay_pool")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

SCRIPT_FILE = os.path.join(OUTPUT_DIR, "story_script.txt")
AUDIO_FILE = os.path.join(OUTPUT_DIR, "story_voice.mp3")
RAW_VIDEO_FILE = os.path.join(OUTPUT_DIR, "uncaptioned_short.mp4")
FINAL_VIDEO_FILE = os.path.join(OUTPUT_DIR, "final_captioned_short.mp4")
SRT_FILE = os.path.join(OUTPUT_DIR, "subtitles.srt")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GAMEPLAY_FOLDER, exist_ok=True)

async def generate_horror_story():
    print("⚡ Pinging Groq's lightning-fast LPUs for a unique script...")
    client = Groq(api_key=GROQ_API_KEY)
    
    horror_themes = [
        "paranoia, hidden spaces, or strange architecture",
        "uncanny technology, smart home malfunctions, or corrupted video feeds",
        "deep-woods isolation, cryptic radio signals, or local folklore legends",
        "suburban dread, a neighbor with a bizarre daily routine, or an unlisted room",
        "ocean depths, abandoned vessels, or an island that shouldn't exist",
        "mirrors, doppelgangers, or a reflection that reacts a second too late",
        "shadows that do not match the objects casting them, or anatomical anomalies",
        "stuck in a loops, liminal spaces like empty malls or endless office halls"
    ]
    
    selected_theme = random.choice(horror_themes)
    print(f"🎲 Selected theme anchor for this run: {selected_theme}")
    
    prompt = (
        "Write an incredibly suspenseful, completely original modern horror micro-story. "
        f"The premise must heavily revolve around themes of: {selected_theme}. "
        "It must be between 100 to 130 words long. "
        "Start directly with a highly engaging, shocking hook sentence. "
        "Build intense dread rapidly. "
        "CRITICAL: Stop the narrative completely mid-sentence right at the peak climax/scariest moment. "
        "Do not write a conclusion, do not resolve the tension, and do not include any meta-text, introductions, or titles. "
        f"Make sure this specific story is entirely distinct from previous variations. Seed ID: {random.randint(1000, 9999)}"
    )
    
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a master of psychological horror and volatile flash fiction. Never repeat plot points."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.95,
        max_tokens=300
    )
    
    script_text = completion.choices[0].message.content.strip()
    script_text = re.sub(r'[*"\'_]', '', script_text)
    
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script_text)
        
    print(f"✍️ Unique script saved to {SCRIPT_FILE}")
    return script_text

async def text_to_speech(text):
    print("🎙️ Generating high-quality voiceover via Edge-TTS...")
    communicate = edge_tts.Communicate(text, VOICE, rate="-7%", pitch="-4Hz")
    await communicate.save(AUDIO_FILE)
    print(f"🎵 Audio narration successfully saved to {AUDIO_FILE}")

def generate_precise_subtitles():
    print("🧠 Initializing Local Whisper Engine for word-accurate tracking...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(AUDIO_FILE, word_timestamps=True)
    
    all_words = []
    for segment in segments:
        for word in segment.words:
            all_words.append({
                "word": word.word.strip().upper(),
                "start": word.start,
                "end": word.end
            })
            
    srt_entries = []
    chunk_size = 3
    entry_idx = 1
    
    for i in range(0, len(all_words), chunk_size):
        chunk = all_words[i:i+chunk_size]
        if not chunk:
            continue
            
        chunk_text = " ".join([w["word"] for w in chunk])
        start_time = timedelta(seconds=chunk[0]["start"])
        end_time = timedelta(seconds=chunk[-1]["end"])
        
        srt_entries.append(srt.Subtitle(
            index=entry_idx,
            start=start_time,
            end=end_time,
            content=chunk_text
        ))
        entry_idx += 1
        
    with open(SRT_FILE, "w", encoding="utf-8") as f:
        f.write(srt.compose(srt_entries))
    print(f"⏱️ Word-accurate tracking file generated at: {SRT_FILE}")

def stitch_video_pipeline():
    print("🎬 Initializing video composite mechanics...")
    videos = [f for f in os.listdir(GAMEPLAY_FOLDER) if f.endswith(('.mp4', '.mov', '.mkv'))]
    if not videos:
        print(f"❌ ERROR: Drop a gameplay video into '{GAMEPLAY_FOLDER}' first.")
        return False
        
    chosen_bg = os.path.join(GAMEPLAY_FOLDER, random.choice(videos))
    audio_clip = AudioFileClip(AUDIO_FILE)
    audio_duration = audio_clip.duration
    
    video_clip = VideoFileClip(chosen_bg)
    if video_clip.duration < audio_duration:
        print("❌ ERROR: Background video is too short.")
        audio_clip.close()
        video_clip.close()
        return False
        
    start_time = random.uniform(0, video_clip.duration - audio_duration)
    video_clip = video_clip.subclip(start_time, start_time + audio_duration)
    
    width, height = video_clip.size
    target_width = int(height * (9 / 16))
    if target_width % 2 != 0:
        target_width -= 1
        
    x1 = (width - target_width) // 2
    x2 = x1 + target_width
    video_clip = video_clip.crop(x1=x1, y1=0, x2=x2, y2=height)
    
    final_clip = video_clip.set_audio(audio_clip)
    
    print("🚀 Compiling intermediate raw uncaptioned short video layer...")
    final_clip.write_videofile(
        RAW_VIDEO_FILE,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        logger=None
    )
    
    audio_clip.close()
    video_clip.close()
    final_clip.close()
    return True

def burn_subtitles():
    print("🔥 Burning premium high-retention text templates onto layout frame...")
    from moviepy.config import get_setting
    FFMPEG_BINARY = get_setting("FFMPEG_BINARY")
    
    # We are restoring your exact relative paths to bypass the FFmpeg Windows colon bug!
    srt_relative = "./output/subtitles.srt"
    raw_video_relative = "./output/uncaptioned_short.mp4"
    final_video_relative = "./output/final_captioned_short.mp4"
    
    font_style = (
        "Fontname=Impact,Fontsize=24,"
        "PrimaryColour=&H00FFFF,OutlineColour=&H000000,"
        "BorderStyle=1,Outline=4,Shadow=1,"
        "Alignment=2,MarginV=180,Bold=1"
    )
    
    ffmpeg_command = (
        f'"{FFMPEG_BINARY}" -y -i "{raw_video_relative}" -vf '
        f'"subtitles={srt_relative}:force_style=\'{font_style}\'" '
        f'-c:v libx264 -c:a copy "{final_video_relative}"'
    )
    
    print("🎬 Rendering active styled frames to destination container...")
    
    result = subprocess.run(ffmpeg_command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ FFmpeg Error:\n{result.stderr}")
    else:
        print(f"🎉 PIPELINE SUCCESS COMPLETE! High-retention short ready at: {final_video_relative}")
        if os.path.exists(raw_video_relative):
            os.remove(raw_video_relative)

            
async def main():
    if not GROQ_API_KEY:
        print("❌ ERROR: Missing GROQ_API_KEY. Please add it to your .env file!")
        return
        
    story_text = await generate_horror_story()
    await text_to_speech(story_text)
    
    generate_precise_subtitles()
    
    if stitch_video_pipeline():
        burn_subtitles()

if __name__ == "__main__":
    asyncio.run(main())