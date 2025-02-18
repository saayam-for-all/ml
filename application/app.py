from recorder import VoiceRecorder
from transcriber import AudioTranscriber


def main():
    print("Recording audio...")
    recorder = VoiceRecorder()
    audio_file = recorder.get_audio_path()

    if audio_file:
        print("Transcribing audio and translating to English...")
        transcriber = AudioTranscriber()
        translation = transcriber.transcribe_audio(audio_file)
        print(f"Translation: {translation}")

    else:
        print("No audio recorded.")

if __name__ == "__main__":
    main()