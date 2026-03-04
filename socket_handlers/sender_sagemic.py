import socket, struct, time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT = Path("/home/katie/sagemic_detections").resolve()
HOST, PORT = "127.0.0.1", 9011


class H(FileSystemEventHandler):
    def __init__(self, c): self.c = c
    def on_created(self, e):
        if e.is_directory or not e.src_path.endswith(".wav"): return

        time.sleep(3)

        p = Path(e.src_path)
        r = p.relative_to(ROOT).as_posix().encode()
        d = p.read_bytes()
        self.c.sendall(struct.pack(">I", len(r)) + r)
        self.c.sendall(struct.pack(">Q", len(d)) + d)
        print("sent", r.decode())

s = socket.socket()
s.bind((HOST, PORT))
s.listen(1)
c, _ = s.accept()

obs = Observer()
obs.schedule(H(c), str(ROOT), recursive=True)
obs.start()

while True: time.sleep(1)
