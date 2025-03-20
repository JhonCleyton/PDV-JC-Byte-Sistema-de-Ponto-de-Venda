import win32print
import win32con
from models import CompanyInfo, Sale
from datetime import datetime
import traceback
import os
import sys
import logging
from fpdf import FPDF

# Configuração da impressora
PRINTER_ENABLED = True  # Variável para controlar se a impressão está habilitada

# Pasta para armazenar os recibos gerados
receipts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'receipts')
os.makedirs(receipts_dir, exist_ok=True)

# Configura logging
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'printer.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Tenta criar o diretório de cupons
try:
    logging.info(f"Diretório de cupons criado/verificado: {receipts_dir}")
except Exception as e:
    logging.error(f"Erro ao criar diretório de cupons: {str(e)}")

class ReceiptPDF(FPDF):
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
        # Quebra o texto em múltiplas linhas se necessário
        words = text.split()
        line = ''
        for word in words:
            test_line = f"{line} {word}".strip()
            if len(test_line) <= self.line_width:
                line = test_line
            else:
                self.cell(0, self.cell_height, line, ln=True)
                line = word
        if line:
            self.cell(0, self.cell_height, line, ln=True)
        
    def add_centered_line(self, text, font_name='Courier', style='', size=7):
        """Adiciona uma linha de texto centralizada"""
        self.set_font(font_name, style, size)
        # Quebra o texto em múltiplas linhas se necessário
        while len(text) > self.line_width:
            part = text[:self.line_width]
            text = text[self.line_width:]
            self.cell(0, self.cell_height, part.center(self.line_width), ln=True)
        if text:
            self.cell(0, self.cell_height, text.center(self.line_width), ln=True)
        
    def add_separator(self, char='-'):
        """Adiciona uma linha separadora"""
        self.cell(0, self.cell_height, char * self.line_width, ln=True)
        
    def add_double_line(self, left_text, right_text, font_name='Courier', style='', size=7):
        """Adiciona uma linha com texto à esquerda e à direita"""
        self.set_font(font_name, style, size)
        # Garante que o texto caiba
        max_left_width = self.line_width - len(right_text) - 1
        if len(left_text) > max_left_width:
            # Se o texto da esquerda for muito longo, quebra em duas linhas
            self.add_line(left_text)
            self.cell(0, self.cell_height, right_text.rjust(self.line_width), ln=True)
        else:
            # Se couber tudo em uma linha
            left_text = left_text[:max_left_width]
            text = f"{left_text}{' ' * (max_left_width - len(left_text))}{right_text}"
            self.cell(0, self.cell_height, text, ln=True)

def get_printer_instance(printer_name=None):
    """
    Retorna uma instância da impressora.
    Como estamos usando PDF para imprimir, retorna None por padrão.
    Esta função serve como uma abstração para quando for implementada 
    a impressão térmica real com biblioteca como python-escpos.
    """
    try:
        logging.info("Obtendo instância da impressora")
        # Por enquanto, retornamos None pois estamos usando PDF
        return None
    except Exception as e:
        logging.error(f"Erro ao obter instância da impressora: {str(e)}")
        return None

def print_test(printer_name=None):
    """Gera um cupom de teste de impressão"""
    try:
        logging.info("=== Iniciando impressão de teste ===")
        
        # Obtem informações da empresa
        company = CompanyInfo.query.first()
        
        # Gera o cupom
        pdf = ReceiptPDF()
        
        # Cabeçalho
        pdf.add_centered_line("*** CUPOM DE TESTE ***", style='B', size=8)
        pdf.add_centered_line(f"{company.name if company else 'Empresa'}", style='B', size=7)
        pdf.add_separator()
        
        # Data e hora
        pdf.add_double_line("Data/Hora", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        pdf.add_separator()
        
        # Texto de teste
        pdf.add_centered_line("Este é um teste de impressão!", style='B')
        pdf.add_line("")
        pdf.add_line("O sistema está verificando se a impressora")
        pdf.add_line("está configurada corretamente.")
        pdf.add_separator()
        
        # Caracteres de teste
        pdf.add_centered_line("CARACTERES DE TESTE:", style='B', size=6)
        pdf.add_line("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        pdf.add_line("abcdefghijklmnopqrstuvwxyz")
        pdf.add_line("0123456789")
        pdf.add_line("!@#$%^&*()")
        pdf.add_separator()
        
        # Código de barras de teste se suportado
        pdf.add_centered_line("CÓDIGO DE BARRAS:", style='B', size=6)
        pdf.add_barcode("12345678901")
        pdf.add_separator()
        
        # Footer
        pdf.add_centered_line("FIM DO TESTE", style='B')
        pdf.add_separator()
        
        # Salva o PDF
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_file = os.path.join(receipts_dir, f'teste_{timestamp}.pdf')
        pdf.output(pdf_file)
        logging.info(f"PDF de teste gerado com sucesso: {pdf_file}")
        
        # Envia para impressão se tiver uma impressora configurada
        if PRINTER_ENABLED:
            logging.info(f"Enviando para impressora: {printer_name}")
            print_result = print_pdf(pdf_file, printer_name)
            if not print_result:
                logging.error("Falha ao imprimir o cupom de teste")
                return False
        else:
            logging.info("Impressão desabilitada. PDF salvo apenas.")
            
        return True
            
    except Exception as e:
        logging.error(f"Erro ao gerar PDF de teste: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_receipt(sale, printer_name=None):
    """Imprime o cupom de venda"""
    try:
        logging.info("=== Iniciando impressão de cupom de venda ===")
        logging.info(f"Venda ID: {getattr(sale, 'id', 'N/A')}")
        
        # Verifica se a venda é válida
        if not sale:
            logging.error("Venda inválida")
            return False
            
        # Obtém informações da empresa
        company = CompanyInfo.query.first()
        if not company:
            logging.error("Informações da empresa não encontradas")
            return False
            
        # Gera o nome do arquivo PDF
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_file = os.path.join(receipts_dir, f'cupom_{sale.id}_{timestamp}.pdf')
        
        # Cria o PDF
        pdf = ReceiptPDF()
        
        # Cabeçalho
        pdf.add_centered_line(company.name, style='B', size=8)
        if company.address:
            pdf.add_centered_line(company.address, size=6)
        if company.city and company.state:
            pdf.add_centered_line(f"{company.city}/{company.state}", size=6)
        if company.cnpj:
            pdf.add_centered_line(f"CNPJ: {company.cnpj}", size=6)
        
        # Adiciona cabeçalho personalizado, se existir
        if company.print_header:
            pdf.add_separator()
            for line in company.print_header.splitlines():
                pdf.add_centered_line(line, size=6)
            
        pdf.add_separator()
        pdf.add_centered_line("COMPROVANTE DE VENDA", style='B', size=8)
        pdf.add_separator()
        
        # Dados da venda
        pdf.add_double_line("Venda #", str(sale.id))
        sale_date = sale.date.strftime("%d/%m/%Y %H:%M") if hasattr(sale.date, 'strftime') else str(sale.date)
        pdf.add_double_line("Data", sale_date)
        
        # Informações do cliente
        if hasattr(sale, 'customer') and sale.customer:
            pdf.add_double_line("Cliente", sale.customer.name)
            if sale.customer.registration:
                pdf.add_double_line("Matrícula", sale.customer.registration)
        
        # Informações do operador/vendedor
        if hasattr(sale, 'user') and sale.user:
            pdf.add_double_line("Operador", sale.user.name or sale.user.username)
        elif hasattr(sale, 'seller') and sale.seller:
            pdf.add_double_line("Vendedor", sale.seller.name)
            
        pdf.add_separator()
        
        # Itens
        pdf.add_centered_line("ITENS", style='B')
        pdf.add_separator('-')
        
        try:
            # Tenta acessar os itens de venda
            items = sale.items
            for item in items:
                # Nome do produto e quantidade
                desc = f"{item.quantity:.0f}x {item.product.name}" if item.product else f"{item.quantity:.0f}x Item"
                pdf.add_line(desc)
                
                # Preço unitário
                unit_price = f"R$ {item.price:.2f}" if hasattr(item, 'price') else "R$ 0.00"
                total_price = f"R$ {item.subtotal:.2f}" if hasattr(item, 'subtotal') else "R$ 0.00"
                
                pdf.add_double_line(f"  {unit_price} cada", total_price)
                
        except Exception as e:
            logging.error(f"Erro ao processar itens da venda: {str(e)}")
            pdf.add_line("Erro ao recuperar itens")
            
        pdf.add_separator()
        
        # Totais
        pdf.add_double_line("Subtotal", f"R$ {sale.subtotal:.2f}" if hasattr(sale, 'subtotal') else "R$ 0.00")
        
        # Adiciona desconto se houver
        if hasattr(sale, 'discount') and sale.discount and sale.discount > 0:
            pdf.add_double_line("Desconto", f"R$ {sale.discount:.2f}")
            
        # Total
        pdf.add_double_line("Total", f"R$ {sale.total:.2f}" if hasattr(sale, 'total') else "R$ 0.00", style='B')
        pdf.add_separator()
        
        # Pagamento
        pdf.add_centered_line("PAGAMENTO", style='B')
        pdf.add_separator('-')
        
        try:
            # Informações de pagamento
            if hasattr(sale, 'payment_method') and sale.payment_method:
                method = sale.payment_method.upper()
                pdf.add_double_line("Forma", method)
                
                # Se for pagamento em dinheiro e houver informações de troco
                if method == 'DINHEIRO' and hasattr(sale, 'received_amount') and sale.received_amount:
                    pdf.add_double_line("Valor Recebido", f"R$ {float(sale.received_amount):.2f}")
                    if hasattr(sale, 'change_amount') and sale.change_amount:
                        pdf.add_double_line("Troco", f"R$ {float(sale.change_amount):.2f}")
                
                # Se for crediário, mostra informações adicionais
                if method == 'CREDIARIO' and hasattr(sale, 'customer') and sale.customer:
                    pdf.add_double_line("Limite do Cliente", f"R$ {float(sale.customer.credit_limit):.2f}")
                    pdf.add_double_line("Dívida Atualizada", f"R$ {float(sale.customer.current_debt):.2f}")
            
            # Tenta acessar os pagamentos se existirem como uma relação
            if hasattr(sale, 'payments') and sale.payments:
                for payment in sale.payments:
                    method = payment.method.upper() if hasattr(payment, 'method') and payment.method else "N/A"
                    amount = f"R$ {payment.amount:.2f}" if hasattr(payment, 'amount') else "R$ 0.00"
                    pdf.add_double_line(method, amount)
                
        except Exception as e:
            logging.error(f"Erro ao processar pagamentos da venda: {str(e)}")
            logging.error(traceback.format_exc())
            pdf.add_line("Erro ao recuperar informações de pagamento")
        
        # Rodapé
        pdf.add_separator()
        
        # Adiciona rodapé personalizado, se existir
        if company.print_footer:
            for line in company.print_footer.splitlines():
                pdf.add_centered_line(line, size=6)
            pdf.add_separator()
            
        pdf.add_centered_line("Obrigado pela preferência!", size=7)
        
        # Informações do vendedor, se ainda não exibiu
        if not (hasattr(sale, 'user') and sale.user) and hasattr(sale, 'seller') and sale.seller:
            pdf.add_centered_line(f"Vendedor: {sale.seller.name}", size=6)
        
        pdf.add_centered_line(f"{company.name}", size=6)
        pdf.add_centered_line("Sistema por JC Byte Soluções em Tecnologia", size=5)
        
        # Salva o PDF
        pdf.output(pdf_file)
        logging.info(f"PDF do cupom gerado com sucesso: {pdf_file}")
        
        # Imprime o PDF
        if PRINTER_ENABLED:
            logging.info(f"Enviando para impressora: {printer_name or 'padrão'}")
            print_result = print_pdf(pdf_file, printer_name)
            if not print_result:
                logging.error("Falha ao imprimir o cupom")
                return False
        else:
            logging.info("Impressão desabilitada. PDF salvo apenas.")
            
        return True
            
    except Exception as e:
        logging.error(f"Erro ao gerar PDF do cupom: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_payment_receipt(payment, customer, receivable, printer_name=None):
    """Imprime o cupom de pagamento de dívida"""
    try:
        logging.info("=== Iniciando impressão do cupom de pagamento ===")
        logging.info(f"Detalhes: Pagamento #{payment.id}, Cliente: {customer.name}, Dívida: #{receivable.id}, Impressora: {printer_name or 'padrão'}")
        
        # Obtem informações da empresa
        company = CompanyInfo.query.first()
        if not company:
            logging.error("Informações da empresa não encontradas")
            return False
        
        # Gera o nome do arquivo PDF
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_file = os.path.join(receipts_dir, f'pagamento_{payment.id}_{timestamp}.pdf')
        
        # Cria o PDF
        pdf = ReceiptPDF()
        
        # Cabeçalho da empresa
        pdf.add_centered_line(company.name, style='B', size=7)
        
        if company.address:
            pdf.add_centered_line(company.address, size=6)
            
        if company.city and company.state:
            pdf.add_centered_line(f"{company.city}/{company.state}", size=6)
            
        if company.cnpj:
            pdf.add_centered_line(f"CNPJ: {company.cnpj}", size=6)
            
        pdf.add_separator()
        pdf.add_centered_line("RECIBO DE PAGAMENTO", style='B', size=8)
        pdf.add_centered_line(f"Recebimento #{payment.id}", size=7)
        pdf.add_separator()
        
        # Data e hora
        payment_date = payment.date.strftime("%d/%m/%Y %H:%M") if hasattr(payment.date, 'strftime') else str(payment.date)
        pdf.add_double_line("Data/Hora", payment_date)
        
        # Informações do cliente
        pdf.add_separator()
        pdf.add_centered_line("CLIENTE", style='B', size=7)
        pdf.add_separator('-')
        pdf.add_line(f"Nome: {customer.name}")
        if customer.registration:
            pdf.add_line(f"Matrícula: {customer.registration}")
        
        # Informações da dívida
        pdf.add_separator()
        pdf.add_centered_line("DETALHES DA DÍVIDA", style='B', size=7)
        pdf.add_separator('-')
        pdf.add_double_line("Dívida #", str(receivable.id))
        pdf.add_double_line("Data Original", receivable.date.strftime("%d/%m/%Y") if hasattr(receivable.date, 'strftime') else str(receivable.date))
        
        # Valores
        pdf.add_separator()
        pdf.add_centered_line("VALORES", style='B', size=7)
        pdf.add_separator('-')
        pdf.add_double_line("Valor Original", f"R$ {float(receivable.original_amount):.2f}")
        
        if float(receivable.interest) > 0:
            pdf.add_double_line("Juros", f"R$ {float(receivable.interest):.2f}")
            
        if float(receivable.fine) > 0:
            pdf.add_double_line("Multa", f"R$ {float(receivable.fine):.2f}")
            
        pdf.add_double_line("Valor Total", f"R$ {float(receivable.amount):.2f}", style='B')
        
        # Pagamento
        pdf.add_separator()
        pdf.add_centered_line("PAGAMENTO", style='B', size=7)
        pdf.add_separator('-')
        pdf.add_double_line("Valor Pago", f"R$ {float(payment.amount):.2f}", style='B')
        pdf.add_double_line("Forma", payment.method.upper() if payment.method else "N/A")
        
        # Saldo
        saldo = float(receivable.amount) - float(payment.amount)
        if saldo > 0:
            pdf.add_double_line("Saldo Restante", f"R$ {saldo:.2f}")
        else:
            pdf.add_centered_line("DÍVIDA QUITADA", style='B', size=7)
        
        # Assinatura
        pdf.add_separator()
        pdf.add_line("")  # Espaço antes da assinatura
        pdf.add_line("")  # Espaço para assinatura
        pdf.add_centered_line("Assinatura do Cliente")
        
        # Rodapé
        pdf.add_separator()
        
        # Adiciona copyright no rodapé
        pdf.add_centered_line(f"{company.name}", size=6)
        pdf.add_centered_line("JC Byte Soluções em Tecnologia", size=5)
        
        # Salva o PDF
        pdf.output(pdf_file)
        logging.info(f"PDF de pagamento gerado com sucesso: {pdf_file}")
        
        # Envia para impressão se tiver uma impressora configurada
        if PRINTER_ENABLED:
            logging.info(f"Enviando para impressora: {printer_name or 'padrão'}")
            
            # Tenta todos os métodos de impressão disponíveis
            print_result = print_pdf(pdf_file, printer_name)
            
            if print_result:
                logging.info("Cupom de pagamento impresso com sucesso!")
                return True
            else:
                logging.error("Falha ao imprimir o comprovante de pagamento")
                # Registra detalhes do ambiente para diagnóstico
                try:
                    import platform
                    os_info = platform.platform()
                    logging.info(f"Sistema Operacional: {os_info}")
                    
                    # Lista impressoras disponíveis
                    try:
                        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
                        logging.info(f"Impressoras disponíveis: {[p[2] for p in printers]}")
                    except:
                        logging.error("Não foi possível listar as impressoras")
                except:
                    logging.error("Erro ao obter informações do sistema")
                
                return False
        else:
            logging.info("Impressão desabilitada. PDF salvo apenas em: " + pdf_file)
            return True
            
    except Exception as e:
        logging.error(f"Erro ao gerar PDF de pagamento: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_cash_report(relatorio):
    """Imprime relatório de caixa com todas as informações de vendas, retiradas e recebimentos."""
    try:
        logging.info("=== Iniciando impressão de relatório de caixa ===")
        
        # Cria o PDF
        pdf = ReceiptPDF()
        
        # Cabeçalho
        pdf.add_centered_line("RELATÓRIO DE CAIXA", style='B', size=8)
        pdf.add_separator()
        
        # Informações básicas do caixa
        pdf.add_line(f"Operador: {relatorio['usuario']}")
        pdf.add_line(f"Abertura: {relatorio['data_abertura']}")
        pdf.add_line(f"Fechamento: {relatorio['data_fechamento']}")
        pdf.add_line(f"Status: {relatorio['status']}")
        pdf.add_separator()
        
        # Valores
        pdf.add_line(f"Valor Inicial: R$ {relatorio['valor_inicial']:.2f}")
        pdf.add_line(f"Valor Final: R$ {relatorio['valor_final']:.2f}")
        
        # Vendas
        pdf.add_separator()
        pdf.add_centered_line("VENDAS", style='B')
        pdf.add_line(f"Total de vendas: {relatorio['total_vendas']}")
        
        # Detalhe por forma de pagamento
        if relatorio['total_por_forma']:
            pdf.add_line("")
            pdf.add_centered_line("POR FORMA DE PAGAMENTO", size=6)
            for forma, valor in relatorio['total_por_forma'].items():
                pdf.add_double_line(forma.capitalize(), f"R$ {valor:.2f}")
        
        # Retiradas
        if relatorio['retiradas']:
            pdf.add_separator()
            pdf.add_centered_line("RETIRADAS", style='B')
            pdf.add_line(f"Total de retiradas: {len(relatorio['retiradas'])}")
            total_retiradas = sum(retirada['valor'] for retirada in relatorio['retiradas'])
            pdf.add_line(f"Valor total: R$ {total_retiradas:.2f}")
            
            for retirada in relatorio['retiradas']:
                pdf.add_line(f"• {retirada['data']}: R$ {retirada['valor']:.2f}")
                if retirada['motivo']:
                    pdf.add_line(f"  Motivo: {retirada['motivo']}")
                    
        # Suprimentos
        if relatorio['suprimentos']:
            pdf.add_separator()
            pdf.add_centered_line("SUPRIMENTOS", style='B')
            pdf.add_line(f"Total de suprimentos: {len(relatorio['suprimentos'])}")
            total_suprimentos = sum(suprimento['valor'] for suprimento in relatorio['suprimentos'])
            pdf.add_line(f"Valor total: R$ {total_suprimentos:.2f}")
            
            for suprimento in relatorio['suprimentos']:
                pdf.add_line(f"• {suprimento['data']}: R$ {suprimento['valor']:.2f}")
                if suprimento['motivo']:
                    pdf.add_line(f"  Motivo: {suprimento['motivo']}")
        
        # Recebimentos
        if relatorio['recebimentos']:
            pdf.add_separator()
            pdf.add_centered_line("RECEBIMENTOS", style='B')
            pdf.add_line(f"Total de recebimentos: {len(relatorio['recebimentos'])}")
            total_recebimentos = sum(recebimento['valor'] for recebimento in relatorio['recebimentos'])
            pdf.add_line(f"Valor total: R$ {total_recebimentos:.2f}")
            
            for recebimento in relatorio['recebimentos']:
                pdf.add_line(f"• {recebimento['data']}: R$ {recebimento['valor']:.2f}")
                pdf.add_line(f"  Cliente: {recebimento['cliente']}")
        
        # Rodapé
        pdf.add_separator()
        pdf.add_centered_line(f"Impresso em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Salva o PDF
        filename = f"relatorio_caixa_{relatorio['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'receipts', filename)
        pdf.output(filepath)
        logging.info(f"Relatório de caixa salvo em: {filepath}")
        
        # Imprime o PDF
        try:
            if PRINTER_ENABLED:
                logging.info("Imprimindo relatório de caixa...")
                printer_name = win32print.GetDefaultPrinter()
                print_result = print_pdf(filepath, printer_name)
                if not print_result:
                    logging.error("Falha ao imprimir o relatório de caixa")
                    return False
            else:
                logging.info("Impressão desabilitada. PDF salvo apenas.")
                    
            return True
        except Exception as e:
            logging.error(f"Erro ao imprimir relatório: {str(e)}")
            return False
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório de caixa: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_pdf_on_windows(pdf_file, printer_name=None):
    """
    Função para enviar um arquivo PDF diretamente para a impressora no Windows
    usando o shell do Windows para maior compatibilidade
    """
    try:
        if not PRINTER_ENABLED:
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
        
        logging.info(f"Tentando imprimir arquivo {pdf_file}")
        
        # Verifica se o arquivo existe
        if not os.path.exists(pdf_file):
            logging.error(f"Arquivo não encontrado: {pdf_file}")
            return False
            
        # Usa o ShellExecute do Windows para imprimir o arquivo
        # Isso utilizará o programa padrão para impressão de PDFs
        import win32api
        import win32con
        
        logging.info(f"Imprimindo usando ShellExecute: {pdf_file}")
        
        # O comando "print" abre o PDF no aplicativo associado e inicia a impressão
        win32api.ShellExecute(
            0,                   # Handle para a janela pai (0 = desktop)
            "print",             # Operação a ser realizada
            pdf_file,            # Arquivo a ser impresso
            None,                # Parâmetros adicionais (nenhum)
            ".",                 # Diretório de trabalho
            0                    # Modo de exibição (0 = oculto)
        )
        
        logging.info(f"Comando de impressão enviado com sucesso para: {pdf_file}")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao imprimir PDF via ShellExecute: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_pdf_sumatra(pdf_file, printer_name=None):
    """
    Função para imprimir um PDF usando o SumatraPDF (precisa estar instalado)
    Esta é uma alternativa para sistemas onde o ShellExecute não funciona
    """
    try:
        if not PRINTER_ENABLED:
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Se um caminho para o SumatraPDF não estiver definido, procura no programa files
        sumatra_path = os.environ.get('SUMATRA_PATH', 
                                     r"C:\Program Files\SumatraPDF\SumatraPDF.exe")
        
        # Se o arquivo SumatraPDF não existir nesse caminho, procura no diretório do app
        if not os.path.exists(sumatra_path):
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sumatra_path = os.path.join(app_dir, 'SumatraPDF.exe')
            
        # Se ainda não encontrou, procura no diretório atual
        if not os.path.exists(sumatra_path):
            sumatra_path = os.path.join(os.getcwd(), 'SumatraPDF.exe')
            
        if not os.path.exists(sumatra_path):
            logging.error("SumatraPDF não encontrado. Por favor, instale-o ou configure o caminho.")
            return False
            
        # Verifica se o arquivo existe
        if not os.path.exists(pdf_file):
            logging.error(f"Arquivo não encontrado: {pdf_file}")
            return False
            
        import subprocess
        
        # Constrói o comando para imprimir
        command = [
            sumatra_path,
            "-print-to", printer_name if printer_name else "default",
            "-silent",
            pdf_file
        ]
        
        logging.info(f"Executando comando: {' '.join(command)}")
        
        # Executa o comando
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"Erro ao imprimir com SumatraPDF: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
        logging.info("Impressão via SumatraPDF concluída com sucesso")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao imprimir PDF via SumatraPDF: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def print_pdf_powershell(pdf_file, printer_name=None):
    """
    Função para imprimir PDF usando PowerShell
    Esta é uma terceira abordagem que pode ser mais confiável em alguns sistemas Windows
    """
    try:
        if not PRINTER_ENABLED:
            logging.info("Impressão desabilitada. Não será enviado para a impressora.")
            return True
            
        # Verifica se o arquivo existe
        if not os.path.exists(pdf_file):
            logging.error(f"Arquivo não encontrado: {pdf_file}")
            return False
            
        # Constrói o comando PowerShell
        printer_param = f'"{printer_name}"' if printer_name else 'default'
        ps_command = f'Start-Process -FilePath "{pdf_file}" -Verb Print'
        
        # Executa o comando via subprocess
        import subprocess
        
        logging.info(f"Tentando imprimir via PowerShell: {pdf_file}")
        
        command = ['powershell', '-Command', ps_command]
        logging.info(f"Executando comando: {' '.join(command)}")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logging.error(f"Erro ao imprimir com PowerShell: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
        logging.info("Impressão via PowerShell enviada com sucesso")
        return True
        
    except Exception as e:
        logging.error(f"Erro ao imprimir PDF via PowerShell: {str(e)}")
        logging.error(traceback.format_exc())
        return False

# Função para imprimir usando qualquer método disponível
def print_pdf(pdf_file, printer_name=None):
    """
    Tenta imprimir o PDF utilizando diversos métodos, na ordem:
    1. ShellExecute do Windows (requer aplicativo padrão para PDFs)
    2. SumatraPDF (se estiver instalado)
    3. PowerShell (como terceira opção)
    4. Aplicativo Padrão do Windows
    """
    try:
        # Primeiro, tenta o método ShellExecute do Windows
        logging.info("Tentando imprimir usando ShellExecute...")
        if print_pdf_on_windows(pdf_file, printer_name):
            logging.info("Impressão via ShellExecute concluída com sucesso")
            return True
            
        # Se falhar, tenta usar o SumatraPDF
        logging.info("ShellExecute falhou, tentando SumatraPDF...")
        if print_pdf_sumatra(pdf_file, printer_name):
            logging.info("Impressão via SumatraPDF concluída com sucesso")
            return True
            
        # Se o SumatraPDF falhar, tenta usar o PowerShell
        logging.info("SumatraPDF falhou, tentando PowerShell...")
        if print_pdf_powershell(pdf_file, printer_name):
            logging.info("Impressão via PowerShell concluída com sucesso")
            return True
            
        # Se todos os métodos anteriores falharem, tenta com o aplicativo padrão
        logging.info("Tentando impressão com aplicativo padrão...")
        try:
            import os
            os.startfile(pdf_file, "print")
            logging.info("Comando de impressão pelo aplicativo padrão executado")
            return True
        except Exception as e:
            logging.error(f"Erro ao imprimir com aplicativo padrão: {str(e)}")
            
        # Se todos os métodos falharem
        logging.error("Todos os métodos de impressão falharam.")
        return False
        
    except Exception as e:
        logging.error(f"Erro ao tentar métodos de impressão: {str(e)}")
        logging.error(traceback.format_exc())
        return False
