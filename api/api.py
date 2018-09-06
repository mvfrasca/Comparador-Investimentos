# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model, get_tipos_entidades
# Importa módulos utilizados do framework Flask
from flask import Blueprint, redirect, render_template, request, url_for, jsonify
# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importando classes para tratamento de Json e requests HTTP
import json, requests
# Importa o módulo Helper
import utils.helper
from utils.helper import _success
from utils.helper import _error
from utils.helper import _variable
from utils.helper import _clean_attributes
from utils.helper import _is_number
from utils.helper import _is_date
from utils.helper import ClientException
# Importa o módulo de log
import logging
# Importa as classes de negócio
from negocio.investimento import Investimento
from negocio.gestaocadastro import GestaoCadastro

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Gerenciador API')
logger.setLevel(logging.INFO)

# Criando blueprint do módulo da API
api = Blueprint('api', __name__)

@api.route('/investimento', methods=['GET'])
def calcular_investimento():
    # Obtém argumentos
    query_parameters = request.args
    # Loga os estado atual do indexador
    logger.info("Parâmetros recebidos para cálculo do investimento: {}".format(query_parameters))
    # Define a precisão da classe Decimal para 7 casas decimais
    getcontext().prec = 7
    # ------------------------------------------------------------------------------ #
    # Resgata e valida os dados de entrada para cálculo da evolução do investimento
    # ------------------------------------------------------------------------------ #
    # Validação - valor
    if 'valor' not in query_parameters:
        message  = _error("Você deve informar o valor inicial do investimento.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    elif _is_number(query_parameters.get('valor')) == False:
        message  = _error("O valor inicial do investimento é inválido. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    else:
        valInvestimentoInicial = query_parameters.get('valor')
    
    # Validação - indexador
    if 'indexador' not in query_parameters:
        message  = _error("Você deve informar o indexador do investimento.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    elif _is_number(query_parameters.get('valor')) == False:
        message  = _error("O valor inicial do investimento é inválido. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    else:
        indexador = query_parameters.get('indexador').lower()

    # Validação - taxa
    if 'taxa' not in query_parameters:
        message  = _error("Você deve informar a taxa relativa ao indexador do investimento.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    elif _is_number(query_parameters.get('taxa')) == False:
        message  = _error("Taxa relativa ao indexador do investimento é inválida. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    else:
        taxa = query_parameters.get('taxa').lower()

    # Validação - dataInicial
    if 'dataInicial' not in query_parameters:
        message  = _error("Você deve informar a data inicial do investimento. Formato esperado: DD/MM/AAAA", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    elif _is_date(query_parameters.get('dataInicial'), '%d/%m/%Y') == False:
        message  = _error("Data inicial do investimento inválida. Formato esperado: DD/MM/AAAA", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    else:
        dataInicial = datetime.strptime(query_parameters.get('dataInicial'), "%d/%m/%Y")

    # Validação - dataFinal
    if 'dataFinal' not in query_parameters:
        message  = _error("Você deve informar a data inicial do investimento. Formato esperado: DD/MM/AAAA", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    elif _is_date(query_parameters.get('dataFinal'), '%d/%m/%Y') == False:
        message  = _error("Data final do investimento inválida. Formato esperado: DD/MM/AAAA", 400)
        logger.error('ClientException: {}'.format(message))
        raise ClientException(message)
    else:
        dataFinal = datetime.strptime(query_parameters.get('dataFinal'), "%d/%m/%Y")
    

    investimento = Investimento(valInvestimentoInicial, indexador, taxa, dataInicial, dataFinal)
    resultadoInvestimento = investimento.calcularInvestimento()

    return jsonify(resultadoInvestimento)

@api.route('/indexadores', methods=['POST'])
def incluir_indexadores():
    """Carga inicial das entidades que representarão os indexadores.
    """
    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)
    gc = GestaoCadastro()
    gs.incluir_indicadores
    return _success({ 'message': 'Indexadores incluidos com sucesso!' }, 200)

@api.route('/indices', methods=['GET'])
def atualizar_indices():
    """Atualiza os índices dos indexadores cadastrados. Obtém os índices atualizados desde a 
    última data de referência importada da API do Banco Central.
    """
    # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
    # zerados caso contrário datasotore não reconhece)
    dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
    # Inicializa o contador geral de registros atualizados
    contadorTotal = 0
    # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à data atual)
    indexadores = get_model().list_indexadores(dataAtual)
        
    # Percorre os indexadores para consulta e atualização
    for indexador in indexadores:
        # Obtém os dados do indexador
        serie = indexador['serie']
        tipoIndice = indexador['id']
        dataUltReferencia = indexador['dt_ult_referencia']
        periodicidade = indexador['periodicidade']
        
        # Loga os estado atual do indexador
        logger.info("Indicador a receber atualização de índices")
        logger.info('indexador={}'.format(indexador))
 
        # Caso o índicador seja de peridicidade mensal e o mês da última atualização é igual ao 
        # mês atual pula para o próximo indexador
        if (periodicidade.lower() == 'mensal') and (datetime.strftime(dataAtual, "%Y%m") == datetime.strftime(dataUltReferencia, "%Y%m")):
            continue     

        # Recupera indices disponíveis do indexador desde a última atualização até hoje 
        indicesAPI = get_indicesAPI(serie,dataUltReferencia,dataAtual)

        # Ordena lista de obtidas da API
        indicesAPI = sorted(indicesAPI, key = lambda campo: datetime.strptime(campo['data'], '%d/%m/%Y'))

        # Loga os índices retornados pela API
        logger.info("Índices recuperados da API - ")
        logger.info('indicesAPI = {}'.format(indicesAPI))

        # Inicializa coleção e contadores
        indicesConsistir = []
        contadorParcial = 0
        contador = 0

        # Varre a lista de índices retornadas pela API
        for indiceAPI in indicesAPI:
            
            logger.info("Índice a ser atualizado: {}".format(tipoIndice))
            logger.info('indiceAPI={}'.format(indiceAPI))
            # Recupera as propriedades do índice (data e valor)
            dataReferencia = datetime.strptime(indiceAPI['data'], "%d/%m/%Y")
            valorIndice = float(indiceAPI['valor'])

            # Verifica se o índice anterior à data do último índice atualizado 
            # e caso positivo pula para o próximo (API do BC retornar sempre um dia pra tras)]
            if (dataReferencia.isocalendar() <= dataUltReferencia.isocalendar()):
                logger.info('Índice descartado por ser anterior a última atualização')
                continue

            id = tipoIndice + '-' + datetime.strftime(dataReferencia, "%Y%m%d")
            # Popula a estrutura de índice a ser consistida
            indice = {}
            indice.update({'id': id})
            indice.update({'tp_indice': tipoIndice })
            indice.update({'dt_referencia': dataReferencia})
            indice.update({'val_indice': valorIndice})
            indice.update({'dt_inclusao': datetime.now()})

            # Inclui o índice na coleção de índices a ser consistida em banco de dados
            indicesConsistir.append(indice)

            # Atualiza contadores
            contadorParcial = contadorParcial + 1
            contador = contador + 1

            # Caso coleção chegou em 100 itens libera a gravação em lote em banco de dados 
            # para não sobrecarregar chamada à API do banco de dados
            if contadorParcial == 100:
                tipoEntidade = get_model().TipoEntidade.INDICES
                get_model().update_multi(tipoEntidade, indicesConsistir)
                indicesConsistir = []
                contadorParcial = 0
                # Atualiza a data do último índice armazanado na entidade do indexador correspondente 
                # para controle de próximas atualizações
                indexador['dt_ult_referencia'] = dataReferencia
                indexador['dt_ult_atualiz'] = datetime.now()
                indexador['qtd_regs_ult_atualiz'] = contador
                tipoEntidade = get_model().TipoEntidade.INDEXADORES
                get_model().update(tipoEntidade, indexador, tipoIndice)

        # Realiza a gravação em lote dos índices no banco de dados caso algum registro tenha
        # sido tratado
        if contadorParcial > 0:
            tipoEntidade = get_model().TipoEntidade.INDICES
            get_model().update_multi(tipoEntidade, indicesConsistir)
            # Atualiza a data do último índice armazanado na entidade do indexador correspondente 
            # para controle de próximas atualizações
            indexador['dt_ult_referencia'] = dataReferencia
            indexador['dt_ult_atualiz'] = datetime.now()
            indexador['qtd_regs_ult_atualiz'] = contador
            tipoEntidade = get_model().TipoEntidade.INDEXADORES
            get_model().update(tipoEntidade, indexador, tipoIndice)

        contadorTotal = contadorTotal + contador

    # Verifica a quantidade de registros atualizados para retornar mensagem mais adequada
    if contadorTotal == 0:
        msgRetorno = "Banco Central não retornou novos registros a serem atualizados."
    elif contadorTotal > 0:
        msgRetorno = "Índices atualizados com sucesso! Total de {} registro(s) atualizado(s).".format(contadorTotal)

    resposta = {'message': msgRetorno}
    resposta.update({'Indexadores': get_model().list_indexadores() })

    return _success(resposta, 200)

def get_indicesAPI(codigoIndice, dataInicial, dataFinal):
    # Padrão de consulta da API
    # http://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={dataInicial}&dataFinal={dataFinal}

    # CDI (Diário)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=01/08/2018&dataFinal=26/08/2018
    # SELIC (Diário)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial=01/08/2018&dataFinal=26/08/2018
    # IPCA (Mensal)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018
    # IGPM (Mensal)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018
    # INCC (Mensal)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.192/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018
    # Poupança (Mensal)
    # https://api.bcb.gov.br/dados/serie/bcdata.sgs.196/dados?formato=json&dataInicial=01/01/2018&dataFinal=26/08/2018

    try:
        # Formatando datas com o formato string esperado pela API
        dataInicial = datetime.strftime(dataInicial, "%d/%m/%Y")
        dataFinal = datetime.strftime(dataFinal, "%d/%m/%Y")
        # Montando a API
        urlAPI = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{0}/dados?formato=json&dataInicial={1}&dataFinal={2}'.format(codigoIndice,dataInicial,dataFinal)
        logger.info('Chamada à API de índices: {}'.format(urlAPI))   
        # Chamando e obtendo a resposta da API
        response = requests.get(urlAPI)
        # Validando o retorno
        if response.status_code == 200:
            logger.info('Retorno da API de índices:')
            logger.info('response: {}'.format(response.json()))
        # else:
        #     raise ClientException('Falha na consulta ao ')    
    except Exception as e:
        logger.error('Exception: {}'.format(e))
        message  = _error('Erro ao tentar acessar a API do Banco Central.', 500)
        raise ClientException(message)
    else:
        # Retorna JSON dos índices recuperados da API
        return response.json()



@api.route('/indexadores/all', methods=['GET'])
def list_indicadores():
    # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à data atual)
    indexadores = get_model().list_indexadores()
    
    return jsonify(indexadores)

@api.route('/indexador/<id>', methods=['GET'])
def get_indicador(id):
    # Obtém od dados do indexador
    tipoEntidade = get_model().TipoEntidade.INDEXADORES
    indexador = get_model().read(tipoEntidade, id.lower())
    
    return jsonify(indexador)