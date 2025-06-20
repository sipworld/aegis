from flask import Flask, jsonify, render_template
import os
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)

# Configuration
BASE_PATH = "/usr/local/antmedia/webapps/LiveApp/streams"
ANTMEDIA_HOST = "http://localhost:5080"
ANTMEDIA_USER = "varunps2003@gmail.com"
ANTMEDIA_PASS = "India@123"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recordings.json")
def recordings():
    """Get recordings from the streams directory"""
    data = {}
    try:
        if not os.path.exists(BASE_PATH):
            print(f"Directory {BASE_PATH} does not exist")
            return jsonify({})
            
        files = sorted(os.listdir(BASE_PATH))
        for f in files:
            if f.endswith(".mp4"):
                # Extract stream name from filename
                if "-" in f:
                    stream_name = f.split("-")[0]
                else:
                    stream_name = f.split(".")[0]
                
                # Create URLs using the domain that works for live streams
                # Use media.cryptovoip.in:5080 instead of localhost:5080
                file_url = f"http://media.cryptovoip.in:5080/LiveApp/streams/{f}"
                hls_url = f"http://media.cryptovoip.in:5080/LiveApp/streams/{f.replace('.mp4', '.m3u8')}"
                
                if stream_name not in data:
                    data[stream_name] = []
                    
                data[stream_name].append({
                    "filename": f,
                    "mp4_url": file_url,
                    "hls_url": hls_url,
                    "timestamp": os.path.getmtime(os.path.join(BASE_PATH, f))
                })
                
        # Sort recordings by timestamp (newest first)
        for stream_name in data:
            data[stream_name].sort(key=lambda x: x["timestamp"], reverse=True)
            
    except Exception as e:
        print(f"Error reading recordings: {e}")
        return jsonify({})
    
    return jsonify(data)

@app.route("/live.json")
def live():
    """Get live streams - multiple fallback methods for Community Edition"""
    
    # Method 1: Try the REST API with authentication
    try:
        print("Attempting Method 1: REST API with auth")
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/list/0/50",
            auth=HTTPBasicAuth(ANTMEDIA_USER, ANTMEDIA_PASS),
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            broadcasts = res.json()
            live_streams = []
            for b in broadcasts:
                if b.get('status') == 'broadcasting':
                    live_streams.append({
                        'streamId': b['streamId'],
                        'name': b.get('name', b['streamId']),
                        'status': b['status']
                    })
            if live_streams:
                print(f"Method 1 successful: Found {len(live_streams)} streams")
                return jsonify(live_streams)
    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: Try without authentication
    try:
        print("Attempting Method 2: REST API without auth")
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/list/0/50",
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            broadcasts = res.json()
            live_streams = []
            for b in broadcasts:
                if b.get('status') == 'broadcasting':
                    live_streams.append({
                        'streamId': b['streamId'],
                        'name': b.get('name', b['streamId']),
                        'status': b['status']
                    })
            if live_streams:
                print(f"Method 2 successful: Found {len(live_streams)} streams")
                return jsonify(live_streams)
    except Exception as e:
        print(f"Method 2 failed: {e}")

    # Method 3: Check for active stream files
    try:
        print("Attempting Method 3: File-based detection")
        live_streams = []
        if os.path.exists(BASE_PATH):
            files = os.listdir(BASE_PATH)
            for f in files:
                if f.endswith('.m3u8'):
                    stream_id = f.replace('.m3u8', '')
                    # Check if the m3u8 file is recent (within last 30 seconds)
                    file_path = os.path.join(BASE_PATH, f)
                    if os.path.getmtime(file_path) > (os.time.time() - 30):
                        live_streams.append({
                            'streamId': stream_id,
                            'name': stream_id,
                            'status': 'broadcasting'
                        })
        
        if live_streams:
            print(f"Method 3 successful: Found {len(live_streams)} streams")
            return jsonify(live_streams)
    except Exception as e:
        print(f"Method 3 failed: {e}")

    # Method 4: Return hardcoded test streams (for debugging)
    try:
        print("Attempting Method 4: Hardcoded test streams")
        # You can add your known stream IDs here for testing
        test_streams = [
            {'streamId': 'test_stream', 'name': 'Test Stream', 'status': 'broadcasting'}
        ]
        return jsonify(test_streams)
    except Exception as e:
        print(f"Method 4 failed: {e}")

    print("All methods failed, returning empty list")
    return jsonify([])

@app.route("/stream-info/<stream_id>")
def stream_info(stream_id):
    """Get detailed information about a specific stream"""
    try:
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/{stream_id}",
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            return jsonify(res.json())
    except Exception as e:
        print(f"Error getting stream info: {e}")
    
    return jsonify({"error": "Stream not found"})

@app.route("/debug/<stream_id>")
def debug_stream(stream_id):
    """Debug endpoint to check stream status"""
    import os
    base_url = "http://localhost:5080/LiveApp"

    debug_info = {
        "stream_id": stream_id,
        "urls_to_test": [
            f"{base_url}/streams/{stream_id}.m3u8",
            f"{base_url}/play.html?name={stream_id}",
            f"{base_url}/rest/v2/broadcasts/{stream_id}"
        ],
        "files_in_streams_dir": []
    }

    # Check if stream files exist
    streams_path = "/usr/local/antmedia/webapps/LiveApp/streams"
    if os.path.exists(streams_path):
        files = [f for f in os.listdir(streams_path) if stream_id in f]
        debug_info["files_in_streams_dir"] = files

    return jsonify(debug_info)

if __name__ == '__main__':
    print(f"Starting server...")
    print(f"Ant Media Host: {ANTMEDIA_HOST}")
    print(f"Recordings Path: {BASE_PATH}")
    app.run(host="0.0.0.0", port=8000, debug=True)

@app.route("/live.json")
def live():
    """Get live streams - multiple fallback methods for Community Edition"""
    
    # Method 1: Try the REST API with authentication
    try:
        print("Attempting Method 1: REST API with auth")
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/list/0/50",
            auth=HTTPBasicAuth(ANTMEDIA_USER, ANTMEDIA_PASS),
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            broadcasts = res.json()
            live_streams = []
            for b in broadcasts:
                if b.get('status') == 'broadcasting':
                    live_streams.append({
                        'streamId': b['streamId'],
                        'name': b.get('name', b['streamId']),
                        'status': b['status']
                    })
            if live_streams:
                print(f"Method 1 successful: Found {len(live_streams)} streams")
                return jsonify(live_streams)
    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: Try without authentication
    try:
        print("Attempting Method 2: REST API without auth")
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/list/0/50",
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            broadcasts = res.json()
            live_streams = []
            for b in broadcasts:
                if b.get('status') == 'broadcasting':
                    live_streams.append({
                        'streamId': b['streamId'],
                        'name': b.get('name', b['streamId']),
                        'status': b['status']
                    })
            if live_streams:
                print(f"Method 2 successful: Found {len(live_streams)} streams")
                return jsonify(live_streams)
    except Exception as e:
        print(f"Method 2 failed: {e}")

    # Method 3: Check for active stream files
    try:
        print("Attempting Method 3: File-based detection")
        live_streams = []
        if os.path.exists(BASE_PATH):
            files = os.listdir(BASE_PATH)
            for f in files:
                if f.endswith('.m3u8'):
                    stream_id = f.replace('.m3u8', '')
                    # Check if the m3u8 file is recent (within last 30 seconds)
                    file_path = os.path.join(BASE_PATH, f)
                    if os.path.getmtime(file_path) > (os.time.time() - 30):
                        live_streams.append({
                            'streamId': stream_id,
                            'name': stream_id,
                            'status': 'broadcasting'
                        })
        
        if live_streams:
            print(f"Method 3 successful: Found {len(live_streams)} streams")
            return jsonify(live_streams)
    except Exception as e:
        print(f"Method 3 failed: {e}")

    # Method 4: Return hardcoded test streams (for debugging)
    try:
        print("Attempting Method 4: Hardcoded test streams")
        # You can add your known stream IDs here for testing
        test_streams = [
            {'streamId': 'test_stream', 'name': 'Test Stream', 'status': 'broadcasting'}
        ]
        return jsonify(test_streams)
    except Exception as e:
        print(f"Method 4 failed: {e}")

    print("All methods failed, returning empty list")
    return jsonify([])

@app.route("/stream-info/<stream_id>")
def stream_info(stream_id):
    """Get detailed information about a specific stream"""
    try:
        res = requests.get(
            f"{ANTMEDIA_HOST}/LiveApp/rest/v2/broadcasts/{stream_id}",
            timeout=5,
            verify=False
        )
        if res.status_code == 200:
            return jsonify(res.json())
    except Exception as e:
        print(f"Error getting stream info: {e}")
    
    return jsonify({"error": "Stream not found"})

if __name__ == '__main__':
    print(f"Starting server...")
    print(f"Ant Media Host: {ANTMEDIA_HOST}")
    print(f"Recordings Path: {BASE_PATH}")
    app.run(host="0.0.0.0", port=8000, debug=True)

