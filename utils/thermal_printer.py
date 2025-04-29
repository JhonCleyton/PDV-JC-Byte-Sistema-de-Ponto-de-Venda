"""
Módulo para impressão direta em impressoras térmicas usando comandos ESC/POS
"""
import os
import win32print
import win32api
import logging
from datetime import datetime
import tempfile
from flask import current_app
from models import CompanyInfo, Sale
import traceback

# Configuração de logging
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'printer.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def get_thermal_printer():
    """Retorna o nome da primeira impressora térmica encontrada ou None"""
    try:
        # Lista todas as impressoras disponíveis
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        logging.info(f"Impressoras disponíveis: {printers}")
        
        # Procura por impressoras térmicas comuns
        thermal_keywords = ['POS', 'TM-', 'Thermal', 'Receipt', 'Ticket', '58mm', '80mm']
        
        for printer in printers:
            for keyword in thermal_keywords:
                if keyword.lower() in printer.lower():
                    logging.info(f"Impressora térmica encontrada: {printer}")
                    return printer
        
        # Se não encontrou nenhuma impressora térmica, usa a padrão
        default_printer = win32print.GetDefaultPrinter()
        logging.info(f"Nenhuma impressora térmica encontrada. Usando a padrão: {default_printer}")
        return default_printer
    except Exception as e:
        logging.error(f"Erro ao buscar impressora térmica: {str(e)}")
        return None

def print_text_to_thermal(text, printer_name=None):
    """Imprime texto diretamente para a impressora térmica usando comandos ESC/POS"""
    try:
        if not printer_name:
            printer_name = get_thermal_printer()
            
        if not printer_name:
            logging.error("Nenhuma impressora disponível")
            return False
            
        # Formata o texto com comandos ESC/POS
        formatted_text = "\x1B@\x1B!\x11\n"  # Inicializa e configura tamanho médio
        formatted_text += text
        formatted_text += "\n\n\n\n\n"  # Espaço para corte
        
        # Abre a impressora
        printer = win32print.OpenPrinter(printer_name)
        try:
            # Inicia um documento
            hJob = win32print.StartDocPrinter(printer, 1, ("Cupom PDV", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer)
                
                # Converte para bytes e envia para a impressora
                win32print.WritePrinter(printer, formatted_text.encode('cp850'))
                
                win32print.EndPagePrinter(printer)
                logging.info(f"Texto impresso com sucesso na impressora: {printer_name}")
                return True
            finally:
                win32print.EndDocPrinter(printer)
        finally:
            win32print.ClosePrinter(printer)
            
    except Exception as e:
        logging.error(f"Erro ao imprimir texto: {str(e)}")
        return False

def format_receipt(sale_data):
    """Formata os dados da venda como texto para impressão térmica"""
    lines = []
    
    # Cabeçalho
    lines.append("=" * 40)
    lines.append(f"{sale_data.get('company_name', 'EMPRESA')}".center(40))
    lines.append(f"{sale_data.get('company_address', 'ENDEREÇO')}".center(40))
    lines.append(f"CNPJ: {sale_data.get('company_cnpj', '00.000.000/0000-00')}".center(40))
    lines.append("=" * 40)
    
    # Informações da venda
    lines.append(f"CUPOM NÃO FISCAL")
    lines.append(f"Data: {sale_data.get('date', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}")
    lines.append(f"Venda #: {sale_data.get('id', '0000')}")
    lines.append(f"Cliente: {sale_data.get('customer_name', 'CONSUMIDOR')}")
    lines.append("-" * 40)
    
    # Itens
    lines.append("ITEM DESCRIÇÃO                  QTD   VALOR   TOTAL")
    lines.append("-" * 40)
    
    items = sale_data.get('items', [])
    for i, item in enumerate(items):
        item_num = f"{i+1:02d}"
        description = item.get('description', '')[:20]
        quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        total = quantity * price
        
        # Formata a linha do item
        item_line = f"{item_num} {description.ljust(20)} {quantity:5.2f} {price:7.2f} {total:7.2f}"
        lines.append(item_line)
    
    lines.append("-" * 40)
    
    # Totais
    subtotal = sale_data.get('subtotal', 0)
    discount = sale_data.get('discount', 0)
    total = sale_data.get('total', 0)
    
    lines.append(f"SUBTOTAL: {subtotal:32.2f}")
    if discount > 0:
        lines.append(f"DESCONTO: {discount:32.2f}")
    lines.append(f"TOTAL:    {total:32.2f}")
    
    # Forma de pagamento
    payment_method = sale_data.get('payment_method', 'DINHEIRO')
    lines.append("-" * 40)
    lines.append(f"FORMA DE PAGAMENTO: {payment_method}")
    
    # Rodapé
    lines.append("=" * 40)
    lines.append("OBRIGADO PELA PREFERÊNCIA!".center(40))
    lines.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S").center(40))
    
    return "\n".join(lines)

def print_sale_receipt(sale_data, printer_name=None):
    """Imprime o cupom de venda na impressora térmica usando comandos ESC/POS"""
    try:
        # Garante que estamos no contexto do Flask
        with current_app.app_context():
            # Se for um objeto Sale, converte para dicionário
            if isinstance(sale_data, Sale):
                # Obtém a empresa
                company_info = CompanyInfo.query.first()
                
                # Se não encontrar a empresa, usa valores padrão
                company_name = company_info.name if company_info else 'EMPRESA NÃO CONFIGURADA'
                company_address = f"{company_info.address}, {company_info.city}-{company_info.state}" if company_info else 'ENDEREÇO NÃO CONFIGURADO'
                company_cnpj = company_info.cnpj if company_info else '00.000.000/0000-00'
                
                # Calcula o subtotal dos itens
                subtotal = sum(float(item.quantity * item.price) for item in sale_data.items)
                
                # Converte o objeto Sale para dicionário
                sale_dict = {
                    'company_name': company_name,
                    'company_address': company_address,
                    'company_cnpj': company_cnpj,
                    'id': sale_data.id,
                    'date': sale_data.date.strftime('%d/%m/%Y %H:%M:%S'),
                    'customer_name': sale_data.customer.name if sale_data.customer else 'CONSUMIDOR',
                    'items': [],
                    'subtotal': subtotal,
                    'discount': 0.0,  # Não temos desconto no modelo atual
                    'total': float(sale_data.total),
                    'payment_method': sale_data.payment_method
                }
                
                # Adiciona os itens
                for item in sale_data.items:
                    sale_dict['items'].append({
                        'description': item.product.name if item.product else 'PRODUTO NÃO ENCONTRADO',
                        'quantity': float(item.quantity),
                        'price': float(item.price)
                    })
                
                sale_data = sale_dict
            
            # Formata o recibo
            receipt_text = format_receipt(sale_data)
            
            # Imprime o texto
            result = print_text_to_thermal(receipt_text, printer_name)
            
            return result
    except Exception as e:
        logging.error(f"Erro ao imprimir cupom de venda: {str(e)}")
        logging.error(traceback.format_exc())
        return False
