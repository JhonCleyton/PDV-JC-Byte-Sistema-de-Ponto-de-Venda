from flask import Blueprint, render_template, request, redirect, url_for, flash
from promotions_models.promotions import Promotion
from models import db, Product
from datetime import datetime

bp = Blueprint('promotions', __name__, url_prefix='/promotions')

# API: Promoção ativa para produto
@bp.route('/api/promotions/active/<int:product_id>')
def get_active_promotion(product_id):
    now = datetime.utcnow()
    promo = Promotion.query.\
        filter(Promotion.active == True).\
        filter(Promotion.start_date <= now, Promotion.end_date >= now).\
        filter(Promotion.products.any(id=product_id)).\
        order_by(Promotion.discount_value.desc()).first()
    if promo:
        return {
            'success': True,
            'promotion': {
                'id': promo.id,
                'discount_type': promo.discount_type,
                'discount_value': promo.discount_value,
                'name': promo.name
            }
        }
    return {'success': True, 'promotion': None}


@bp.route('/')
def list_promotions():
    promotions = Promotion.query.order_by(Promotion.start_date.desc()).all()
    return render_template('promotions/list.html', promotions=promotions)

@bp.route('/create', methods=['GET', 'POST'])
def create_promotion():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        discount_type = request.form['discount_type']
        discount_value = float(request.form['discount_value'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        active = 'active' in request.form
        product_ids_str = request.form.get('products')
        product_ids = [int(pid) for pid in product_ids_str.split(',') if pid.strip()] if product_ids_str else []
        promo = Promotion(
            name=name,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            start_date=start_date,
            end_date=end_date,
            active=active
        )
        # Associar produtos selecionados
        if product_ids:
            selected_products = Product.query.filter(Product.id.in_(product_ids)).all()
            promo.products.extend(selected_products)
        db.session.add(promo)
        db.session.commit()
        flash('Promoção criada com sucesso!', 'success')
        return redirect(url_for('promotions.list_promotions'))
    # Para GET, buscar todos os produtos
    products = Product.query.order_by(Product.name).all()
    return render_template('promotions/create.html', products=products)

@bp.route('/<int:promo_id>/edit', methods=['GET', 'POST'])
def edit_promotion(promo_id):
    promo = Promotion.query.get_or_404(promo_id)
    if request.method == 'POST':
        promo.name = request.form['name']
        promo.description = request.form['description']
        promo.discount_type = request.form['discount_type']
        promo.discount_value = float(request.form['discount_value'])
        promo.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        promo.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        promo.active = 'active' in request.form
        # Atualizar associação de produtos
        product_ids_str = request.form.get('products')
        product_ids = [int(pid) for pid in product_ids_str.split(',') if pid.strip()] if product_ids_str else []
        if product_ids:
            selected_products = Product.query.filter(Product.id.in_(product_ids)).all()
            promo.products = selected_products
        else:
            promo.products = []
        db.session.commit()
        flash('Promoção atualizada!', 'success')
        return redirect(url_for('promotions.list_promotions'))
    # Para GET, buscar todos os produtos e os já selecionados
    products = Product.query.order_by(Product.name).all()
    selected_products = [p.id for p in promo.products]
    return render_template('promotions/edit.html', promo=promo, products=products, selected_products=selected_products)

@bp.route('/<int:promo_id>/delete', methods=['POST'])
def delete_promotion(promo_id):
    promo = Promotion.query.get_or_404(promo_id)
    db.session.delete(promo)
    db.session.commit()
    flash('Promoção removida!', 'success')
    return redirect(url_for('promotions.list_promotions'))
