import eventlet
eventlet.monkey_patch() # Patch standard libraries for async operations

from flask import Flask, render_template
from flask_socketio import SocketIO
from scapy.all import sniff, IP
from threading import Thread, Event
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# --- Basic Flask App Setup ---
# Explicitly point Flask to the non-standard template directory name: 'templet'
app = Flask(__name__, template_folder='templet')
app.config['SECRET_KEY'] = 'your_secret_key!' # Change this to a random secret key

# Use eventlet for async and allow CORS for local testing
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')

# --- Background Sniffer Thread ---
thread = Thread()
thread_stop_event = Event()
is_sniffer_running = False
IST_TZ = ZoneInfo("Asia/Kolkata")

def packet_sniffer():
    """
    The packet sniffing logic.
    Instead of printing, it emits data through the WebSocket.
    """
    def packet_capture(packet):
        if packet.haslayer(IP):
            source_ip = packet[IP].src
            dest_ip = packet[IP].dst
            packet_len = len(packet)
            timestamp_ist = datetime.now(IST_TZ).isoformat()
            
            # Create a dictionary with the packet data
            data = {
                'source_ip': source_ip,
                'dest_ip': dest_ip,
                'length': packet_len,
                'timestamp': timestamp_ist
            }
            
            # Emit the data to all connected web clients
            socketio.emit('new_packet', data)

    # The sniff function is blocking; use stop_filter to stop when event is set
    sniff(prn=packet_capture, store=0, stop_filter=lambda _: thread_stop_event.is_set())

@app.route('/')
def index():
    # Render the main webpage
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    Called when a new websocket client connects.
    Do not auto-start sniffer; wait for explicit start command.
    """
    print('Client connected')
    socketio.emit('sniffer_status', {
        'status': 'connected',
        'timestamp': datetime.now(IST_TZ).isoformat()
    })

@socketio.on('start_sniff')
def handle_start_sniff():
    global thread, thread_stop_event, is_sniffer_running
    if is_sniffer_running and thread.is_alive():
        socketio.emit('sniffer_status', {
            'status': 'already_running',
            'timestamp': datetime.now(IST_TZ).isoformat()
        })
        return

    # Reset stop event and start thread
    thread_stop_event = Event()
    thread = Thread(target=packet_sniffer, daemon=True)
    thread.start()
    is_sniffer_running = True
    socketio.emit('sniffer_status', {
        'status': 'started',
        'timestamp': datetime.now(IST_TZ).isoformat()
    })

@socketio.on('stop_sniff')
def handle_stop_sniff():
    global thread_stop_event, is_sniffer_running
    if not is_sniffer_running:
        socketio.emit('sniffer_status', {
            'status': 'already_stopped',
            'timestamp': datetime.now(IST_TZ).isoformat()
        })
        return

    thread_stop_event.set()
    is_sniffer_running = False
    socketio.emit('sniffer_status', {
        'status': 'stopped',
        'timestamp': datetime.now(IST_TZ).isoformat()
    })

# --- Main Execution ---
if __name__ == '__main__':
    # Start the Flask-SocketIO server
    # Remember: This needs root privileges because of Scapy
    print("Starting web server on http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000)