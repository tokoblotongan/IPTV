from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_headers(mac):
    return {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
        "X-User-Agent": "Model: MAG200; Link: Ethernet",
        "Cookie": f"mac={mac}; stb_lang=en; timezone=Europe/London",
        "Accept": "*/*",
    }

def proxy_request(portal, action, mac, extra_params=None):
    if extra_params is None:
        extra_params = {}
    url = f"{portal.rstrip('/')}/portal.php"
    params = {"action": action, "JsHttpRequest": "1-xml", **extra_params}
    headers = get_headers(mac)
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/test', methods=['POST'])
@app.route('/api/test', methods=['POST'])
def test():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        portal = data.get('portal') or data.get('server')
        mac = data.get('mac') or data.get('mac_address')
        
        if not portal or not mac:
            return jsonify({"status": "error", "message": "portal dan mac wajib diisi"}), 400
        
        result = proxy_request(portal, "handshake", mac, {"type": "stb"})
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
