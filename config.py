"""
Configurações do aplicativo
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações gerais do aplicativo"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'pdv.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de impressão
    PRINTER_ENABLED = True
    AUTO_PRINT = True
    RECEIPTS_DIR = os.path.join(basedir, 'cupons')  # Diretório para salvar os cupons
