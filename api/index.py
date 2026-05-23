from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_headers(mac):
    return {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver:2 rev:250 Safari/533.3",
        "X-User-Agent": "Model: MAG200; Link: Ethernet",
        "Cookie": f"mac={mac}; stb_lang=en; timezone=Europe/London",
        "Accept": "*/*"
    }


def proxy_request(portal, action, mac, extra_params=None):
    if extra_params is None:
        extra_params = {}

    url = f"{portal.rstrip('/')}/portal.php"

    params = {
        "type": "stb",
        "action": action,
        "JsHttpRequest": "1-xml",
        **extra_params
    }

    headers = get_headers(mac)

    try:
        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15,
            verify=False
        )

        return {
            "status": "success",
            "http_code": r.status_code,
            "data": r.text[:3000]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "IPTV Proxy Running"
    })


@app.route("/api/test", methods=["POST"])
@app.route("/test", methods=["POST"])
def test():

    try:
        data = request.get_json(force=True)

        portal = data.get("portal")
        mac = data.get("mac")

        if not portal:
            return jsonify({
                "status":"error",
                "message":"portal kosong"
            }),400

        if not mac:
            return jsonify({
                "status":"error",
                "message":"mac kosong"
            }),400

        result = proxy_request(
            portal,
            "handshake",
            mac
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status":"error",
            "message":str(e)
        }),500


if __name__ == "__main__":
    app.run()
