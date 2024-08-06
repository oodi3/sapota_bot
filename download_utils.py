import os
import time
import yt_dlp


async def process_video_download(message) -> None:
    url = message.text
    try:
        await message.reply_text("Downloading video(s)...")
        download_videos(url)
        await message.reply_text("Download completed! 😊 Your video(s) are saved locally.")
    except Exception as e:
        await message.reply_text(f"Failed to download video(s). 😿 Error: {e}")


def download_videos(url, directory='downloads') -> list:
    start_timer = time.time()

    if not os.path.exists(directory):
        os.makedirs(directory)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{directory}/%(title)s.%(ext)s',
        'noplaylist': False,
        # launch video converter ffmpeg :
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print("Video downloaded successfully!")

    downloaded_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            downloaded_files.append(os.path.join(root, file))

    end_timer = time.time() - start_timer
    print(f"Time taken: {end_timer:.2f} seconds")

    return downloaded_files
