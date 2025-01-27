from voxpopuli import Voice

print(Voice.list_voice_ids())
voice = Voice(lang="us")
wav = voice.to_audio("This is a test message")

with open("testing.wav", "wb") as wavfile:
    wavfile.write(wav)