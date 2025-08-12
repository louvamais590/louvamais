from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.escala import db, Escala

escala_bp = Blueprint('escala', __name__)

@escala_bp.route('/escalas', methods=['GET'])
def listar_escalas():
    """Lista todas as escalas ordenadas por data"""
    try:
        # Parâmetros de filtro opcionais
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        query = Escala.query
        
        if mes and ano:
            # Filtrar por mês e ano
            inicio_mes = datetime(ano, mes, 1).date()
            if mes == 12:
                fim_mes = datetime(ano + 1, 1, 1).date() - timedelta(days=1)
            else:
                fim_mes = datetime(ano, mes + 1, 1).date() - timedelta(days=1)
            
            query = query.filter(Escala.data >= inicio_mes, Escala.data <= fim_mes)
        elif ano:
            # Filtrar apenas por ano
            inicio_ano = datetime(ano, 1, 1).date()
            fim_ano = datetime(ano, 12, 31).date()
            query = query.filter(Escala.data >= inicio_ano, Escala.data <= fim_ano)
        
        escalas = query.order_by(Escala.data).all()
        
        return jsonify({
            'success': True,
            'escalas': [escala.to_dict() for escala in escalas],
            'total': len(escalas)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>', methods=['GET'])
def obter_escala(escala_id):
    """Obtém uma escala específica por ID"""
    try:
        escala = Escala.query.get_or_404(escala_id)
        return jsonify({
            'success': True,
            'escala': escala.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas', methods=['POST'])
def criar_escala():
    """Cria uma nova escala"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('data') or not data.get('dia_semana'):
            return jsonify({
                'success': False,
                'error': 'Data e dia da semana são obrigatórios'
            }), 400
        
        # Converter string de data para objeto date
        data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
        
        # Verificar se já existe escala para esta data
        escala_existente = Escala.query.filter_by(data=data_obj).first()
        if escala_existente:
            return jsonify({
                'success': False,
                'error': 'Já existe uma escala para esta data'
            }), 400
        
        # Criar nova escala
        nova_escala = Escala(
            data=data_obj,
            dia_semana=data['dia_semana'],
            pregacao=data.get('pregacao'),
            equipe_musicos=data.get('equipe_musicos'),
            conducao_animacao=data.get('conducao_animacao'),
            acolhida=data.get('acolhida'),
            responsavel_abastecimento=data.get('responsavel_abastecimento')
        )
        
        db.session.add(nova_escala)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'escala': nova_escala.to_dict(),
            'message': 'Escala criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>', methods=['PUT'])
def atualizar_escala(escala_id):
    """Atualiza uma escala existente"""
    try:
        escala = Escala.query.get_or_404(escala_id)
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'pregacao' in data:
            escala.pregacao = data['pregacao']
        if 'equipe_musicos' in data:
            escala.equipe_musicos = data['equipe_musicos']
        if 'conducao_animacao' in data:
            escala.conducao_animacao = data['conducao_animacao']
        if 'acolhida' in data:
            escala.acolhida = data['acolhida']
        if 'responsavel_abastecimento' in data:
            escala.responsavel_abastecimento = data['responsavel_abastecimento']
        
        escala.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'escala': escala.to_dict(),
            'message': 'Escala atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>', methods=['DELETE'])
def deletar_escala(escala_id):
    """Deleta uma escala"""
    try:
        escala = Escala.query.get_or_404(escala_id)
        
        db.session.delete(escala)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Escala deletada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/inicializar', methods=['POST'])
def inicializar_escalas():
    """Inicializa as escalas com todas as datas até o final de 2025"""
    try:
        # Verificar se já existem escalas
        escalas_existentes = Escala.query.count()
        if escalas_existentes > 0:
            return jsonify({
                'success': False,
                'error': 'Já existem escalas cadastradas. Use o endpoint de atualização individual.'
            }), 400
        
        # Gerar datas como no script original
        hoje = datetime.now()
        
        # Encontrar a próxima terça (weekday 1) ou quarta (weekday 2)
        dias_ate_terca = (1 - hoje.weekday()) % 7
        dias_ate_quarta = (2 - hoje.weekday()) % 7
        
        if dias_ate_terca == 0 and hoje.hour >= 19:
            dias_ate_terca = 7
        if dias_ate_quarta == 0 and hoje.hour >= 19:
            dias_ate_quarta = 7
            
        proxima_terca = hoje + timedelta(days=dias_ate_terca)
        proxima_quarta = hoje + timedelta(days=dias_ate_quarta)
        
        # Data final - 31 de dezembro de 2025
        data_final = datetime(2025, 12, 31)
        
        escalas_criadas = []
        
        # Gerar todas as terças
        data_atual = proxima_terca
        while data_atual.date() <= data_final.date():
            escala = Escala(
                data=data_atual.date(),
                dia_semana='Terça-feira'
            )
            escalas_criadas.append(escala)
            data_atual += timedelta(days=7)
        
        # Gerar todas as quartas
        data_atual = proxima_quarta
        while data_atual.date() <= data_final.date():
            escala = Escala(
                data=data_atual.date(),
                dia_semana='Quarta-feira'
            )
            escalas_criadas.append(escala)
            data_atual += timedelta(days=7)
        
        # Salvar todas as escalas
        db.session.add_all(escalas_criadas)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(escalas_criadas)} escalas inicializadas com sucesso',
            'total_escalas': len(escalas_criadas)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Obtém estatísticas das escalas"""
    try:
        total_escalas = Escala.query.count()
        total_tercas = Escala.query.filter_by(dia_semana='Terça-feira').count()
        total_quartas = Escala.query.filter_by(dia_semana='Quarta-feira').count()
        
        # Escalas preenchidas (pelo menos um campo não vazio)
        escalas_preenchidas = Escala.query.filter(
            (Escala.pregacao.isnot(None) & (Escala.pregacao != '')) |
            (Escala.equipe_musicos.isnot(None) & (Escala.equipe_musicos != '')) |
            (Escala.conducao_animacao.isnot(None) & (Escala.conducao_animacao != '')) |
            (Escala.acolhida.isnot(None) & (Escala.acolhida != '')) |
            (Escala.responsavel_abastecimento.isnot(None) & (Escala.responsavel_abastecimento != ''))
        ).count()
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_escalas': total_escalas,
                'total_tercas': total_tercas,
                'total_quartas': total_quartas,
                'escalas_preenchidas': escalas_preenchidas,
                'escalas_vazias': total_escalas - escalas_preenchidas
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



# ===== ROTAS PARA GERENCIAR PESSOAS NAS ESCALAS =====

@escala_bp.route('/escalas/<int:escala_id>/pessoas', methods=['GET'])
def listar_pessoas_escala(escala_id):
    """Lista todas as pessoas de uma escala específica"""
    try:
        escala = Escala.query.get_or_404(escala_id)
        
        # Organizar pessoas por função
        pessoas_por_funcao = {}
        for ep in escala.pessoas:
            if ep.funcao not in pessoas_por_funcao:
                pessoas_por_funcao[ep.funcao] = []
            pessoas_por_funcao[ep.funcao].append(ep.to_dict())
        
        return jsonify({
            'success': True,
            'escala_id': escala_id,
            'pessoas_por_funcao': pessoas_por_funcao
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>/pessoas', methods=['POST'])
def adicionar_pessoa_escala(escala_id):
    """Adiciona uma pessoa a uma função específica da escala"""
    try:
        from src.models.escala_pessoa import EscalaPessoa
        from src.models.pessoa import Pessoa
        
        escala = Escala.query.get_or_404(escala_id)
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('pessoa_id') or not data.get('funcao'):
            return jsonify({
                'success': False,
                'error': 'pessoa_id e funcao são obrigatórios'
            }), 400
        
        pessoa_id = data['pessoa_id']
        funcao = data['funcao']
        
        # Verificar se a pessoa existe
        pessoa = Pessoa.query.get(pessoa_id)
        if not pessoa:
            return jsonify({
                'success': False,
                'error': 'Pessoa não encontrada'
            }), 404
        
        # Verificar se já existe esta pessoa nesta função desta escala
        escala_pessoa_existente = EscalaPessoa.query.filter_by(
            escala_id=escala_id,
            pessoa_id=pessoa_id,
            funcao=funcao
        ).first()
        
        if escala_pessoa_existente:
            return jsonify({
                'success': False,
                'error': 'Esta pessoa já está escalada para esta função'
            }), 400
        
        # Verificar limite de 10 pessoas por função
        pessoas_na_funcao = EscalaPessoa.query.filter_by(
            escala_id=escala_id,
            funcao=funcao
        ).count()
        
        if pessoas_na_funcao >= 10:
            return jsonify({
                'success': False,
                'error': 'Limite máximo de 10 pessoas por função atingido'
            }), 400
        
        # Criar nova associação
        nova_escala_pessoa = EscalaPessoa(
            escala_id=escala_id,
            pessoa_id=pessoa_id,
            funcao=funcao,
            confirmado=data.get('confirmado', False),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(nova_escala_pessoa)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'escala_pessoa': nova_escala_pessoa.to_dict(),
            'message': 'Pessoa adicionada à escala com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>/pessoas/<int:pessoa_id>/<funcao>', methods=['DELETE'])
def remover_pessoa_escala(escala_id, pessoa_id, funcao):
    """Remove uma pessoa de uma função específica da escala"""
    try:
        from src.models.escala_pessoa import EscalaPessoa
        
        escala_pessoa = EscalaPessoa.query.filter_by(
            escala_id=escala_id,
            pessoa_id=pessoa_id,
            funcao=funcao
        ).first()
        
        if not escala_pessoa:
            return jsonify({
                'success': False,
                'error': 'Pessoa não encontrada nesta função da escala'
            }), 404
        
        db.session.delete(escala_pessoa)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pessoa removida da escala com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@escala_bp.route('/escalas/<int:escala_id>/pessoas/funcao', methods=['PUT'])
def atualizar_pessoas_funcao(escala_id):
    """Atualiza todas as pessoas de uma função específica da escala"""
    try:
        from src.models.escala_pessoa import EscalaPessoa
        from src.models.pessoa import Pessoa
        
        escala = Escala.query.get_or_404(escala_id)
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('funcao') or 'pessoas_ids' not in data:
            return jsonify({
                'success': False,
                'error': 'funcao e pessoas_ids são obrigatórios'
            }), 400
        
        funcao = data['funcao']
        pessoas_ids = data['pessoas_ids']
        
        # Validar limite de 10 pessoas
        if len(pessoas_ids) > 10:
            return jsonify({
                'success': False,
                'error': 'Máximo de 10 pessoas por função'
            }), 400
        
        # Remover todas as pessoas existentes desta função
        EscalaPessoa.query.filter_by(
            escala_id=escala_id,
            funcao=funcao
        ).delete()
        
        # Adicionar novas pessoas
        for pessoa_id in pessoas_ids:
            # Verificar se a pessoa existe
            pessoa = Pessoa.query.get(pessoa_id)
            if pessoa and pessoa.ativo:
                nova_escala_pessoa = EscalaPessoa(
                    escala_id=escala_id,
                    pessoa_id=pessoa_id,
                    funcao=funcao,
                    confirmado=False
                )
                db.session.add(nova_escala_pessoa)
        
        db.session.commit()
        
        # Retornar escala atualizada
        escala_atualizada = Escala.query.get(escala_id)
        
        return jsonify({
            'success': True,
            'escala': escala_atualizada.to_dict(),
            'message': f'Função {funcao} atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

