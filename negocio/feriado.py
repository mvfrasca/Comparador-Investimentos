# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe Feriado')
logger.setLevel(logging.INFO)

class Feriado(BaseObject):
    """Classe que representa um Feriado.
    
    Argumentos:
        dt_feriado: data do feriado (formato datetime.date)
        descricao: nome do feriado
    """
    # Método criador
    def __init__(self, dt_feriado: datetime.date, descricao: str):
        # Define chave única para o índice
        self.id = datetime.strftime(dt_feriado,"%Y%m%d")
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.dt_feriado = dt_feriado
        self.descricao = descricao


