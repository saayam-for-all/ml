import os
import wave # type: ignore
import time
import threading # type: ignore
import tkinter as tk
import pyaudio


class VoiceRecorder:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.button = tk.Button(text = "🎙️", font = ("Arial", 120, "bold"),
                                command=self.click_handler)
        self.label = tk.Label(text="00:00:00")
        self.button.pack()
        self.recording = False
        self.audio_path = None
        self.root.mainloop()

    
    def click_handler(self):
        if self.recording:
            self.recording = False
            self.button.config(fg = "black")
        
        else:
            self.recording = True
            self.button.config(fg="red")
            threading.Thread(target=self.record).start()

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                            input=True, frames_per_buffer=1024)
        
        frames = []
        start = time.time()

        while self.recording:
            data = stream.read(1024)
            frames.append(data)

            passed = time.time() - start
            secs = passed % 60
            mins = passed // 60
            hours = mins // 60
            self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")


        stream.stop_stream()
        stream.close()
        audio.terminate()

        self.audio_path = os.path.join(os.getcwd(), "recording.wav")

        # Save recorded audio
        with wave.open(self.audio_path, "wb") as sound_file:
            sound_file.setnchannels(1)
            sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            sound_file.setframerate(44100)
            sound_file.writeframes(b"".join(frames))

    def get_audio_path(self):
        return self.audio_path


# if __name__ == "__main__":
#     VoiceRecorder()