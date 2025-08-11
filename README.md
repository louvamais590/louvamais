# LouvaMais - Gestão de Escalas

Sistema completo para organização e gerenciamento das escalas do seu grupo de oração. Simplifique a coordenação e fortaleça a comunidade.

## 🎯 Funcionalidades

- **Gestão de Pessoas**: Cadastro completo com telefone, email e observações
- **Gestão de Equipes**: Organização por funções (Pregação, Músicos, Condução, Acolhida, Abastecimento)
- **Escalas Automáticas**: Geração de escalas para terças e quartas até dezembro/2025
- **Seleção Múltipla**: Até 10 pessoas por função
- **Exportação**: Arquivo de texto e planilha CSV
- **Interface Responsiva**: Funciona em desktop, tablet e mobile
- **Animação de Entrada**: Tela de boas-vindas moderna e elegante

## 🚀 Tecnologias

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite
- **Estilo**: CSS moderno com gradientes e animações
- **Ícones**: Font Awesome

## 📁 Estrutura do Projeto

```
louvamais/
├── src/
│   ├── static/
│   │   ├── entrada.html      # Página de entrada com animação
│   │   ├── index.html        # Sistema principal
│   │   ├── styles.css        # Estilos CSS
│   │   ├── script.js         # JavaScript
│   │   └── logo.png          # Logo do projeto
│   ├── models/               # Modelos do banco de dados
│   ├── routes/               # Rotas da API
│   └── main.py              # Arquivo principal
├── requirements.txt          # Dependências Python
└── README.md                # Este arquivo
```

## 🛠️ Instalação Local

1. **Clone ou baixe o projeto**
2. **Instale o Python 3.8+**
3. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Execute o projeto**:
   ```bash
   python src/main.py
   ```
6. **Acesse**: http://localhost:5000

## 🌐 Deploy em Produção

Consulte o arquivo `DEPLOY.md` para instruções completas de deploy gratuito.

## 📝 Licença

Este projeto é de uso livre para grupos de oração e comunidades religiosas.

## 🙏 Suporte

Para dúvidas ou suporte, consulte a documentação completa no arquivo `DEPLOY.md`.

