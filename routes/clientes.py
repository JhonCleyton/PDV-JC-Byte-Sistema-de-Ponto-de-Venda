from flask import Blueprint, request, jsonify
from models import db, Customer
from flask_login import login_required

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/api/clientes')
@login_required
def list_customers():
    """Lista todos os clientes"""
    try:
        customers = Customer.query.all()
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in customers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/buscar/<registration>')
@login_required
def find_customer(registration):
    """Busca um cliente pela matrícula"""
    try:
        print("\n=== Buscando cliente ===")
        print(f"Matrícula recebida: {registration}")
        
        # Lista todos os clientes para debug
        print("\nClientes no banco:")
        for c in Customer.query.all():
            print(f"- {c.name} (ID: {c.id}, Matrícula: {c.registration})")
        
        # Remove zeros à esquerda
        registration = registration.lstrip('0')
        print(f"Matrícula sem zeros à esquerda: {registration}")
        
        # Tenta encontrar por matrícula
        customer = Customer.query.filter_by(registration=registration).first()
        print(f"SQL: {Customer.query.filter_by(registration=registration)}")
        print(f"Resultado da busca por matrícula: {customer}")
        
        if customer:
            print(f"Cliente encontrado: {customer.name}")
            print(f"Dados do cliente: {customer.to_dict()}")
            return jsonify({
                'success': True,
                'data': customer.to_dict()
            })
        
        # Se não encontrou por matrícula, tenta por CPF
        customer = Customer.query.filter_by(cpf=registration).first()
        print(f"Resultado da busca por CPF: {customer}")
        
        if customer:
            print(f"Cliente encontrado: {customer.name}")
            print(f"Dados do cliente: {customer.to_dict()}")
            return jsonify({
                'success': True,
                'data': customer.to_dict()
            })
        
        print("Cliente não encontrado")    
        return jsonify({
            'success': False,
            'error': 'Cliente não encontrado'
        })
        
    except Exception as e:
        print(f"Erro ao buscar cliente: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/<int:id>')
@login_required
def get_customer(id):
    """Busca um cliente pelo ID"""
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            })
        
        return jsonify({
            'success': True,
            'data': customer.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes', methods=['POST'])
@login_required
def create_customer():
    """Cria um novo cliente"""
    try:
        data = request.get_json()
        
        # Verifica se já existe cliente com essa matrícula
        if Customer.query.filter_by(registration=data['registration']).first():
            return jsonify({
                'success': False,
                'error': 'Já existe um cliente com essa matrícula'
            })
        
        # Verifica se já existe cliente com esse CPF
        if data.get('cpf') and Customer.query.filter_by(cpf=data['cpf']).first():
            return jsonify({
                'success': False,
                'error': 'Já existe um cliente com esse CPF'
            })
        
        customer = Customer(
            name=data['name'],
            registration=data['registration'],
            cpf=data.get('cpf'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            credit_limit=data.get('credit_limit', 0)
        )
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': customer.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/<int:id>', methods=['PUT'])
@login_required
def update_customer(id):
    """Atualiza um cliente"""
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            })
        
        data = request.get_json()
        
        # Verifica se já existe outro cliente com essa matrícula
        if data.get('registration'):
            existing = Customer.query.filter_by(
                registration=data['registration']
            ).first()
            if existing and existing.id != id:
                return jsonify({
                    'success': False,
                    'error': 'Já existe um cliente com essa matrícula'
                })
        
        # Verifica se já existe outro cliente com esse CPF
        if data.get('cpf'):
            existing = Customer.query.filter_by(cpf=data['cpf']).first()
            if existing and existing.id != id:
                return jsonify({
                    'success': False,
                    'error': 'Já existe um cliente com esse CPF'
                })
        
        # Atualiza os campos
        if 'name' in data:
            customer.name = data['name']
        if 'registration' in data:
            customer.registration = data['registration']
        if 'cpf' in data:
            customer.cpf = data['cpf']
        if 'email' in data:
            customer.email = data['email']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'address' in data:
            customer.address = data['address']
        if 'credit_limit' in data:
            customer.credit_limit = data['credit_limit']
        if 'status' in data:
            customer.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': customer.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    """Deleta um cliente"""
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            })
        
        # Verifica se o cliente tem dívidas pendentes
        if customer.current_debt > 0:
            return jsonify({
                'success': False,
                'error': 'Cliente possui dívidas pendentes'
            })
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/<int:id>/sales')
@login_required
def get_customer_sales(id):
    """Busca o histórico de vendas do cliente"""
    try:
        customer = Customer.query.get(id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            })
        
        # Busca as vendas do cliente
        sales = []
        for sale in customer.sales:
            sale_dict = sale.to_dict()
            # Adiciona os itens da venda
            sale_dict['items'] = [item.to_dict() for item in sale.items]
            sales.append(sale_dict)
        
        # Busca as parcelas a receber
        receivables = []
        for receivable in customer.receivables:
            receivables.append(receivable.to_dict())
        
        return jsonify({
            'success': True,
            'data': {
                'sales': sales,
                'receivables': receivables
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/busca')
@login_required
def find_customer_by_query():
    """Busca um cliente pela matrícula via parâmetro de consulta"""
    try:
        matricula = request.args.get('matricula')
        
        if not matricula:
            return jsonify({
                'success': False,
                'error': 'Matrícula não informada'
            })
            
        print(f"Buscando cliente pela matrícula: {matricula}")
        
        # Remove zeros à esquerda
        matricula = matricula.lstrip('0')
        
        # Tenta encontrar por matrícula
        customer = Customer.query.filter_by(registration=matricula).first()
        
        if customer:
            # Calcula o limite disponível
            limite_disponivel = customer.credit_limit - customer.current_debt
            if limite_disponivel < 0:
                limite_disponivel = 0
                
            return jsonify({
                'success': True,
                'customer': {
                    'id': customer.id,
                    'registration': customer.registration,
                    'name': customer.name,
                    'credit_limit': float(customer.credit_limit),
                    'current_debt': float(customer.current_debt),
                    'available_credit': float(limite_disponivel)
                }
            })
        
        return jsonify({
            'success': False,
            'error': 'Cliente não encontrado'
        })
        
    except Exception as e:
        print(f"Erro ao buscar cliente: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@clientes_bp.route('/api/clientes/atualizar-saldos', methods=['POST'])
@login_required
def atualizar_saldos_clientes():
    """
    Atualiza o saldo de todos os clientes com base nas parcelas em aberto.
    Esta rota recalcula os saldos de débito de todos os clientes, garantindo
    que o sistema esteja com valores corretos.
    """
    try:
        # Buscar todos os clientes
        clientes = Customer.query.all()
        
        total_clientes = len(clientes)
        clientes_atualizados = 0
        
        for cliente in clientes:
            # Salvar o saldo atual para comparação
            saldo_anterior = cliente.current_debt
            
            # Chamar o método para atualizar o saldo
            cliente.update_debt()
            
            # Se o saldo mudou, contar como atualizado
            if saldo_anterior != cliente.current_debt:
                clientes_atualizados += 1
        
        # Salvar as alterações no banco de dados
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Foram atualizados os saldos de {clientes_atualizados} de {total_clientes} clientes.',
            'total_clientes': total_clientes,
            'clientes_atualizados': clientes_atualizados
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        })
