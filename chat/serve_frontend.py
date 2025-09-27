#!/usr/bin/env python3
"""
🚀 Servidor do Frontend - Hackathon Flow Blockchain Agents
Roda na porta 3333
"""

import http.server
import socketserver
import os
import sys

PORT = 3333
# Detecta automaticamente o diretório onde o script está
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = SCRIPT_DIR  # Serve arquivos do diretório atual

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers para permitir comunicação com a API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Cache control para desenvolvimento
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Log mais limpo sem mostrar cada requisição
        if '/favicon.ico' not in args[0]:
            super().log_message(format, *args)

try:
    # Verifica se o index.html existe
    index_path = os.path.join(DIRECTORY, 'index.html')
    if not os.path.exists(index_path):
        print(f"⚠️ Aviso: index.html não encontrado em {DIRECTORY}")
        print("Certifique-se de que o arquivo existe no diretório")

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🔧 HACKATHON FLOW BLOCKCHAIN AGENTS - FRONTEND")
        print("=" * 60)
        print(f"📡 Servidor rodando na porta {PORT}")
        print(f"🔗 Acesse: http://localhost:{PORT}")
        print(f"📁 Servindo de: {DIRECTORY}")
        print(f"📄 Arquivos disponíveis:")

        # Lista arquivos HTML no diretório
        for file in os.listdir(DIRECTORY):
            if file.endswith('.html'):
                print(f"   • {file}")

        print("=" * 60)
        print("💡 Backend API deve estar rodando na porta 8888")
        print("🛑 Pressione Ctrl+C para parar")
        print("=" * 60)
        httpd.serve_forever()
except OSError as e:
    if e.errno == 48:  # Address already in use
        print(f"❌ Erro: Porta {PORT} já está em uso")
        print("Tente parar o processo existente ou use outra porta")
    else:
        print(f"❌ Erro ao iniciar servidor: {e}")
except KeyboardInterrupt:
    print("\n🔴 Servidor parado")