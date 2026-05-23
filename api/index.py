from flask import Flask, jsonify, request, Response, render_template
import requests

app = Flask(__name__, template_folder='../templates')

def get_stalker_headers(mac):
    return {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
        "X-User-Agent": "Model: MAG200; Link: Ethernet",
        "Cookie": f"mac={mac}; stb_lang=en; timezone=Europe/London",
        "Accept": "*/*",
    }

def proxy_portal_request(portal, action, mac, extra_params=None):
    if extra_params is None:
        extra_params = {}
    
    url = f"{portal.rstrip('/')}/portal.php"
    params = {"action": action, "JsHttpRequest": "1-xml", **extra_params}
    headers = get_stalker_headers(mac)
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def test_code():
    mode = request.form.get('mode')
    server = request.form.get('server', '').strip().rstrip('/')
    
    if mode == 'mac':
        mac = request.form.get('mac_address', '').strip().upper()
        if not mac:
            return jsonify({"status": "error", "message": "MAC wajib diisi"}), 400
            
        result = proxy_portal_request(server, "handshake", mac, {"type": "stb"})
        
        if "error" not in str(result):
            return jsonify({"status": "success", "message": "✅ Handshake berhasil!"})
        else:
            return jsonify(result)
    
    # ... (sisanya kode test xtream dan url kamu bisa ditambahkan lagi)

    return jsonify({"status": "error", "message": "Mode tidak dikenal"}), 400

if __name__ == '__main__':
    app.run(debug=True)
