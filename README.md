# Music Player 🎵

After seeing the Spotify payment hit my card, I decided to build a **fully-featured music player** for Windows. It’s lightweight, supports folders, files, shuffle, repeat, themes, album art, and keeps all your settings saved for next time.

## How it works
1. Open the app and pick a music file or an entire folder.
2. Control playback with:
   - **Play / Pause / Next / Previous**
   - **Volume and seek sliders**
   - **Shuffle** and **repeat modes**
   - **Variable playback speed** (0.5x, 1x, 1.5x, 2x)
3. Switch between **Dark** and **Light** theme.
4. Album art will display automatically if your MP3 files contain it.
5. All settings (volume, last track, playlist, theme, repeat/shuffle, playback rate) are **saved and loaded on startup**.
6. Minimize to system tray to keep it running in the background.

## What I learned while making it
- **PyQt5 QMediaPlayer and QMediaPlaylist** for handling audio.
- **Persistent settings** with JSON for saving user preferences.
- **Dynamic UI updates**, including album art loading and theme switching.
- **System tray integration** for background operation.
- **Handling folders and individual files** efficiently in Python.

## Dependencies  
Install missing libraries using:
```bash
pip install -r requirements.txt
```
This app also needs **FFmpeg** for pulling .opus file cover art, please make sure you have it in your path.

## Files  
- `player_ui.py` → UI logic created with Qt Designer.
- `musicplayer.pyw` → Main application code.
- `icon.ico` → Window and system tray icon made by me!
- `requirements.txt` → The required packages for the code to work.

## Note 📝  
Unlike some of my older projects, I’m **actively planning to use this one**, so expect occasional updates and bugfixes.  
