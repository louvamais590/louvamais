from flask import Blueprint, request, jsonify, make_response
from src.models.user import db
from src.models.escala import Escala
from datetime import datetime
import csv
import io

exportacao_bp = Blueprint('exportacao', __name__)

@exportacao_bp.route('/escalas/exportar-csv', methods=['GET'])
def exportar_escalas_csv():
    """Exporta as escalas em formato CSV simplificado"""
    try:
        # Parâmetros de filtro
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        # Query base
        query = Escala.query.order_by(Escala.data)
        
        # Aplicar filtros se fornecidos
        if mes and ano:
            query = query.filter(
                db.extract('month', Escala.data) == mes,
                db.extract('year', Escala.data) == ano
            )
        elif ano:
            query = query.filter(db.extract('year', Escala.data) == ano)
        
        escalas = query.all()
        
        if not escalas:
            return jsonify({
                'success': False,
                'error': 'Nenhuma escala encontrada para exportar'
            }), 404
        
        # Criar CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            'Data',
            'Dia da Semana',
            'Pregação',
            'Equipe Músicos',
            'Condução de Animação/Oração',
            'Acolhida',
            'Responsável Condução Abastecimento'
        ])
        
        # Dados
        for escala in escalas:
            if escala.dia_semana.lower().find('terça') != -1:
                # Terça-feira
                writer.writerow([
                    escala.data.strftime('%d/%m/%Y'),
                    escala.dia_semana,
                    escala.pregacao_display or '',
                    escala.musicos_display or '',
                    escala.conducao_animacao_display or '',
                    escala.acolhida_display or '',
                    ''  # Abastecimento vazio para terças
                ])
            else:
                # Quarta-feira
                writer.writerow([
                    escala.data.strftime('%d/%m/%Y'),
                    escala.dia_semana,
                    '',  # Campos vazios para quartas
                    '',
                    '',
                    '',
                    escala.abastecimento_display or ''
                ])
        
        # Preparar resposta
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        # Nome do arquivo
        nome_arquivo = "escala_grupo_oracao"
        if mes and ano:
            nome_arquivo += f"_{ano}_{mes:02d}"
        elif ano:
            nome_arquivo += f"_{ano}"
        nome_arquivo += ".csv"
        
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar CSV: {str(e)}'
        }), 500

@exportacao_bp.route('/escalas/exportar-texto', methods=['GET'])
def exportar_escalas_texto():
    """Exporta as escalas em formato de texto simples e limpo"""
    try:
        # Parâmetros de filtro
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        # Query base
        query = Escala.query.order_by(Escala.data)
        
        # Aplicar filtros se fornecidos
        if mes and ano:
            query = query.filter(
                db.extract('month', Escala.data) == mes,
                db.extract('year', Escala.data) == ano
            )
        elif ano:
            query = query.filter(db.extract('year', Escala.data) == ano)
        
        escalas = query.all()
        
        if not escalas:
            return jsonify({
                'success': False,
                'error': 'Nenhuma escala encontrada para exportar'
            }), 404
        
        # Criar conteúdo de texto
        linhas = []
        linhas.append("=" * 60)
        linhas.append("ESCALA DO GRUPO DE ORAÇÃO")
        
        # Título com período
        if mes and ano:
            meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            linhas.append(f"{meses[mes]} de {ano}")
        elif ano:
            linhas.append(f"Ano {ano}")
        else:
            linhas.append("Todas as escalas")
        
        linhas.append("=" * 60)
        linhas.append("")
        
        # Agrupar escalas por mês
        escalas_por_mes = {}
        for escala in escalas:
            mes_ano = escala.data.strftime('%Y-%m')
            if mes_ano not in escalas_por_mes:
                escalas_por_mes[mes_ano] = []
            escalas_por_mes[mes_ano].append(escala)
        
        # Gerar conteúdo para cada mês
        for mes_ano, escalas_mes in escalas_por_mes.items():
            # Título do mês
            data_mes = datetime.strptime(mes_ano, '%Y-%m')
            titulo_mes = data_mes.strftime('%B %Y').upper()
            linhas.append(titulo_mes)
            linhas.append("-" * len(titulo_mes))
            linhas.append("")
            
            # Escalas do mês
            for escala in escalas_mes:
                data_formatada = escala.data.strftime('%d/%m/%Y')
                linhas.append(f"{data_formatada} - {escala.dia_semana}")
                
                if escala.dia_semana.lower().find('terça') != -1:
                    # Terça-feira
                    if escala.pregacao_display:
                        linhas.append(f"  Pregação: {escala.pregacao_display}")
                    if escala.musicos_display:
                        linhas.append(f"  Equipe Músicos: {escala.musicos_display}")
                    if escala.conducao_animacao_display:
                        linhas.append(f"  Condução/Oração: {escala.conducao_animacao_display}")
                    if escala.acolhida_display:
                        linhas.append(f"  Acolhida: {escala.acolhida_display}")
                    
                    # Verificar se está vazia
                    if not any([escala.pregacao_display, escala.musicos_display, 
                              escala.conducao_animacao_display, escala.acolhida_display]):
                        linhas.append("  (Escala não preenchida)")
                else:
                    # Quarta-feira
                    if escala.abastecimento_display:
                        linhas.append(f"  Responsável Abastecimento: {escala.abastecimento_display}")
                    else:
                        linhas.append("  (Escala não preenchida)")
                
                linhas.append("")  # Linha em branco entre escalas
            
            linhas.append("")  # Linha em branco entre meses
        
        # Rodapé
        linhas.append("=" * 60)
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        linhas.append(f"Relatório gerado em {data_geracao}")
        linhas.append("=" * 60)
        
        # Juntar todas as linhas
        conteudo = "\n".join(linhas)
        
        # Nome do arquivo
        nome_arquivo = "escala_grupo_oracao"
        if mes and ano:
            nome_arquivo += f"_{ano}_{mes:02d}"
        elif ano:
            nome_arquivo += f"_{ano}"
        nome_arquivo += ".txt"
        
        response = make_response(conteudo.encode('utf-8'))
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar arquivo de texto: {str(e)}'
        }), 500

@exportacao_bp.route('/escalas/visualizar', methods=['GET'])
def visualizar_escalas():
    """Retorna as escalas em formato JSON para visualização simplificada"""
    try:
        # Parâmetros de filtro
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        # Query base
        query = Escala.query.order_by(Escala.data)
        
        # Aplicar filtros se fornecidos
        if mes and ano:
            query = query.filter(
                db.extract('month', Escala.data) == mes,
                db.extract('year', Escala.data) == ano
            )
        elif ano:
            query = query.filter(db.extract('year', Escala.data) == ano)
        
        escalas = query.all()
        
        # Preparar dados simplificados
        escalas_simplificadas = []
        for escala in escalas:
            escala_data = {
                'data': escala.data.strftime('%d/%m/%Y'),
                'dia_semana': escala.dia_semana,
                'preenchida': escala.tem_pessoas_definidas
            }
            
            if escala.dia_semana.lower().find('terça') != -1:
                escala_data.update({
                    'tipo': 'terca',
                    'pregacao': escala.pregacao_display or '',
                    'musicos': escala.musicos_display or '',
                    'conducao_oracao': escala.conducao_animacao_display or '',
                    'acolhida': escala.acolhida_display or ''
                })
            else:
                escala_data.update({
                    'tipo': 'quarta',
                    'abastecimento': escala.abastecimento_display or ''
                })
            
            escalas_simplificadas.append(escala_data)
        
        return jsonify({
            'success': True,
            'escalas': escalas_simplificadas,
            'total': len(escalas_simplificadas),
            'periodo': {
                'mes': mes,
                'ano': ano
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao carregar escalas: {str(e)}'
        }), 500

