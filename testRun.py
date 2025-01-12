from pythonespeak import espeak
from voxpopuli import Voice

test = espeak.ESpeak()
test.save("Ready to listen.", "test.wav")

print(Voice.list_voice_ids())
voice = Voice(lang="us")
wav = voice.to_audio("This is a test message")

with open("testing.wav", "wb") as wavfile:
    wavfile.write(wav)