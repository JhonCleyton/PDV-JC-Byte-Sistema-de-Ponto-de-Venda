import sys
import os
import socket
import subprocess
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStatusBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap

class ServerThread(threading.Thread):
    """Thread que executa o servidor Flask"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True  # O thread será fechado quando o programa principal fechar
        
    def run(self):
        # Inicia o servidor Flask usando o mesmo comando do batch script
        subprocess.run(["python", "app.py"])

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

class PDVWindow(QMainWindow):
    """Janela principal do PDV"""
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.setWindowTitle("PDV - JC Byte")
        self.setMinimumSize(1024, 700)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | 
                          Qt.WindowMinMaxButtonsHint | Qt.WindowTitleHint)
        self.showMaximized()  # Inicia maximizado
        
        # Obtém o endereço IP
        self.ip_address = get_ip_address()
        if self.ip_address != "localhost" and self.ip_address != "127.0.0.1":
            self.base_url = f"http://{self.ip_address}:5000"
        else:
            self.base_url = "http://localhost:5000"
        
        # Componentes da UI
        self.setup_ui()
        
        # Timer para verificar quando o servidor estiver pronto
        self.server_check_timer = QTimer(self)
        self.server_check_timer.timeout.connect(self.check_server)
        self.server_check_timer.start(1000)  # Verifica a cada segundo
        
        # Mensagem inicial no status bar
        self.statusBar().showMessage(f"Iniciando servidor... Aguarde.")
        
    def setup_ui(self):
        """Configura os elementos da interface"""
        # Define ícone da aplicação
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "static", "logo_merc.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens
        main_layout.setSpacing(0)  # Remove espaçamento
        
        # Componente WebView
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("about:blank"))  # Página inicial em branco
        main_layout.addWidget(self.web_view)
        
        # Barra de status (mantida para mostrar o endereço)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Define o estilo geral
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #555;
                font-size: 11px;
                max-height: 16px;
                border-top: 1px solid #ddd;
            }
        """)
    
    def check_server(self):
        """Verifica se o servidor Flask está pronto e carrega a página"""
        try:
            # Tenta fazer uma conexão ao servidor
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            host = self.ip_address if self.ip_address != "localhost" else "127.0.0.1"
            s.connect((host, 5000))
            s.close()
            
            # Se chegou aqui, o servidor está pronto
            self.server_check_timer.stop()
            self.load_pdv()
        except:
            # O servidor ainda não está pronto
            pass
    
    def load_pdv(self):
        """Carrega a página do PDV no WebView"""
        self.web_view.setUrl(QUrl(self.base_url))
        self.statusBar().showMessage(f"Conectado: {self.base_url}")
        
        # Injetar JavaScript para traduzir as mensagens de diálogo
        self.web_view.page().runJavaScript("""
        // Sobrescrever mensagens de confirmação para português
        window.onbeforeunload = function(e) {
            e.preventDefault();
            return "Tem certeza que deseja sair? As alterações não salvas serão perdidas.";
        };
        """)
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela"""
        # Fecha o aplicativo
        event.accept()

def main():
    """Função principal"""
    # Inicia o servidor Flask em uma thread separada
    server_thread = ServerThread()
    server_thread.start()
    
    # Inicia a aplicação Qt
    app = QApplication(sys.argv)
    
    # Aplica estilo nativo do sistema operacional
    app.setStyle('Fusion')
    
    # Mostra mensagem de carregamento
    splash_text = "Iniciando PDV JC Byte..."
    splash = QLabel()
    splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    splash.setAlignment(Qt.AlignCenter)
    splash.setStyleSheet("""
        background-color: #FFD700;
        color: #333;
        font-size: 18px;
        font-weight: bold;
        padding: 20px 40px;
        border-radius: 10px;
    """)
    splash.setText(splash_text)
    splash.show()
    app.processEvents()
    
    # Dá um tempo para o servidor iniciar e mostra splash screen
    time.sleep(2)
    
    # Cria e mostra a janela principal
    window = PDVWindow()
    window.show()
    
    # Fecha a splash screen
    splash.close()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
