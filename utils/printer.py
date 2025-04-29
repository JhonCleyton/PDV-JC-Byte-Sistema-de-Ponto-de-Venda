import os
import sys
import logging
from flask import current_app
from models import CompanyInfo, Sale
from datetime import datetime
import traceback
import platform
from fpdf import FPDF

# Import system-specific modules
if platform.system() == 'Windows':
    import win32print
    import win32con
else:
    import cups

# Configuração de logging
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'printer.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def ensure_receipts_directory():
    """Garante que o diretório de cupons exista"""
    receipts_dir = current_app.config.get('RECEIPTS_DIR', 'cupons')
    if not os.path.exists(receipts_dir):
        os.makedirs(receipts_dir)
        logging.info(f"Diretório de cupons criado: {receipts_dir}")
    return receipts_dir

class ReceiptPDF(FPDF):
    """Classe para gerar PDFs de recibos"""
    def __init__(self):
        # 80mm = 8cm = aproximadamente 3.14961 polegadas
        # Reduzindo a largura para 70mm para garantir que caiba
        super().__init__(format=(70, 200))  # 70mm de largura
        self.set_margins(0.5, 0.5, 0.5)  # Margens mínimas: 0.5mm
        self.set_auto_page_break(auto=True, margin=0.5)
        self.add_page()
        self.set_font('Courier', '', 7)  # Fonte ainda menor: 7pt
        self.cell_height = 2.5  # Altura menor: 2.5mm
        self.line_width = 32  # Reduzido para caber na largura menor
    
    def add_line(self, text, font_name='Courier', style='', size=7):
        """Adiciona uma linha de texto com a fonte especificada"""
        self.set_font(font_name, style, size)
        self.cell(0, self.cell_height, text, 0, 1)
    
    def add_centered_line(self, text, font_name='Courier', style='', size=7):
        """Adiciona uma linha de texto centralizada"""
        self.set_font(font_name, style, size)
        self.cell(0, self.cell_height, text, 0, 1, 'C')
    
    def add_separator(self, char='-'):
        """Adiciona uma linha separadora"""
        self.set_font('Courier', '', 7)
        self.cell(0, self.cell_height, char * self.line_width, 0, 1)
    
    def add_double_line(self, left_text, right_text, font_name='Courier', style='', size=7):
        """Adiciona uma linha com texto à esquerda e à direita"""
        self.set_font(font_name, style, size)
        self.cell(0, self.cell_height, f"{left_text.ljust(20)} {right_text.rjust(10)}", 0, 1)

def get_printer_instance(printer_name=None):
    """
    Retorna uma instância da impressora.
    """
    try:
        if platform.system() == 'Windows':
            if not printer_name:
                printer_name = win32print.GetDefaultPrinter()
            return win32print.OpenPrinter(printer_name)
        else:
            # For Linux, use CUPS
            conn = cups.Connection()
            if not printer_name:
                printer_name = conn.getDefault()
            return conn, printer_name
    except Exception as e:
        logging.error(f"Erro ao obter impressora: {str(e)}")
        return None

def print_test(printer_name=None):
    """Gera um cupom de teste de impressão usando as configurações do CompanyInfo"""
    try:
        if not current_app.config.get('PRINTER_ENABLED', True):
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Garante que o diretório de cupons exista
        receipts_dir = ensure_receipts_directory()
            
        # Obtém as configurações do cupom
        company = CompanyInfo.query.first()
        if not company:
            logging.error("Configurações da empresa não encontradas")
            return False
            
        # Cria o texto do cupom usando as configurações do CompanyInfo
        text = company.print_header or ""  # Usa o cabeçalho configurado
        
        # Adiciona o conteúdo do teste
        text += "\n"  # Linha em branco
        text += "Data: {date}\n".format(date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        text += "\n"  # Linha em branco
        
        # Adiciona o rodapé configurado
        text += company.print_footer or ""
        
        # Salva o texto em um arquivo
        filename = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        filepath = os.path.join(receipts_dir, filename)
        
        with open(filepath, 'w', encoding='cp850') as f:
            f.write(text)
        
        logging.info(f"Texto do cupom de teste salvo: {filepath}")
        
        # Imprime o cupom usando a impressão térmica
        result = print_thermal_receipt(text, printer_name)
        
        if result:
            logging.info("Cupom de teste impresso com sucesso!")
        else:
            logging.error("Falha ao imprimir cupom de teste!")
            
        return result
        
    except Exception as e:
        logging.error(f"Erro ao imprimir cupom de teste: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_receipt(sale_data, printer_name=None):
    """
    Gera e imprime um cupom de venda seguindo o formato especificado
    """
    try:
        if not current_app.config.get('PRINTER_ENABLED', True):
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Garante que estamos no contexto do Flask
        with current_app.app_context():
            # Obtém as configurações do cupom
            company = CompanyInfo.query.first()
            if not company:
                logging.error("Configurações da empresa não encontradas")
                return False
                
            # Inicia o texto com o cabeçalho configurado (em negrito)
            text = "**"
            text += company.print_header or ""
            text += "**\n"
            text += "==\n"  # Linha separadora
            
            # Adiciona o nome da empresa
            text += f"{company.name}\n" if company.name else "\n"
            text += "==\n"  # Linha separadora
            
            # Adiciona os itens da venda
            text += "**PRODUTOS**\n"
            text += "==\n"
            
            # Formato: ID | DESCRIÇÃO | QTD | VALOR UNIT | VALOR TOTAL
            for item in sale_data.items:
                text += f"{item.product.code} {item.product.name}"
                text += f" x{item.quantity}"
                text += f" R$ {float(item.price):.2f}"
                text += f" R$ {float(item.subtotal):.2f}\n"
            
            text += "==\n"  # Linha separadora
            
            # Subtotal (se houver mais de um item)
            if len(sale_data.items) > 1:
                text += f"SUBTOTAL: R$ {float(sale_data.total):.2f}\n"
                text += "==\n"  # Linha separadora
            
            # Quantidade de itens
            total_items = sum(item.quantity for item in sale_data.items)
            text += f"ITENS: {total_items}\n"
            text += "==\n"  # Linha separadora
            
            # Valor total
            text += f"TOTAL: R$ {float(sale_data.total):.2f}\n"
            text += "==\n"  # Linha separadora
            
            # Forma de pagamento
            text += f"PAGAMENTO: {sale_data.payment_method}\n"
            
            # Se for pagamento em dinheiro, mostra o troco
            if sale_data.payment_method == "dinheiro" and hasattr(sale_data, 'received_amount'):
                received = float(sale_data.received_amount or 0)
                if received > float(sale_data.total):
                    text += f"TROCO: R$ {received - float(sale_data.total):.2f}\n"
            
            text += "==\n"  # Linha separadora
            
            # Atendente
            if sale_data.user:
                text += f"ATENDENTE: {sale_data.user.name}\n"
            
            text += "==\n"  # Linha separadora
            
            # Adiciona o rodapé configurado (em negrito)
            text += "**"
            text += company.print_footer or ""
            text += "**\n"
            text += "==\n"  # Linha separadora
            
            # Versão do sistema em fonte menor
            text += "$$Sistema: PDV-JC Byte / versão: 1.2.100$$\n"
            
            # Salva o texto do cupom
            filename = f"sale_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
            filepath = os.path.join(ensure_receipts_directory(), filename)
            
            with open(filepath, 'w', encoding='cp850') as f:
                f.write(text)
            
            logging.info(f"Texto do cupom de venda salvo: {filepath}")
            
            # Imprime o cupom usando a impressão térmica
            result = print_thermal_receipt(text, printer_name)
            
            if result:
                logging.info(f"Cupom impresso com sucesso na impressora térmica para venda")
                return True
            else:
                logging.error(f"Falha ao imprimir na impressora térmica")
                return False
                
    except Exception as e:
        logging.error(f"Erro ao imprimir cupom de venda: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_payment_receipt(payment, customer, receivable, printer_name=None):
    """Imprime o cupom de pagamento de dívida"""
    try:
        if not current_app.config.get('PRINTER_ENABLED', True):
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Cria o PDF
        pdf = ReceiptPDF()
        
        # Adiciona o cabeçalho
        pdf.add_centered_line("RECIBO DE PAGAMENTO", style='B', size=8)
        pdf.add_separator()
        
        # Informações do pagamento
        pdf.add_line(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        pdf.add_line(f"Cliente: {customer.name}")
        if customer.registration:
            pdf.add_line(f"Matrícula: {customer.registration}")
        pdf.add_separator()
        
        # Detalhes do pagamento
        pdf.add_line(f"Forma de Pagamento: {payment.payment_method}")
        pdf.add_line(f"Valor: R$ {float(payment.amount):.2f}")
        pdf.add_line(f"Venda: #{receivable.sale_id if receivable.sale_id else 'N/A'}")
        pdf.add_separator()
        
        # Totais
        pdf.add_double_line("Total Pago:", f"R$ {float(payment.amount):.2f}")
        pdf.add_double_line("Saldo Restante:", f"R$ {float(receivable.remaining_amount):.2f}")
        pdf.add_separator()
        
        # Rodapé
        pdf.add_centered_line("OBRIGADO PELA PREFERÊNCIA!")
        pdf.add_centered_line(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        # Salva o PDF
        filename = f"payment_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(ensure_receipts_directory(), filename)
        pdf.output(filepath)
        
        logging.info(f"Recibo de pagamento gerado: {filepath}")
        
        # Imprime o PDF
        result = print_pdf(filepath, printer_name)
        
        if result:
            logging.info("Recibo de pagamento impresso com sucesso!")
        else:
            logging.error("Falha ao imprimir recibo de pagamento!")
            
        return result
        
    except Exception as e:
        logging.error(f"Erro ao imprimir recibo de pagamento: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_cash_report(relatorio):
    """Imprime relatório de caixa com todas as informações de vendas, retiradas e recebimentos."""
    try:
        if not current_app.config.get('PRINTER_ENABLED', True):
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Cria o PDF
        pdf = ReceiptPDF()
        
        # Adiciona o cabeçalho
        pdf.add_centered_line("RELATÓRIO DE CAIXA", style='B', size=8)
        pdf.add_separator()
        
        # Informações do relatório
        pdf.add_line(f"Data: {relatorio['data']}")
        pdf.add_line(f"Usuário: {relatorio['usuario']}")
        pdf.add_separator()
        
        # Vendas
        pdf.add_centered_line("VENDAS", style='B')
        for venda in relatorio['vendas']:
            pdf.add_line(f"#{venda['id']} - {venda['descricao']}")
            pdf.add_line(f"Valor: R$ {venda['valor']:.2f}")
            pdf.add_separator()
        
        # Retiradas
        if relatorio['retiradas']:
            pdf.add_centered_line("RETIRADAS", style='B')
            for retirada in relatorio['retiradas']:
                pdf.add_line(f"#{retirada['id']} - {retirada['descricao']}")
                pdf.add_line(f"Valor: R$ {retirada['valor']:.2f}")
                pdf.add_separator()
        
        # Recebimentos
        if relatorio['recebimentos']:
            pdf.add_centered_line("RECEBIMENTOS", style='B')
            for recebimento in relatorio['recebimentos']:
                pdf.add_line(f"#{recebimento['id']} - {recebimento['descricao']}")
                pdf.add_line(f"Valor: R$ {recebimento['valor']:.2f}")
                pdf.add_separator()
        
        # Totais
        pdf.add_centered_line("TOTAIS", style='B')
        pdf.add_double_line("Total Vendas:", f"R$ {relatorio['total_vendas']:.2f}")
        pdf.add_double_line("Total Retiradas:", f"R$ {relatorio['total_retiradas']:.2f}")
        pdf.add_double_line("Total Recebimentos:", f"R$ {relatorio['total_recebimentos']:.2f}")
        pdf.add_double_line("Saldo Final:", f"R$ {relatorio['saldo_final']:.2f}", style='B')
        
        # Salva o PDF
        filename = f"relatorio_caixa_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(ensure_receipts_directory(), filename)
        pdf.output(filepath)
        
        logging.info(f"Relatório de caixa gerado: {filepath}")
        
        # Imprime o PDF
        result = print_pdf(filepath)
        
        if result:
            logging.info("Relatório de caixa impresso com sucesso!")
        else:
            logging.error("Falha ao imprimir relatório de caixa!")
            
        return result
        
    except Exception as e:
        logging.error(f"Erro ao imprimir relatório de caixa: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_pdf(pdf_file, printer_name=None):
    """
    Tenta imprimir o PDF usando o método adequado para o sistema operacional
    """
    try:
        if platform.system() == 'Windows':
            # Código existente para Windows
            try:
                # Tenta usar win32print
                printer = win32print.OpenPrinter(printer_name)
                job = win32print.StartDocPrinter(printer, 1, ("PDF Document", None, "RAW"))
                win32print.StartPagePrinter(printer)
                win32print.WritePrinter(printer, open(pdf_file, "rb").read())
                win32print.EndPagePrinter(printer)
                win32print.EndDocPrinter(printer)
                win32print.ClosePrinter(printer)
                return True
            except:
                # Se falhar, tenta usar ShellExecute
                import win32api
                win32api.ShellExecute(0, "print", pdf_file, None, ".", 0)
                return True
        else:
            # Para Linux, usa CUPS
            conn = cups.Connection()
            if not printer_name:
                printer_name = conn.getDefault()
            job_id = conn.printFile(printer_name, pdf_file, "PDF Document", {})
            logging.info(f"Impressão enviada para {printer_name} como job {job_id}")
            return True
    except Exception as e:
        logging.error(f"Erro ao imprimir PDF: {str(e)}")
        return False

def format_line(text, width=24, align='left', bold=False, underline=False, font_size='normal', is_product=False):
    """Formata uma linha com alinhamento, negrito, sublinhado e tamanho de fonte"""
    # Remove caracteres especiais que podem causar problemas
    text = ''.join(c for c in text if ord(c) < 128)
    
    # Define o tamanho da fonte
    if is_product:  # Para produtos, usa tamanho menor
        text = f"\x1B\x21\x00{text}\x1B\x21\x00"  # Fonte pequena
    elif font_size == 'small':
        text = f"\x1B\x21\x00{text}\x1B\x21\x00"  # Fonte pequena
    elif font_size == 'large':
        text = f"\x1B\x21\x10{text}\x1B\x21\x10"  # Fonte grande
    else:
        text = f"\x1B\x21\x00{text}\x1B\x21\x00"  # Fonte normal
    
    # Aplica formatação
    if bold:
        text = f"\x1B\x45\x01{text}\x1B\x45\x00"  # Ativa e desativa negrito
    if underline:
        text = f"\x1B\x2D\x01{text}\x1B\x2D\x00"  # Ativa e desativa sublinhado
    
    # Alinha o texto
    if align == 'center':
        text = text.center(width)
    elif align == 'right':
        text = text.rjust(width)
    else:  # left
        text = text.ljust(width)
    
    return text

def print_thermal_receipt(text, printer_name=None):
    """
    Imprime texto diretamente na impressora térmica usando comandos ESC/POS
    """
    try:
        if not current_app.config.get('PRINTER_ENABLED', True):
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Obtém a impressora padrão se não for especificada
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()
            
        # Abre a impressora
        hPrinter = win32print.OpenPrinter(printer_name)
        
        try:
            # Inicia um novo documento
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cupom PDV", None, "RAW"))
            
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # Formata o texto para impressão térmica
                formatted_text = """
                \x1B\x40\n"""  # Inicializa impressora
                
                # Adiciona cada linha do texto formatada
                for line in text.split('\n'):
                    if line.strip():  # Ignora linhas em branco
                        # Verifica se a linha contém marcadores de formatação
                        if line.startswith('**') and line.endswith('**'):
                            # Texto em negrito e tamanho normal
                            formatted_text += format_line(line[2:-2], width=24, bold=True, font_size='normal') + "\n"
                        elif line.startswith('==') and line.endswith('=='):
                            # Linha separadora
                            formatted_text += format_line("=" * 24, width=24, font_size='small') + "\n"
                        elif line.startswith('##') and line.endswith('##'):
                            # Texto centralizado e em negrito
                            formatted_text += format_line(line[2:-2], width=24, align='center', bold=True, font_size='normal') + "\n"
                        elif line.startswith('$$') and line.endswith('$$'):
                            # Texto sublinhado
                            formatted_text += format_line(line[2:-2], width=24, underline=True, font_size='small') + "\n"
                        else:
                            # Verifica se é uma linha de produto (contém código e preço)
                            if any(char.isdigit() for char in line) and "R$" in line:
                                # Formato menor para produtos
                                formatted_text += format_line(line, width=24, is_product=True) + "\n"
                            else:
                                # Texto normal em tamanho pequeno
                                formatted_text += format_line(line, width=24, font_size='small') + "\n"
                        
                        # Adiciona espaçamento mínimo entre linhas
                        formatted_text += ""  # Nenhuma linha em branco entre linhas
                
                # Adiciona 3 linhas em branco antes de cortar o papel
                formatted_text += "\n\n\n"
                
                formatted_text += "\x1D\x56\x41\x00"  # Corta o papel
                
                # Converte para bytes usando CP850
                data = formatted_text.encode('cp850')
                
                # Envia para a impressora
                win32print.WritePrinter(hPrinter, data)
                win32print.EndPagePrinter(hPrinter)
                
            finally:
                win32print.EndDocPrinter(hPrinter)
                
            logging.info(f"Cupom impresso com sucesso na impressora: {printer_name}")
            return True
            
        finally:
            win32print.ClosePrinter(hPrinter)
            
    except Exception as e:
        logging.error(f"Erro ao imprimir cupom térmico: {str(e)}")
        logging.error(traceback.format_exc())
        return False
