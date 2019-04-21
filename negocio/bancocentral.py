# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importando classes para tratamento de Json e requests HTTP
import json, requests
# Importa o módulo Helper
import utils.helper
from utils.helper import _is_number
from utils.helper import _is_date
from utils.helper import _converter_datas_dict
from utils.helper import ServerException
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe BancoCentral')
logger.setLevel(logging.INFO)

class BancoCentral(BaseObject):
    """Classe que representa a entidade Banco Central e dispobiliza os métodos para consulta de índices via APIs do Banco Central.
    """
    def __init__(self):
       pass
    
    def list_indices(self, serie: str, dataInicial: datetime, dataFinal: datetime):
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
            urlAPI = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{0}/dados?formato=json&dataInicial={1}&dataFinal={2}'.format(serie,dataInicial,dataFinal)
            logger.info('Chamada à API de índices: {}'.format(urlAPI))   
            # Chamando e obtendo a resposta da API
            response = requests.get(urlAPI)
            # Validando o retorno
            if response.status_code == 200:
                logger.info('Retorno da API de índices: {}'.format(response.json()))
            else:
                logger.info('Erro no retorno da API do Banco Central: {}'.format(response))
                raise ServerException(response)
            
            # TODO: Tratar campos retornados para os tipos de dados adequados
            # Ordena lista de obtidas da API
            datas_converter = {'data':'%d/%m/%Y'}
            indices = list(map(lambda item: _converter_datas_dict(item, datas_converter), response.json()))
            indices = sorted(indices, key = lambda campo: campo['data'])

        except Exception as e:
            raise ServerException(e)
        else:
            # Retorna JSON dos índices recuperados da API
            return indices