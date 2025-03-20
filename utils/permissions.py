from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def admin_required(f):
    """
    Decorator que restringe o acesso apenas a usuários com papel de admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'admin':
            flash('Acesso negado. Você precisa ser administrador para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def non_cashier_required(f):
    """
    Decorator que restringe o acesso a usuários que NÃO são do tipo caixa
    Qualquer usuário que não seja caixa pode acessar (admin, manager, etc.)
    
    Se o usuário for do tipo 'caixa', redireciona para a página do PDV Professional
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role == 'caixa':
            return redirect(url_for('vendas.create_professional'))
        return f(*args, **kwargs)
    return decorated_function

def cashier_or_admin_required(f):
    """
    Decorator que permite acesso por usuários do tipo caixa ou admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['caixa', 'admin']:
            flash('Acesso negado. Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
