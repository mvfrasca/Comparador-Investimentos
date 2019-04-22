# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe Feriado')
logger.setLevel(logging.INFO)

class Indice(BaseObject):
    """Classe que representa um Feriado.
    
    Argumentos:
        dt_feriado: data do feriado (formato datetime.date)
        descricao: nome do feriado
    """
    # Método criador
    def __init__(self, dt_feriado: datetime.date, descricao: str):
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        # Define chave única para o índice
        self.id = datetime.strftime(dt_feriado,"%Y%m%d")
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.dt_feriado = dt_feriado
        self.descricao = descricao

    
    @classmethod
    def listDiasUteis(cls, dataInicial:datetime.date, dataFinal:datetime.date, feriados:list):
        """Lista os dias úteis referente ao período solicitado considerando a lista de feriados informada.

        Argumentos: 
            - dataInicial: data inicial do período
            - dataFinal: data final do período
            - feriados: lista com feriados no tipo Feriado
        Retorno:
            - Lista com itens no formato dict contendo os dias úteis do período solicitado. 
            Ex. retorno: [{"data": datetime.date(2019, 4, 30), "data": datetime.date(2019, 5, 2), ... }]
        """
        if not type(dataInicial).__name__ == 'date':
            raise TypeError('listDiasUteis: argumento dataInicial deve ser do tipo datetime.date')
        elif not type(dataFinal).__name__ == 'date':
            raise TypeError('listDiasUteis: argumento dataFinal deve ser do tipo datetime.date')
        elif not isinstance(feriados, dict):
            raise TypeError('listDiasUteis: argumento feriados deve ser do tipo dict')
        elif dataFinal < dataInicial:
            raise ValueError("Data final do período deve ser maior ou igual à data inicial.")
        
        try:
            data = dataInicial
            while data <= dataFinal:
                # Se dia da semana for sábado (5) ou domingo (6)
                if datetime.now().date().weekday() in (5,6) 
                    continue # pula para próxima data
                # elif data in feriados.
                #     #TODO: TERMINAR FERIADOS
                #     continue # pula para próxima data
                # Acrescenta 1 dia
                data+= timedelta(days=1)

        except Exception:
            raise ValueError('Formato inválido de dados de entrada - dataInicial: {0}, dataFinal: {1}, feriados: {2}'.format(dataInicial, dataFinal, feriados))
        
        return periodo





