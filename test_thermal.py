"""
Script para testar a impressão térmica
"""
import os
import sys
import logging
from utils.thermal_printer import print_text_to_thermal, get_thermal_printer, print_sale_receipt

def test_simple_print():
    """Testa a impressão de texto simples"""
    print("Testando impressão de texto simples...")
    
    # Texto de teste
    test_text = """
==================================
         TESTE DE IMPRESSÃO
==================================
    
Este é um teste de impressão térmica
para verificar se a impressora está
funcionando corretamente.

1. Linha de teste 1
2. Linha de teste 2
3. Linha de teste 3

==================================
      TESTE CONCLUÍDO COM SUCESSO
==================================


"""
    
    # Obtém a impressora térmica
    printer = get_thermal_printer()
    print(f"Impressora térmica detectada: {printer}")
    
    # Imprime o texto
    result = print_text_to_thermal(test_text, printer)
    
    if result:
        print("Teste de impressão enviado com sucesso!")
    else:
        print("Falha ao enviar teste de impressão.")
    
    return result

def test_receipt_print():
    """Testa a impressão de um cupom formatado"""
    print("Testando impressão de cupom...")
    
    # Dados de exemplo para um cupom
    sale_data = {
        'company_name': 'EMPRESA TESTE LTDA',
        'company_address': 'Rua Teste, 123 - Centro, Cidade-UF',
        'company_cnpj': '00.000.000/0000-00',
        'id': '12345',
        'date': '02/04/2025 20:45:00',
        'customer_name': 'CLIENTE TESTE',
        'items': [
            {
                'description': 'Produto 1',
                'quantity': 2,
                'price': 10.50,
            },
            {
                'description': 'Produto 2',
                'quantity': 1,
                'price': 15.75,
            },
            {
                'description': 'Produto 3',
                'quantity': 3,
                'price': 5.25,
            }
        ],
        'subtotal': 52.50,
        'discount': 2.50,
        'total': 50.00,
        'payment_method': 'DINHEIRO'
    }
    
    # Imprime o cupom
    result = print_sale_receipt(sale_data)
    
    if result:
        print("Cupom enviado para impressão com sucesso!")
    else:
        print("Falha ao enviar cupom para impressão.")
    
    return result

def main():
    """Função principal"""
    print("=== TESTE DE IMPRESSÃO TÉRMICA ===")
    print("Escolha uma opção:")
    print("1. Testar impressão de texto simples")
    print("2. Testar impressão de cupom formatado")
    print("0. Sair")
    
    try:
        choice = input("Opção: ")
        
        if choice == '1':
            test_simple_print()
        elif choice == '2':
            test_receipt_print()
        elif choice == '0':
            print("Saindo...")
        else:
            print("Opção inválida!")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    main()
