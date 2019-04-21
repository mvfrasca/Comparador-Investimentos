# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa módulos utilizados do framework Flask
from flask import Blueprint, redirect, render_template, request, url_for, jsonify
# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa módulo pra tratamento de arquivos json
import json
# Importa o módulo Helper
import utils.helper
from utils.helper import _success
from utils.helper import _error
from utils.helper import _variable
from utils.helper import _clean_attributes
from utils.helper import _is_number
from utils.helper import _is_date
from utils.helper import _converter_datas_dict
from utils.helper import InputException
from utils.helper import BusinessException
from utils.helper import ServerException
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
    """Calcula a evolução do investimento a partir de um valor inicial aplicando os indices referentes 
    ao período, indexador e taxa informados.
    
    Argumentos:
        tipoInvestimento: tipo de investimento (ex.: CDB, LCI, LCA, Poupanca)
        valor: valor inicial do investimento
        indexador: nome identificador do indexador (ex.: ipca, selic)
        taxa: percentual aplicado sobre o índice (ex.: 130 (130% do cdi), 7 (IPCA + 7%))
        dataInicial: data inicial do investimento
        dataFinal: data de vencimento do investimento
    Retorno:
            Retorna uma lista contendo dictionaries referentes aos valores 
            de saldo e rentabilidade do investimento além de uma sublista 
            da evolução do valor inicial em função do tempo (período informado)
    """
    # Obtém argumentos
    queryParameters = request.args
    
    # Loga os estado atual do indexador
    logger.info("Parâmetros recebidos para cálculo do investimento: {}".format(queryParameters))
    # Define a precisão da classe Decimal para 9 casas decimais
    getcontext().prec = 9
    # ------------------------------------------------------------------------------ #
    # Resgata e valida os dados de entrada para cálculo da evolução do investimento
    # ------------------------------------------------------------------------------ #
    # Validação - indexador
    if 'tipoInvestimento' not in queryParameters:
        mensagem  = "Você deve informar o tipo de investimento."
        raise InputException('tipoInvestimento', mensagem)
    else:
        tipoInvestimento = queryParameters.get('tipoInvestimento')
    
    # TODO: Verificar se é um tipo de investimento válido

    # Validação - valor
    if 'valor' not in queryParameters:
        mensagem  = "Você deve informar o valor inicial do investimento."
        raise InputException('valor', mensagem)
    elif _is_number(queryParameters.get('valor')) == False:
        mensagem  = "O valor inicial do investimento é inválido. Utilizar ponto ao invés de virgula para casas decimais."
        raise InputException('valor', mensagem)
    else:
        valInvestimentoInicial = Decimal(queryParameters.get('valor'))
    
    # Validação - indexador
    if 'indexador' not in queryParameters:
        mensagem  = "Você deve informar o indexador do investimento."
        raise InputException('indexador', mensagem)
    else:
        indexador = queryParameters.get('indexador')
    
    # TODO: Verificar se é um indexador válido

    # Validação - taxa
    if 'taxa' not in queryParameters:
        mensagem  = "Você deve informar a taxa relativa ao indexador do investimento."
        raise InputException('taxa', mensagem)
    elif _is_number(queryParameters.get('taxa')) == False:
        mensagem  = "Taxa relativa ao indexador do investimento é inválida. Utilizar ponto ao invés de virgula para casas decimais."
        raise InputException('taxa', mensagem)
    else:
        taxa = Decimal(queryParameters.get('taxa'))

    # Validação - dataInicial
    if 'dataInicial' not in queryParameters:
        mensagem  = "Você deve informar a data inicial do investimento. Formato esperado: AAAA-MM-DD"
        raise InputException('dataInicial', mensagem)
    elif _is_date(queryParameters.get('dataInicial'), "%Y-%m-%d") == False:
        mensagem  = "Data inicial do investimento inválida. Formato esperado: AAAA-MM-DD"
        raise InputException('dataInicial', mensagem)
    else:
        dataInicial = datetime.strptime(queryParameters.get('dataInicial'), "%Y-%m-%d").date()

    # Validação - dataFinal
    if 'dataFinal' not in queryParameters:
        # mensagem  = "Você deve informar a data final do investimento. Formato esperado: AAAA-MM-DD"
        # raise InputException('dataFinal', mensagem)
        # Quando não informada assumir data atual
        dataFinal = datetime.now()
    elif _is_date(queryParameters.get('dataFinal'), '%Y-%m-%d') == False:
        mensagem  = "Data final do investimento inválida. Formato esperado: AAAA-MM-DD"
        raise InputException('dataFinal', mensagem)
    else:
        dataFinal = datetime.strptime(queryParameters.get('dataFinal'), "%Y-%m-%d").date()
    
    try: 
        # Instancia a classe de negócio Investimento 
        objInvest = Investimento(tipoInvestimento, valInvestimentoInicial, indexador, taxa, dataInicial, dataFinal)
        # Realiza o cálculo de evolução do investimento
        resultadoInvestimento = objInvest.calcular_investimento()
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:
        return _success({ 'mensagem': 'Cálculo do investimento realizado com sucesso!', 'resultadoInvestimento': resultadoInvestimento }, 200), 200, {'Access-Control-Allow-Origin': '*'} 

@api.route('/investimento', methods=['OPTIONS'])
def investimento_options (self):
    return {'Allow' : 'GET' }, [200,400], \
    { 'Access-Control-Allow-Origin': '*', \
    'Access-Control-Allow-Methods' : 'GET' }

@api.route('/indexadores', methods=['POST'])
def post_indexadores():
    """Carga inicial das entidades que representarão os indexadores.
    """
    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)
    try:
        # Instancia o a classe de negócio GestaoCadastro
        objGestaoCadastro = GestaoCadastro()
        # Realiza a carga inicial dos indexadores
        objGestaoCadastro.criar_indexadores()
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:
        return _success({ 'mensagem': 'Indexadores incluidos/atualizados com sucesso!' }, 201), 201, {'Access-Control-Allow-Origin': '*'} 

@api.route('/feriados', methods=['POST'])
def post_feriados():
    """Carga inicial das entidades que representarão os feriados.
    """
    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)
    try:
        # Instancia o a classe de negócio GestaoCadastro
        objGestaoCadastro = GestaoCadastro()
        # Realiza a carga inicial dos indexadores
        qtdFeriados = objGestaoCadastro.criar_feriados()
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:
        return _success({ 'mensagem': '{} feriados incluidos/atualizados com sucesso!'.format(qtdFeriados) }, 201), 201, {'Access-Control-Allow-Origin': '*'} 

@api.route('/indexadores/all/indices', methods=['GET'])
def atualizar_indices():
    """Atualiza os índices dos indexadores cadastrados. Obtém os índices atualizados desde a 
    última data de referência importada da API do Banco Central.
    """
    # Instancia a classe de negócios responsável pela gestão de cadastros da API
    objGestaoCadastro = GestaoCadastro()

    try:
        # Solicita a atualização dos índices 
        contadorTotal = objGestaoCadastro.atualizar_indices() 
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)

    # Verifica a quantidade de registros atualizados para retornar mensagem mais adequada
    if contadorTotal == 0:
        statusCode = 204
        mensagem = "Banco Central não retornou novos registros a serem atualizados."
    elif contadorTotal > 0:
        statusCode = 201
        mensagem = "Índices atualizados com sucesso! Total de {} registro(s) atualizado(s).".format(contadorTotal)

    resposta = {'mensagem': mensagem}
    resposta.update({'indexadores': objGestaoCadastro.list_indexadores()})
    return _success(resposta, statusCode), statusCode, {'Access-Control-Allow-Origin': '*'} 

@api.route('/indexadores/all', methods=['GET'])
def list_indexadores():
    """ Retorna lista com todos os indexadores cadastrados
    """
    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Obtém a lista de indexadores cadastrados
        indexadores = objGestaoCadastro.list_indexadores()
        #
        # indexadores = list(map(lambda item: _converter_datas_dict(item, datas_converter), indexadores))
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:
        resposta = {'mensagem': 'Consulta aos indexadores realizada com sucesso'}
        resposta.update({'indexadores': indexadores})
        return _success(resposta, 200), 200, {'Access-Control-Allow-Origin': '*'} 

@api.route('/indexadores/all', methods=['OPTIONS'])
def indexadores_options (self):
    return {'Allow' : 'GET' }, 200, \
    { 'Access-Control-Allow-Origin': '*', \
    'Access-Control-Allow-Methods' : 'GET' }
    
@api.route('/indexadores/<id>', methods=['GET'])
def get_indexador(id):
    """Retorna o indexador solicitado
    """
    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Obtém o indexadores através do id
        indexador = objGestaoCadastro.get_indexador(id)
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:  
        resposta = {'mensagem': 'Consulta ao indexador realizada com sucesso'}
        resposta.update({'indexador': indexador})
        return _success(resposta, 200), 200, {'Access-Control-Allow-Origin': '*'} 

@api.route('/indexadores/<id>/indices', methods=['GET'])
def list_indices(id):
    """Retorna lista de índices referente ao indexador e período solicitado

    Argumentos path:
        indexador: código do indexador. Ex.: ipca, poupanca, cdi.
    Argumentos Query string:
        dataInicial: data inicial do período de índices a ser consultado.
        dataFinal: data final do período de índices a ser consultado.
    Retorno:
        Lista de índices com data e valor
    """
    # Obtém argumentos
    queryParameters = request.args
    # Loga os estado atual do indexador
    logger.info("Parâmetros recebidos para retorno dos índices: {}".format(queryParameters))
    
    # Validação - indexador
    if id is None:
        mensagem  = "Você deve informar o indexador para consulta aos índices."
        raise InputException('indexador', mensagem)
    else:
        indexador = id.lower()

    # Validação - dataInicial
    if 'dataInicial' not in queryParameters:
        mensagem  = "Você deve informar a data inicial do período de índices a serem retornados. Formato esperado: AAAA-MM-DD"
        raise InputException('dataInicial', mensagem)
    elif _is_date(queryParameters.get('dataInicial'), '%Y-%m-%d') == False:
        mensagem  = "Data inicial do período inválida. Formato esperado: AAAA-MM-DD"
        raise InputException('dataInicial', mensagem)
    else:
        dataInicial = datetime.strptime(queryParameters.get('dataInicial'), "%Y-%m-%d").date()

    # Validação - dataFinal
    if 'dataFinal' not in queryParameters:
        mensagem  = "Você deve informar a data final do período de índices a serem retornados. Formato esperado: AAAA-MM-DD"
        raise InputException('dataFinal', mensagem)
    elif _is_date(queryParameters.get('dataFinal'), '%Y-%m-%d') == False:
        mensagem  = "Data final do período inválida. Formato esperado: AAAA-MM-DD"
        raise InputException('dataFinal', mensagem)
    else:
        dataFinal = datetime.strptime(queryParameters.get('dataFinal'), "%Y-%m-%d").date()

    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Obtém o indexadores através do id
        indices = objGestaoCadastro.list_indices(indexador, dataInicial, dataFinal)
    except BusinessException as be:
        raise be
    except Exception as e:
        raise ServerException(e)
    else:  
        resposta = {'mensagem': 'Consulta aos índices realizada com sucesso'}
        resposta.update({'indices': indices})
        return _success(resposta, 200), 200, {'Access-Control-Allow-Origin': '*'} 
