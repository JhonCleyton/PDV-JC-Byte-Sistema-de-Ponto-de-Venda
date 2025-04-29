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

# Importa o SQLAlchemy do models.py
from models import db, CompanyInfo, Sale, SaleItem

# Inicializa o SQLAlchemy com o app
with app.app_context():
    db.init_app(app)

# Importa o módulo de impressão
from utils.printer import print_receipt
from utils.thermal_printer import print_sale_receipt

# Cria o contexto do Flask para todo o script
app_context = app.app_context()
app_context.push()

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
            
        # Garante que estamos no contexto do app antes de criar os objetos
        with app.app_context():
            # Cria um objeto de venda de teste
            sale = Sale(
                customer_id=None,
                supervisor_id=1,
                user_id=1,
                date=datetime.now(),
                total=100.0,
                payment_method="DINHEIRO",
                status="finalized",
                description="Teste de impressão"
            )
            
            # Adiciona um item de teste
            item = SaleItem(
                product_id=1,
                quantity=2,
                price=50.0,
                sale_id=None  # Será preenchido automaticamente
            )
            sale.items.append(item)
            
            # Adiciona uma segunda linha de teste
            item2 = SaleItem(
                product_id=2,
                quantity=1,
                price=100.0,
                sale_id=None
            )
            sale.items.append(item2)
            
            # Salva a venda no banco de dados
            db.session.add(sale)
            db.session.commit()
            
            # Atualiza os IDs dos itens
            for item in sale.items:
                item.sale_id = sale.id
            db.session.commit()
            
            logging.info(f"Venda criada com sucesso. ID: {sale.id}")
            
            # Tenta imprimir o cupom
            try:
                logging.info("Tentando imprimir cupom...")
                result = print_sale_receipt(sale, "POS-58")
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
    with app.app_context():
        main()
    # Remove o contexto do Flask ao finalizar
    app_context.pop()
