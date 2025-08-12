// ===== VARIÁVEIS GLOBAIS =====
let escalas = [];
let pessoas = [];
let equipes = [];
let escalaAtual = null;
let funcaoAtual = null;

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventListeners();
    carregarEscalas();
    carregarPessoas();
    carregarEquipes();
});

// ===== EVENT LISTENERS =====
function inicializarEventListeners() {
    // Botões principais
    document.getElementById('btn-inicializar').addEventListener('click', inicializarEscalas);
    document.getElementById('btn-estatisticas').addEventListener('click', mostrarEstatisticas);
    document.getElementById('btn-pessoas').addEventListener('click', mostrarModalPessoas);
    document.getElementById('btn-exportar').addEventListener('click', mostrarModalExportacao);
    
    // Filtros
    document.getElementById('btn-filtrar').addEventListener('click', aplicarFiltros);
    document.getElementById('btn-limpar').addEventListener('click', limparFiltros);
    
    // Modal de escala
    document.getElementById('btn-salvar-escala').addEventListener('click', salvarEscala);
    document.getElementById('btn-cancelar-escala').addEventListener('click', fecharModalEscala);
    
    // Modal de pessoas
    document.getElementById('btn-nova-pessoa').addEventListener('click', () => mostrarFormPessoa());
    document.getElementById('btn-nova-equipe').addEventListener('click', () => mostrarFormEquipe());
    document.getElementById('btn-inicializar-equipes').addEventListener('click', inicializarEquipes);
    
    // Tabs de pessoas
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            trocarTab(tab);
        });
    });
    
    // Busca de pessoas
    document.getElementById('busca-pessoa').addEventListener('input', (e) => {
        filtrarPessoas(e.target.value);
    });
    
    // Modal de seleção
    document.getElementById('btn-confirmar-selecao').addEventListener('click', confirmarSelecaoPessoas);
    document.getElementById('btn-cancelar-selecao').addEventListener('click', fecharModalSelecao);
    document.getElementById('busca-selecao').addEventListener('input', (e) => {
        filtrarSelecaoPessoas(e.target.value);
    });
    
    // Fechar modais
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            fecharModal(modal);
        });
    });
    
    // Fechar modal clicando fora
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                fecharModal(modal);
            }
        });
    });
}

// ===== FUNÇÕES DE API =====
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro na requisição');
        }
        
        return data;
    } catch (error) {
        console.error('Erro na API:', error);
        mostrarToast(error.message, 'error');
        throw error;
    }
}

// ===== FUNÇÕES DE ESCALAS =====
async function carregarEscalas() {
    try {
        mostrarLoading(true);
        const data = await apiRequest('/api/escalas');
        escalas = data.escalas || [];
        renderizarEscalas();
    } catch (error) {
        console.error('Erro ao carregar escalas:', error);
    } finally {
        mostrarLoading(false);
    }
}

async function inicializarEscalas() {
    if (confirm('Deseja inicializar as escalas? Isso criará todas as datas até dezembro de 2025.')) {
        try {
            const data = await apiRequest('/api/escalas/inicializar', { method: 'POST' });
            mostrarToast(data.message, 'success');
            carregarEscalas();
        } catch (error) {
            console.error('Erro ao inicializar escalas:', error);
        }
    }
}

async function salvarEscala() {
    if (!escalaAtual) return;
    
    try {
        // Coletar dados das pessoas selecionadas
        const pessoasPorFuncao = {};
        
        document.querySelectorAll('.pessoas-selector').forEach(selector => {
            const funcao = selector.dataset.funcao;
            const pessoasIds = [];
            
            selector.querySelectorAll('.pessoa-tag').forEach(tag => {
                const pessoaId = parseInt(tag.dataset.pessoaId);
                if (pessoaId) {
                    pessoasIds.push(pessoaId);
                }
            });
            
            pessoasPorFuncao[funcao] = pessoasIds;
        });
        
        // Salvar cada função separadamente
        for (const [funcao, pessoasIds] of Object.entries(pessoasPorFuncao)) {
            if (pessoasIds.length > 0) {
                await apiRequest(`/api/escalas/${escalaAtual.id}/pessoas/funcao`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        funcao: funcao,
                        pessoas_ids: pessoasIds
                    })
                });
            }
        }
        
        mostrarToast('Escala atualizada com sucesso!', 'success');
        fecharModalEscala();
        carregarEscalas();
    } catch (error) {
        console.error('Erro ao salvar escala:', error);
    }
}

// ===== FUNÇÕES DE PESSOAS =====
async function carregarPessoas() {
    try {
        const data = await apiRequest('/api/pessoas');
        pessoas = data.pessoas || [];
        renderizarPessoas();
    } catch (error) {
        console.error('Erro ao carregar pessoas:', error);
    }
}

async function carregarEquipes() {
    try {
        const data = await apiRequest('/api/equipes');
        equipes = data.equipes || [];
        renderizarEquipes();
    } catch (error) {
        console.error('Erro ao carregar equipes:', error);
    }
}

async function inicializarEquipes() {
    if (confirm('Deseja inicializar as equipes padrão?')) {
        try {
            const data = await apiRequest('/api/equipes/inicializar', { method: 'POST' });
            mostrarToast(data.message, 'success');
            carregarEquipes();
        } catch (error) {
            console.error('Erro ao inicializar equipes:', error);
        }
    }
}

// ===== FUNÇÕES DE RENDERIZAÇÃO =====
function renderizarEscalas() {
    const container = document.getElementById('escalas-container');
    const emptyState = document.getElementById('empty-state');
    
    if (escalas.length === 0) {
        container.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    container.style.display = 'block';
    emptyState.style.display = 'none';
    
    container.innerHTML = escalas.map(escala => {
        const isPreenchida = verificarEscalaPreenchida(escala);
        const statusClass = isPreenchida ? 'preenchida' : 'vazia';
        const statusText = isPreenchida ? 'Preenchida' : 'Vazia';
        
        return `
            <div class="escala-card ${escala.dia_semana.toLowerCase().includes('terça') ? 'terca' : 'quarta'}">
                <div class="escala-header">
                    <div class="escala-data">
                        <h3>${escala.data_formatada}</h3>
                        <span class="dia-semana">${escala.dia_semana}</span>
                    </div>
                    <div class="escala-status ${statusClass}">
                        ${statusText}
                    </div>
                </div>
                <div class="escala-content">
                    ${renderizarCamposEscala(escala)}
                </div>
                <div class="escala-actions">
                    <button class="btn btn-primary" onclick="editarEscala(${escala.id})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderizarCamposEscala(escala) {
    if (escala.dia_semana.includes('Terça')) {
        return `
            <div class="campo-escala">
                <label>Pregação:</label>
                <span>${escala.pregacao_display || 'Não definido'}</span>
            </div>
            <div class="campo-escala">
                <label>Equipe Músicos:</label>
                <span>${escala.musicos_display || 'Não definido'}</span>
            </div>
            <div class="campo-escala">
                <label>Condução de Animação/Oração:</label>
                <span>${escala.conducao_animacao_display || 'Não definido'}</span>
            </div>
            <div class="campo-escala">
                <label>Acolhida:</label>
                <span>${escala.acolhida_display || 'Não definido'}</span>
            </div>
        `;
    } else {
        return `
            <div class="campo-escala">
                <label>Responsável Condução Abastecimento:</label>
                <span>${escala.abastecimento_display || 'Não definido'}</span>
            </div>
        `;
    }
}

function renderizarPessoas() {
    const container = document.getElementById('lista-pessoas');
    
    if (pessoas.length === 0) {
        container.innerHTML = `
            <div class="empty-pessoas">
                <i class="fas fa-users"></i>
                <h3>Nenhuma pessoa cadastrada</h3>
                <p>Clique em "Nova Pessoa" para começar.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = pessoas.map(pessoa => `
        <div class="pessoa-item">
            <div class="pessoa-info">
                <div class="pessoa-nome">${pessoa.nome}</div>
                <div class="pessoa-detalhes">
                    ${pessoa.telefone ? `📞 ${pessoa.telefone}` : ''}
                    ${pessoa.email ? `📧 ${pessoa.email}` : ''}
                </div>
                <div class="pessoa-equipes">
                    ${pessoa.equipes.map(equipe => `
                        <span class="equipe-tag">${equipe}</span>
                    `).join('')}
                </div>
            </div>
            <div class="pessoa-actions">
                <button class="btn-icon edit" onclick="editarPessoa(${pessoa.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" onclick="deletarPessoa(${pessoa.id})" title="Remover">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function renderizarEquipes() {
    const container = document.getElementById('lista-equipes');
    
    if (equipes.length === 0) {
        container.innerHTML = `
            <div class="empty-equipes">
                <i class="fas fa-users-cog"></i>
                <h3>Nenhuma equipe cadastrada</h3>
                <p>Clique em "Inicializar Equipes Padrão" ou "Nova Equipe".</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = equipes.map(equipe => `
        <div class="equipe-item">
            <div class="equipe-info">
                <div class="equipe-nome" style="color: ${equipe.cor}">${equipe.nome}</div>
                <div class="equipe-detalhes">
                    ${equipe.descricao || 'Sem descrição'} • ${equipe.total_pessoas} pessoas
                </div>
            </div>
            <div class="equipe-actions">
                <button class="btn-icon edit" onclick="editarEquipe(${equipe.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" onclick="deletarEquipe(${equipe.id})" title="Remover">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// ===== FUNÇÕES DE MODAL =====
function mostrarModalPessoas() {
    document.getElementById('modal-pessoas').style.display = 'flex';
    carregarPessoas();
    carregarEquipes();
}

function editarEscala(escalaId) {
    escalaAtual = escalas.find(e => e.id === escalaId);
    if (!escalaAtual) return;
    
    // Preencher dados básicos
    document.getElementById('escala-data').value = escalaAtual.data_formatada;
    document.getElementById('escala-dia-semana').value = escalaAtual.dia_semana;
    document.getElementById('modal-titulo').textContent = `Editar Escala - ${escalaAtual.data_formatada}`;
    
    // Mostrar campos apropriados
    const isTerca = escalaAtual.dia_semana.includes('Terça');
    document.getElementById('campos-terca').style.display = isTerca ? 'block' : 'none';
    document.getElementById('campos-quarta').style.display = isTerca ? 'none' : 'block';
    
    // Carregar pessoas já escaladas
    carregarPessoasEscala(escalaId);
    
    document.getElementById('modal-editar-escala').style.display = 'flex';
}

async function carregarPessoasEscala(escalaId) {
    try {
        const data = await apiRequest(`/api/escalas/${escalaId}/pessoas`);
        const pessoasPorFuncao = data.pessoas_por_funcao || {};
        
        // Limpar seleções anteriores
        document.querySelectorAll('.pessoas-selected').forEach(container => {
            container.innerHTML = '';
        });
        
        // Preencher pessoas por função
        for (const [funcao, pessoasEscala] of Object.entries(pessoasPorFuncao)) {
            const container = document.getElementById(`${funcao}-selected`);
            if (container) {
                pessoasEscala.forEach(pessoaEscala => {
                    adicionarPessoaTag(container, {
                        id: pessoaEscala.pessoa_id,
                        nome: pessoaEscala.pessoa_nome
                    });
                });
            }
        }
    } catch (error) {
        console.error('Erro ao carregar pessoas da escala:', error);
    }
}

function mostrarSelecaoPessoas(funcao) {
    funcaoAtual = funcao;
    document.getElementById('modal-selecao-titulo').textContent = `Selecionar Pessoas - ${funcao}`;
    
    // Renderizar lista de pessoas
    renderizarSelecaoPessoas();
    
    document.getElementById('modal-selecionar-pessoas').style.display = 'flex';
}

function renderizarSelecaoPessoas(filtro = '') {
    const container = document.getElementById('lista-selecao-pessoas');
    const pessoasFiltradas = pessoas.filter(pessoa => 
        pessoa.nome.toLowerCase().includes(filtro.toLowerCase())
    );
    
    // Obter pessoas já selecionadas
    const pessoasSelecionadas = [];
    const selectedContainer = document.getElementById(`${funcaoAtual}-selected`);
    if (selectedContainer) {
        selectedContainer.querySelectorAll('.pessoa-tag').forEach(tag => {
            pessoasSelecionadas.push(parseInt(tag.dataset.pessoaId));
        });
    }
    
    container.innerHTML = pessoasFiltradas.map(pessoa => `
        <div class="pessoa-selecao-item">
            <input type="checkbox" 
                   id="pessoa-${pessoa.id}" 
                   value="${pessoa.id}"
                   ${pessoasSelecionadas.includes(pessoa.id) ? 'checked' : ''}>
            <div class="pessoa-selecao-info">
                <div class="pessoa-selecao-nome">${pessoa.nome}</div>
                <div class="pessoa-selecao-equipes">${pessoa.equipes.join(', ')}</div>
            </div>
        </div>
    `).join('');
}

function confirmarSelecaoPessoas() {
    const checkboxes = document.querySelectorAll('#lista-selecao-pessoas input[type="checkbox"]:checked');
    
    if (checkboxes.length > 10) {
        mostrarToast('Máximo de 10 pessoas por função', 'error');
        return;
    }
    
    const container = document.getElementById(`${funcaoAtual}-selected`);
    container.innerHTML = '';
    
    checkboxes.forEach(checkbox => {
        const pessoaId = parseInt(checkbox.value);
        const pessoa = pessoas.find(p => p.id === pessoaId);
        if (pessoa) {
            adicionarPessoaTag(container, pessoa);
        }
    });
    
    fecharModalSelecao();
}

function adicionarPessoaTag(container, pessoa) {
    const tag = document.createElement('div');
    tag.className = 'pessoa-tag';
    tag.dataset.pessoaId = pessoa.id;
    tag.innerHTML = `
        ${pessoa.nome}
        <button class="remove" onclick="removerPessoaTag(this)">×</button>
    `;
    container.appendChild(tag);
}

function removerPessoaTag(button) {
    button.parentElement.remove();
}

// ===== FUNÇÕES DE UTILIDADE =====
function verificarEscalaPreenchida(escala) {
    if (escala.dia_semana.includes('Terça')) {
        return (escala.pregacao_display && escala.pregacao_display !== 'Não definido') ||
               (escala.musicos_display && escala.musicos_display !== 'Não definido') ||
               (escala.conducao_animacao_display && escala.conducao_animacao_display !== 'Não definido') ||
               (escala.acolhida_display && escala.acolhida_display !== 'Não definido');
    } else {
        return escala.abastecimento_display && escala.abastecimento_display !== 'Não definido';
    }
}

function trocarTab(tabName) {
    // Atualizar botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Atualizar conteúdo
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

function filtrarPessoas(filtro) {
    // Implementar filtro de pessoas
    const pessoasFiltradas = pessoas.filter(pessoa => 
        pessoa.nome.toLowerCase().includes(filtro.toLowerCase())
    );
    // Renderizar pessoas filtradas
}

function filtrarSelecaoPessoas(filtro) {
    renderizarSelecaoPessoas(filtro);
}

function mostrarLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function fecharModal(modal) {
    modal.style.display = 'none';
}

function fecharModalEscala() {
    fecharModal(document.getElementById('modal-editar-escala'));
    escalaAtual = null;
}

function fecharModalSelecao() {
    fecharModal(document.getElementById('modal-selecionar-pessoas'));
    funcaoAtual = null;
}

function mostrarToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// ===== FUNÇÕES DE ESTATÍSTICAS =====
async function mostrarEstatisticas() {
    try {
        const data = await apiRequest('/api/escalas/estatisticas');
        
        document.getElementById('stat-total').textContent = data.total_escalas;
        document.getElementById('stat-tercas').textContent = data.tercas;
        document.getElementById('stat-quartas').textContent = data.quartas;
        document.getElementById('stat-preenchidas').textContent = data.escalas_preenchidas;
        document.getElementById('stat-vazias').textContent = data.escalas_vazias;
        document.getElementById('stat-progresso').textContent = data.progresso + '%';
        
        document.getElementById('modal-estatisticas').style.display = 'flex';
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ===== FUNÇÕES DE FILTRO =====
function aplicarFiltros() {
    const mes = document.getElementById('filtro-mes').value;
    const ano = document.getElementById('filtro-ano').value;
    
    let escalasFiltradas = [...escalas];
    
    if (mes) {
        escalasFiltradas = escalasFiltradas.filter(escala => {
            const dataEscala = new Date(escala.data);
            return dataEscala.getMonth() + 1 === parseInt(mes);
        });
    }
    
    if (ano) {
        escalasFiltradas = escalasFiltradas.filter(escala => {
            const dataEscala = new Date(escala.data);
            return dataEscala.getFullYear() === parseInt(ano);
        });
    }
    
    escalas = escalasFiltradas;
    renderizarEscalas();
}

function limparFiltros() {
    document.getElementById('filtro-mes').value = '';
    document.getElementById('filtro-ano').value = '';
    carregarEscalas();
}

// ===== EVENT LISTENERS PARA BOTÕES DE ADICIONAR PESSOA =====
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-add-pessoa') || e.target.parentElement.classList.contains('btn-add-pessoa')) {
        const button = e.target.classList.contains('btn-add-pessoa') ? e.target : e.target.parentElement;
        const funcao = button.dataset.funcao;
        mostrarSelecaoPessoas(funcao);
    }
});

// ===== FUNÇÕES DE EXPORTAÇÃO SIMPLIFICADA =====
function mostrarModalExportacao() {
    const mes = document.getElementById('filtro-mes').value;
    const ano = document.getElementById('filtro-ano').value;
    
    let filtros = '';
    if (mes) filtros += `&mes=${mes}`;
    if (ano) filtros += `&ano=${ano}`;
    
    let periodoTexto = 'todas as escalas';
    if (mes && ano) {
        const meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        periodoTexto = `${meses[parseInt(mes)]} de ${ano}`;
    } else if (ano) {
        periodoTexto = `ano ${ano}`;
    }
    
    let html = `
        <div class="modal" id="modal-exportacao" style="display: flex;">
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h2><i class="fas fa-download"></i> Exportar Escalas</h2>
                    <button class="modal-close" onclick="fecharModal(document.getElementById('modal-exportacao'))">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <p style="color: #64748b; margin-bottom: 8px;">Período selecionado:</p>
                        <p style="font-weight: 600; color: #1e293b; font-size: 16px;">${periodoTexto}</p>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <button class="btn btn-primary" onclick="exportarTexto('${filtros}'); fecharModal(document.getElementById('modal-exportacao'))" style="justify-content: center; padding: 16px;">
                            <i class="fas fa-file-alt"></i> 
                            <div style="margin-left: 12px; text-align: left;">
                                <div style="font-weight: 600;">Arquivo de Texto</div>
                                <div style="font-size: 12px; opacity: 0.8;">Formato simples e limpo (.txt)</div>
                            </div>
                        </button>
                        
                        <button class="btn btn-success" onclick="exportarCSV('${filtros}'); fecharModal(document.getElementById('modal-exportacao'))" style="justify-content: center; padding: 16px;">
                            <i class="fas fa-table"></i>
                            <div style="margin-left: 12px; text-align: left;">
                                <div style="font-weight: 600;">Planilha CSV</div>
                                <div style="font-size: 12px; opacity: 0.8;">Para Excel e Google Sheets (.csv)</div>
                            </div>
                        </button>
                        
                        <button class="btn btn-info" onclick="visualizarEscalas('${filtros}'); fecharModal(document.getElementById('modal-exportacao'))" style="justify-content: center; padding: 16px;">
                            <i class="fas fa-eye"></i>
                            <div style="margin-left: 12px; text-align: left;">
                                <div style="font-weight: 600;">Visualizar</div>
                                <div style="font-size: 12px; opacity: 0.8;">Ver resumo antes de exportar</div>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modal-exportacao');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar novo modal
    document.body.insertAdjacentHTML('beforeend', html);
}

async function exportarTexto(filtros = '') {
    try {
        mostrarToast('Gerando arquivo de texto...', 'info');
        
        const response = await fetch(`/api/escalas/exportar-texto?${filtros.substring(1)}`);
        
        if (!response.ok) {
            throw new Error('Erro ao gerar arquivo de texto');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `escala_grupo_oracao_${new Date().getTime()}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        mostrarToast('Arquivo de texto gerado com sucesso!', 'success');
    } catch (error) {
        console.error('Erro ao exportar texto:', error);
        mostrarToast('Erro ao gerar arquivo de texto', 'error');
    }
}

async function exportarCSV(filtros = '') {
    try {
        mostrarToast('Gerando planilha CSV...', 'info');
        
        const response = await fetch(`/api/escalas/exportar-csv?${filtros.substring(1)}`);
        
        if (!response.ok) {
            throw new Error('Erro ao gerar CSV');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `escala_grupo_oracao_${new Date().getTime()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        mostrarToast('Planilha CSV gerada com sucesso!', 'success');
    } catch (error) {
        console.error('Erro ao exportar CSV:', error);
        mostrarToast('Erro ao gerar planilha CSV', 'error');
    }
}

async function visualizarEscalas(filtros = '') {
    try {
        mostrarToast('Carregando visualização...', 'info');
        
        const response = await fetch(`/api/escalas/visualizar?${filtros.substring(1)}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Erro ao carregar escalas');
        }
        
        mostrarModalVisualizacao(data.escalas, data.periodo);
        
    } catch (error) {
        console.error('Erro ao visualizar escalas:', error);
        mostrarToast('Erro ao carregar visualização', 'error');
    }
}

function mostrarModalVisualizacao(escalas, periodo) {
    let periodoTexto = 'Todas as escalas';
    if (periodo.mes && periodo.ano) {
        const meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        periodoTexto = `${meses[periodo.mes]} de ${periodo.ano}`;
    } else if (periodo.ano) {
        periodoTexto = `Ano ${periodo.ano}`;
    }
    
    let html = `
        <div class="modal" id="modal-visualizacao" style="display: flex;">
            <div class="modal-content modal-large">
                <div class="modal-header">
                    <h2><i class="fas fa-eye"></i> Visualização das Escalas</h2>
                    <button class="modal-close" onclick="fecharModal(document.getElementById('modal-visualizacao'))">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="text-align: center; margin-bottom: 24px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <h3 style="color: #1e293b; margin-bottom: 8px;">${periodoTexto}</h3>
                        <p style="color: #64748b;">Total: ${escalas.length} escalas</p>
                    </div>
                    
                    <div style="max-height: 400px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
    `;
    
    escalas.forEach((escala, index) => {
        const bgColor = escala.tipo === 'terca' ? '#f0f9ff' : '#f0fdf4';
        const borderColor = escala.tipo === 'terca' ? '#0ea5e9' : '#22c55e';
        const statusColor = escala.preenchida ? '#22c55e' : '#ef4444';
        const statusTexto = escala.preenchida ? 'Preenchida' : 'Vazia';
        
        html += `
            <div style="padding: 16px; border-bottom: 1px solid #f1f5f9; background: ${bgColor}; ${index === 0 ? 'border-top-left-radius: 8px; border-top-right-radius: 8px;' : ''} ${index === escalas.length - 1 ? 'border-bottom: none; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;' : ''}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <strong style="color: #1e293b;">${escala.data} - ${escala.dia_semana}</strong>
                    </div>
                    <span style="background: ${statusColor}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                        ${statusTexto}
                    </span>
                </div>
        `;
        
        if (escala.tipo === 'terca') {
            html += `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; font-size: 14px;">
                    <div><strong>Pregação:</strong> ${escala.pregacao || 'Não definido'}</div>
                    <div><strong>Músicos:</strong> ${escala.musicos || 'Não definido'}</div>
                    <div><strong>Condução/Oração:</strong> ${escala.conducao_oracao || 'Não definido'}</div>
                    <div><strong>Acolhida:</strong> ${escala.acolhida || 'Não definido'}</div>
                </div>
            `;
        } else {
            html += `
                <div style="font-size: 14px;">
                    <strong>Responsável Abastecimento:</strong> ${escala.abastecimento || 'Não definido'}
                </div>
            `;
        }
        
        html += `</div>`;
    });
    
    html += `
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="fecharModal(document.getElementById('modal-visualizacao'))">
                        <i class="fas fa-times"></i> Fechar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente se houver
    const modalExistente = document.getElementById('modal-visualizacao');
    if (modalExistente) {
        modalExistente.remove();
    }
    
    // Adicionar novo modal
    document.body.insertAdjacentHTML('beforeend', html);
}

// ===== FUNÇÕES COMPLETAS DE CRUD =====
async function mostrarFormPessoa(pessoaId = null) {
    try {
        let pessoa = null;
        if (pessoaId) {
            const response = await apiRequest(`/api/pessoas/${pessoaId}`);
            pessoa = response.pessoa;
        }
        
        // Carregar equipes para seleção
        const equipesResponse = await apiRequest('/api/equipes');
        const equipes = equipesResponse.equipes || [];
        
        const isEdicao = !!pessoaId;
        const titulo = isEdicao ? 'Editar Pessoa' : 'Nova Pessoa';
        
        let html = `
            <div class="modal" id="modal-form-pessoa" style="display: flex;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2><i class="fas fa-user"></i> ${titulo}</h2>
                        <button class="modal-close" onclick="fecharModal(document.getElementById('modal-form-pessoa'))">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="form-pessoa-dados">
                            <div class="form-group">
                                <label for="pessoa-nome">Nome *</label>
                                <input type="text" id="pessoa-nome" value="${pessoa?.nome || ''}" required>
                            </div>
                            <div class="form-group">
                                <label for="pessoa-telefone">Telefone</label>
                                <input type="tel" id="pessoa-telefone" value="${pessoa?.telefone || ''}">
                            </div>
                            <div class="form-group">
                                <label for="pessoa-email">Email</label>
                                <input type="email" id="pessoa-email" value="${pessoa?.email || ''}">
                            </div>
                            <div class="form-group">
                                <label for="pessoa-observacoes">Observações</label>
                                <textarea id="pessoa-observacoes" rows="3">${pessoa?.observacoes || ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label>Equipes</label>
                                <div id="equipes-checkboxes">
        `;
        
        equipes.forEach(equipe => {
            const checked = pessoa?.equipes?.includes(equipe.nome) ? 'checked' : '';
            html += `
                <div style="margin-bottom: 8px;">
                    <input type="checkbox" id="equipe-${equipe.id}" value="${equipe.id}" ${checked}>
                    <label for="equipe-${equipe.id}" style="margin-left: 8px; font-weight: normal;">${equipe.nome}</label>
                </div>
            `;
        });
        
        html += `
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-success" onclick="salvarPessoa(${pessoaId})">
                            <i class="fas fa-save"></i> Salvar
                        </button>
                        <button class="btn btn-outline" onclick="fecharModal(document.getElementById('modal-form-pessoa'))">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente se houver
        const modalExistente = document.getElementById('modal-form-pessoa');
        if (modalExistente) {
            modalExistente.remove();
        }
        
        // Adicionar novo modal
        document.body.insertAdjacentHTML('beforeend', html);
        
    } catch (error) {
        console.error('Erro ao carregar formulário de pessoa:', error);
        mostrarToast('Erro ao carregar formulário', 'error');
    }
}

async function salvarPessoa(pessoaId = null) {
    try {
        const nome = document.getElementById('pessoa-nome').value.trim();
        const telefone = document.getElementById('pessoa-telefone').value.trim();
        const email = document.getElementById('pessoa-email').value.trim();
        const observacoes = document.getElementById('pessoa-observacoes').value.trim();
        
        if (!nome) {
            mostrarToast('Nome é obrigatório', 'error');
            return;
        }
        
        // Coletar equipes selecionadas
        const equipesIds = [];
        document.querySelectorAll('#equipes-checkboxes input[type="checkbox"]:checked').forEach(checkbox => {
            equipesIds.push(parseInt(checkbox.value));
        });
        
        const dados = {
            nome,
            telefone,
            email,
            observacoes,
            equipes_ids: equipesIds
        };
        
        let response;
        if (pessoaId) {
            response = await apiRequest(`/api/pessoas/${pessoaId}`, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        } else {
            response = await apiRequest('/api/pessoas', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        }
        
        mostrarToast(response.message, 'success');
        fecharModal(document.getElementById('modal-form-pessoa'));
        carregarPessoas();
        
    } catch (error) {
        console.error('Erro ao salvar pessoa:', error);
    }
}

async function deletarPessoa(pessoaId) {
    if (confirm('Deseja realmente remover esta pessoa?')) {
        try {
            const response = await apiRequest(`/api/pessoas/${pessoaId}`, {
                method: 'DELETE'
            });
            mostrarToast(response.message, 'success');
            carregarPessoas();
        } catch (error) {
            console.error('Erro ao deletar pessoa:', error);
        }
    }
}

async function mostrarFormEquipe(equipeId = null) {
    try {
        let equipe = null;
        if (equipeId) {
            const response = await apiRequest(`/api/equipes/${equipeId}`);
            equipe = response.equipe;
        }
        
        const isEdicao = !!equipeId;
        const titulo = isEdicao ? 'Editar Equipe' : 'Nova Equipe';
        
        let html = `
            <div class="modal" id="modal-form-equipe" style="display: flex;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2><i class="fas fa-users-cog"></i> ${titulo}</h2>
                        <button class="modal-close" onclick="fecharModal(document.getElementById('modal-form-equipe'))">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="form-equipe-dados">
                            <div class="form-group">
                                <label for="equipe-nome">Nome *</label>
                                <input type="text" id="equipe-nome" value="${equipe?.nome || ''}" required>
                            </div>
                            <div class="form-group">
                                <label for="equipe-descricao">Descrição</label>
                                <textarea id="equipe-descricao" rows="3">${equipe?.descricao || ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label for="equipe-cor">Cor</label>
                                <input type="color" id="equipe-cor" value="${equipe?.cor || '#667eea'}">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-success" onclick="salvarEquipe(${equipeId})">
                            <i class="fas fa-save"></i> Salvar
                        </button>
                        <button class="btn btn-outline" onclick="fecharModal(document.getElementById('modal-form-equipe'))">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal existente se houver
        const modalExistente = document.getElementById('modal-form-equipe');
        if (modalExistente) {
            modalExistente.remove();
        }
        
        // Adicionar novo modal
        document.body.insertAdjacentHTML('beforeend', html);
        
    } catch (error) {
        console.error('Erro ao carregar formulário de equipe:', error);
        mostrarToast('Erro ao carregar formulário', 'error');
    }
}

async function salvarEquipe(equipeId = null) {
    try {
        const nome = document.getElementById('equipe-nome').value.trim();
        const descricao = document.getElementById('equipe-descricao').value.trim();
        const cor = document.getElementById('equipe-cor').value;
        
        if (!nome) {
            mostrarToast('Nome é obrigatório', 'error');
            return;
        }
        
        const dados = {
            nome,
            descricao,
            cor
        };
        
        let response;
        if (equipeId) {
            response = await apiRequest(`/api/equipes/${equipeId}`, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        } else {
            response = await apiRequest('/api/equipes', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        }
        
        mostrarToast(response.message, 'success');
        fecharModal(document.getElementById('modal-form-equipe'));
        carregarEquipes();
        
    } catch (error) {
        console.error('Erro ao salvar equipe:', error);
    }
}

async function deletarEquipe(equipeId) {
    if (confirm('Deseja realmente remover esta equipe?')) {
        try {
            const response = await apiRequest(`/api/equipes/${equipeId}`, {
                method: 'DELETE'
            });
            mostrarToast(response.message, 'success');
            carregarEquipes();
        } catch (error) {
            console.error('Erro ao deletar equipe:', error);
        }
    }
}

function editarPessoa(pessoaId) {
    mostrarFormPessoa(pessoaId);
}

function editarEquipe(equipeId) {
    mostrarFormEquipe(equipeId);
}

