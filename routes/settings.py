from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, CompanyInfo
import win32print
import win32con
from datetime import datetime
import logging
import traceback

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/company', methods=['GET'])
@login_required
def get_company_info():
    """Retorna as informações da empresa"""
    try:
        company = CompanyInfo.query.first()
        if not company:
            company = CompanyInfo()
            db.session.add(company)
            db.session.commit()
            
        return jsonify({
            'success': True,
            'data': company.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/company', methods=['POST'])
@login_required
def update_company_info():
    """Atualiza as informações da empresa"""
    try:
        data = request.get_json()
        company = CompanyInfo.query.first()
        
        if not company:
            company = CompanyInfo()
            db.session.add(company)
        
        # Atualiza os campos
        for field in ['name', 'cnpj', 'ie', 'phone', 'email', 'address', 'city', 'state', 'zip_code']:
            if field in data:
                setattr(company, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': company.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/printers', methods=['GET'])
@login_required
def get_printers():
    """Retorna a lista de impressoras instaladas"""
    try:
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printers.append(printer[2])
            
        return jsonify({
            'success': True,
            'printers': printers
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/receipt-config', methods=['GET'])
@login_required
def get_receipt_config():
    """Retorna as configurações do cupom"""
    try:
        company = CompanyInfo.query.first()
        if not company:
            company = CompanyInfo()
            # Define o rodapé padrão com o copyright em fonte pequena
            company.print_footer = "\n<small>JC Byte - Soluções em tecnologia</small>\n<small>Tel: (73) 99854-7885</small>"
            db.session.add(company)
            db.session.commit()
            
        return jsonify({
            'success': True,
            'data': {
                'printer_name': company.printer_name,
                'print_header': company.print_header,
                'print_footer': company.print_footer,
                'auto_print': company.auto_print
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/receipt-config', methods=['POST'])
@login_required
def update_receipt_config():
    """Atualiza as configurações do cupom"""
    try:
        data = request.get_json()
        company = CompanyInfo.query.first()
        
        if not company:
            company = CompanyInfo()
            db.session.add(company)
        
        # Atualiza os campos
        company.printer_name = data.get('printer_name', company.printer_name)
        company.print_header = data.get('print_header', company.print_header)
        company.print_footer = data.get('print_footer', company.print_footer)
        company.auto_print = data.get('auto_print', company.auto_print)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'printer_name': company.printer_name,
                'print_header': company.print_header,
                'print_footer': company.print_footer,
                'auto_print': company.auto_print
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/test-print', methods=['POST'])
@login_required
def test_print():
    """Imprime um cupom de teste"""
    try:
        # Log inicial
        logging.info("=== Iniciando rota de teste de impressão ===")
        
        # Obtém dados do request
        data = request.get_json()
        printer_name = data.get('printer_name')
        logging.info(f"Impressora selecionada: {printer_name}")
        
        if not printer_name:
            logging.error("Nome da impressora não informado")
            return jsonify({
                'success': False,
                'error': 'Nome da impressora não informado'
            }), 400
            
        # Tenta imprimir o cupom de teste
        try:
            from utils.printer import print_test
            logging.info("Chamando função print_test")
            result = print_test(printer_name)
            logging.info(f"Resultado do print_test: {result}")
            
            if result:
                return jsonify({
                    'success': True,
                    'message': 'Cupom de teste gerado com sucesso'
                })
            else:
                logging.error("print_test retornou False")
                return jsonify({
                    'success': False,
                    'error': 'Erro ao gerar cupom de teste. Verifique o arquivo printer.log para mais detalhes.'
                }), 500
                
        except Exception as e:
            logging.error(f"Erro ao chamar print_test: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Erro ao tentar imprimir: {str(e)}'
            }), 500
            
    except Exception as e:
        logging.error(f"Erro geral na rota: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/test_print', methods=['GET'])
def test_print_route():
    """Rota para testar a impressão"""
    try:
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        logging.info("=== INICIANDO TESTE DE IMPRESSÃO ===")
        
        from utils.printer import print_test, PRINTER_ENABLED
        import win32print
        import logging
        
        # Obtém a impressora padrão
        printer_name = None
        try:
            printer_name = win32print.GetDefaultPrinter()
            logging.info(f"Impressora padrão encontrada: {printer_name}")
        except Exception as e:
            logging.error(f"Erro ao obter impressora padrão: {str(e)}")
            
        if not printer_name:
            logging.error("Nenhuma impressora padrão configurada no sistema")
            return jsonify({"success": False, "error": "Nenhuma impressora padrão configurada no sistema"})
            
        if not PRINTER_ENABLED:
            logging.error("Impressão desativada nas configurações")
            return jsonify({"success": False, "error": "Impressão desativada nas configurações. Verifique as configurações do sistema."})
            
        # Tenta imprimir um cupom de teste
        logging.info(f"Iniciando impressão de teste para a impressora: {printer_name}")
        result = print_test(printer_name)
        
        if result:
            logging.info("Impressão de teste concluída com sucesso")
            return jsonify({"success": True, "message": f"Impressão de teste enviada para a impressora: {printer_name}"})
        else:
            logging.error("Falha no teste de impressão")
            return jsonify({"success": False, "error": "Falha ao imprimir o cupom de teste. Verifique os logs para mais detalhes."})
            
    except Exception as e:
        import traceback
        logging.error(f"Erro no teste de impressão: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"Erro no teste de impressão: {str(e)}"})
