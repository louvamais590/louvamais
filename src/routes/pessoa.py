from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.pessoa import Pessoa, Equipe, PessoaEquipe
from src.models.escala_pessoa import EscalaPessoa
from sqlalchemy import or_

pessoa_bp = Blueprint('pessoa', __name__)

# ===== ROTAS PARA PESSOAS =====

@pessoa_bp.route('/pessoas', methods=['GET'])
def listar_pessoas():
    """Lista todas as pessoas"""
    try:
        # Parâmetros de filtro opcionais
        busca = request.args.get('busca', '')
        equipe_id = request.args.get('equipe_id', type=int)
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        
        query = Pessoa.query.filter_by(ativo=ativo)
        
        if busca:
            query = query.filter(
                or_(
                    Pessoa.nome.ilike(f'%{busca}%'),
                    Pessoa.email.ilike(f'%{busca}%'),
                    Pessoa.telefone.ilike(f'%{busca}%')
                )
            )
        
        if equipe_id:
            query = query.join(PessoaEquipe).filter(PessoaEquipe.equipe_id == equipe_id)
        
        pessoas = query.order_by(Pessoa.nome).all()
        
        return jsonify({
            'success': True,
            'pessoas': [pessoa.to_dict() for pessoa in pessoas],
            'total': len(pessoas)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pessoa_bp.route('/pessoas/<int:pessoa_id>', methods=['GET'])
def obter_pessoa(pessoa_id):
    """Obtém uma pessoa específica por ID"""
    try:
        pessoa = Pessoa.query.get_or_404(pessoa_id)
        return jsonify({
            'success': True,
            'pessoa': pessoa.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pessoa_bp.route('/pessoas', methods=['POST'])
def criar_pessoa():
    """Cria uma nova pessoa"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('nome'):
            return jsonify({
                'success': False,
                'error': 'Nome é obrigatório'
            }), 400
        
        # Verificar se já existe pessoa com o mesmo nome
        pessoa_existente = Pessoa.query.filter_by(nome=data['nome']).first()
        if pessoa_existente:
            return jsonify({
                'success': False,
                'error': 'Já existe uma pessoa com este nome'
            }), 400
        
        # Criar nova pessoa
        nova_pessoa = Pessoa(
            nome=data['nome'],
            telefone=data.get('telefone'),
            email=data.get('email'),
            observacoes=data.get('observacoes'),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(nova_pessoa)
        db.session.flush()  # Para obter o ID
        
        # Associar às equipes se fornecidas
        equipes_ids = data.get('equipes', [])
        for equipe_id in equipes_ids:
            equipe = Equipe.query.get(equipe_id)
            if equipe:
                pessoa_equipe = PessoaEquipe(pessoa_id=nova_pessoa.id, equipe_id=equipe_id)
                db.session.add(pessoa_equipe)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pessoa': nova_pessoa.to_dict(),
            'message': 'Pessoa criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pessoa_bp.route('/pessoas/<int:pessoa_id>', methods=['PUT'])
def atualizar_pessoa(pessoa_id):
    """Atualiza uma pessoa existente"""
    try:
        pessoa = Pessoa.query.get_or_404(pessoa_id)
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'nome' in data:
            # Verificar se já existe outra pessoa com o mesmo nome
            pessoa_existente = Pessoa.query.filter(
                Pessoa.nome == data['nome'],
                Pessoa.id != pessoa_id
            ).first()
            if pessoa_existente:
                return jsonify({
                    'success': False,
                    'error': 'Já existe outra pessoa com este nome'
                }), 400
            pessoa.nome = data['nome']
        
        if 'telefone' in data:
            pessoa.telefone = data['telefone']
        if 'email' in data:
            pessoa.email = data['email']
        if 'observacoes' in data:
            pessoa.observacoes = data['observacoes']
        if 'ativo' in data:
            pessoa.ativo = data['ativo']
        
        # Atualizar equipes se fornecidas
        if 'equipes' in data:
            # Remover associações existentes
            PessoaEquipe.query.filter_by(pessoa_id=pessoa_id).delete()
            
            # Adicionar novas associações
            equipes_ids = data['equipes']
            for equipe_id in equipes_ids:
                equipe = Equipe.query.get(equipe_id)
                if equipe:
                    pessoa_equipe = PessoaEquipe(pessoa_id=pessoa_id, equipe_id=equipe_id)
                    db.session.add(pessoa_equipe)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'pessoa': pessoa.to_dict(),
            'message': 'Pessoa atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pessoa_bp.route('/pessoas/<int:pessoa_id>', methods=['DELETE'])
def deletar_pessoa(pessoa_id):
    """Deleta uma pessoa (soft delete)"""
    try:
        pessoa = Pessoa.query.get_or_404(pessoa_id)
        
        # Soft delete - apenas marca como inativo
        pessoa.ativo = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pessoa removida com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== ROTAS PARA EQUIPES =====

equipe_bp = Blueprint('equipe', __name__)

@equipe_bp.route('/equipes', methods=['GET'])
def listar_equipes():
    """Lista todas as equipes"""
    try:
        ativo = request.args.get('ativo', 'true').lower() == 'true'
        
        equipes = Equipe.query.filter_by(ativo=ativo).order_by(Equipe.nome).all()
        
        return jsonify({
            'success': True,
            'equipes': [equipe.to_dict() for equipe in equipes],
            'total': len(equipes)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@equipe_bp.route('/equipes/<int:equipe_id>', methods=['GET'])
def obter_equipe(equipe_id):
    """Obtém uma equipe específica por ID"""
    try:
        equipe = Equipe.query.get_or_404(equipe_id)
        
        # Incluir pessoas da equipe
        pessoas = [pe.pessoa.to_dict() for pe in equipe.pessoas if pe.pessoa and pe.pessoa.ativo]
        
        equipe_dict = equipe.to_dict()
        equipe_dict['pessoas'] = pessoas
        
        return jsonify({
            'success': True,
            'equipe': equipe_dict
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@equipe_bp.route('/equipes', methods=['POST'])
def criar_equipe():
    """Cria uma nova equipe"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data.get('nome'):
            return jsonify({
                'success': False,
                'error': 'Nome é obrigatório'
            }), 400
        
        # Verificar se já existe equipe com o mesmo nome
        equipe_existente = Equipe.query.filter_by(nome=data['nome']).first()
        if equipe_existente:
            return jsonify({
                'success': False,
                'error': 'Já existe uma equipe com este nome'
            }), 400
        
        # Criar nova equipe
        nova_equipe = Equipe(
            nome=data['nome'],
            descricao=data.get('descricao'),
            cor=data.get('cor', '#667eea'),
            ativo=data.get('ativo', True)
        )
        
        db.session.add(nova_equipe)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'equipe': nova_equipe.to_dict(),
            'message': 'Equipe criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@equipe_bp.route('/equipes/<int:equipe_id>', methods=['PUT'])
def atualizar_equipe(equipe_id):
    """Atualiza uma equipe existente"""
    try:
        equipe = Equipe.query.get_or_404(equipe_id)
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'nome' in data:
            # Verificar se já existe outra equipe com o mesmo nome
            equipe_existente = Equipe.query.filter(
                Equipe.nome == data['nome'],
                Equipe.id != equipe_id
            ).first()
            if equipe_existente:
                return jsonify({
                    'success': False,
                    'error': 'Já existe outra equipe com este nome'
                }), 400
            equipe.nome = data['nome']
        
        if 'descricao' in data:
            equipe.descricao = data['descricao']
        if 'cor' in data:
            equipe.cor = data['cor']
        if 'ativo' in data:
            equipe.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'equipe': equipe.to_dict(),
            'message': 'Equipe atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@equipe_bp.route('/equipes/<int:equipe_id>', methods=['DELETE'])
def deletar_equipe(equipe_id):
    """Deleta uma equipe (soft delete)"""
    try:
        equipe = Equipe.query.get_or_404(equipe_id)
        
        # Soft delete - apenas marca como inativo
        equipe.ativo = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipe removida com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@equipe_bp.route('/equipes/inicializar', methods=['POST'])
def inicializar_equipes():
    """Inicializa as equipes padrão do grupo de oração"""
    try:
        # Verificar se já existem equipes
        equipes_existentes = Equipe.query.count()
        if equipes_existentes > 0:
            return jsonify({
                'success': False,
                'error': 'Já existem equipes cadastradas'
            }), 400
        
        # Equipes padrão
        equipes_padrao = [
            {'nome': 'Pregação', 'descricao': 'Responsáveis pela pregação nas terças-feiras', 'cor': '#667eea'},
            {'nome': 'Músicos', 'descricao': 'Equipe de músicos para as terças-feiras', 'cor': '#48bb78'},
            {'nome': 'Condução de Animação/Oração', 'descricao': 'Responsáveis pela condução da animação e oração', 'cor': '#ed8936'},
            {'nome': 'Acolhida', 'descricao': 'Equipe de acolhida nas terças-feiras', 'cor': '#9f7aea'},
            {'nome': 'Abastecimento', 'descricao': 'Responsáveis pelo abastecimento nas quartas-feiras', 'cor': '#38b2ac'}
        ]
        
        equipes_criadas = []
        for equipe_data in equipes_padrao:
            equipe = Equipe(**equipe_data)
            db.session.add(equipe)
            equipes_criadas.append(equipe)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(equipes_criadas)} equipes inicializadas com sucesso',
            'equipes': [equipe.to_dict() for equipe in equipes_criadas]
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Registrar blueprint das equipes no blueprint das pessoas
pessoa_bp.register_blueprint(equipe_bp)

