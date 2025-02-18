import os
import torchaudio
from transformers import AutoProcessor, SeamlessM4TModel
from recorder import VoiceRecorder


class AudioTranscriber:
    def __init__(self, model_name="facebook/hf-seamless-m4t-medium"):
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = SeamlessM4TModel.from_pretrained(model_name)

    def transcribe_audio(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        audio, orig_freq = torchaudio.load(audio_path)
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000)  # 16 kHz required
        audio_inputs = self.processor(audios=audio, return_tensors="pt")

        output_tokens = self.model.generate(**audio_inputs, tgt_lang="eng", generate_speech=False)
        translated_text = self.processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

        # Delete the audio file after processing
        os.remove(audio_path)

        return translated_text


if __name__ == "__main__":
    recorder = VoiceRecorder()
    audio_file_path = recorder.get_audio_path()

    if audio_file_path:
        transcriber = AudioTranscriber()
        result = transcriber.transcribe_audio(audio_file_path)
        print(result)
    else:
        print("No audio recorded.")