import pyttsx3
import threading
import queue
import time

class VoiceEngine:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.running = False
        self.thread = None

    def start(self):
        """Starts the background voice worker."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        print("[VOICE] System initialized and ready.")

    def _worker(self):
        """Background thread that processes the speech queue."""
        while self.running:
            try:
                # Use a timeout so we can check the 'running' flag periodically
                text = self.speech_queue.get(timeout=1)
                
                # RE-INITIALIZE per phrase for maximum stability on Windows threads
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                
                engine.say(text)
                engine.runAndWait()
                
                # Cleanup
                del engine
                
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VOICE ERROR] {e}")

    def speak(self, text):
        """Adds text to the speech queue."""
        print(f"[RA3 VOICE] {text}")
        self.speech_queue.put(text)

    def stop(self):
        """Stops the voice engine."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[VOICE] Engine stopped.")
