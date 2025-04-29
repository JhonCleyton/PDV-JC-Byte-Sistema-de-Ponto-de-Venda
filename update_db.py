from app import app, db
from models import CompanyInfo

with app.app_context():
    db.create_all()
    print("Banco de dados atualizado com sucesso!")
