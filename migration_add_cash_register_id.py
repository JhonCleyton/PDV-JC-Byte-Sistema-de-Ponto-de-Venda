"""
Script para adicionar a coluna cash_register_id à tabela sales.
"""
from app import app, db
from sqlalchemy import text

def add_column():
    with app.app_context():
        try:
            # Verifica se a coluna já existe
            db.session.execute(text("SELECT cash_register_id FROM sales LIMIT 1"))
            print("A coluna cash_register_id já existe na tabela sales.")
        except Exception:
            # Adiciona a coluna
            db.session.execute(text("ALTER TABLE sales ADD COLUMN cash_register_id INTEGER REFERENCES cash_registers(id)"))
            db.session.commit()
            print("Coluna cash_register_id adicionada com sucesso à tabela sales.")

if __name__ == "__main__":
    add_column()
