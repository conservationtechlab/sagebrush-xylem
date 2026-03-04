import socket, struct, os
from pathlib import Path

DEST = Path("/mnt/sagebase/sagemic1_ac6").resolve()
HOST, PORT = "127.0.0.1", 19001

# protection from a larger file than we expect being pushed
MAX_BYTES = 1 * 1024 * 1024  # 5 MB

def recv(s, n):
    b = b""
    while len(b) < n:
        x = s.recv(n - len(b))
        if not x:
            raise SystemExit
        b += x
    return b

def safe_dest_path(rel: str) -> Path:
    p = Path(rel)
    # protect from a hack where a diff path than the one we provide
    # has a push attempt
    if p.is_absolute():
        raise ValueError(f"Absolute path rejected: {rel}")
    # protect from path traversal commands
    if ".." in p.parts:
        raise ValueError(f"Path traversal rejected: {rel}")

    out = (DEST / p).resolve()
    if not str(out).startswith(str(DEST) + os.sep) and out != DEST:
        raise ValueError(f"Escapes DEST rejected: {rel}")
    return out

s = socket.socket()
s.connect((HOST, PORT))

while True:
    n = struct.unpack(">I", recv(s, 4))[0]
    r = recv(s, n).decode("utf-8", errors="strict")
    sz = struct.unpack(">Q", recv(s, 8))[0]

    if sz > MAX_BYTES:
        raise ValueError(f"File too large: {sz} bytes > {MAX_BYTES}")

    out = safe_dest_path(r)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")

    with open(tmp, "wb") as f:
        remaining = sz
        while remaining:
            b = s.recv(min(65536, remaining))
            if not b:
                raise SystemExit
            f.write(b)
            remaining -= len(b)

    os.replace(tmp, out)
    print("wrote", r)
