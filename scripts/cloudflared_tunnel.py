import os
import platform
import stat
import subprocess
import threading
import urllib.request
import re
from modules import script_callbacks, shared

EXT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(EXT_DIR, "bin")
BIN_PATH = os.path.join(BIN_DIR, "cloudflared")

def get_cloudflared_token():
    token = getattr(shared.cmd_opts, "cloudflared", None)
    if token is None:
        return None

    token = token.strip()
    if not token:
        print("Cloudflared: --cloudflared provided without a token; falling back to quick tunnel mode.")
        return None

    return token

def get_system_arch():
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        if "amd64" in machine or "x86_64" in machine:
            return "windows", "amd64"
        elif "386" in machine:
            return "windows", "386"
        else:
            return "windows", "amd64"
    elif system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return "linux", "arm64"
        elif "arm" in machine:
            return "linux", "arm"
        elif "x86_64" in machine or "amd64" in machine:
            return "linux", "amd64"
        elif "386" in machine:
            return "linux", "386"
        else:
            return "linux", "amd64"
    elif system == "darwin":
        return "darwin", "amd64"
    return system, machine

def get_download_url():
    system, arch = get_system_arch()
    if system == "windows":
        return f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-{arch}.exe"
    elif system == "linux":
        return f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{arch}"
    elif system == "darwin":
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
    else:
        return None

def download_cloudflared():
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR, exist_ok=True)
    
    system, _ = get_system_arch()
    bin_ext = ".exe" if system == "windows" else ""
    expected_bin_path = BIN_PATH + bin_ext

    if os.path.exists(expected_bin_path):
        return expected_bin_path
        
    url = get_download_url()
    if not url:
        print("Cloudflared: Unsupported OS/Architecture.")
        return None
        
    print(f"Downloading cloudflared from {url}...")
    
    try:
        if url.endswith('.tgz'):
            import tarfile
            tgz_path = os.path.join(BIN_DIR, "cloudflared.tgz")
            urllib.request.urlretrieve(url, tgz_path)
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extractall(path=BIN_DIR)
            os.remove(tgz_path)
            
            # Find the extracted binary which is usually named 'cloudflared' inside the tgz
            if os.path.exists(BIN_PATH):
                expected_bin_path = BIN_PATH
            else:
                print("Cloudflared: Could not find extracted binary.")
                return None
        else:
            urllib.request.urlretrieve(url, expected_bin_path)
            
        st = os.stat(expected_bin_path)
        os.chmod(expected_bin_path, st.st_mode | stat.S_IEXEC)
        return expected_bin_path
    except Exception as e:
        print(f"Cloudflared download failed: {e}")
        return None

def start_cloudflared(port):
    # Only start if cmd_opts.cloudflared is true?
    # Since it's a standalone extension, we'll run it automatically if installed and enabled.
    
    # We can use shared.opts to allow users to toggle it on/off in settings
    enabled = getattr(shared.opts, "cloudflared_enable", True)
    if not enabled:
        return
        
    bin_path = download_cloudflared()
    if not bin_path:
        return

    token = get_cloudflared_token()
    if token:
        print("Starting cloudflared tunnel with token...")
        cmd = [bin_path, "tunnel", "--no-autoupdate", "run", "--token", token]
    else:
        print(f"Starting cloudflared quick tunnel on port {port}...")
        cmd = [bin_path, "tunnel", "--url", f"http://127.0.0.1:{port}"]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        def monitor_output():
            url_found = False
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                if not url_found and not token:
                    match = re.search(r"https://[-a-zA-Z0-9]+\.trycloudflare\.com", line)
                    if match:
                        print(f"\n==================================================================")
                        print(f"Cloudflared Tunnel URL: {match.group(0)}")
                        print(f"==================================================================\n")
                        url_found = True
                elif token:
                    # In token mode, print useful connection logs
                    if "Registered tunnel connection" in line or "Ready" in line or "INF" in line:
                        print(f"Cloudflared: {line.strip()}")

        thread = threading.Thread(target=monitor_output, daemon=True)
        thread.start()
    except Exception as e:
        print(f"Failed to start cloudflared: {e}")

def on_app_started(demo, app):
    port = shared.cmd_opts.port if shared.cmd_opts.port else 7860
    start_cloudflared(port)

def on_ui_settings():
    shared.opts.add_option(
        "cloudflared_enable",
        shared.OptionInfo(True, "Enable Cloudflared Tunnel on Startup", section=("cloudflared", "Cloudflared Tunnel"))
    )

script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_settings(on_ui_settings)
