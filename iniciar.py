import sys
import os
import socket
import subprocess
import threading
import time
import platform
from flask import Flask
import app

# Verifica se estamos em um ambiente sem GUI (como VPS)
IS_VPS = platform.system() != 'Windows'

# Função para inicializar o banco de dados
def init_database():
    print("Inicializando banco de dados...")
    with app.app.app_context():
        app.db.create_all()
        print("Banco de dados criado")
        app.init_admin()
        app.init_company_info()
        print("Dados iniciais criados")

class ServerThread(threading.Thread):
    """Thread que executa o servidor Flask"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True  # O thread será fechado quando o programa principal fechar
        
    def run(self):
        # Inicia o servidor Flask
        app.app.run(host='0.0.0.0', port=5000)

def get_ip_address():
    """Obtém o endereço IP da máquina na rede"""
    try:
        # Cria um socket e tenta se conectar ao Google DNS para obter o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Se não conseguir, tenta obter o hostname
        try:
            host_name = socket.gethostname()
            ip = socket.gethostbyname(host_name)
            if ip.startswith("127."):
                # Se o IP começa com 127, procure interfaces de rede
                for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
                    if not ip.startswith("127."):
                        return ip
            return ip
        except:
            # Se tudo falhar, retorna localhost
            return "localhost"

def main():
    try:
        # Inicializa o banco de dados
        init_database()
        
        # Obtém o IP da máquina
        ip = get_ip_address()
        print(f"\nServidor iniciado em: http://{ip}:5000")
        print("Acesse este endereço em um navegador web para usar o sistema")
        print("Ctrl+C para encerrar o servidor\n")
        
        # Inicia o servidor Flask
        app.app.run(host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nServidor encerrado")
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
