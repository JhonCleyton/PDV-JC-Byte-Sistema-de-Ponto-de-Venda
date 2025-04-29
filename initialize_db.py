"""
Script para inicializar o banco de dados e configurar o contexto do Flask
"""
import os
import sys
import logging
import win32print
import win32api
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import tempfile

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Config:
    """Configurações básicas"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pdv.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRINTER_ENABLED = True
    AUTO_PRINT = True

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Customer(db.Model):
    """Modelo para clientes"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    registration = db.Column(db.String(50), unique=True)
    sales = db.relationship('Sale', backref='customer', lazy=True)

class CompanyInfo(db.Model):
    """Modelo para informações da empresa"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    cnpj = db.Column(db.String(18))
    auto_print = db.Column(db.Boolean, default=True)

class Sale(db.Model):
    """Modelo para vendas"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    payment_method = db.Column(db.String(50))
    supervisor_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    total = db.Column(db.Float)
    date = db.Column(db.DateTime)
    subtotal = db.Column(db.Float)
    discount = db.Column(db.Float)
    items = db.relationship('SaleItem', backref='sale', lazy=True)

class SaleItem(db.Model):
    """Modelo para itens de venda"""
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Float)
    price = db.Column(db.Float)
    subtotal = db.Column(db.Float)

def initialize_database():
    """Inicializa o banco de dados e cria as tabelas"""
    try:
        with app.app_context():
            db.create_all()
            
            # Cria uma empresa de teste se não existir
            company = CompanyInfo.query.first()
            if not company:
                company = CompanyInfo(
                    name="EMPRESA TESTE",
                    address="Rua Teste, 123",
                    city="Cidade",
                    state="UF",
                    cnpj="00.000.000/0000-00",
                    auto_print=True
                )
                db.session.add(company)
                db.session.commit()
                
            logging.info("Banco de dados inicializado com sucesso!")
            return True
            
    except Exception as e:
        logging.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        return False

def main():
    """Função principal"""
    print("=== INICIALIZAÇÃO DO BANCO DE DADOS ===")
    
    if initialize_database():
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Falha ao inicializar o banco de dados.")

if __name__ == "__main__":
    main()
