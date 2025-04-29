"""
Script para testar a impressão de cupons
"""
import os
import sys
import logging
from utils.printer import print_test, print_pdf
import win32print

def main():
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Listar impressoras disponíveis
    print("Impressoras disponíveis:")
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
    for i, printer in enumerate(printers):
        print(f"{i+1}. {printer}")
    
    # Obter impressora padrão
    default_printer = win32print.GetDefaultPrinter()
    print(f"\nImpressora padrão: {default_printer}")
    
    # Testar impressão
    print("\nTestando impressão...")
    result = print_test()
    
    if result:
        print("Teste de impressão enviado com sucesso!")
    else:
        print("Falha ao enviar teste de impressão.")
    
    # Testar impressão de PDF existente
    receipts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'receipts')
    pdf_files = [f for f in os.listdir(receipts_dir) if f.endswith('.pdf')]
    
    if pdf_files:
        print("\nPDFs disponíveis para teste:")
        for i, pdf in enumerate(pdf_files):
            print(f"{i+1}. {pdf}")
        
        try:
            choice = int(input("\nEscolha um PDF para imprimir (0 para sair): "))
            if choice > 0 and choice <= len(pdf_files):
                pdf_path = os.path.join(receipts_dir, pdf_files[choice-1])
                print(f"Imprimindo {pdf_path}...")
                
                result = print_pdf(pdf_path)
                if result:
                    print("PDF enviado para impressão com sucesso!")
                else:
                    print("Falha ao enviar PDF para impressão.")
        except ValueError:
            print("Opção inválida.")
    else:
        print("Nenhum PDF encontrado para teste.")

if __name__ == "__main__":
    main()
