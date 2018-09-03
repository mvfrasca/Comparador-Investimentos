# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
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
# Importa o módulo de log
import logging
# Importa as classes internas
from investimento import Investimento


# Inicializar configura o objeto para gravação de logs
logger = logging.getLogger('Gerenciador API')
logger.setLevel(logging.INFO)

# Criando blueprint do módulo da API
api = Blueprint('api', __name__)

@api.route('/investimento', methods=['GET'])
def calcularInvestimento():
    # Obtém argumentos
    query_parameters = request.args
    # Resgata o valor do investimento
    valInvestimentoInicial = query_parameters.get('valor')
    indexador = query_parameters.get('indexador').lower()
    taxa = query_parameters.get('taxa').lower()
    dataInicial = datetime.strptime(query_parameters.get('dataInicial'), "%d/%m/%Y")
    dataFinal = datetime.strptime(query_parameters.get('dataFinal'), "%d/%m/%Y")
    
    print("Entrada:")
    print(dataInicial)
    print(dataFinal)
    
    #print(query_parameters.get('val_investimento'))

    # Valida se parâmetro do valor do investimento foi informado
    if not (valInvestimentoInicial):
        return page_not_found(404)
    # Valida se parâmetro do valor do investimento é numérico  
    # if not str.isdecimal(val_investimento):
    #     return "Valor do investimento inválido. Informe um valor (utilize . para separação de decimais)" 
    
    # Define a precisão para 7 casas decimais
    getcontext().prec = 7

    # Testando a conversão para decimal já que o isnumeric e isdecimal não funcionou corretamente
    try:
        valInvestimentoInicial = Decimal(valInvestimentoInicial)
    except InvalidOperation:
        return "Valor do investimento inválido. Informe um valor numérico (utilize . (ponto) para separação de decimais)" 

    investimento = Investimento(valInvestimentoInicial, indexador, taxa, dataInicial, dataFinal)
    resultadoInvestimento = investimento.calcularInvestimento()

    return jsonify(resultadoInvestimento)

# [INICIO INDICADOR]
@api.route('/indicadores', methods=['POST'])
def criarIndicadores():
    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)

    #     book = get_model().create(data)

    #     return redirect(url_for('.view', id=book['id']))
    
    # with open('static\json\indicadores.json') as f:
    #     indicadores = f.buffer().json()
    #     # indicadores = list(map(lambda x: dict(x.keys(), x.values()), list(f)))
    # print(indicadores)
    # get_model().update_multi("Indicadores", indicadores)

    keys = []
    # Poupança
    indicador = {}
    indicador.update({'nome': 'Poupança'})
    indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
    indicador.update({'periodicidade': 'mensal'})
    indicador.update({'serie': '196'})
    indicador.update({'qtd_regs_ult_atualiz': 0})
    key = get_model().create('Indicadores', indicador, 'poupanca')
    keys.append({key})
    print(indicador)
    # IPCA
    indicador = {}
    indicador.update({'nome': 'IPCA'})
    indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
    indicador.update({'periodicidade': 'mensal'})
    indicador.update({'serie': '433'})
    indicador.update({'qtd_regs_ult_atualiz': 0})
    key = get_model().create('Indicadores', indicador, 'ipca')
    keys.append({key})
    # CDI
    indicador = {}
    indicador.update({'nome': 'CDI'})
    indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
    indicador.update({'periodicidade': 'diario'})
    indicador.update({'serie': '12'})
    indicador.update({'qtd_regs_ult_atualiz': 0})
    key = get_model().create('Indicadores', indicador, 'cdi')
    keys.append({key})
    # SELIC
    indicador = {}
    indicador.update({'nome': 'SELIC'})
    indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
    indicador.update({'periodicidade': 'diario'})
    indicador.update({'serie': '12'})
    indicador.update({'qtd_regs_ult_atualiz': 0})
    key = get_model().create('Indicadores', indicador, 'selic')
    keys.append({key})

    return _success({ 'message': 'Indicadores incluidos com sucesso!' }, 200)
# [FIM criar_indicadores]

@api.route('/indice', methods=['GET'])
def put_indices():

    # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
    # zerados caso contrário datasotore não reconhece)
    dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
    # Inicializa o contador geral de registros atualizados
    contadorTotal = 0
    # Obtém a lista de indicadores para atualização (cuja data de última atualização é anterior à data atual)
    indicadores = get_model().list_indicadores(dataAtual)

    # Percorre os indicadores para consulta e atualização
    for indicador in indicadores:
        # Obtém os dados do indicador
        serie = indicador['serie']
        tipoIndice = indicador['id']
        dataUltReferencia = indicador['dt_ult_referencia']
        periodicidade = indicador['periodicidade']
        
        # Loga os estado atual do indicador
        logger.info("Indicador a receber atualização de índices - ")
        logger.info('indicador={}'.format(indicador))
 
        # Caso o índicador seja de peridicidade mensal e o mês da última atualização é igual ao 
        # mês atual pula para o próximo indicador
        if (periodicidade.lower() == 'mensal') and (datetime.strftime(dataAtual, "%Y%m") == datetime.strftime(dataUltReferencia, "%Y%m")):
            continue     

        # Recupera indices disponíveis do indicador desde a última atualização até hoje 
        indicesAPI = get_indicesAPI(serie,dataUltReferencia,dataAtual)

        # Loga os índices retornados pela API
        logger.info("Índices recuperados da API - ")
        logger.info('indicesAPI={}'.format(indicesAPI))

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
                get_model().update_multi("Indices", indicesConsistir)
                indicesConsistir = []
                contadorParcial = 0
                # Atualiza a data do último índice armazanado na entidade do indicador correspondente 
                # para controle de próximas atualizações
                indicador['dt_ult_referencia'] = dataReferencia
                indicador['dt_ult_atualiz'] = datetime.now()
                indicador['qtd_regs_ult_atualiz'] = contador
                get_model().update("Indicadores", indicador, tipoIndice)

        # Realiza a gravação em lote dos índices no banco de dados caso algum registro tenha
        # sido tratado
        if contadorParcial > 0:
            get_model().update_multi("Indices", indicesConsistir)
            # Atualiza a data do último índice armazanado na entidade do indicador correspondente 
            # para controle de próximas atualizações
            indicador['dt_ult_referencia'] = dataReferencia
            indicador['dt_ult_atualiz'] = datetime.now()
            indicador['qtd_regs_ult_atualiz'] = contador
            get_model().update("Indicadores", indicador, tipoIndice)

        contadorTotal = contadorTotal + contador

    # Verifica a quantidade de registros atualizados para retornar mensagem mais adequada
    if contadorTotal == 0:
        msgRetorno = "Banco Central não retornou novos registros a serem atualizados."
    elif contadorTotal > 0:
        msgRetorno = "Índices atualizados com sucesso! Total de {} registro(s) atualizado(s).".format(contadorTotal)

    resposta = {'message': msgRetorno}
    resposta.update({'indicadores': get_model().list_indicadores() })

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
        message  = _error('Erro ao efetuar a integracao com servicos da AWS', 500)
        # raise ClientException(message)
    else:
        # Retorna JSON dos índices recuperados da API
        return response.json()



@api.route('/indicadores/all', methods=['GET'])
def list_indicadores():
    # Obtém a lista de indicadores para atualização (cuja data de última atualização é anterior à data atual)
    indicadores = get_model().list_indicadores()
    
    return jsonify(indicadores)

@api.route('/indicador/<id>', methods=['GET'])
def get_indicador(id):
    # Obtém od dados do indicador
    indicador = get_model().read_indicador(id.lower())
    
    return jsonify(indicador)