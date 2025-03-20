import os
import sys
from decimal import Decimal

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importando os modelos e instanciando o app
from models import db, CashRegister
from app import app

def atualizar_valores_esperados():
    """Atualiza os valores esperados e diferenças para todos os caixas fechados"""
    with app.app_context():
        # Busca todos os caixas fechados
        caixas = CashRegister.query.filter_by(status='closed').all()
        count = 0
        
        print(f"Encontrados {len(caixas)} caixas fechados.")
        print("\nAtualizando valores esperados...")
        
        for caixa in caixas:
            expected = caixa.calculate_expected_amount()
            print(f"Caixa #{caixa.id}:")
            print(f"  Valor Inicial: R$ {float(caixa.opening_amount):.2f}")
            print(f"  Valor Esperado Antigo: R$ {float(caixa.expected_amount or 0):.2f}")
            print(f"  Valor Esperado Novo: R$ {float(expected):.2f}")
            
            # Atualiza o valor esperado
            caixa.expected_amount = expected
            
            # Recalcula a diferença
            if caixa.closing_amount:
                old_diff = caixa.difference or 0
                new_diff = caixa.closing_amount - expected
                caixa.difference = new_diff
                print(f"  Diferença Antiga: R$ {float(old_diff):.2f}")
                print(f"  Diferença Nova: R$ {float(new_diff):.2f}")
            
            db.session.add(caixa)
            count += 1
            print("---")
        
        # Salva as alterações
        db.session.commit()
        print(f"\nAtualizados {count} caixas com sucesso!")

if __name__ == "__main__":
    atualizar_valores_esperados()
