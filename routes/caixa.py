from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user
from models import db, CashRegister, CashWithdrawal, User, Sale, Payment
from datetime import datetime, timedelta
from pytz import timezone
from decimal import Decimal
from sqlalchemy import func, and_, or_
from utils.permissions import non_cashier_required
from utils.printer import print_cash_report

caixa_bp = Blueprint('caixa', __name__, url_prefix='/caixa')

@caixa_bp.route('/verificar')
@login_required
def verificar_caixa():
    """Verifica se existe um caixa aberto para o usuário atual"""
    try:
        # Verifica se o usuário é um caixa
        if current_user.role != 'caixa':
            return jsonify({'success': True, 'caixa_aberto': True})
            
        # Busca o caixa aberto para o usuário atual
        hoje = datetime.today().date()
        caixa_aberto = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open',
            func.date(CashRegister.opening_date) == hoje
        ).first()
        
        return jsonify({
            'success': True,
            'caixa_aberto': bool(caixa_aberto),
            'caixa': caixa_aberto.to_dict() if caixa_aberto else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/abrir', methods=['POST'])
@login_required
def abrir_caixa():
    """Abre o caixa para o usuário atual"""
    try:
        data = request.get_json()
        valor_inicial = data.get('valor_inicial', 0)
        
        # Verifica se já existe um caixa aberto para o usuário hoje
        hoje = datetime.today().date()
        caixa_existente = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open',
            func.date(CashRegister.opening_date) == hoje
        ).first()
        
        if caixa_existente:
            return jsonify({
                'success': False, 
                'error': 'Já existe um caixa aberto para este usuário hoje'
            })
        
        # Cria um novo registro de caixa
        novo_caixa = CashRegister(
            user_id=current_user.id,
            opening_amount=valor_inicial,
            opening_date=datetime.now(timezone('America/Sao_Paulo')),
            status='open'
        )
        
        db.session.add(novo_caixa)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'caixa': novo_caixa.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/fechar', methods=['POST'])
@login_required
def fechar_caixa():
    """Fecha o caixa aberto para o usuário atual"""
    try:
        data = request.get_json()
        valor_final = data.get('valor_final', 0)
        
        # Busca o caixa aberto para o usuário atual
        caixa = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open'
        ).first()
        
        if not caixa:
            return jsonify({
                'success': False,
                'error': 'Não existe caixa aberto para este usuário'
            })
        
        # Fecha o caixa
        caixa.close(valor_final)
        db.session.commit()
        
        # Gera o relatório de fechamento
        relatorio = gerar_relatorio_caixa(caixa.id)
        
        # Imprime o relatório
        print_cash_report(relatorio)
        
        return jsonify({
            'success': True,
            'caixa': caixa.to_dict(),
            'relatorio': relatorio,
            'caixa_id': caixa.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/retirada', methods=['POST'])
@login_required
def retirada_caixa():
    """Registra uma retirada de dinheiro do caixa"""
    try:
        data = request.get_json()
        valor = data.get('valor', 0)
        motivo = data.get('motivo', '')
        senha = data.get('senha', '')
        id_autorizador = data.get('autorizador_id')
        
        # Verifica se o usuário atual é um caixa
        if current_user.role != 'caixa':
            # Se não for caixa, é um gerente ou admin autorizando sua própria retirada
            autorizador = current_user
        else:
            # Se for caixa, precisa de um gerente/admin para autorizar
            if not id_autorizador:
                return jsonify({
                    'success': False,
                    'error': 'É necessário um gerente ou administrador para autorizar a retirada'
                })
            
            autorizador = User.query.get(id_autorizador)
            if not autorizador:
                return jsonify({
                    'success': False,
                    'error': 'Usuário autorizador não encontrado'
                })
            
            # Verifica se o autorizador é um gerente ou admin
            if autorizador.role not in ['admin', 'gerente', 'manager']:
                return jsonify({
                    'success': False,
                    'error': 'Apenas gerentes ou administradores podem autorizar retiradas'
                })
            
            # Verifica a senha do autorizador
            if not autorizador.verify_password(senha):
                return jsonify({
                    'success': False,
                    'error': 'Senha incorreta'
                })
        
        # Busca o caixa aberto
        caixa = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open'
        ).first()
        
        if not caixa:
            return jsonify({
                'success': False,
                'error': 'Não existe caixa aberto'
            })
        
        # Cria o registro de retirada
        retirada = CashWithdrawal(
            cash_register_id=caixa.id,
            authorizer_id=autorizador.id,
            amount=valor,
            reason=motivo,
            date=datetime.now()
        )
        
        db.session.add(retirada)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'retirada': retirada.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/relatorio/<int:caixa_id>')
@login_required
def relatorio_caixa(caixa_id):
    """Gera e exibe um relatório detalhado do caixa"""
    try:
        # Log inicial
        print(f"[RELATORIO] Iniciando geração de relatório para caixa ID {caixa_id}")
        
        # Verifica se o usuário tem permissão para ver o relatório
        if current_user.role == 'caixa':
            # Caixas só podem ver seus próprios relatórios
            caixa = CashRegister.query.filter_by(id=caixa_id, user_id=current_user.id).first()
            print(f"[RELATORIO] Usuário com papel 'caixa', verificando permissão: {caixa is not None}")
        else:
            # Admins e gerentes podem ver qualquer relatório
            caixa = CashRegister.query.get(caixa_id)
            print(f"[RELATORIO] Usuário admin/gerente, buscando caixa: {caixa is not None}")
        
        if not caixa:
            print(f"[RELATORIO] Caixa não encontrado ou permissão negada para ID {caixa_id}")
            flash('Caixa não encontrado ou você não tem permissão para acessá-lo', 'danger')
            return redirect(url_for('index'))
        
        print(f"[RELATORIO] Gerando relatório para caixa ID {caixa_id}")
        relatorio = gerar_relatorio_caixa(caixa_id)
        print(f"[RELATORIO] Relatório gerado com sucesso: {relatorio is not None}")
        
        print(f"[RELATORIO] Renderizando template relatorio.html")
        return render_template(
            'caixa/relatorio.html',
            caixa=caixa,
            relatorio=relatorio
        )
    except Exception as e:
        print(f"[RELATORIO] ERRO: {str(e)}")
        import traceback
        print(f"[RELATORIO] Traceback: {traceback.format_exc()}")
        flash(f'Erro ao gerar relatório: {str(e)}', 'danger')
        return redirect(url_for('index'))

@caixa_bp.route('/imprimir/<int:caixa_id>')
@login_required
def imprimir_relatorio(caixa_id):
    """Imprime o relatório do caixa"""
    try:
        # Verifica se o usuário tem permissão para imprimir o relatório
        if current_user.role == 'caixa':
            # Caixas só podem imprimir seus próprios relatórios
            caixa = CashRegister.query.filter_by(id=caixa_id, user_id=current_user.id).first()
        else:
            # Admins e gerentes podem imprimir qualquer relatório
            caixa = CashRegister.query.get(caixa_id)
        
        if not caixa:
            return jsonify({
                'success': False,
                'error': 'Caixa não encontrado ou você não tem permissão para acessá-lo'
            })
        
        relatorio = gerar_relatorio_caixa(caixa_id)
        
        # Imprime o relatório
        print_cash_report(relatorio)
        
        return jsonify({
            'success': True,
            'message': 'Relatório enviado para impressão'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/listar')
@login_required
@non_cashier_required
def listar_caixas():
    """Lista todos os caixas para administradores e gerentes"""
    try:
        # Busca todos os caixas (limitados por data se fornecida)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = CashRegister.query
        
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(CashRegister.opening_date >= data_inicio)
        
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim = data_fim + timedelta(days=1)  # Para incluir o último dia
            query = query.filter(CashRegister.opening_date < data_fim)
        
        caixas = query.order_by(CashRegister.opening_date.desc()).all()
        
        # Atualiza os valores esperados para caixas fechados sem valor esperado
        for caixa in caixas:
            if caixa.status == 'closed' and (caixa.expected_amount is None or caixa.expected_amount == 0):
                # Calcula o valor esperado
                expected = caixa.calculate_expected_amount()
                caixa.expected_amount = expected
                # Recalcula a diferença
                if caixa.closing_amount:
                    caixa.difference = caixa.closing_amount - expected
                db.session.add(caixa)
        
        db.session.commit()
        
        return render_template('caixa/listar.html', caixas=caixas)
    except Exception as e:
        flash(f'Erro ao listar caixas: {str(e)}', 'danger')
        return redirect(url_for('index'))

@caixa_bp.route('/remind')
@login_required
def verificar_lembrete():
    """Verifica se deve mostrar o lembrete de fechamento de caixa"""
    try:
        # Verifica se o usuário é um caixa
        if current_user.role != 'caixa':
            return jsonify({'success': True, 'mostrar_lembrete': False})
        
        # Busca o caixa aberto para o usuário atual
        caixa = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open'
        ).first()
        
        if not caixa:
            return jsonify({'success': True, 'mostrar_lembrete': False})
        
        # Verifica se o caixa está aberto há mais de 4 horas
        agora = datetime.now()
        diff = agora - caixa.opening_date
        mostrar_lembrete = diff.total_seconds() > 4 * 60 * 60  # 4 horas em segundos
        
        return jsonify({
            'success': True,
            'mostrar_lembrete': mostrar_lembrete,
            'tempo_aberto': int(diff.total_seconds() / 60)  # minutos
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/verificar-aberto')
@login_required
def verificar_caixa_aberto():
    """Verifica se existe um caixa aberto para o usuário atual (usado pelo JavaScript)"""
    try:
        # Verifica se o usuário é um caixa
        if current_user.role != 'caixa':
            return jsonify({
                'success': True, 
                'aberto': True,
                'caixa_id': 0,  # ID especial para indicar que não é um caixa real
                'hora_abertura': datetime.now().isoformat()
            })
            
        # Busca o caixa aberto para o usuário atual
        caixa_aberto = CashRegister.query.filter(
            CashRegister.user_id == current_user.id,
            CashRegister.status == 'open'
        ).first()
        
        return jsonify({
            'success': True,
            'aberto': bool(caixa_aberto),
            'caixa_id': caixa_aberto.id if caixa_aberto else None,
            'hora_abertura': caixa_aberto.opening_date.isoformat() if caixa_aberto else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/fechar/<int:caixa_id>', methods=['POST'])
@login_required
def fechar_caixa_especifico(caixa_id):
    """Fecha um caixa específico pelo ID"""
    try:
        data = request.get_json()
        valor_final = data.get('valor_final', 0)
        
        # Busca o caixa
        caixa = CashRegister.query.get(caixa_id)
        
        if not caixa:
            return jsonify({
                'success': False,
                'error': 'Caixa não encontrado'
            })
        
        # Verifica permissão
        if current_user.role == 'caixa' and caixa.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Você não tem permissão para fechar este caixa'
            })
        
        # Fecha o caixa
        caixa.closing_date = datetime.now()
        caixa.closing_amount = valor_final
        
        # Calcula o valor esperado (inicial + vendas em dinheiro - retiradas)
        vendas_dinheiro = db.session.query(func.sum(Payment.amount)).join(Sale).filter(
            Sale.cash_register_id == caixa_id,
            Payment.method == 'dinheiro'
        ).scalar() or 0
        
        retiradas = db.session.query(func.sum(CashWithdrawal.amount)).filter(
            CashWithdrawal.cash_register_id == caixa_id
        ).scalar() or 0
        
        caixa.expected_amount = float(caixa.opening_amount) + float(vendas_dinheiro) - float(retiradas)
        caixa.difference = float(valor_final) - float(caixa.expected_amount)
        caixa.status = 'closed'
        
        db.session.commit()
        
        # Gera o relatório para retornar ao JavaScript
        relatorio = gerar_relatorio_caixa(caixa_id)
        
        return jsonify({
            'success': True,
            'caixa_id': caixa_id,
            'relatorio': relatorio
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/retirada/<int:caixa_id>', methods=['POST'])
@login_required
def retirada_caixa_especifico(caixa_id):
    """Registra uma retirada de dinheiro de um caixa específico"""
    try:
        data = request.get_json()
        valor = data.get('valor', 0)
        motivo = data.get('motivo', '')
        senha = data.get('senha', '')
        autorizador_id = data.get('autorizador_id')
        
        # Busca o caixa
        caixa = CashRegister.query.get(caixa_id)
        if not caixa:
            return jsonify({
                'success': False,
                'error': 'Caixa não encontrado'
            })
        
        # Verifica permissão
        if current_user.role == 'caixa' and caixa.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Você não tem permissão para realizar retiradas deste caixa'
            })
        
        # Busca o autorizador
        autorizador = User.query.get(autorizador_id)
        if not autorizador:
            return jsonify({
                'success': False,
                'error': 'Autorizador não encontrado'
            })
        
        # Verifica se é um autorizador válido
        if autorizador.role not in ['admin', 'gerente', 'manager']:
            return jsonify({
                'success': False,
                'error': 'Apenas gerentes e administradores podem autorizar retiradas'
            })
        
        # Verifica a senha
        if not autorizador.verify_password(senha):
            return jsonify({
                'success': False,
                'error': 'Senha incorreta'
            })
        
        # Cria a retirada
        retirada = CashWithdrawal(
            cash_register_id=caixa_id,
            authorizer_id=autorizador_id,
            amount=valor,
            reason=motivo,
            date=datetime.now()
        )
        
        db.session.add(retirada)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Retirada realizada com sucesso',
            'retirada': retirada.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/listar_autorizadores')
@login_required
def listar_autorizadores():
    """Lista todos os usuários que podem autorizar retiradas (gerentes e admins)"""
    try:
        autorizadores = User.query.filter(User.role.in_(['admin', 'gerente', 'manager'])).all()
        
        return jsonify({
            'success': True,
            'autorizadores': [
                {'id': a.id, 'name': a.name} for a in autorizadores
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/autorizadores')
@login_required
def buscar_autorizadores():
    """Lista todos os usuários que podem autorizar retiradas (gerentes e admins)"""
    try:
        autorizadores = User.query.filter(User.role.in_(['admin', 'gerente', 'manager'])).all()
        
        return jsonify({
            'success': True,
            'autorizadores': [
                {'id': a.id, 'name': a.name} for a in autorizadores
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@caixa_bp.route('/corrigir-vendas')
@login_required
def corrigir_vendas_sem_caixa():
    """
    Corrige as vendas que não estão associadas a um caixa.
    Esta rota vai buscar todas as vendas sem caixa e tentar associá-las ao caixa correto
    com base no operador da venda.
    """
    try:
        # Obter todas as vendas que não estão associadas a um caixa
        vendas_sem_caixa = db.session.query(Sale).filter(Sale.cash_register_id == None).all()
        
        total_vendas = len(vendas_sem_caixa)
        vendas_corrigidas = 0
        
        for venda in vendas_sem_caixa:
            # Tentar encontrar o caixa aberto pelo operador no dia da venda
            operador_id = venda.user_id
            data_venda = venda.created_at
            
            # Buscar o caixa aberto pelo operador na data da venda
            caixa = db.session.query(CashRegister).filter(
                CashRegister.user_id == operador_id,
                CashRegister.opening_date <= data_venda,
                CashRegister.closing_date >= data_venda
            ).first()
            
            # Se não encontrou, buscar qualquer caixa aberto na data da venda
            if not caixa:
                caixa = db.session.query(CashRegister).filter(
                    CashRegister.opening_date <= data_venda,
                    CashRegister.closing_date >= data_venda
                ).first()
            
            # Se encontrou um caixa, associar a venda a ele
            if caixa:
                venda.cash_register_id = caixa.id
                vendas_corrigidas += 1
        
        # Salvar as alterações no banco de dados
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Foram corrigidas {vendas_corrigidas} de {total_vendas} vendas sem caixa.',
            'total_vendas_sem_caixa': total_vendas,
            'vendas_corrigidas': vendas_corrigidas
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        })

def gerar_relatorio_caixa(caixa_id):
    """Gera um relatório detalhado do caixa"""
    caixa = CashRegister.query.get(caixa_id)
    if not caixa:
        raise Exception('Caixa não encontrado')
    
    # Busca as vendas do caixa
    vendas = Sale.query.filter_by(cash_register_id=caixa_id).all()
    
    # Informações básicas
    relatorio = {
        'caixa': caixa.to_dict(),
        'usuario': caixa.user.name if caixa.user else 'Desconhecido',
        'data_abertura': caixa.opening_date.strftime('%d/%m/%Y %H:%M:%S'),
        'data_fechamento': caixa.closing_date.strftime('%d/%m/%Y %H:%M:%S') if caixa.closing_date else 'Em aberto',
        'status': 'Fechado' if caixa.status == 'closed' else 'Aberto',
        'valor_inicial': float(caixa.opening_amount),
        'valor_final': float(caixa.closing_amount) if caixa.closing_amount else 0,
        'valor_esperado': float(caixa.expected_amount) if caixa.expected_amount else 0,
        'diferenca': float(caixa.difference) if caixa.difference else 0,
        
        # Contadores
        'total_vendas': 0,
        'valor_total_vendas': 0,
        
        # Meios de pagamento
        'vendas_dinheiro': 0,
        'vendas_pix': 0,
        'vendas_credito': 0,
        'vendas_debito': 0,
        'vendas_crediario': 0,
        'vendas_ticket_alimentacao': 0,
        
        # Pagamentos de dívidas
        'pagamentos_divida': 0,
        'pagamentos_divida_dinheiro': 0,
        'pagamentos_divida_outros': 0,
        
        # Retiradas
        'retiradas': [retirada.to_dict() for retirada in caixa.withdrawals],
        'total_retiradas': sum([float(retirada.amount) for retirada in caixa.withdrawals]),
        
        # Recebimentos
        'recebimentos': [],
        'total_recebimentos': 0,
        'total_recebimentos_dinheiro': 0,
        'total_recebimentos_outros': 0,
    }
    
    # Processamento das vendas, separando vendas normais dos pagamentos de dívida
    vendas_normais = []
    pagamentos_divida = []
    
    for venda in vendas:
        if venda.description and ('Pagamento de dívida' in venda.description or 'Pagamento de conta a receber' in venda.description):
            pagamentos_divida.append(venda)
        else:
            vendas_normais.append(venda)
    
    # Cálculos para vendas normais
    relatorio['total_vendas'] = len(vendas_normais)
    relatorio['valor_total_vendas'] = sum([float(venda.total) for venda in vendas_normais])
    
    # Vendas por meio de pagamento
    relatorio['vendas_dinheiro'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'dinheiro'])
    relatorio['vendas_pix'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'pix'])
    relatorio['vendas_credito'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'cartao_credito'])
    relatorio['vendas_debito'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'cartao_debito'])
    relatorio['vendas_crediario'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'crediario'])
    relatorio['vendas_ticket_alimentacao'] = sum([float(venda.total) for venda in vendas_normais if venda.payment_method == 'ticket_alimentacao'])
    
    # Cálculos para pagamentos de dívida
    relatorio['pagamentos_divida'] = sum([float(pagamento.total) for pagamento in pagamentos_divida])
    relatorio['pagamentos_divida_dinheiro'] = sum([float(pagamento.total) for pagamento in pagamentos_divida if pagamento.payment_method == 'dinheiro'])
    relatorio['pagamentos_divida_outros'] = sum([float(pagamento.total) for pagamento in pagamentos_divida if pagamento.payment_method != 'dinheiro'])
    
    # Cálculo correto do valor esperado no caixa
    if caixa.status == 'closed':
        valor_inicial = float(caixa.opening_amount)
        entradas_dinheiro = relatorio['vendas_dinheiro'] + relatorio['pagamentos_divida_dinheiro']
        retiradas = relatorio['total_retiradas']
        
        # Valor esperado = Valor inicial + Entradas em dinheiro - Retiradas
        valor_esperado = valor_inicial + entradas_dinheiro - retiradas
        relatorio['valor_esperado'] = round(valor_esperado, 2)
        
        # Recalcula diferença
        relatorio['diferenca'] = round(float(caixa.closing_amount) - valor_esperado, 2)
    
    return relatorio
