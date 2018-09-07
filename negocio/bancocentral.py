# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importando classes para tratamento de Json e requests HTTP
import json, requests
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
# Importa o módulo Helper
import utils.helper
from utils.helper import _success
from utils.helper import _error
from utils.helper import _variable
from utils.helper import _clean_attributes
from utils.helper import _is_number
from utils.helper import _is_date
from utils.helper import InputException
# Importa o módulo de log
import logging

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe BancoCentral')
logger.setLevel(logging.INFO)

class BancoCentral(object):
    """Classe que representa a entidade Banco Central e dispobiliza os métodos para consulta de índices via APIs do Banco Central.
    """
    def __init__(self):
       self.__init__()
    
    def get_indices(self, serie: str, dataInicial: datetime, dataFinal: datetime):
        """Acessa a API do Banco Central e retorna os índices referentes à série e período informados.

        Argumentos:
            serie: código da série que identifica o indexador
                CDI (Diário): 12
                SELIC (Diário): 11
                IPCA (Mensal): 433
                IGPM (Mensal): 189 
                Poupança (Mensal): 196
            dataInicial: data inicial da consulta à série de índices
            dataFinal: data final da consulta à série de índices
    
        Retorno:
            Retorna uma lista contendo data e valor do índice de cada data do período solicitado. 
            Exemplo de retorno:
                [{"data": "01/08/2018", "valor": "0.025555"},{"data": "02/08/2018","valor": "0.025555"}]
            Se o indexador é mensal, retorna os índices referenciando o dia 01 de cada mês dentro do período solicitado. 
                Ex.: [{"data": "03/08/2018", "valor": "0.025555"},{"data": "06/08/2018","valor": "0.025555"}]
            Se o indexador é diário, retorna os índices dos dias úteis dentro do período solicitado.
        """
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
            else:
                message = response. ce.response['Error']['Message']
                code = ce.response['ResponseMetadata']['HTTPStatusCode']
                raise InputException('Falha na consulta ao ')    
        except Exception as e:
            logger.error('Exception: {}'.format(e))
            message  = _error('Erro ao tentar acessar a API do Banco Central.', 500)
            raise InputException(message)
        else:
            # Retorna JSON dos índices recuperados da API
            return response.json()