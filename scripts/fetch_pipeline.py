import subprocess
import os
import re

# CONFIGURATION
output_dir = "research/youtube-transcripts"
os.makedirs(output_dir, exist_ok=True)
author = "chris_walker"
video_ids = ["WVD9dzd0SL4", "YdEpv0ZAP10", "jjLryGdFJZA", "JkXom1dC_20", "dZx610FbOBc"]

def fetch_via_ytdlp(vid, author):
    print(f"📥 Fetching transcript for: {vid}")
    base_path = f"{output_dir}/{author}_{vid}"
    vtt_path = f"{base_path}.en.vtt"
    txt_path = f"{base_path}.txt"
    
    # Removed --cookies-from-browser flag
    cmd = [
        "yt-dlp",
        "--write-auto-sub", 
        "--skip-download", 
        "--sub-lang", "en",
        "--output", base_path,
        f"https://www.youtube.com/watch?v={vid}"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        if os.path.exists(vtt_path):
            with open(vtt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Clean VTT timestamps and tags
            clean_text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', content)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(clean_text.strip())
            os.remove(vtt_path)
            print(f"✅ Success! Saved clean text to {txt_path}")
        else:
            print(f"❌ No transcript found for {vid}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    for vid in video_ids:
        fetch_via_ytdlp(vid, author)