"""
Script para testar a impressão direta na impressora POS-58
"""
import os
import sys
import logging
import win32print
import win32api
import time

def test_impressao():
    """
    Testa a impressão direta na impressora POS-58
    """
    try:
        # Obtém a impressora POS-58
        printer_name = "POS-58"
        print(f"Testando impressão na impressora: {printer_name}")
        
        # Verifica se a impressora existe
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        if printer_name not in printers:
            print(f"Impressora {printer_name} não encontrada!")
            return False
            
        # Define a impressora como padrão
        original_printer = win32print.GetDefaultPrinter()
        win32print.SetDefaultPrinter(printer_name)
        
        # Cria um texto de teste
        texto = """
==================================
         TESTE DE IMPRESSÃO
==================================

Data: {}

1. Teste de impressão 1
2. Teste de impressão 2
3. Teste de impressão 3

==================================
      TESTE CONCLUÍDO
==================================


""".format(time.strftime("%d/%m/%Y %H:%M:%S"))
        
        # Abre o manipulador da impressora
        hPrinter = win32print.OpenPrinter(printer_name)
        
        try:
            # Inicia um documento
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Teste de Impressão", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # Converte o texto para bytes e envia para a impressora
                win32print.WritePrinter(hPrinter, texto.encode('utf-8'))
                
                win32print.EndPagePrinter(hPrinter)
                print("Teste de impressão enviado com sucesso!")
                return True
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            
        # Restaura a impressora original
        win32print.SetDefaultPrinter(original_printer)
        
    except Exception as e:
        print(f"Erro ao imprimir: {str(e)}")
        return False

def main():
    """Função principal"""
    print("=== TESTE DE IMPRESSÃO POS-58 ===")
    
    # Tenta imprimir
    if test_impressao():
        print("Impressão testada com sucesso!")
    else:
        print("Falha ao testar impressão.")

if __name__ == "__main__":
    main()
