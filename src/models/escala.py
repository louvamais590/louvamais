from src.models.user import db
from datetime import datetime

class Escala(db.Model):
    __tablename__ = 'escalas'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, unique=True)
    dia_semana = db.Column(db.String(20), nullable=False)  # 'Terça-feira' ou 'Quarta-feira'
    
    # Campos legados para compatibilidade (serão removidos gradualmente)
    pregacao = db.Column(db.String(100), nullable=True)
    equipe_musicos = db.Column(db.String(200), nullable=True)
    conducao_animacao = db.Column(db.String(100), nullable=True)
    acolhida = db.Column(db.String(100), nullable=True)
    responsavel_abastecimento = db.Column(db.String(100), nullable=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com pessoas
    pessoas = db.relationship('EscalaPessoa', back_populates='escala', cascade='all, delete-orphan')
    
    def get_pessoas_por_funcao(self, funcao):
        """Retorna lista de pessoas para uma função específica"""
        return [ep.pessoa for ep in self.pessoas if ep.funcao == funcao and ep.pessoa]
    
    def get_nomes_por_funcao(self, funcao):
        """Retorna lista de nomes para uma função específica"""
        pessoas = self.get_pessoas_por_funcao(funcao)
        return [p.nome for p in pessoas]
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        # Funções para terças-feiras
        pregacao_pessoas = self.get_nomes_por_funcao('pregacao')
        musicos_pessoas = self.get_nomes_por_funcao('musicos')
        conducao_pessoas = self.get_nomes_por_funcao('conducao_animacao')
        acolhida_pessoas = self.get_nomes_por_funcao('acolhida')
        
        # Função para quartas-feiras
        abastecimento_pessoas = self.get_nomes_por_funcao('abastecimento')
        
        return {
            'id': self.id,
            'data': self.data.strftime('%Y-%m-%d'),
            'data_formatada': self.data.strftime('%d/%m/%Y'),
            'dia_semana': self.dia_semana,
            
            # Campos legados (para compatibilidade)
            'pregacao': self.pregacao,
            'equipe_musicos': self.equipe_musicos,
            'conducao_animacao': self.conducao_animacao,
            'acolhida': self.acolhida,
            'responsavel_abastecimento': self.responsavel_abastecimento,
            
            # Novos campos com pessoas
            'pregacao_pessoas': pregacao_pessoas,
            'musicos_pessoas': musicos_pessoas,
            'conducao_animacao_pessoas': conducao_pessoas,
            'acolhida_pessoas': acolhida_pessoas,
            'abastecimento_pessoas': abastecimento_pessoas,
            
            # Strings formatadas para exibição
            'pregacao_display': ', '.join(pregacao_pessoas) if pregacao_pessoas else (self.pregacao or ''),
            'musicos_display': ', '.join(musicos_pessoas) if musicos_pessoas else (self.equipe_musicos or ''),
            'conducao_animacao_display': ', '.join(conducao_pessoas) if conducao_pessoas else (self.conducao_animacao or ''),
            'acolhida_display': ', '.join(acolhida_pessoas) if acolhida_pessoas else (self.acolhida or ''),
            'abastecimento_display': ', '.join(abastecimento_pessoas) if abastecimento_pessoas else (self.responsavel_abastecimento or ''),
            
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Escala {self.data} - {self.dia_semana}>'

