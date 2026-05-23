from flask import Flask, jsonify, request
import requests
import datetime
import random
import re
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlparse

# Mematikan warning ssl requests
requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

@app.route('/')
def home():
    return "API IPTV Ultimate Tool v9 Berhasil Berjalan di Vercel!"

@app.route('/convert')
def convert():
    # 1. Mengambil input parameter dari URL browser secara dinamis
    # Contoh penggunaan link: https://iptv-eosin-omega.vercel.app/convert?url=http://contoh.com:8080&user=username_anda&pass=password_anda
    server_url = request.args.get('url')
    username = request.args.get('user')
    password = request.args.get('pass')
    
    if not all([server_url, username, password]):
        return jsonify({
            "error": "Gagal! Parameter 'url', 'user', dan 'pass' wajib diisi di dalam link URL."
        }), 400
        
    try:
        # 2. Membersihkan format URL server
        server_url = server_url.rstrip('/')
        
        # 3. Jalur API Xtremecodes untuk mengambil semua data live stream
        # (Silakan sesuaikan endpoint ini dengan logika asli dari Google Colab Anda)
        action_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_live_streams"
        
        response = requests.get(action_url, timeout=15, verify=False)
        
        if response.status_code != 200:
            return f"Error: Server Xtremecodes merespon dengan kode {response.status_code}", 500
            
        data_streams = response.json()
        
        # Jika respon berupa dict error dari Xtremecodes
        if isinstance(data_streams, dict) and data_streams.get('user_info', {}).get('auth') == 0:
            return "Error: Autentikasi Xtremecodes gagal (Username atau Password salah).", 401
            
        # 4. Proses menyusun isi File M3U
        m3u_lines = ["#EXTM3U"]
        
        for stream in data_streams:
            # Mengambil data nama, id, dan kategori saluran
            name = stream.get('name', 'Unknown Channel')
            stream_id = stream.get('stream_id')
            category_id = stream.get('category_id', '')
            ext = stream.get('container_extension', 'ts')
            
            if stream_id:
                # Membuat link stream lurus untuk player IPTV
                stream_link = f"{server_url}/{username}/{password}/{stream_id}.{ext}"
                
                # Menyusun baris tag M3U standar
                m3u_lines.append(f'#EXTINF:-1 tvg-id="" tvg-name="{name}" group-title="{category_id}",{name}')
                m3u_lines.append(stream_link)
                
        # Menggabungkan seluruh baris menjadi satu string teks utuh
        full_m3u_content = "\n".join(m3u_lines)
        
        # 5. Mengirimkan hasil langsung sebagai file teks M3U ke browser / aplikasi player
        return full_m3u_content, 200, {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': 'inline; filename="playlist.m3u"'
        }
        
    except requests.exceptions.RequestException as e:
        return f"Error koneksi ke server Xtremecodes: {str(e)}", 500
    except Exception as e:
        return f"Terjadi kesalahan internal server: {str(e)}", 500
