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
from utils.helper import InputException
from utils.helper import BusinessException
from utils.helper import ServerException
# Importa o módulo de log
import logging
# Importa as classes de negócio
from negocio.investimento import Investimento
from negocio.gestaocadastro import GestaoCadastro
from negocio.bancocentral import BancoCentral
from negocio.indice import Indice

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Gerenciador API')
logger.setLevel(logging.INFO)

# Criando blueprint do módulo da API
api = Blueprint('api', __name__)

@api.route('/investimento', methods=['GET'])
def calcular_investimento():
    # Obtém argumentos
    queryParameters = request.args
    
    # Loga os estado atual do indexador
    logger.info("Parâmetros recebidos para cálculo do investimento: {}".format(queryParameters))
    # Define a precisão da classe Decimal para 7 casas decimais
    getcontext().prec = 7
    # ------------------------------------------------------------------------------ #
    # Resgata e valida os dados de entrada para cálculo da evolução do investimento
    # ------------------------------------------------------------------------------ #
    # Validação - valor
    if 'valor' not in queryParameters:
        mensagem  = _error("Você deve informar o valor inicial do investimento.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('valor', mensagem)
    elif _is_number(queryParameters.get('valor')) == False:
        mensagem  = _error("O valor inicial do investimento é inválido. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('valor', mensagem)
    else:
        valInvestimentoInicial = Decimal(queryParameters.get('valor'))
    
    # Validação - indexador
    if 'indexador' not in queryParameters:
        mensagem  = _error("Você deve informar o indexador do investimento.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('indexador', mensagem)
    elif _is_number(queryParameters.get('valor')) == False:
        mensagem  = _error("O valor inicial do investimento é inválido. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('indexador', mensagem)
    else:
        indexador = queryParameters.get('indexador').lower()

    # Validação - taxa
    if 'taxa' not in queryParameters:
        mensagem  = _error("Você deve informar a taxa relativa ao indexador do investimento.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('taxa', mensagem)
    elif _is_number(queryParameters.get('taxa')) == False:
        mensagem  = _error("Taxa relativa ao indexador do investimento é inválida. Utilizar ponto ao invés de virgula para casas decimais.", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('taxa', mensagem)
    else:
        taxa = Decimal(queryParameters.get('taxa'))

    # Validação - dataInicial
    if 'dataInicial' not in queryParameters:
        mensagem  = _error("Você deve informar a data inicial do investimento. Formato esperado: DD/MM/AAAA", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('dataInicial', mensagem)
    elif _is_date(queryParameters.get('dataInicial'), '%d/%m/%Y') == False:
        mensagem  = _error("Data inicial do investimento inválida. Formato esperado: DD/MM/AAAA", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('dataInicial', mensagem)
    else:
        dataInicial = datetime.strptime(queryParameters.get('dataInicial'), "%d/%m/%Y")

    # Validação - dataFinal
    if 'dataFinal' not in queryParameters:
        mensagem  = _error("Você deve informar a data inicial do investimento. Formato esperado: DD/MM/AAAA", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('dataFinal', mensagem)
    elif _is_date(queryParameters.get('dataFinal'), '%d/%m/%Y') == False:
        mensagem  = _error("Data final do investimento inválida. Formato esperado: DD/MM/AAAA", 400)
        logger.error('InputException: {}'.format(mensagem))
        raise InputException('dataFinal', mensagem)
    else:
        dataFinal = datetime.strptime(queryParameters.get('dataFinal'), "%d/%m/%Y")
    
    try: 
        # Instancia a classe de negócio Investimento 
        objInvest = Investimento(valInvestimentoInicial, indexador, taxa, dataInicial, dataFinal)
        # Realiza o cálculo de evolução do investimento
        resultadoInvestimento = objInvest.calcular_investimento()
    except BusinessException as be:
        raise be
    except Exception as e:
        mensagem  = _error("Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde.", 500)
        logger.error('Exception: {}'.format(e))
        raise ServerException(mensagem)
    else:
        return jsonify(resultadoInvestimento)

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
        mensagem  = _error("Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde.", 500)
        logger.error('Exception: {}'.format(e))
        raise ServerException(mensagem)
    else:
        return _success({ 'mensagem': 'Indexadores incluidos com sucesso!' }, 200)

@api.route('/indices', methods=['GET'])
def atualizar_indices():
    """Atualiza os índices dos indexadores cadastrados. Obtém os índices atualizados desde a 
    última data de referência importada da API do Banco Central.
    """
    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
        # zerados caso contrário datasotore não reconhece)
        dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
        # Inicializa o contador geral de registros atualizados
        contadorTotal = 0
        # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à data atual)
        indexadores = objGestaoCadastro.list_indexadores(dataAtual)
    except BusinessException as be:
        raise be
    except Exception as e:
        mensagem  = _error("Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde.", 500)
        logger.error('Exception: {}'.format(e))
        raise ServerException(mensagem)

    # Percorre os indexadores para consulta e atualização
    for indexador in indexadores:
        # Loga os estado atual do indexador
        logger.info('Indexador a receber atualização de índices: {}'.format(indexador))
        # Obtém os dados do indexador
        serie = indexador['serie']
        tipoIndice = indexador['id']
        dataUltReferencia = indexador['dt_ult_referencia']
        periodicidade = indexador['periodicidade']
        # Caso o índicador seja de peridicidade mensal e o mês da última atualização é igual ao 
        # mês atual pula para o próximo indexador
        if (periodicidade.lower() == 'mensal') and (datetime.strftime(dataAtual, "%Y%m") == datetime.strftime(dataUltReferencia, "%Y%m")):
            # Pula para o próximo indexador
            continue
        # Instancia a classe de negócios responsável pela consulta à API do Banco Central
        objBC = BancoCentral()
        # Recupera indices disponíveis do indexador desde a última atualização até hoje 
        indicesAPI = objBC.list_indices(serie,dataUltReferencia,dataAtual)

        # Inicializa coleção e contadores
        indicesConsistir = []
        contadorParcial = 0
        contador = 0
        
        # Varre a lista de índices retornadas pela API
        for indiceAPI in indicesAPI:
            logger.info('Índice a ser atualizado: {0}, dados: {1}'.format(tipoIndice, indiceAPI))
            # Recupera as propriedades do índice (data e valor)
            dataReferencia = datetime.strptime(indiceAPI['data'], "%d/%m/%Y")
            valorIndice = float(indiceAPI['valor'])
            # Verifica se data de referência do índice é anterior à data da última atualização 
            # e caso positivo pula para o próximo (API do BC retornar sempre um dia pra tras)]
            if (dataReferencia.isocalendar() <= dataUltReferencia.isocalendar()):
                logger.info('Índice descartado por ser anterior a última atualização')
                continue
    
            # Popula uma instancia de índice a ser consistida
            indice = Indice(tp_indice = tipoIndice, dt_referencia = dataReferencia, val_indice = valorIndice, dt_inclusao = datetime.now())

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
        statusCode = 204
        msgRetorno = "Banco Central não retornou novos registros a serem atualizados."
    elif contadorTotal > 0:
        statusCode = 201
        msgRetorno = "Índices atualizados com sucesso! Total de {} registro(s) atualizado(s).".format(contadorTotal)

    resposta = {'mensagem': msgRetorno}
    resposta.update({'Indexadores': get_model().list_indexadores() })

    return _success(resposta, statusCode)

@api.route('/indexadores/all', methods=['GET'])
def list_indexadores():
    """ Retorna lista com todos os indexadores cadastrados
    """
    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Obtém a lista de indexadores cadastrados
        indexadores = objGestaoCadastro.list_indexadores()
    except BusinessException as be:
        raise be
    except Exception as e:
        mensagem  = _error("Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde.", 500)
        logger.error('Exception: {}'.format(e))
        print(e)
        raise ServerException(mensagem)

    return jsonify(indexadores)

@api.route('/indexadores/<id>', methods=['GET'])
def get_indexador(id):
    """Retorna lista com todos o indexador solicitado
    """
    try:
        # Instancia a classe de negócios responsável pela gestão de cadastros da API
        objGestaoCadastro = GestaoCadastro()
        # Obtém o indexadores através do id
        indexador = objGestaoCadastro.get_indexador(id)
    except BusinessException as be:
        raise be
    except Exception as e:
        mensagem  = _error("Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde.", 500)
        logger.error('Exception: {}'.format(e))
        raise ServerException(mensagem)
        
    return jsonify(indexador)