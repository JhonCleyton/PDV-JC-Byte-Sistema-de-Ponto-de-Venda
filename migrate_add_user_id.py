from app import app, db
from sqlalchemy import text
import sys

def migrate_db():
    with app.app_context():
        print("Iniciando migração para adicionar campo user_id na tabela sales...")
        
        # Verificar se a coluna existe
        try:
            # Verifica se a coluna já existe usando SQL direto
            query = text("PRAGMA table_info(sales)")
            result = db.session.execute(query)
            columns = [row[1] for row in result]
            
            if 'user_id' in columns:
                print("Campo user_id já existe na tabela!")
                print("Migração não necessária.")
                return True
            else:
                print("Campo não existe, adicionando...")
        except Exception as e:
            print(f"Erro ao verificar coluna: {str(e)}")
            return False
        
        # Adicionar a coluna
        try:
            # SQL para SQLite - adiciona a coluna
            alter_query = text('ALTER TABLE sales ADD COLUMN user_id INTEGER REFERENCES users(id)')
            db.session.execute(alter_query)
            
            # Atualizar registros existentes
            update_query = text('UPDATE sales SET user_id = supervisor_id')
            db.session.execute(update_query)
            
            # Commit das alterações
            db.session.commit()
            
            print("Coluna user_id adicionada com sucesso!")
            print("Dados existentes foram atualizados!")
            print("Migração concluída com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro durante a migração: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    if migrate_db():
        print("Migração realizada com sucesso!")
    else:
        print("Ocorreu um erro na migração.")
        sys.exit(1)
