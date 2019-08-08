# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo de log
import logging
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa a classe base
from negocio.baseobject import BaseObject
from negocio.feriado import Feriado

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe Feriado')
logger.setLevel(logging.INFO)

class Calendario(BaseObject):
    """Classe que representa um Calendario.
    """
    # Método criador
    def __init__(self):
        return None
    
    @classmethod
    def listDiasUteis(cls, dataInicial:datetime.date, dataFinal:datetime.date):
        """Lista os dias úteis referente ao período solicitado.

        Argumentos: 
            - dataInicial: data inicial do período
            - dataFinal: data final do período
        Retorno:
            - Lista com itens no formato dict contendo os dias úteis do período solicitado. 
            Ex. retorno: [{"data": datetime.date(2019, 4, 30)}, {"data": datetime.date(2019, 5, 2)}, ... ]
        """
        if not type(dataInicial).__name__ == 'date':
            raise TypeError('listDiasUteis: argumento dataInicial deve ser do tipo datetime.date')
        elif not type(dataFinal).__name__ == 'date':
            raise TypeError('listDiasUteis: argumento dataFinal deve ser do tipo datetime.date')
        elif dataFinal < dataInicial:
            raise ValueError("Data final do período deve ser maior ou igual à data inicial.")
        
        # Obtém a lista de feriados do período solicitado
        feriados = list(map(Feriado.fromDict, get_model().list_feriados(dataInicial, dataFinal)))
        # Define a variável que armazenará a lista de dias úteis do período solicitado
        diasUteis = []

        try:
            data = dataInicial
            while data <= dataFinal:
                # Se dia da semana for sábado (5) ou domingo (6)
                if data.date().weekday() not in (5,6) and data not in feriados:
                    diasUteis.append(data)
                # Acrescenta 1 dia
                data+= timedelta(days=1)

        except Exception:
            raise ValueError('Formato inválido de dados de entrada - dataInicial: {0}, dataFinal: {1}'.format(dataInicial, dataFinal))
        
        return diasUteis





