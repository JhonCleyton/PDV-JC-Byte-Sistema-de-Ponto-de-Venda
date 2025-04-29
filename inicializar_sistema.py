"""
Script para inicializar o sistema e configurar a impressão automática
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class CompanyInfo(db.Model):
    """Modelo para informações da empresa"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    cnpj = db.Column(db.String(18))
    auto_print = db.Column(db.Boolean, default=True)

with app.app_context():
    # Cria as tabelas
    print("Criando tabelas do banco de dados...")
    db.create_all()
    
    # Verifica e configura a impressão automática
    company = CompanyInfo.query.first()
    if company:
        print(f"Empresa encontrada: {company.name}")
        print(f"Impressão automática atual: {company.auto_print}")
        
        # Se não estiver configurada, configura
        if not company.auto_print:
            company.auto_print = True
            db.session.commit()
            print("Impressão automática ativada com sucesso!")
    else:
        print("Nenhuma empresa encontrada no banco de dados!")
        print("Criando configuração padrão...")
        
        # Cria configuração padrão
        company = CompanyInfo(
            name="EMPRESA",
            address="ENDEREÇO",
            city="CIDADE",
            state="UF",
            cnpj="00.000.000/0000-00",
            auto_print=True
        )
        db.session.add(company)
        db.session.commit()
        print("Configuração padrão criada com impressão automática ativada!")

    # Verifica novamente
    company = CompanyInfo.query.first()
    print(f"Impressão automática final: {company.auto_print}")

if __name__ == "__main__":
    pass
