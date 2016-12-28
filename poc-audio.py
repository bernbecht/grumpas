from mutagen.mp3 import MP3

audio = MP3("/home/pi/Music/m.mp3")
print audio.info.length, audio.info.bitrate
