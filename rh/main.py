import librosa
import lib.beat as beat

# Load the song from a mp3 file
y, sr = librosa.load('song.mp3')

# Detects the beat in the sub and low frequencies
beats = beat.detect_combi_beats(y, sr)