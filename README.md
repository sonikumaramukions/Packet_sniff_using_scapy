# Sniff Packet - Flask + Socket.IO + Scapy

A minimal live packet sniffer web app using Flask-SocketIO and Scapy. Packets are streamed to the browser in real time. UI lets you Start/Stop sniffing and shows bytes and timestamps (IST).

## 1) Requirements
- Python 3.9+ (tested on Linux/Kali)
- Root privileges (or capabilities) for packet capture
- System libs: `libpcap` (usually present on Kali)

## 2) Project layout
- App: `app.py`
- Templates: `templet/index.html`
- Python deps: `requirements.txt`

## 3) One-time setup
```bash
cd "/home/soni-lap/Documents/cyber security projects/sniff packet"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```

## 4) How to run (two options)
### Option A: Run with sudo (simplest)
```bash
cd "/home/soni-lap/Documents/cyber security projects/sniff packet"
source .venv/bin/activate
sudo -E env PATH="$PATH" python app.py
```

### Option B: Run without sudo using capabilities
Grant raw socket capabilities to your venv's Python (so Scapy can sniff):
```bash
sudo setcap cap_net_raw,cap_net_admin=eip \
"/home/soni-lap/Documents/cyber security projects/sniff packet/.venv/bin/python"
```
Then run normally:
```bash
cd "/home/soni-lap/Documents/cyber security projects/sniff packet"
source .venv/bin/activate
python app.py
```

The server prints: `Starting web server on http://127.0.0.1:5000`.
Open your browser at `http://127.0.0.1:5000`.

## 5) Using the app
- Click "Start" to begin capturing packets; "Stop" to stop.
- Status bar shows connection and sniffer state with IST timestamps.
- The packet list shows: `source_ip → dest_ip | bytes | time (IST)`.

## 6) Troubleshooting
- No packets? Generate traffic (open websites, ping, apt update). On quiet links you may see nothing.
- Permission errors: use sudo (Option A) or set capabilities (Option B).
- Port in use: change port in `socketio.run(..., port=5000)` in `app.py`.
- ZoneInfo errors: ensure Python 3.9+; on some minimal systems install tzdata: `sudo apt install tzdata`.
- Dependency issues: re-run `pip install -r requirements.txt` inside the venv.

## 7) Notes
- Templating folder is `templet/` (non-standard name configured in code).
- Uses `eventlet` async for Flask-SocketIO.
- Timestamps are emitted in Asia/Kolkata (IST) on the server.
- Default interface is system default; you can add an `iface="eth0"` argument to Scapy's `sniff(...)` if you need a specific interface.

## 8) Developer commands
```bash
# Activate venv
source "/home/soni-lap/Documents/cyber security projects/sniff packet/.venv/bin/activate"

# Deactivate venv
deactivate
```
