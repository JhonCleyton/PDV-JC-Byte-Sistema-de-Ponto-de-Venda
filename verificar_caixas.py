import os
import sys
from decimal import Decimal

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importando os modelos e instanciando o app
from models import db, CashRegister, Sale, Receivable
from app import app

def listar_caixas():
    """Lista todos os caixas no sistema e seus status"""
    with app.app_context():
        caixas = CashRegister.query.all()
        
        print(f"Total de caixas: {len(caixas)}")
        print("\n=== LISTA DE CAIXAS ===")
        
        for caixa in caixas:
            print(f"ID: {caixa.id}")
            print(f"Status: {caixa.status}")
            print(f"Data Abertura: {caixa.opening_date}")
            print(f"Data Fechamento: {caixa.closing_date}")
            print(f"Valor Inicial: R$ {float(caixa.opening_amount):.2f}")
            print(f"Valor Final: R$ {float(caixa.closing_amount) if caixa.closing_amount else 0:.2f}")
            print("---")

if __name__ == "__main__":
    listar_caixas()
