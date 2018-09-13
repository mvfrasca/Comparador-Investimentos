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
# Importa a classe base
from negocio.baseobject import BaseObject

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe GestaoCadastro')
logger.setLevel(logging.INFO)

class Indice(BaseObject):
    """Classe que representa um Índice.
    
    Argumentos:
        tp_indice: tipo de índice (indexador). Ex.: ipca, poupanca, cdi.
        dt_referencia: data de referência do índice
        val_indice: valor do índice em percentual. Ex.: 0.0123
        dt_inclusao: data da inclusão do índice na base de dados de índices
    """
    # Método criador
    def __init__(self, tp_indice: str, dt_referencia: datetime, val_indice: float, dt_inclusao: datetime):
        # Define a precisão para 7 casas decimais
        getcontext().prec = 7
        # Define chave única para o índice
        self.id = tp_indice.lower() + '-' + datetime.strftime(dt_referencia, "%Y%m%d")
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.tp_indice = tp_indice.lower()
        self.dt_referencia = dt_referencia
        self.val_indice = val_indice
        self.dt_inclusao = dt_inclusao

    @classmethod
    def fromDict(lista:dict):
        indice = Indice(tp_indice = lista['tp_indice'], dt_referencia = lista['dt_referencia'], val_indice = lista['val_indice'], dt_inclusao = lista['dt_inclusao'])

