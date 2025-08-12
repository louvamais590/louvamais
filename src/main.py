import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.pessoa import Pessoa, Equipe, PessoaEquipe
from src.models.escala_pessoa import EscalaPessoa
from src.routes.user import user_bp
from src.routes.escala import escala_bp
from src.routes.pessoa import pessoa_bp
from src.routes.exportacao_simples import exportacao_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Configurar CORS para permitir requisições do frontend
CORS(app, origins=['*'])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(escala_bp, url_prefix='/api')
app.register_blueprint(pessoa_bp, url_prefix='/api')
app.register_blueprint(exportacao_bp, url_prefix='/api')

# Configuração do banco de dados
# Em produção, usa PostgreSQL via DATABASE_URL
# Em desenvolvimento, usa SQLite local
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Produção - PostgreSQL
    # Fix para Heroku/Render que pode usar postgres:// em vez de postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Desenvolvimento - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Rota principal agora redireciona para a página de entrada
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'entrada.html')

# Rota para o sistema de escalas
@app.route('/sistema')
def sistema():
    return send_from_directory(app.static_folder, 'index.html')

# Rota para servir arquivos estáticos
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Health check para plataformas de cloud
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'LouvaMais está funcionando!'}, 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Porta configurável para diferentes plataformas
    port = int(os.environ.get('PORT', 5000))
    # Em produção, não usar debug mode
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

