from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, Sale, SaleItem, Product, Customer, User, Receivable, Payment, ReceivablePayment, CompanyInfo, CashRegister
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ConversionSyntax
from utils.permissions import non_cashier_required
import re
import logging
from utils.printer import print_receipt, print_payment_receipt
from sqlalchemy import func

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

vendas_bp = Blueprint('vendas', __name__)

# Função para converter valores de forma segura para Decimal
def safe_decimal(value):
    """Converte de forma segura um valor para Decimal"""
    if value is None:
        return Decimal('0')
        
    if isinstance(value, Decimal):
        return value
        
    # Se for número, converte para string primeiro
    if isinstance(value, (int, float)):
        value = str(value)
        
    # Garante que a string está em formato adequado para conversão
    if isinstance(value, str):
        # Remove caracteres não numéricos exceto ponto e vírgula
        value = re.sub(r'[^\d.,]', '', value)
        # Substitui vírgula por ponto
        value = value.replace(',', '.')
        
        try:
            return Decimal(value)
        except (InvalidOperation, ConversionSyntax) as e:
            logger.error(f"Erro ao converter '{value}' para Decimal: {str(e)}")
            return Decimal('0')
    
    # Se não for nenhum dos tipos acima, tenta converter para string e depois para Decimal
    try:
        return Decimal(str(value))
    except (InvalidOperation, ConversionSyntax) as e:
        logger.error(f"Erro ao converter '{value}' (tipo {type(value)}) para Decimal: {str(e)}")
        return Decimal('0')

@vendas_bp.route('/vendas')
@login_required
@non_cashier_required
def list_sales():
    """Lista todas as vendas"""
    try:
        sales = Sale.query.order_by(Sale.date.desc()).all()
        return render_template('vendas/list.html', sales=sales)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/vendas/nova')
@login_required
@non_cashier_required
def create():
    """Página do PDV"""
    try:
        return render_template('vendas/pdv.html')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/vendas/nova/modern')
@login_required
@non_cashier_required
def create_modern():
    """Página do PDV com interface moderna"""
    try:
        # Passar a data/hora atual para o template
        now = datetime.now()
        return render_template('vendas/pdv_modern.html', now=now)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/vendas/nova/professional')
@login_required
def create_professional():
    """Página do PDV com interface profissional"""
    try:
        # Passar a data/hora atual para o template
        now = datetime.now()
        # Verifica se o usuário está autenticado
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return render_template('vendas/pdv_professional.html', now=now)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/api/vendas', methods=['POST'])
@login_required
def criar_venda():
    """Cria uma nova venda"""
    data = request.get_json()
        
    # Log para debug
    print("Dados recebidos:", data)
    if data.get('receivables'):
        for i, rcv in enumerate(data['receivables']):
            print(f"Parcela {i+1}: {rcv}")
            print(f"  amount: {rcv.get('amount')} (tipo: {type(rcv.get('amount'))})")
        
    # Validação dos dados
    if not data.get('items'):
        return jsonify({
            'success': False,
            'error': 'Nenhum item informado'
        })
        
    # Converte valores para string antes de calcular o total
    for item in data['items']:
        if isinstance(item['quantity'], (int, float)):
            item['quantity'] = str(item['quantity'])
        if isinstance(item['price'], (int, float)):
            item['price'] = str(item['price'])
                
    # Calcula o total da venda com tratamento para evitar erros de conversão
    try:
        total = sum(safe_decimal(item['quantity']) * safe_decimal(item['price']) for item in data['items'])
        print(f"Total calculado: {total} (tipo: {type(total)})")
    except Exception as e:
        print(f"Erro ao calcular total: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao calcular total da venda: {str(e)}'
        }), 400
        
    # Se for venda no crediário
    if data.get('payment_method') == 'crediario':
        # Verifica se tem cliente
        if not data.get('customer_id'):
            return jsonify({
                'success': False,
                'error': 'Cliente não informado para venda no crediário'
            })
            
        # Busca o cliente
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Cliente não encontrado'
            })
            
        # Verifica o limite apenas se não for uma venda autorizada
        if not data.get('authorized'):
            limite_disponivel = customer.credit_limit - customer.current_debt
            if total > limite_disponivel:
                return jsonify({
                    'success': False,
                    'error': 'Cliente não possui limite disponível'
                })
        
    # Cria a venda
    sale = Sale(
        customer_id=data.get('customer_id'),
        supervisor_id=current_user.id,
        user_id=current_user.id,  # Adiciona o usuário atual como operador
        total=total,
        payment_method=data.get('payment_method', 'dinheiro'),
        status='completed',
        date=datetime.now()
    )
    
    # Associa a venda ao caixa aberto do operador
    try:
        # Busca o caixa aberto para o usuário atual
        hoje = datetime.today().date()
        caixa_aberto = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open',
            func.date(CashRegister.opening_date) == hoje
        ).first()
        
        if caixa_aberto:
            sale.cash_register_id = caixa_aberto.id
            print(f"Venda associada ao caixa ID: {caixa_aberto.id}")
        else:
            print("Nenhum caixa aberto encontrado para o operador atual!")
    except Exception as e:
        print(f"Erro ao associar venda ao caixa: {str(e)}")
        # Não interrompe o fluxo se falhar apenas a associação com o caixa
    
    db.session.add(sale)
    db.session.flush()  # Para obter o ID da venda
        
    # Adiciona os itens
    for item_data in data['items']:
        try:
            # Garantir que os valores são strings válidas para conversão
            quantity_str = str(item_data['quantity'])
            price_str = str(item_data['price'])
                
            # Converter para Decimal
            quantity = safe_decimal(quantity_str)
            price = safe_decimal(price_str)
            subtotal = quantity * price
                
            item = SaleItem(
                product_id=item_data['product_id'],
                quantity=quantity,
                price=price,
                subtotal=subtotal
            )
            sale.items.append(item)
                
            # Atualiza o estoque
            product = Product.query.get(item_data['product_id'])
            if product:
                product.stock -= quantity
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao processar item: {str(e)}")
            print(f"Dados do item: {item_data}")
            return jsonify({
                'success': False,
                'error': f"Erro ao processar item: {str(e)}"
            }), 400
        
    # Se for crediário, cria as parcelas
    if data.get('payment_method') == 'crediario' and data.get('receivables'):
        for receivable_data in data['receivables']:
            try:
                # Converter a string de data para objeto datetime
                due_date = datetime.strptime(receivable_data['due_date'], '%Y-%m-%d')
                    
                # Log para debug
                print(f"Valor da parcela antes da conversão: {receivable_data['amount']}")
                print(f"Tipo do valor: {type(receivable_data['amount'])}")
                    
                # Converter o valor para Decimal - tratamento extra para garantir
                try:
                    # Se for número float ou int, converter para string primeiro
                    if isinstance(receivable_data['amount'], (float, int)):
                        amount_str = "{:.2f}".format(receivable_data['amount'])
                    else:
                        # Se já for string, garantir formato correto
                        amount_str = str(receivable_data['amount']).replace(',', '.')
                        
                    print(f"Valor formatado para conversão: {amount_str}")
                    amount = safe_decimal(amount_str)
                except Exception as e:
                    print(f"Erro específico na conversão: {str(e)}")
                    # Tenta uma última alternativa
                    amount = safe_decimal(round(float(receivable_data['amount']), 2))
                    
                # Cria uma descrição automática
                description = f"Venda #{sale.id} - Parcela {receivable_data.get('installment', 1)}"
                    
                receivable = Receivable(
                    customer_id=data['customer_id'],
                    sale_id=sale.id,
                    amount=amount,
                    due_date=due_date,
                    status='pending',
                    description=description
                )
                db.session.add(receivable)
                    
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': f'Erro ao processar parcela: {str(e)}'
                }), 400
        
        # Atualizar o saldo do cliente após registrar as parcelas
        try:
            customer = Customer.query.get(data['customer_id'])
            if customer:
                # Atualizar a dívida atual do cliente
                customer.update_debt()
                print(f"Dívida do cliente atualizada para: {customer.current_debt}")
        except Exception as e:
            print(f"Erro ao atualizar saldo do cliente: {str(e)}")
            # Não interrompe o fluxo se falhar apenas a atualização do saldo
        
    # Se for dinheiro, registra o pagamento e possível troco
    elif data.get('payment_method') == 'dinheiro' and data.get('received_amount'):
        try:
            received_amount = safe_decimal(data['received_amount'])
            change = received_amount - total if received_amount > total else Decimal('0')
                
            # Mostra valores para debug
            print(f"Valor recebido: {received_amount} (tipo: {type(received_amount)})")
            print(f"Total da venda: {total} (tipo: {type(total)})")
            print(f"Troco calculado: {change} (tipo: {type(change)})")
                
            # Atualiza a venda com informações de pagamento
            sale.received_amount = received_amount
            sale.change_amount = change
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Erro ao processar pagamento em dinheiro: {str(e)}'
            }), 400
    # Para cartão de crédito, débito e pix, apenas registramos o método de pagamento
    # que já foi definido ao criar a venda, sem processamento adicional
    # Tratamento de outros métodos de pagamento (cartão de crédito, débito e pix)
    # Neste caso, apenas registramos o método de pagamento e não realizamos
    # nenhuma ação adicional, pois o pagamento é processado externamente
        
    try:
        db.session.commit()
            
        # Imprime o recibo
        try:
            print_receipt(sale)
            print("Recibo impresso com sucesso")
        except Exception as e:
            print(f"Erro ao imprimir recibo: {str(e)}")
            # Não falha a venda se a impressão falhar
            
        return jsonify({
            'success': True,
            'sale_id': sale.id,
            'message': 'Venda realizada com sucesso!'
        })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vendas_bp.route('/api/clientes/<registration>/dividas')
@login_required
@non_cashier_required
def get_customer_debts(registration):
    """Retorna as dívidas de um cliente"""
    try:
        customer = Customer.query.filter_by(registration=registration).first()
        if not customer:
            return jsonify({'success': False, 'error': 'Cliente não encontrado'})
        
        receivables = Receivable.query.filter_by(
            customer_id=customer.id,
            status='pending'
        ).all()
        
        return jsonify({
            'success': True,
            'dividas': [r.to_dict() for r in receivables]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/api/dividas/<int:receivable_id>/pagar', methods=['POST'])
@login_required
def pay_debt(receivable_id):
    """Registra um pagamento em uma dívida"""
    try:
        data = request.get_json()
        receivable = Receivable.query.get(receivable_id)
        if not receivable:
            return jsonify({'success': False, 'error': 'Dívida não encontrada'})
        
        # Verifica se o valor não é maior que o restante
        valor = safe_decimal(data['valor'])
        if valor > receivable.remaining_amount:
            return jsonify({
                'success': False,
                'error': 'Valor maior que o restante da dívida'
            })
        
        # Registra o pagamento
        payment = ReceivablePayment(
            receivable_id=receivable.id,
            amount=valor,
            payment_method=data['forma_pagamento']
        )
        db.session.add(payment)
        
        # Atualiza o valor pago
        receivable.paid_amount += valor
        receivable.update_remaining_amount()
        
        # Atualiza o status da dívida
        if receivable.remaining_amount == 0:
            receivable.status = 'paid'
        elif receivable.paid_amount > 0:
            receivable.status = 'partial'
        else:
            receivable.status = 'pending'
        
        # Atualiza a dívida do cliente
        customer = None
        if receivable.customer:
            customer = receivable.customer
            receivable.customer.update_debt()
        
        # Associa o pagamento ao caixa aberto do operador atual
        try:
            # Busca o caixa aberto para o usuário atual
            hoje = datetime.today().date()
            caixa_aberto = CashRegister.query.filter(
                CashRegister.user_id == current_user.id,
                CashRegister.status == 'open',
                func.date(CashRegister.opening_date) == hoje
            ).first()
            
            if not caixa_aberto:
                print("Alerta: Nenhum caixa aberto encontrado para registrar o pagamento da dívida!")
            else:
                print(f"Pagamento de dívida associado ao caixa ID: {caixa_aberto.id}")
                # Criar uma venda virtual para registrar o pagamento no caixa
                payment_sale = Sale(
                    customer_id=receivable.customer_id if receivable.customer_id else None,
                    payment_method=data['forma_pagamento'],
                    supervisor_id=current_user.id,
                    user_id=current_user.id,
                    total=valor,
                    date=datetime.now(),
                    cash_register_id=caixa_aberto.id,
                    description=f"Pagamento de dívida #{receivable_id}"
                )
                db.session.add(payment_sale)
        except Exception as e:
            print(f"Erro ao associar pagamento de dívida ao caixa: {str(e)}")
            import traceback
            traceback.print_exc()
            # Não interrompe o fluxo se falhar apenas a associação com o caixa
        
        # Commit das mudanças no banco
        db.session.commit()
        
        # Imprime o cupom de pagamento
        try:
            from utils.printer import print_payment_receipt
            # Obtém as configurações da impressora
            company_info = CompanyInfo.query.first()
            printer_name = company_info.printer_name if company_info else None
            
            print_success = False
            print_success = print_payment_receipt(payment, customer, receivable, printer_name)
            
            if print_success:
                print("Cupom de pagamento impresso com sucesso!")
                success_message = "Pagamento registrado com sucesso. Cupom impresso."
            else:
                print("Não foi possível imprimir o cupom de pagamento.")
                # Tenta uma segunda vez com um pequeno atraso
                import time
                time.sleep(1)
                print_success = print_payment_receipt(payment, customer, receivable, printer_name)
                if print_success:
                    print("Cupom de pagamento impresso com sucesso na segunda tentativa!")
                    success_message = "Pagamento registrado com sucesso. Cupom impresso."
                else:
                    success_message = "Pagamento registrado com sucesso, mas não foi possível imprimir o cupom."
        except Exception as e:
            print(f"Erro ao imprimir cupom de pagamento: {str(e)}")
            import traceback
            traceback.print_exc()
            success_message = "Pagamento registrado com sucesso, mas ocorreu um erro ao imprimir o cupom."
        
        return jsonify({
            'success': True,
            'data': receivable.to_dict(),
            'message': success_message
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

@vendas_bp.route('/api/produtos/buscar')
@login_required
def search_product_pdv():
    """Busca produtos por código ou nome"""
    try:
        query = request.args.get('q')
        
        products = Product.query.filter(
            (Product.code.like(f'%{query}%')) | 
            (Product.name.like(f'%{query}%')) |
            (Product.barcode.like(f'%{query}%'))
        ).filter(Product.status == 'active').all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'price': float(product.selling_price),
                'stock': float(product.stock)
            })
        
        return jsonify({'success': True, 'products': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/api/produtos/buscar_produto')
@login_required
def search_product_ui():
    """Busca produtos por código ou nome para o UI"""
    try:
        query = request.args.get('q')
        
        produtos = Product.query.filter(
            (Product.code.like(f'%{query}%')) | 
            (Product.name.like(f'%{query}%')) |
            (Product.barcode.like(f'%{query}%'))
        ).all()
        
        return jsonify({
            'success': True,
            'products': [produto.to_dict() for produto in produtos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/api/clientes/<registration>')
@login_required
@non_cashier_required
def get_customer_by_registration(registration):
    """Retorna um cliente pela matrícula"""
    try:
        cliente = Customer.query.filter_by(registration=registration).first()
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'})
        
        # Calcula o limite disponível
        limite_disponivel = cliente.credit_limit - cliente.current_debt
        if limite_disponivel < 0:
            limite_disponivel = 0
        
        return jsonify({
            'success': True,
            'customer': {
                'id': cliente.id,
                'registration': cliente.registration,
                'name': cliente.name,
                'credit_limit': float(cliente.credit_limit),
                'current_debt': float(cliente.current_debt),
                'available_credit': float(limite_disponivel)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendas_bp.route('/api/sales/<int:id>')
@login_required
@non_cashier_required
def get_sale(id):
    """Busca os detalhes de uma venda"""
    try:
        sale = Sale.query.get(id)
        if not sale:
            return jsonify({
                'success': False,
                'error': 'Venda não encontrada'
            })
        
        # Converte a venda para dicionário
        sale_dict = sale.to_dict()
        
        # Adiciona os itens da venda
        items = []
        total = Decimal('0')
        
        for item in sale.items:
            item_dict = item.to_dict()
            items.append(item_dict)
            # Calcula o subtotal do item
            subtotal = safe_decimal(str(item.quantity)) * safe_decimal(str(item.price))
            item_dict['subtotal'] = float(subtotal)
            total += subtotal
        
        sale_dict['items'] = items
        sale_dict['total'] = float(total)
        
        # Adiciona as parcelas se for venda a prazo
        if sale.payment_method == 'crediario':
            sale_dict['receivables'] = [r.to_dict() for r in sale.receivables]
        
        return jsonify({
            'success': True,
            'data': sale_dict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@vendas_bp.route('/api/sales/<int:id>/print')
@login_required
@non_cashier_required
def print_sale(id):
    """Imprime uma venda específica"""
    try:
        # Busca a venda
        sale = Sale.query.get(id)
        if not sale:
            return jsonify({
                'success': False,
                'error': 'Venda não encontrada'
            }), 404
            
        # Busca as configurações da empresa
        company = CompanyInfo.query.first()
        if not company:
            return jsonify({
                'success': False,
                'error': 'Configurações da empresa não encontradas'
            }), 404
            
        # Tenta imprimir o cupom
        result = print_receipt(sale)
        
        return jsonify({
            'success': True,
            'message': 'Cupom enviado para impressão'
        })
        
    except Exception as e:
        print(f"Erro ao imprimir venda: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_bp.route('/api/vendas/autorizar', methods=['POST'])
@login_required
@non_cashier_required
def autorizar_venda():
    """Autoriza uma venda para cliente sem limite"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Busca o usuário
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            })
        
        # Verifica a senha
        if not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Senha incorreta'
            })
        
        # Verifica se o usuário tem permissão
        if user.role not in ['supervisor', 'gerente', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Usuário sem permissão para autorizar vendas'
            })
        
        return jsonify({
            'success': True,
            'message': 'Venda autorizada com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@vendas_bp.route('/api/vendas/finalizar', methods=['POST'])
@login_required
@non_cashier_required
def finalizar_venda():
    """Finaliza uma venda (API para o PDV moderno)"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({
                'success': False,
                'message': 'Nenhum item informado'
            })
        
        # Calcula o total da venda
        total_amount = safe_decimal(data.get('total_amount', 0))
        
        # Cria a venda
        sale = Sale(
            customer_id=data.get('customer_id'),
            payment_method=data.get('payment_method', 'dinheiro'),
            supervisor_id=current_user.id,
            user_id=current_user.id,  # Adiciona o usuário atual como operador
            total=total_amount,
            date=datetime.now()
        )
        
        # Associa a venda ao caixa aberto do operador
        try:
            # Busca o caixa aberto para o usuário atual
            hoje = datetime.today().date()
            caixa_aberto = CashRegister.query.filter(
                CashRegister.user_id == current_user.id,
                CashRegister.status == 'open',
                func.date(CashRegister.opening_date) == hoje
            ).first()
            
            if caixa_aberto:
                sale.cash_register_id = caixa_aberto.id
                print(f"Venda associada ao caixa ID: {caixa_aberto.id}")
            else:
                print("Nenhum caixa aberto encontrado para o operador atual!")
        except Exception as e:
            print(f"Erro ao associar venda ao caixa: {str(e)}")
            # Não interrompe o fluxo se falhar apenas a associação com o caixa
        
        db.session.add(sale)
        db.session.commit()
        
        # Adiciona os itens
        for item_data in data['items']:
            product_id = item_data['product_id']
            quantity = safe_decimal(item_data['quantity'])
            unit_price = safe_decimal(item_data['unit_price'])
            total = safe_decimal(item_data['total'])
            
            item = SaleItem(
                product_id=product_id,
                quantity=quantity,
                price=unit_price,
                subtotal=total
            )
            sale.items.append(item)
            
            # Atualiza o estoque
            product = Product.query.get(product_id)
            if product:
                product.stock_quantity -= quantity
        
        # Se for fiado, verifica o limite e cria conta a receber
        if data.get('payment_method') == 'fiado':
            if not data.get('customer_id'):
                return jsonify({
                    'success': False,
                    'message': 'Cliente não informado para venda fiado'
                })
            
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({
                    'success': False,
                    'message': 'Cliente não encontrado'
                })
            
            # Verifica se a venda foi autorizada, caso contrário verifica o limite
            if not data.get('authorized'):
                limite_disponivel = customer.credit_limit - customer.current_debt
                if total_amount > limite_disponivel:
                    return jsonify({
                        'success': False,
                        'message': 'Cliente não possui limite disponível'
                    })
            
            # Cria conta a receber
            receivable = Receivable(
                customer_id=data['customer_id'],
                date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                total_amount=total_amount,
                paid_amount=0,
                status='pending',
                description=f"Venda PDV - {datetime.now().strftime('%d/%m/%Y')}"
            )
            
            db.session.add(receivable)
            
            # Atualiza a dívida do cliente
            customer.current_debt += total_amount
        
        db.session.commit()
        
        # Cria o registro de pagamento (exceto para fiado)
        if data.get('payment_method') != 'fiado':
            payment = Payment(
                sale_id=sale.id,
                amount=total_amount,
                method=data['payment_method'],
                installments=data.get('installments', 1),
                status='confirmed'
            )
            db.session.add(payment)
            db.session.commit()
        
        # Imprime o cupom se configurado
        receipt_id = None
        try:
            company = CompanyInfo.query.first()
            if company and company.auto_print:
                receipt_id = sale.id
                print_receipt(sale)
        except Exception as e:
            print(f"Erro ao tentar imprimir: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Venda finalizada com sucesso',
            'sale_id': sale.id,
            'receipt_id': receipt_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@vendas_bp.route('/api/produtos/<codigo>')
@login_required
def get_product_by_code(codigo):
    """Retorna um produto pelo código"""
    try:
        produto = Product.query.filter_by(code=codigo).first()
        if not produto:
            return jsonify({'success': False, 'message': 'Produto não encontrado'})
        
        return jsonify({
            'success': True,
            'product': {
                'id': produto.id,
                'code': produto.code,
                'name': produto.name,
                'selling_price': float(produto.selling_price),
                'unit': produto.unit,
                'stock_quantity': float(produto.stock_quantity),
                'image_url': produto.image_url if hasattr(produto, 'image_url') else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendas_bp.route('/api/clientes/<matricula>')
@login_required
@non_cashier_required
def get_customer_modern(matricula):
    """Retorna um cliente pela matrícula"""
    try:
        cliente = Customer.query.filter_by(registration=matricula).first()
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'})
        
        # Calcula o limite disponível
        limite_disponivel = cliente.credit_limit - cliente.current_debt
        if limite_disponivel < 0:
            limite_disponivel = 0
        
        return jsonify({
            'success': True,
            'customer': {
                'id': cliente.id,
                'registration': cliente.registration,
                'name': cliente.name,
                'credit_limit': float(cliente.credit_limit),
                'current_debt': float(cliente.current_debt),
                'available_credit': float(limite_disponivel)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendas_bp.route('/api/auth/authorize', methods=['POST'])
@login_required
@non_cashier_required
def autorizar_venda_modern():
    """Autoriza uma venda para cliente sem limite"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Usuário e senha obrigatórios'
            })
        
        # Busca o usuário
        from werkzeug.security import check_password_hash
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'success': False,
                'message': 'Usuário ou senha inválidos'
            })
        
        # Verifica se o usuário tem permissão
        if user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'message': 'Usuário não tem permissão para autorizar'
            })
        
        return jsonify({
            'success': True,
            'message': 'Autorização concedida'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@vendas_bp.route('/api/contas_a_receber/cliente/<matricula>')
@login_required
@non_cashier_required
def get_customer_receivables(matricula):
    """Retorna as contas a receber de um cliente"""
    try:
        cliente = Customer.query.filter_by(registration=matricula).first()
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'})
        
        receivables = Receivable.query.filter_by(
            customer_id=cliente.id,
            status='pending'
        ).order_by(Receivable.due_date).all()
        
        return jsonify({
            'success': True,
            'receivables': [{
                'id': r.id,
                'date': r.date.strftime('%Y-%m-%d'),
                'due_date': r.due_date.strftime('%Y-%m-%d'),
                'total_amount': float(r.total_amount),
                'paid_amount': float(r.paid_amount),
                'status': r.status,
                'description': r.description
            } for r in receivables]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendas_bp.route('/api/contas_a_receber/<int:receivable_id>')
@login_required
@non_cashier_required
def get_receivable(receivable_id):
    """Retorna uma conta a receber pelo ID"""
    try:
        receivable = Receivable.query.get(receivable_id)
        if not receivable:
            return jsonify({'success': False, 'message': 'Conta a receber não encontrada'})
        
        return jsonify({
            'success': True,
            'receivable': {
                'id': receivable.id,
                'date': receivable.date.strftime('%Y-%m-%d'),
                'due_date': receivable.due_date.strftime('%Y-%m-%d'),
                'total_amount': float(receivable.total_amount),
                'paid_amount': float(receivable.paid_amount),
                'status': receivable.status,
                'description': receivable.description
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@vendas_bp.route('/api/contas_a_receber/<int:receivable_id>/pagar', methods=['POST'])
@login_required
def pay_receivable(receivable_id):
    """Registra um pagamento em uma conta a receber"""
    try:
        data = request.get_json()
        receivable = Receivable.query.get(receivable_id)
        if not receivable:
            return jsonify({'success': False, 'message': 'Conta a receber não encontrada'})
        
        payment_amount = safe_decimal(data.get('payment_amount', 0))
        payment_method = data.get('payment_method', 'dinheiro')
        
        if payment_amount <= 0:
            return jsonify({'success': False, 'message': 'Valor de pagamento inválido'})
        
        # Verifica se o valor não é maior que o restante
        valor_restante = receivable.total_amount - receivable.paid_amount
        if payment_amount > valor_restante:
            return jsonify({'success': False, 'message': 'Valor de pagamento maior que o valor restante'})
        
        # Registra o pagamento
        receivable_payment = ReceivablePayment(
            receivable_id=receivable.id,
            payment_date=datetime.now(),
            amount=payment_amount,
            payment_method=payment_method
        )
        
        # Atualiza a conta a receber
        receivable.paid_amount += payment_amount
        
        # Se foi pago totalmente, atualiza o status
        if receivable.paid_amount >= receivable.total_amount:
            receivable.status = 'paid'
        
        # Atualiza a dívida do cliente
        customer = Customer.query.get(receivable.customer_id)
        if customer:
            customer.current_debt -= payment_amount
        
        # Associa o pagamento ao caixa aberto do operador atual
        try:
            # Busca o caixa aberto para o usuário atual
            hoje = datetime.today().date()
            caixa_aberto = CashRegister.query.filter(
                CashRegister.user_id == current_user.id,
                CashRegister.status == 'open',
                func.date(CashRegister.opening_date) == hoje
            ).first()
            
            if not caixa_aberto:
                print("Alerta: Nenhum caixa aberto encontrado para registrar o pagamento de conta a receber!")
            else:
                print(f"Pagamento de conta a receber associado ao caixa ID: {caixa_aberto.id}")
                # Criar uma venda virtual para registrar o pagamento no caixa
                payment_sale = Sale(
                    customer_id=receivable.customer_id if receivable.customer_id else None,
                    payment_method=payment_method,
                    supervisor_id=current_user.id,
                    user_id=current_user.id,
                    total=payment_amount,
                    date=datetime.now(),
                    cash_register_id=caixa_aberto.id,
                    description=f"Pagamento de conta a receber #{receivable_id}"
                )
                db.session.add(payment_sale)
        except Exception as e:
            print(f"Erro ao associar pagamento de conta a receber ao caixa: {str(e)}")
            import traceback
            traceback.print_exc()
            # Não interrompe o fluxo se falhar apenas a associação com o caixa
        
        db.session.add(receivable_payment)
        db.session.commit()
        
        # Imprime o cupom de pagamento
        try:
            from utils.printer import print_payment_receipt
            # Obtém as configurações da impressora
            company_info = CompanyInfo.query.first()
            printer_name = company_info.printer_name if company_info else None
            
            print_success = False
            print_success = print_payment_receipt(receivable_payment, customer, receivable, printer_name)
            
            if print_success:
                print("Cupom de pagamento impresso com sucesso!")
                success_message = "Pagamento registrado com sucesso. Cupom impresso."
            else:
                print("Não foi possível imprimir o cupom de pagamento.")
                # Tenta uma segunda vez com um pequeno atraso
                import time
                time.sleep(1)
                print_success = print_payment_receipt(receivable_payment, customer, receivable, printer_name)
                if print_success:
                    print("Cupom de pagamento impresso com sucesso na segunda tentativa!")
                    success_message = "Pagamento registrado com sucesso. Cupom impresso."
                else:
                    success_message = "Pagamento registrado com sucesso, mas não foi possível imprimir o cupom."
        except Exception as e:
            print(f"Erro ao imprimir cupom de pagamento: {str(e)}")
            import traceback
            traceback.print_exc()
            success_message = "Pagamento registrado com sucesso, mas ocorreu um erro ao imprimir o cupom."
        
        return jsonify({
            'success': True,
            'message': success_message
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })
