from flask import Flask
from routes.caixa import gerar_relatorio_caixa
from models import db, Sale, CashRegister

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pdv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        caixa_id = 4
        print(f"Verificando caixa {caixa_id}")
        
        # Verificar se o caixa existe
        caixa = CashRegister.query.get(caixa_id)
        if not caixa:
            print(f"Caixa ID {caixa_id} não encontrado!")
            exit(1)
        
        print(f"Caixa encontrado: ID={caixa.id}, Status={caixa.status}")
        
        # Buscar vendas do caixa
        vendas = Sale.query.filter_by(cash_register_id=caixa_id).all()
        print(f"Total de vendas encontradas: {len(vendas)}")
        
        # Verificar se as vendas têm o campo description 
        for i, venda in enumerate(vendas):
            if i < 5:  # Mostrar apenas as 5 primeiras para não poluir o output
                print(f"Venda ID={venda.id}, Descrição={venda.description}, Método={venda.payment_method}")
        
        # Tentar gerar o relatório
        print("\nTentando gerar relatório...")
        relatorio = gerar_relatorio_caixa(caixa_id)
        
        # Verificar as chaves do relatório
        print("\nChaves do relatório:")
        for chave in relatorio.keys():
            print(f"- {chave}")
        
        print("\nRelatório gerado com sucesso!")
    except Exception as e:
        import traceback
        print(f"ERRO: {str(e)}")
        print(traceback.format_exc())
