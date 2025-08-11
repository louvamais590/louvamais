# 🚀 Guia de Deploy Gratuito - LouvaMais

Este guia apresenta várias opções **100% gratuitas** para colocar o LouvaMais em produção, incluindo soluções com banco de dados persistente.

## 📋 Índice

1. [Opções de Deploy](#opções-de-deploy)
2. [Opção 1: Render (Recomendado)](#opção-1-render-recomendado)
3. [Opção 2: Railway](#opção-2-railway)
4. [Opção 3: PythonAnywhere](#opção-3-pythonanywhere)
5. [Opção 4: Heroku (Limitado)](#opção-4-heroku-limitado)
6. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
7. [Domínio Personalizado](#domínio-personalizado)
8. [Monitoramento e Manutenção](#monitoramento-e-manutenção)

---



## 🎯 Opções de Deploy

O LouvaMais é uma aplicação Flask que precisa de:
- **Servidor Python** para executar o backend
- **Banco de dados** para armazenar escalas, pessoas e equipes
- **Arquivos estáticos** para servir HTML, CSS, JS e imagens

### 📊 Comparação das Opções Gratuitas

| Plataforma | Banco de Dados | Uptime | Facilidade | Limitações |
|------------|----------------|--------|------------|------------|
| **Render** | PostgreSQL | 24/7 | ⭐⭐⭐⭐⭐ | Sleep após inatividade |
| **Railway** | PostgreSQL | 24/7 | ⭐⭐⭐⭐ | 500h/mês grátis |
| **PythonAnywhere** | MySQL | 24/7 | ⭐⭐⭐ | 1 app web grátis |
| **Heroku** | PostgreSQL | 24/7 | ⭐⭐⭐⭐ | Plano pago obrigatório |

**🏆 Recomendação**: **Render** - Melhor opção gratuita com PostgreSQL incluído.

---


## 🥇 Opção 1: Render (Recomendado)

O Render oferece hospedagem gratuita para aplicações Python com PostgreSQL incluído.

### 📋 Pré-requisitos
- Conta no GitHub (gratuita)
- Conta no Render (gratuita)

### 🔧 Passo a Passo

#### 1. Preparar o Repositório GitHub

1. **Crie uma conta no GitHub** (se não tiver): https://github.com
2. **Crie um novo repositório**:
   - Nome: `louvamais`
   - Visibilidade: Público (para plano gratuito)
   - Inicialize com README: ✅

3. **Faça upload dos arquivos**:
   - Clique em "uploading an existing file"
   - Arraste toda a pasta `louvamais-source-code`
   - Commit: "Primeira versão do LouvaMais"

#### 2. Configurar o Render

1. **Acesse o Render**: https://render.com
2. **Crie uma conta gratuita** usando sua conta GitHub
3. **Conecte seu repositório**:
   - Dashboard → "New" → "Web Service"
   - Connect GitHub → Selecione o repositório `louvamais`

#### 3. Configurações do Deploy

**Configurações básicas**:
- **Name**: `louvamais`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main.py`

**Variáveis de ambiente**:
- `FLASK_ENV`: `production`
- `DATABASE_URL`: (será preenchida automaticamente)

#### 4. Configurar Banco de Dados

1. **No dashboard do Render**:
   - "New" → "PostgreSQL"
   - Name: `louvamais-db`
   - Plan: Free

2. **Conectar ao Web Service**:
   - Vá para seu Web Service
   - Environment → Add Environment Variable
   - Key: `DATABASE_URL`
   - Value: (copie da página do PostgreSQL)

#### 5. Deploy Automático

1. **Clique em "Create Web Service"**
2. **Aguarde o build** (5-10 minutos)
3. **Acesse sua aplicação**: `https://louvamais.onrender.com`

### ✅ Vantagens do Render
- **Banco PostgreSQL gratuito** (1GB)
- **SSL automático** (HTTPS)
- **Deploy automático** a cada push no GitHub
- **Logs em tempo real**
- **Uptime 24/7** (com sleep após inatividade)

### ⚠️ Limitações
- **Sleep após 15min** de inatividade (desperta em ~30s)
- **750 horas/mês** de execução
- **Bandwidth limitado** (100GB/mês)

---


## 🥈 Opção 2: Railway

Plataforma moderna com excelente experiência de desenvolvedor.

### 🔧 Passo a Passo

1. **Acesse**: https://railway.app
2. **Login com GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione** o repositório `louvamais`
5. **Add PostgreSQL** plugin
6. **Configure variáveis**:
   - `PORT`: `5000`
   - `DATABASE_URL`: (automático)

### ✅ Vantagens
- **Interface moderna**
- **PostgreSQL incluído**
- **Deploy instantâneo**

### ⚠️ Limitações
- **500 horas/mês** grátis
- **1GB RAM** máximo

---

## 🥉 Opção 3: PythonAnywhere

Especializada em Python, ideal para iniciantes.

### 🔧 Passo a Passo

1. **Crie conta**: https://www.pythonanywhere.com
2. **Plan**: Beginner (gratuito)
3. **Upload arquivos**:
   - Files → Upload → Selecione pasta do projeto
4. **Configurar Web App**:
   - Web → Add new web app
   - Python 3.10 → Flask
   - Source code: `/home/seuusuario/louvamais`
5. **Configurar banco**:
   - Databases → Create database
   - Nome: `louvamais`

### ✅ Vantagens
- **MySQL gratuito** (512MB)
- **Uptime 24/7**
- **Console Python** integrado

### ⚠️ Limitações
- **1 web app** apenas
- **Tráfego limitado**
- **CPU seconds** limitados

---

## 🔄 Opção 4: Heroku (Limitado)

**⚠️ Atenção**: Heroku removeu o plano gratuito em 2022, mas ainda é uma opção popular.

### 💰 Custos
- **Dyno básico**: $7/mês
- **PostgreSQL**: Gratuito até 10k linhas

### 🔧 Deploy (se optar por pagar)

1. **Instale Heroku CLI**
2. **Login**: `heroku login`
3. **Crie app**: `heroku create louvamais`
4. **Add PostgreSQL**: `heroku addons:create heroku-postgresql:hobby-dev`
5. **Deploy**: `git push heroku main`

---


## 🗄️ Configuração do Banco de Dados

### 📝 Migração do SQLite para PostgreSQL

O projeto usa SQLite localmente, mas em produção recomenda-se PostgreSQL.

#### Modificações Necessárias

1. **Instale psycopg2** (já incluído no requirements.txt):
```bash
pip install psycopg2-binary
```

2. **Configure variável de ambiente** no arquivo de produção:
```python
import os
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
```

### 🔄 Backup e Restauração

#### Backup Local (SQLite)
```bash
# Backup
cp src/database/app.db backup_$(date +%Y%m%d).db

# Restauração
cp backup_20231201.db src/database/app.db
```

#### Backup PostgreSQL (Produção)
```bash
# Via Render/Railway dashboard
# Ou usando pg_dump se tiver acesso direto
```

---

## 🌐 Domínio Personalizado

### 🆓 Opções Gratuitas

1. **Subdomínios gratuitos**:
   - Render: `louvamais.onrender.com`
   - Railway: `louvamais.up.railway.app`
   - PythonAnywhere: `seuusuario.pythonanywhere.com`

2. **Domínio próprio gratuito**:
   - **Freenom**: .tk, .ml, .ga (gratuitos por 1 ano)
   - **GitHub Student Pack**: Domínio .me gratuito

### ⚙️ Configuração DNS

1. **Registre domínio** (ex: louvamais.tk)
2. **Configure DNS**:
   - Tipo: CNAME
   - Nome: @
   - Valor: `louvamais.onrender.com`
3. **Configure na plataforma**:
   - Render: Settings → Custom Domains

---

## 📊 Monitoramento e Manutenção

### 🔍 Logs e Debug

#### Render
```bash
# Via dashboard: Logs tab
# Ou via CLI: render logs -s louvamais
```

#### Railway
```bash
# Via dashboard: Deployments → View Logs
```

### 📈 Uptime Monitoring

**Opções gratuitas**:
1. **UptimeRobot**: https://uptimerobot.com
   - 50 monitores gratuitos
   - Alertas por email
   - Ping a cada 5 minutos

2. **StatusCake**: https://www.statuscake.com
   - 10 testes gratuitos
   - Alertas SMS/email

### 🔧 Manutenção Regular

1. **Backup semanal** do banco de dados
2. **Monitor de uptime** configurado
3. **Logs de erro** verificados mensalmente
4. **Atualizações de segurança** quando necessário

---

## 🆘 Solução de Problemas

### ❌ Problemas Comuns

#### 1. "Application Error" no Render
**Causa**: Erro no código ou configuração
**Solução**: 
- Verifique logs no dashboard
- Confirme variáveis de ambiente
- Teste localmente primeiro

#### 2. Banco de dados não conecta
**Causa**: DATABASE_URL incorreta
**Solução**:
- Verifique variável de ambiente
- Confirme credenciais do PostgreSQL
- Teste conexão local

#### 3. Arquivos estáticos não carregam
**Causa**: Configuração de paths
**Solução**:
- Verifique paths relativos
- Configure STATIC_FOLDER corretamente

### 📞 Suporte

1. **Documentação oficial** das plataformas
2. **Stack Overflow** para problemas técnicos
3. **GitHub Issues** para bugs do projeto
4. **Discord/Telegram** da comunidade

---

## ✅ Checklist Final

Antes de colocar em produção:

- [ ] Código testado localmente
- [ ] Requirements.txt atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados criado
- [ ] SSL/HTTPS funcionando
- [ ] Domínio configurado (opcional)
- [ ] Monitoring configurado
- [ ] Backup inicial realizado
- [ ] Documentação atualizada

---

## 🎉 Conclusão

Com este guia, você tem várias opções **100% gratuitas** para colocar o LouvaMais em produção. A opção **Render** é recomendada pela facilidade e recursos incluídos.

**Tempo estimado de deploy**: 30-60 minutos
**Custo**: R$ 0,00
**Manutenção**: Mínima

Seu grupo de oração terá um sistema profissional de gestão de escalas acessível de qualquer lugar! 🙏

