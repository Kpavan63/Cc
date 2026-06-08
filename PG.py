#!/usr/bin/env python3
"""
================================================================
  PG WIFI PRANK PENTEST v1.0
  "Your Hacked" Popup Notification System
  Authorized Security Awareness Testing
================================================================
"""

import os, sys, json, time, hashlib, socket, ssl, urllib.request, threading
import http.server, socketserver, random, string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# COLOR ENGINE
# ============================================================
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'; N = '\033[0m'
    BOLD = '\033[1m'; DIM = '\033[2m'; BLINK = '\033[5m'

# ============================================================
# BANNER
# ============================================================
def show_banner():
    os.system('clear')
    print(f"""{C.R}
  ██████╗  ██████╗     ██╗    ██╗██╗███████╗██╗
  ██╔════╝ ██╔════╝     ██║    ██║██║██╔════╝██║
  ██║  ███╗██║  ███╗    ██║ █╗ ██║██║█████╗  ██║
  ██║   ██║██║   ██║    ██║███╗██║██║██╔══╝  ██║
  ╚██████╔╝╚██████╔╝    ╚███╔███╔╝██║██║     ██║
   ╚═════╝  ╚═════╝      ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝
  {C.N}
  {C.G}╔══════════════════════════════════════════════════════════╗{C.N}
  {C.G}║{C.N}  {C.BOLD}{C.Y}PG WIFI PRANK PENTEST v1.0 — AUTHORIZED TEST{C.N}          {C.G}║{C.N}
  {C.G}║{C.N}  {C.DIM}Scan Network → Find Devices → Send "UR HACKED" Popup{C.N}  {C.G}║{C.N}
  {C.G}╚══════════════════════════════════════════════════════════╝{C.N}
""")
    time.sleep(1)

# ============================================================
# NETWORK DETECTION
# ============================================================
def detect_network():
    print(f"\n  {C.B}[NETWORK]{C.N} {C.BOLD}Detecting your network...{C.N}")
    
    # Get local IP and subnet
    try:
        # Try multiple methods
        ip = None
        methods = [
            "ip addr show | grep 'inet ' | awk '{print $2}'",
            "ifconfig | grep 'inet ' | awk '{print $2}'",
            "hostname -I"
        ]
        
        for cmd in methods:
            try:
                out = os.popen(cmd).read()
                if out:
                    ips = out.strip().split()
                    for potential_ip in ips:
                        p = potential_ip.split('/')[0]
                        if p.startswith('192.') or p.startswith('10.') or p.startswith('172.'):
                            ip = p
                            break
                if ip:
                    break
            except:
                continue
        
        if not ip:
            # Ask user
            print(f"  {C.Y}⚠ Could not auto-detect IP{C.N}")
            ip = input(f"  {C.Y}Enter your local IP (e.g., 192.168.1.50): {C.N}").strip()
        
        subnet = '.'.join(ip.split('.')[:3])
        print(f"  {C.G}✓{C.N} Your IP: {ip}")
        print(f"  {C.G}✓{C.N} Subnet: {subnet}.0/24")
        return {"ip": ip, "subnet": subnet}
    
    except Exception as e:
        print(f"  {C.R}✖ Error: {e}{C.N}")
        subnet = input(f"  {C.Y}Enter subnet (e.g., 192.168.1): {C.N}").strip()
        return {"ip": f"{subnet}.1", "subnet": subnet}

# ============================================================
# NETWORK SCANNER
# ============================================================
def scan_network(subnet):
    print(f"\n  {C.B}[SCAN]{C.N} {C.BOLD}Scanning {subnet}.0/24 for devices...{C.N}")
    print(f"  {C.DIM}This will find phones, laptops, smart TVs, etc.{C.N}\n")
    
    live_hosts = []
    total = 254
    
    def scan_ip(ip):
        try:
            # Try common ports
            for port in [80, 8080, 443, 554, 3000, 5000, 8000]:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    if s.connect_ex((ip, port)) == 0:
                        s.close()
                        return (ip, port)
                    s.close()
                except:
                    pass
            
            # Ping fallback
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((ip, 80)) == 0 or s.connect_ex((ip, 443)) == 0:
                    s.close()
                    return (ip, None)
                s.close()
            except:
                pass
        except:
            pass
        return None
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_ip, f"{subnet}.{i}"): i for i in range(1, 256)}
        
        completed = 0
        for future in futures:
            completed += 1
            result = future.result()
            if result:
                ip, port = result
                live_hosts.append(ip)
                print(f"  {C.G}📱{C.N} Found: {ip}" + (f" (port {port})" if port else ""))
            
            # Progress
            if completed % 50 == 0:
                pct = int(completed / total * 100)
                bar = f"{C.G}{'█' * (pct // 2)}{C.DIM}{'▒' * (50 - pct // 2)}{C.N}"
                print(f"\r  {C.B}[SCAN]{C.N} [{bar}] {C.Y}{pct}%{C.N} ({len(live_hosts)} found)", end='', flush=True)
    
    print(f"\n\n  {C.G}✓{C.N} Scan complete: {len(live_hosts)} device(s) found")
    return live_hosts

# ============================================================
# DEVICE INFO
# ============================================================
def get_device_name(ip):
    """Try to get device hostname."""
    try:
        name = socket.gethostbyaddr(ip)[0]
        return name
    except:
        return "Unknown Device"

def get_device_vendor(ip):
    """Check common web interfaces."""
    try:
        req = urllib.request.Request(f"http://{ip}/", timeout=2)
        resp = urllib.request.urlopen(req)
        html = resp.read().decode(errors='ignore').lower()
        if 'android' in html: return "Android"
        if 'iphone' in html or 'ios' in html: return "iPhone"
        if 'windows' in html: return "Windows PC"
        if 'samsung' in html: return "Samsung"
        if 'miui' in html or 'xiaomi' in html: return "Xiaomi"
        if 'router' in html or 'tplink' in html: return "Router/AP"
        if 'camera' in html or 'tapo' in html: return "Camera"
        return "Web Device"
    except:
        return None

# ============================================================
# THE "UR HACKED" POPUP SERVER
# ============================================================
class PopupHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        
        # The prank page
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚠ SECURITY ALERT</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: #0a0a0a;
            font-family: 'Orbitron', monospace;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}
        
        .container {{
            text-align: center;
            padding: 40px;
            position: relative;
        }}
        
        .glitch {{
            font-size: 72px;
            font-weight: 900;
            color: #ff0000;
            text-shadow: 
                2px 2px 0 #00ff00,
                -2px -2px 0 #0000ff;
            animation: glitch 1s infinite;
            letter-spacing: 10px;
        }}
        
        @keyframes glitch {{
            0% {{ transform: translate(0); }}
            20% {{ transform: translate(-3px, 3px); }}
            40% {{ transform: translate(-3px, -3px); }}
            60% {{ transform: translate(3px, 3px); }}
            80% {{ transform: translate(3px, -3px); }}
            100% {{ transform: translate(0); }}
        }}
        
        .subtitle {{
            font-size: 28px;
            color: #ff4444;
            margin-top: 30px;
            animation: blink 0.5s infinite;
            text-shadow: 0 0 20px #ff0000;
        }}
        
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
        
        .info {{
            font-size: 14px;
            color: #666;
            margin-top: 40px;
            font-family: Arial, sans-serif;
        }}
        
        .matrix {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.1;
            font-size: 14px;
            color: #00ff00;
            overflow: hidden;
            font-family: monospace;
        }}
        
        .skull {{
            font-size: 120px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        .progress-bar {{
            width: 300px;
            height: 4px;
            background: #1a1a1a;
            margin: 30px auto;
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: #ff0000;
            animation: progress 3s linear;
            width: 100%;
        }}
        
        @keyframes progress {{
            from {{ width: 0%; }}
            to {{ width: 100%; }}
        }}
        
        .cursor {{
            display: inline-block;
            width: 10px;
            height: 20px;
            background: #ff0000;
            animation: cursor-blink 0.5s infinite;
            vertical-align: middle;
        }}
        
        @keyframes cursor-blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
        
        .typing {{
            color: #00ff00;
            font-size: 16px;
            margin-top: 20px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="matrix" id="matrix"></div>
    
    <div class="container">
        <div class="skull">💀</div>
        <div class="glitch">HACKED</div>
        <div class="subtitle">⚠ YOUR DEVICE HAS BEEN COMPROMISED ⚠</div>
        
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        
        <div class="typing" id="typing"></div>
        
        <div class="info">
            <p>🔒 IP: {self.client_address[0]}</p>
            <p>🕒 Time: {datetime.now().strftime('%H:%M:%S')}</p>
            <p>📡 Network: PG WIFI</p>
            <p style="margin-top:10px; color:#333;">This is an authorized security awareness test.</p>
        </div>
    </div>
    
    <script>
        // Matrix rain effect
        const matrix = document.getElementById('matrix');
        const chars = '01アイウエオカキクケコサシスセソタチツテト';
        let matrixHTML = '';
        for (let i = 0; i < 100; i++) {{
            matrixHTML += chars[Math.floor(Math.random() * chars.length)] + ' ';
        }}
        matrix.innerHTML = matrixHTML.repeat(50);
        
        // Typing effect
        const texts = [
            "> ACCESS GRANTED...",
            "> EXTRACTING DATA...",
            "> DOWNLOADING CONTACTS...",
            "> ACCESSING CAMERA...",
            "> COLLECTING PASSWORDS...",
            "> SYSTEM COMPROMISED...",
            "> YOU HAVE BEEN HACKED!"
        ];
        
        const typingElement = document.getElementById('typing');
        let textIndex = 0;
        let charIndex = 0;
        
        function typeText() {{
            if (textIndex < texts.length) {{
                if (charIndex < texts[textIndex].length) {{
                    typingElement.innerHTML = texts[textIndex].substring(0, charIndex + 1) + '<span class="cursor"></span>';
                    charIndex++;
                    setTimeout(typeText, 50 + Math.random() * 100);
                }} else {{
                    typingElement.innerHTML = texts[textIndex];
                    charIndex = 0;
                    textIndex++;
                    setTimeout(typeText, 500);
                }}
            }}
        }}
        
        setTimeout(typeText, 1000);
        
        // Prevent easy exit
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.addEventListener('keydown', e => {{
            if (e.key === 'F11' || e.key === 'Escape') {{
                e.preventDefault();
            }}
        }});
    </script>
</body>
</html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def start_popup_server():
    """Start local HTTP server to serve the popup."""
    port = random.randint(8000, 8999)
    handler = PopupHandler
    
    try:
        server = socketserver.TCPServer(("0.0.0.0", port), handler)
        server.timeout = 0.5
        print(f"\n  {C.G}✓{C.N} Popup server running on port {port}")
        return server, port
    except OSError:
        # Port in use, try another
        return start_popup_server()

# ============================================================
# SEND POPUP TO DEVICE
# ============================================================
def send_popup(ip, port, server_ip, server_port):
    """Send the popup to a device by redirecting their browser."""
    print(f"\n  {C.Y}▸{C.N} Targeting {ip}...")
    
    methods_tried = []
    
    # Method 1: Open HTTP port redirect
    for target_port in [80, 8080, 3000, 5000, 8000]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, target_port)) == 0:
                s.close()
                
                # Try to inject via HTTP redirect
                try:
                    # Send a redirect response if device has HTTP server
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((ip, target_port))
                    
                    redirect = (
                        f"GET / HTTP/1.1\r\n"
                        f"Host: {ip}\r\n"
                        f"User-Agent: Mozilla/5.0\r\n"
                        f"Accept: text/html\r\n"
                        f"Connection: close\r\n\r\n"
                    )
                    sock.send(redirect.encode())
                    sock.close()
                    print(f"  {C.G}  ✓{C.N} Probed port {target_port}")
                except:
                    pass
            s.close()
        except:
            pass
    
    # Method 2: SSDP/UPnP discovery broadcast
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        
        # SSDP NOTIFY packet
        ssdp_msg = (
            "NOTIFY * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "NT: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\n"
            "NTS: ssdp:alive\r\n"
            "LOCATION: http://{}:{}/\r\n".format(server_ip, server_port) +
            "CACHE-CONTROL: max-age=180\r\n"
            "SERVER: Linux/5.10 UPnP/1.0 HACKER/1.0\r\n"
            "USN: uuid:12345678-1234-1234-1234-123456789012\r\n\r\n"
        )
        
        sock.sendto(ssdp_msg.encode(), (ip, 1900))
        sock.close()
        print(f"  {C.G}  ✓{C.N} Sent SSDP notification")
    except:
        pass
    
    # Method 3: Try to open URLs via common services
    for target_port in [80, 8080, 3000, 5000]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((ip, target_port)) == 0:
                # Send HTTP redirect
                response = (
                    f"HTTP/1.1 302 Found\r\n"
                    f"Location: http://{server_ip}:{server_port}/\r\n"
                    f"Content-Length: 0\r\n"
                    f"Connection: close\r\n\r\n"
                )
                sock.send(response.encode())
                sock.close()
                print(f"  {C.G}  ✓{C.N} Redirect sent to port {target_port}")
            sock.close()
        except:
            pass

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    show_banner()
    
    print(f"  {C.R}⚠{C.N} {C.BOLD}SECURITY AWARENESS TEST — PG WIFI NETWORK{C.N}")
    print(f"  {C.DIM}This tool demonstrates how easily devices on the same network{C.N}")
    print(f"  {C.DIM}can be targeted. All testing is authorized.{C.N}\n")
    
    input(f"  {C.Y}Press Enter to start network reconnaissance...{C.N}")
    
    # Step 1: Detect network
    network = detect_network()
    
    # Step 2: Scan devices
    devices = scan_network(network["subnet"])
    
    if not devices:
        print(f"\n  {C.R}✖ No devices found!{C.N}")
        print(f"  {C.Y}  Make sure you're connected to the PG WiFi.{C.N}")
        return
    
    # Step 3: Identify devices
    print(f"\n  {C.B}[IDENTIFY]{C.N} {C.BOLD}Identifying devices...{C.N}\n")
    device_list = []
    
    for ip in devices:
        name = get_device_name(ip)
        vendor = get_device_vendor(ip)
        device_list.append({"ip": ip, "name": name, "vendor": vendor})
        vendor_str = f" ({vendor})" if vendor else ""
        print(f"  {C.G}📱{C.N} {ip:<16} {name}{vendor_str}")
    
    # Step 4: Ask what to do
    print(f"\n  {C.B}[ATTACK]{C.N} {C.BOLD}Select target for popup demonstration:{C.N}")
    print(f"  [{C.Y}1{C.N}] Send to ALL devices")
    print(f"  [{C.Y}2{C.N}] Choose specific device")
    print(f"  [{C.Y}3{C.N}] Just start the server (manual testing)")
    print(f"  [{C.Y}n{C.N}] Cancel")
    
    choice = input(f"\n  {C.C}▶{C.N} Select: ").strip()
    
    if choice == 'n':
        print(f"\n  {C.Y}Test cancelled.{C.N}")
        return
    
    # Step 5: Start the popup server
    print(f"\n  {C.B}[SERVER]{C.N} {C.BOLD}Starting popup server...{C.N}")
    server, port = start_popup_server()
    server_ip = network["ip"]
    
    print(f"  {C.G}✓{C.N} Server URL: http://{server_ip}:{port}/")
    print(f"  {C.G}✓{C.N} Anyone who opens this URL sees the 'HACKED' page\n")
    
    # Step 6: Send popups
    if choice == '1':
        print(f"  {C.B}[ATTACK]{C.N} {C.BOLD}Sending popup to ALL {len(devices)} devices...{C.N}")
        print(f"  {C.DIM}This may take a moment...{C.N}\n")
        
        for device in devices:
            send_popup(device, port, server_ip, port)
            time.sleep(0.5)
    
    elif choice == '2':
        print(f"\n  Select device:")
        for i, d in enumerate(device_list):
            vendor = f" ({d['vendor']})" if d.get('vendor') else ""
            print(f"  [{C.Y}{i+1}{C.N}] {d['ip']} — {d['name']}{vendor}")
        
        dev_choice = input(f"\n  {C.C}▶{C.N} Device number: ").strip()
        if dev_choice.isdigit():
            idx = int(dev_choice) - 1
            if 0 <= idx < len(device_list):
                send_popup(device_list[idx]["ip"], port, server_ip, port)
    
    # Step 7: Keep server running
    print(f"\n  {C.G}╔══════════════════════════════════════════════════╗{C.N}")
    print(f"{C.G}║{C.N}  {C.BOLD}{C.R}💀 POPUP SERVER ACTIVE{C.N}                         {C.G}║{C.N}")
    print(f"{C.G}║{C.N}  {C.Y}URL: http://{server_ip}:{port}/{C.N}                         {C.G}║{C.N}")
    print(f"{C.G}║{C.N}  {C.Y}Any device on PG WiFi can open this URL{C.N}           {C.G}║{C.N}")
    print(f"{C.G}║{C.N}  {C.DIM}They will see the 'UR HACKED' popup{C.N}                {C.G}║{C.N}")
    print(f"{C.G}║{C.N}  {C.DIM}Press Ctrl+C to stop the server{C.N}                   {C.G}║{C.N}")
    print(f"{C.G}╚══════════════════════════════════════════════════╝{C.N}")
    
    # Try to broadcast SSDP to notify all devices
    print(f"\n  {C.B}[BROADCAST]{C.N} {C.BOLD}Sending network-wide notification...{C.N}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        broadcast_msg = (
            "NOTIFY * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "NT: urn:schemas-upnp-org:device:1\r\n"
            "NTS: ssdp:alive\r\n"
            "LOCATION: http://{}:{}/\r\n".format(server_ip, port) +
            "CACHE-CONTROL: max-age=180\r\n"
            "SERVER: HACKER/1.0\r\n"
            "USN: uuid:deadbeef-dead-beef-dead-beefdeadbeef\r\n\r\n"
        )
        
        # Broadcast to subnet
        subnet = network["subnet"]
        sock.sendto(broadcast_msg.encode(), (f"{subnet}.255", 1900))
        sock.sendto(broadcast_msg.encode(), ("239.255.255.250", 1900))
        sock.close()
        print(f"  {C.G}✓{C.N} Broadcast sent to network")
    except:
        pass
    
    # Keep alive
    try:
        while True:
            server.handle_request()
    except KeyboardInterrupt:
        print(f"\n\n  {C.Y}Server stopped.{C.N}")
    finally:
        server.server_close()
        print(f"\n  {C.G}✓{C.N} Server closed.")
        print(f"\n  {C.R}{'='*60}{C.N}")
        print(f"{C.R}  💀 PRANK COMPLETE — AUTHORIZED SECURITY TEST{C.N}")
        print(f"{C.R}{'='*60}{C.N}")
        print(f"\n  {C.Y}Note:{C.N} The 'HACKED' popup is a harmless HTML page.")
        print(f"  {C.Y}No actual hacking occurred.{C.N}")
        print(f"  {C.Y}This demonstrates how easily devices on shared WiFi{C.N}")
        print(f"  {C.Y}can be targeted.{C.N}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.Y}Test cancelled by user.{C.N}\n")
    except Exception as e:
        print(f"\n\n  {C.R}⚠ Error: {e}{C.N}\n")
        import traceback
        traceback.print_exc()
