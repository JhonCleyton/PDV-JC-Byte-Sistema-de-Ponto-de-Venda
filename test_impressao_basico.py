"""
Script básico para testar impressão direta
"""
import win32print
import win32api
import logging
import time

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_impressao_basico():
    """Testa impressão básica usando comandos ESC/POS"""
    try:
        # Obtém a impressora padrão
        printer_name = "POS-58"
        logging.info(f"Testando impressão na impressora: {printer_name}")
        
        # Texto de teste com comandos ESC/POS
        texto = """
\x1B@\x1B!\x11\n"""  # Inicializa e configura tamanho médio
        texto += """==================================\n         TESTE BÁSICO\n==================================\n\n"""
        texto += f"Data: {time.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        texto += "1. Linha de teste\n"
        texto += "2. Linha de teste\n"
        texto += "3. Linha de teste\n\n"
        texto += "==================================\n      TESTE CONCLUÍDO\n==================================\n\n\n\n\n"  # Espaço para corte
        
        # Abre a impressora
        printer = win32print.OpenPrinter(printer_name)
        try:
            # Inicia um documento
            hJob = win32print.StartDocPrinter(printer, 1, ("Teste Básico", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer)
                
                # Envia o texto para a impressora
                win32print.WritePrinter(printer, texto.encode('cp850'))
                
                win32print.EndPagePrinter(printer)
                logging.info("Impressão enviada com sucesso!")
                return True
            finally:
                win32print.EndDocPrinter(printer)
        finally:
            win32print.ClosePrinter(printer)
            
    except Exception as e:
        logging.error(f"Erro ao imprimir: {str(e)}")
        return False

def main():
    """Função principal"""
    print("=== TESTE DE IMPRESSÃO BÁSICO ===")
    
    if test_impressao_basico():
        print("Impressão testada com sucesso!")
    else:
        print("Falha ao testar impressão.")

if __name__ == "__main__":
    main()
