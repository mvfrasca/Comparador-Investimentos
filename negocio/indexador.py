# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject
# Importa classe para Enumeradores
from enum import Enum

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe Indexador')
logger.setLevel(logging.INFO)

class Indexador(BaseObject):
    """Classe que representa um Indexador.
    
    Argumentos:
        id: identificador do indexador. Ex.: ipca, poupanca, cdi.
        nome: nome de apresentação do indexador.
        dt_ult_referencia: última data de referência importada do tipo indexador na entidade de Índices (formato datetime.date).
        periodicidade: periodicidade correspondente do indexador. Esperado: Mensal, Diário.
        tipo_atualizacao: forma de atualização dos índices do indexador. Esperado: automatica (através de consulta à API do Banco Central) ou calculada (calculada com base em outro índice de periodicidade diferente).
        serie: Número da série histórica do indexador na API do Banco Central.
        qtd_regs_ult_atualiz: quantidade de índices incluida/atualizada na última atualização.
        dth_ult_atualiz: data/hora da da última atualização de índices na base de dados de índices (formato datetime)
    """
    # Método criador
    def __init__(self, id: str, nome: str, dt_ult_referencia: datetime.date, periodicidade: str, tipo_atualizacao: str, serie: str, qtd_regs_ult_atualiz: int, dth_ult_atualiz: datetime):
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.id = id.lower()
        self.nome = nome
        self.dt_ult_referencia = dt_ult_referencia
        self.periodicidade = periodicidade
        self.tipo_atualizacao = tipo_atualizacao
        self.serie = serie
        self.qtd_regs_ult_atualiz = qtd_regs_ult_atualiz
        self.dth_ult_atualiz = dth_ult_atualiz

# Enum de tipos de indexadores - para evitar buscas excessivas no banco dado que não não mudam tanto
class TipoIndexador(Enum):
    ''' Enum que define os tipos das indexadores disponíveis para cálculo de investimento
    '''
    CDI = 'cdi'
    IGPM = 'igpm'
    IPCA = 'ipca'
    POUPANCA = 'poupanca'
    SELIC = 'selic'

    @classmethod
    def values(cls):
        lista = []
        for item in cls.__members__.values():
	        lista.append(item.value)
        lista.sort()
        return lista

# Enum de tipos de atualização de índices dos indexadores - para evitar buscas excessivas no banco dado que não não mudam tanto
class TipoAtualizacao(Enum):
    ''' Enum que define os tipos das atualização possíveis para um indexador
    '''
    AUTOMATICA = 'automatica'
    CALCULADA = 'calculada'

    @classmethod
    def values(cls):
        lista = []
        for item in cls.__members__.values():
	        lista.append(item.value)
        lista.sort()
        return lista
