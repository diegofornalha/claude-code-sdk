#!/usr/bin/env python3
"""
Servidor simples para o frontend
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server(port=8080):
    # Muda para o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("🔧 HACKATHON FLOW BLOCKCHAIN AGENTS - FRONTEND")
    print("=" * 60)
    print(f"📡 Servidor rodando na porta {port}")
    print(f"🔗 Acesse: http://localhost:{port}")
    print(f"📁 Servindo arquivos de: {script_dir}")
    print("=" * 60)
    print("💡 Backend API deve estar rodando na porta 8080")
    print("🛑 Pressione Ctrl+C para parar")
    print("=" * 60)

    try:
        with HTTPServer(('localhost', port), CORSRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🔴 Servidor parado")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:
            print(f"\n❌ Porta {port} já está em uso!")
            print("Tentando porta alternativa...")
            # Tenta portas alternativas
            for alt_port in [8080, 3003, 8080, 8080]:
                try:
                    print(f"Tentando porta {alt_port}...")
                    with HTTPServer(('localhost', alt_port), CORSRequestHandler) as httpd:
                        print(f"✅ Servidor rodando na porta {alt_port}")
                        print(f"🔗 Acesse: http://localhost:{alt_port}")
                        httpd.serve_forever()
                        break
                except:
                    continue
        else:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_server()