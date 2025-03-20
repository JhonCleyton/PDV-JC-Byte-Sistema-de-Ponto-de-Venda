import os
import sys
from decimal import Decimal
from sqlalchemy import desc

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importando os modelos e instanciando o app
from models import db, CashRegister, Sale, Receivable
from routes.caixa import gerar_relatorio_caixa
from app import app

def testar_calculo_esperado(caixa_id):
    """Testa o cálculo do valor esperado no caixa"""
    with app.app_context():
        caixa = CashRegister.query.get(caixa_id)
        if not caixa:
            print(f"Caixa #{caixa_id} não encontrado!")
            return
        
        # Versão manual do cálculo
        valor_inicial = float(caixa.opening_amount)
        
        # Obtem vendas deste caixa
        vendas = Sale.query.filter_by(cash_register_id=caixa.id).all()
        
        # Separa vendas normais dos pagamentos de dívida
        vendas_normais = []
        pagamentos_divida = []
        
        for venda in vendas:
            if venda.description and ('Pagamento de dívida' in venda.description or 'Pagamento de conta a receber' in venda.description):
                pagamentos_divida.append(venda)
            else:
                vendas_normais.append(venda)
        
        # Calcula valor das vendas em dinheiro
        vendas_dinheiro = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'dinheiro'])
        
        # Calcula valor dos pagamentos de dívida em dinheiro
        pagamentos_divida_dinheiro = sum([float(pagamento.total) for pagamento in pagamentos_divida if pagamento.payment_method == 'dinheiro'])
        
        # Calcula retiradas
        retiradas = sum([float(retirada.amount) for retirada in caixa.withdrawals])
        
        # Cálculo final
        valor_esperado = valor_inicial + vendas_dinheiro + pagamentos_divida_dinheiro - retiradas
        
        print(f"=== CAIXA #{caixa_id} ===")
        print(f"Status: {caixa.status}")
        print(f"Valor Inicial: R$ {valor_inicial:.2f}")
        print(f"Vendas em Dinheiro: R$ {vendas_dinheiro:.2f}")
        print(f"Pagamentos de Dívida em Dinheiro: R$ {pagamentos_divida_dinheiro:.2f}")
        print(f"Retiradas: R$ {retiradas:.2f}")
        print(f"Valor Esperado (calculado manualmente): R$ {valor_esperado:.2f}")
        print(f"Valor Final Declarado: R$ {float(caixa.closing_amount):.2f}")
        print(f"Diferença: R$ {(float(caixa.closing_amount) - valor_esperado):.2f}")
        
        # Teste com a função do sistema
        relatorio = gerar_relatorio_caixa(caixa_id)
        print(f"\nValor Esperado (calculado pelo sistema): R$ {relatorio['valor_esperado']:.2f}")
        print(f"Diferença (calculada pelo sistema): R$ {relatorio['diferenca']:.2f}")

if __name__ == "__main__":
    # Obtém o ID do caixa a partir dos argumentos da linha de comando
    if len(sys.argv) > 1:
        caixa_id = int(sys.argv[1])
    else:
        # Pega o último caixa fechado
        with app.app_context():
            ultimo_caixa = CashRegister.query.filter_by(status='closed').order_by(desc(CashRegister.id)).first()
            if ultimo_caixa:
                caixa_id = ultimo_caixa.id
            else:
                print("Nenhum caixa fechado encontrado!")
                sys.exit(1)
    
    testar_calculo_esperado(caixa_id)
