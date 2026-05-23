from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

# ========================================
# HEADER MAG / STB
# ========================================

def mag_headers(mac="00:1A:79:00:00:01"):

    return {
        "User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver:2 rev:250 Safari/533.3",
        "X-User-Agent":"Model: MAG250; Link: Ethernet",
        "Cookie":f"mac={mac}; stb_lang=en; timezone=Europe/London",
        "Accept":"*/*",
        "Connection":"Keep-Alive"
    }


# ========================================
# HOME
# ========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status":"online",
        "message":"IPTV Proxy Running",
        "endpoints":[
            "/api/test",
            "/api/mac",
            "/api/xtream",
            "/api/url"
        ]
    })


# ========================================
# TEST ENDPOINT
# ========================================

@app.route("/api/test", methods=["GET","POST"])
def test():

    if request.method=="GET":

        return jsonify({
            "status":"online",
            "message":"POST ke endpoint ini"
        })

    try:

        data=request.get_json(force=True)

        return jsonify({
            "status":"success",
            "received":data
        })

    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }),500


# ========================================
# MAC PORTAL
# ========================================

@app.route("/api/mac", methods=["POST"])
def mac():

    try:

        data=request.get_json(force=True)

        portal=data.get("portal","")
        mac=data.get("mac","")

        if portal=="":
            return jsonify({
                "status":"error",
                "message":"portal kosong"
            }),400

        if mac=="":
            return jsonify({
                "status":"error",
                "message":"mac kosong"
            }),400

        url=f"{portal.rstrip('/')}/portal.php"

        params={

            "type":"stb",
            "action":"handshake",
            "JsHttpRequest":"1-xml"

        }

        r=requests.get(
            url,
            headers=mag_headers(mac),
            params=params,
            timeout=15,
            verify=False
        )

        return jsonify({

            "status":"success",
            "http_code":r.status_code,
            "response":r.text[:3000]

        })

    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }),500


# ========================================
# XTREAM CODES
# ========================================

@app.route("/api/xtream", methods=["POST"])
def xtream():

    try:

        data=request.get_json(force=True)

        server=data.get("server","")
        username=data.get("username","")
        password=data.get("password","")

        if server=="":
            return jsonify({
                "status":"error",
                "message":"server kosong"
            }),400

        url=f"{server}/player_api.php?username={username}&password={password}"

        r=requests.get(
            url,
            timeout=15,
            verify=False
        )

        return jsonify({

            "status":"success",
            "http_code":r.status_code,
            "response":r.json()

        })

    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }),500


# ========================================
# URL CHECK
# ========================================

@app.route("/api/url", methods=["POST"])
def url_test():

    try:

        data=request.get_json(force=True)

        url=data.get("url","")

        if url=="":

            return jsonify({
                "status":"error",
                "message":"url kosong"
            }),400

        r=requests.get(
            url,
            timeout=15,
            verify=False,
            allow_redirects=True
        )

        return jsonify({

            "status":"success",
            "http_code":r.status_code,
            "content_type":r.headers.get(
                "Content-Type",
                "unknown"
            ),
            "final_url":r.url

        })

    except Exception as e:

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500


# ========================================
# RUN
# ========================================

if __name__=="__main__":
    app.run()
