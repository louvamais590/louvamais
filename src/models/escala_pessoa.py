from src.models.user import db
from datetime import datetime

class EscalaPessoa(db.Model):
    __tablename__ = 'escala_pessoa'
    
    id = db.Column(db.Integer, primary_key=True)
    escala_id = db.Column(db.Integer, db.ForeignKey('escalas.id'), nullable=False)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoas.id'), nullable=False)
    funcao = db.Column(db.String(50), nullable=False)  # 'pregacao', 'musicos', 'conducao_animacao', 'acolhida', 'abastecimento'
    confirmado = db.Column(db.Boolean, default=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    escala = db.relationship('Escala', back_populates='pessoas')
    pessoa = db.relationship('Pessoa')
    
    # Constraint para evitar duplicatas da mesma pessoa na mesma função da mesma escala
    __table_args__ = (db.UniqueConstraint('escala_id', 'pessoa_id', 'funcao', name='unique_escala_pessoa_funcao'),)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'escala_id': self.escala_id,
            'pessoa_id': self.pessoa_id,
            'pessoa_nome': self.pessoa.nome if self.pessoa else None,
            'funcao': self.funcao,
            'confirmado': self.confirmado,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<EscalaPessoa {self.pessoa.nome if self.pessoa else "?"} - {self.funcao}>'

