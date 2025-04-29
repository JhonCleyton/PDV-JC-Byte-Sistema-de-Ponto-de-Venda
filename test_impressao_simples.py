"""
Script de teste simples para impressão direta
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

def test_impressao_simples():
    """Testa impressão simples usando RAW data"""
    try:
        # Obtém a impressora padrão
        printer_name = win32print.GetDefaultPrinter()
        logging.info(f"Impressora padrão: {printer_name}")
        
        # Texto de teste com comandos ESC/POS
        texto = """
\x1B@\x1B!\x11\n"""  # Inicializa e configura tamanho médio
        texto += """==================================\n         TESTE DE IMPRESSÃO\n==================================\n\n"""
        texto += f"Data: {time.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        texto += "1. Teste de impressão\n"
        texto += "2. Linha de teste 2\n"
        texto += "3. Linha de teste 3\n\n"
        texto += "==================================\n      TESTE CONCLUÍDO\n==================================\n\n\n\n\n"  # Espaço para corte
        
        # Abre a impressora
        printer = win32print.OpenPrinter(printer_name)
        try:
            # Inicia um documento
            hJob = win32print.StartDocPrinter(printer, 1, ("Teste de Impressão", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer)
                
                # Converte para bytes e envia para a impressora
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
    print("=== TESTE DE IMPRESSÃO SIMPLES ===")
    
    if test_impressao_simples():
        print("Impressão testada com sucesso!")
    else:
        print("Falha ao testar impressão.")

if __name__ == "__main__":
    main()
