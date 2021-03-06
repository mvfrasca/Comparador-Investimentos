# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe Indice')
logger.setLevel(logging.INFO)

class Indice(BaseObject):
    """Classe que representa um Índice.
    
    Argumentos:
        tp_indice: tipo de índice (indexador). Ex.: ipca, poupanca, cdi.
        dt_referencia: data de referência do índice (formato datetime.date)
        val_indice: valor do índice em percentual. Ex.: 0.0123
        dth_inclusao: data/hora da inclusão do índice na base de dados de índices (formato datetime)
    """
    # Método criador
    def __init__(self, tp_indice: str, dt_referencia: datetime.date, val_indice: float, dth_inclusao: datetime):
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        # Define chave única para o índice
        self.id = tp_indice.lower() + '-' + datetime.strftime(dt_referencia,"%Y%m%d")
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.tp_indice = tp_indice.lower()
        self.dt_referencia = dt_referencia
        self.val_indice = val_indice
        self.dth_inclusao = dth_inclusao




