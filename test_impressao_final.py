"""
Script para testar impressão de venda com Flask inicializado corretamente
"""
import os
import sys
import logging
import win32print
import win32api
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import tempfile

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Config:
    """Configurações básicas"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pdv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRINTER_ENABLED = True
    AUTO_PRINT = True

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Importa os modelos
from models import CompanyInfo, Sale, SaleItem

# Importa o módulo de impressão
from utils.printer import print_receipt

with app.app_context():
    def test_impressao_venda():
        """
        Testa impressão de venda completa
        """
        try:
            # Lista todas as impressoras disponíveis
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            logging.info(f"Impressoras disponíveis: {printers}")
            
            # Verifica se a impressora POS-58 está disponível
            if "POS-58" not in printers:
                logging.error("Impressora POS-58 não encontrada!")
                return False
            
            # Cria um objeto de venda de teste
            sale = Sale(
                customer_id=None,
                supervisor_id=1,
                user_id=1,
                date=datetime.now(),
                total=100.0,
                payment_method="DINHEIRO",
                status="finalized"
            )
            
            # Adiciona um item de teste
            item = SaleItem(
                product_id=1,
                quantity=2,
                price=50.0,
                discount=0.0,
                subtotal=100.0
            )
            sale.items.append(item)
            
            # Salva a venda no banco de dados
            db.session.add(sale)
            db.session.commit()
            
            logging.info(f"Venda criada com sucesso. ID: {sale.id}")
            
            # Tenta imprimir o cupom
            try:
                logging.info("Tentando imprimir cupom...")
                result = print_receipt(sale, "POS-58")
                if result:
                    logging.info("Cupom impresso com sucesso!")
                    return True
                else:
                    logging.error("Falha ao imprimir cupom!")
                    return False
            except Exception as e:
                logging.error(f"Erro ao imprimir: {str(e)}")
                return False
                
        except Exception as e:
            logging.error(f"Erro geral: {str(e)}")
            return False

def main():
    """Função principal"""
    print("=== TESTE DE IMPRESSÃO DE VENDA ===")
    
    if test_impressao_venda():
        print("Impressão de venda testada com sucesso!")
    else:
        print("Falha ao testar impressão de venda.")

if __name__ == "__main__":
    main()
