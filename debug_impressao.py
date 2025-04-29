"""
Script para debug da impressão
"""
import os
import sys
import logging
import win32print
import win32api
import time
from utils.thermal_printer import print_sale_receipt
from models import Sale, SaleItem, db
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_impressao_detalhada():
    """
    Testa a impressão com logs detalhados
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
            payment_method="DINHEIRO",
            supervisor_id=1,
            user_id=1,
            total=100.0,
            date=datetime.now()
        )
        
        # Adiciona um item de teste
        item = SaleItem(
            product_id=1,
            quantity=2,
            price=50.0,
            subtotal=100.0
        )
        sale.items.append(item)
        
        # Salva a venda no banco de dados
        db.session.add(sale)
        db.session.commit()
        
        logging.info(f"Venda criada com sucesso. ID: {sale.id}")
        
        # Tenta imprimir usando a impressão térmica
        try:
            logging.info("Tentando impressão térmica...")
            result = print_sale_receipt(sale, "POS-58")
            if result:
                logging.info("Impressão térmica bem-sucedida!")
                return True
            else:
                logging.error("Impressão térmica falhou!")
        except Exception as e:
            logging.error(f"Erro na impressão térmica: {str(e)}")
            
        # Se falhar, tenta imprimir como PDF
        try:
            logging.info("Tentando impressão PDF...")
            from utils.printer import print_receipt
            result = print_receipt(sale, "POS-58")
            if result:
                logging.info("Impressão PDF bem-sucedida!")
                return True
            else:
                logging.error("Impressão PDF falhou!")
        except Exception as e:
            logging.error(f"Erro na impressão PDF: {str(e)}")
            
        return False
        
    except Exception as e:
        logging.error(f"Erro geral: {str(e)}")
        return False

def main():
    """Função principal"""
    print("=== DEBUG DE IMPRESSÃO ===")
    print("Testando impressão detalhada...")
    
    # Testa a impressão
    if test_impressao_detalhada():
        print("Impressão testada com sucesso!")
    else:
        print("Falha ao testar impressão.")

if __name__ == "__main__":
    main()
