from src.models.user import db
from datetime import datetime

class Pessoa(db.Model):
    __tablename__ = 'pessoas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com equipes
    equipes = db.relationship('PessoaEquipe', back_populates='pessoa', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'observacoes': self.observacoes,
            'ativo': self.ativo,
            'equipes': [pe.equipe.nome for pe in self.equipes if pe.equipe],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Pessoa {self.nome}>'


class Equipe(db.Model):
    __tablename__ = 'equipes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    cor = db.Column(db.String(7), default='#667eea')  # Cor em hexadecimal
    ativo = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com pessoas
    pessoas = db.relationship('PessoaEquipe', back_populates='equipe', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'ativo': self.ativo,
            'total_pessoas': len([pe for pe in self.pessoas if pe.pessoa and pe.pessoa.ativo]),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Equipe {self.nome}>'


class PessoaEquipe(db.Model):
    __tablename__ = 'pessoa_equipe'
    
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoas.id'), nullable=False)
    equipe_id = db.Column(db.Integer, db.ForeignKey('equipes.id'), nullable=False)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pessoa = db.relationship('Pessoa', back_populates='equipes')
    equipe = db.relationship('Equipe', back_populates='pessoas')
    
    # Constraint para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('pessoa_id', 'equipe_id', name='unique_pessoa_equipe'),)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'pessoa_id': self.pessoa_id,
            'equipe_id': self.equipe_id,
            'pessoa_nome': self.pessoa.nome if self.pessoa else None,
            'equipe_nome': self.equipe.nome if self.equipe else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PessoaEquipe {self.pessoa.nome if self.pessoa else "?"} - {self.equipe.nome if self.equipe else "?"}>'

