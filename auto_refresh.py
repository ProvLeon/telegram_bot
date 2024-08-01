import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class ChangeHandler(PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(ignore_patterns=["*/__pycache__/*", "*.pyc", "*.pyo", "*.db-journal", "subscribers.*"])

    def on_any_event(self, event):
        if event.is_directory:
            return
        elif event.event_type in ['created', 'modified']:
            print(f"Change detected in {event.src_path}. Restarting...")
            restart_app()

def restart_app():
    global process
    if 'process' in globals():
        process.terminate()
        process.wait()
    process = subprocess.Popen(["python", "app.py"])

if __name__ == "__main__":
    path = "."
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    restart_app()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
    finally:
        if 'process' in globals():
            process.terminate()
            process.wait()
