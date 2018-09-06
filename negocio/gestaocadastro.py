# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa módulo pra tratamento de arquivos json
import json
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
# Importa o módulo de log
import logging

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe GestaoCadastro')
logger.setLevel(logging.INFO)

class GestaoCadastro(object):
    """Classe que gerencia os cadastros que dão suporte aos cálculos de investimento.
    """
    def __init__(self):
       self.__init__()
    
    def criar_indexadores(self):
        """Realiza a carga inicial das entidades que representarão os indexadores.
    
        Retorno:
            Retorna uma lista contendo os indexadores que foram inclusos.
        """
        # Carrega arquivo JSON que contém a carga inicial dos indexadores
        with open(r'''static\json\indexadores.json''',encoding='UTF8') as f:
            indexadores = json.load(f)
            # indexadores = list(map(lambda x: dict(x.keys(), x.values()), list(f)))
            # Prepara o dicionário com os nomes dos campos data e respectivo formato no json
            # para que a função _converter_datas_dict realize a conversão para datetime
            datas_converter = {'dt_ult_referencia':'%d/%m/%Y', 'dt_ult_atualiz':'%d/%m/%Y'}
            indexadores = map(lambda item: _converter_datas_dict(item, datas_converter), indexadores)
            # Loga os estado atual do indicador
            logger.info("Carga inicial de indexadores")
            logger.info('indexadores = {}'.format(indexadores))
            # Inclui/atualiza a base de dados com os indexadores
            get_model().update_multi("Indexadores", indexadores)

        # keys = []
        # # Poupança
        # indexador = {}
        # indexador.update({'nome': 'Poupança'})
        # indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        # indexador.update({'periodicidade': 'mensal'})
        # indexador.update({'serie': '196'})
        # indexador.update({'qtd_regs_ult_atualiz': 0})
        # key = get_model().create('Indexadores', indexador, 'poupanca')
        # keys.append({key})
        # print(indexador)
        # # IPCA
        # indexador = {}
        # indexador.update({'nome': 'IPCA'})
        # indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        # indexador.update({'periodicidade': 'mensal'})
        # indexador.update({'serie': '433'})
        # indexador.update({'qtd_regs_ult_atualiz': 0})
        # key = get_model().create('Indexadores', indexador, 'ipca')
        # keys.append({key})
        # # CDI
        # indexador = {}
        # indexador.update({'nome': 'CDI'})
        # indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        # indexador.update({'periodicidade': 'diario'})
        # indexador.update({'serie': '12'})
        # indexador.update({'qtd_regs_ult_atualiz': 0})
        # key = get_model().create('Indexadores', indexador, 'cdi')
        # keys.append({key})
        # # SELIC
        # indexador = {}
        # indexador.update({'nome': 'SELIC'})
        # indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        # indexador.update({'periodicidade': 'diario'})
        # indexador.update({'serie': '12'})
        # indexador.update({'qtd_regs_ult_atualiz': 0})
        # key = get_model().create('Indexadores', indexador, 'selic')
        # keys.append({key})