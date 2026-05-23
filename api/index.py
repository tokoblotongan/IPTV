from flask import Flask, jsonify, request, render_template, Response
import requests
import json

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

# ==========================================
# 1. FUNGSI UTAMA: TES KODE IPTV (TOMBOL 1)
# ==========================================
@app.route('/test', methods=['POST'])
def test_code():
    mode = request.form.get('mode')
    server = request.form.get('server', '').strip().rstrip('/')
    
    # --- PENGUJIAN MODE XTREAM CODES ---
    if mode == 'xtream':
        username = request.form.get('user', '').strip()
        password = request.form.get('pass', '').strip()
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username dan Password wajib diisi untuk mode Xtream!"}), 400
            
        test_url = f"{server}/player_api.php?username={username}&password={password}"
        try:
            response = requests.get(test_url, timeout=7)
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('user_info', {})
                auth = user_info.get('auth', 0)
                status = user_info.get('status', '')
                
                if auth == 1 and status == 'Active':
                    exp_date = user_info.get('exp_date')
                    max_conn = user_info.get('max_connections', 1)
                    return jsonify({
                        "status": "success",
                        "message": f"✅ KODE VALID! Status: {status} | Max Connections: {max_conn} | Exp Date Timestamp: {exp_date}"
                    })
                else:
                    return jsonify({"status": "failed", "message": f"❌ Kode ditolak oleh server. Status: {status or 'Tidak Diketahui'}"})
            else:
                return jsonify({"status": "error", "message": f" Server merespons dengan HTTP {response.status_code}"})
        except Exception as e:
            return jsonify({"status": "error", "message": f" Gagal terhubung ke server: {str(e)}"})

    # --- PENGUJIAN MODE MAC PORTAL (STALKER) ---
    elif mode == 'mac':
        mac = request.form.get('mac_address', '').strip()
        if not mac:
            return jsonify({"status": "error", "message": "MAC Address wajib diisi untuk mode Stalker!"}), 400
            
        # Menggunakan handshake awal Stalker Portal
        handshake_url = f"{server}/portal.php?type=stb&action=handshake"
        headers = {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3'}
        try:
            res = requests.get(handshake_url, headers=headers, timeout=7)
            if res.status_code == 200:
                return jsonify({
                    "status": "success",
                    "message": f"✅ PORTAL MERESPONS! Handshake berhasil dijalankan pada {server}. Jalur Mac siap diproses."
                })
            else:
                return jsonify({"status": "failed", "message": f"❌ Portal ada namun memberikan respons HTTP {res.status_code}"})
        except Exception as e:
            return jsonify({"status": "error", "message": f" Gagal terhubung ke Mac Portal: {str(e)}"})

    # --- PENGUJIAN MODE RAW URL M3U ---
    elif mode == 'url':
        try:
            res = requests.head(server, timeout=7, allow_redirects=True)
            if res.status_code == 200:
                return jsonify({"status": "success", "message": "✅ URL AKTIF! Link M3U/M3U8 merespons dengan status 200 OK."})
            else:
                return jsonify({"status": "failed", "message": f"❌ Link mengembalikan respons HTTP {res.status_code}"})
        except Exception as e:
            return jsonify({"status": "error", "message": f" Gagal memverifikasi URL: {str(e)}"})

    return jsonify({"status": "error", "message": "Mode tidak dikenal!"}), 400

# ==========================================
# 2. FUNGSI UTAMA: CONVERT KE M3U (TOMBOL 2)
# ==========================================
@app.route('/convert', methods=['POST'])
def convert_m3u():
    mode = request.form.get('mode')
    server = request.form.get('server', '').strip().rstrip('/')
    
    # Simulasi pembuatan string teks berformat #EXTM3U
    m3u_content = "#EXTM3U\n"
    
    if mode == 'xtream':
        username = request.form.get('user', '').strip()
        password = request.form.get('pass', '').strip()
        m3u_content += f"#EXTINF:-1,Channel Contoh (Xtream)\n{server}/live/{username}/{password}/1.ts\n"
        filename = "xtream_channels.m3u"
        
    elif mode == 'mac':
        mac = request.form.get('mac_address', '').strip()
        m3u_content += f"#EXTINF:-1,Channel Contoh (Stalker MAC)\n{server}/portal.php?type=stb&action=get_ordered_channels&mac={mac}\n"
        filename = "stalker_channels.m3u"
        
    else:
        m3u_content += f"#EXTINF:-1,Channel Contoh (Raw URL)\n{server}\n"
        filename = "converted_channels.m3u"
        
    # Mengirimkan response balik berupa file download mentah ke browser pengguna
    return Response(
        m3u_content,
        mimetype="audio/x-mpegurl",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
