# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext, ROUND_HALF_UP
# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa classe para Enumeradores
from enum import Enum
# Importa a classe base
from negocio.baseobject import BaseObject
from negocio.gestaocadastro import GestaoCadastro
from negocio.indexador import TipoIndexador
from negocio.calendario import Calendario
# Import o módulo para cálculos matemáticos
import math
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
from utils.helper import BusinessException

class Investimento(BaseObject):
    """Classe que representa um Investimento.
    
    Argumentos:
        valInvestimentoInicial: valor inicial do investimento
        indexador: nome identificador do indexador (ex.: ipca, selic)
        taxa: percentual aplicado sobre o índice (ex.: 130 (130% do cdi), 7 (IPCA + 7%))
        dataInicial: data inicial do investimento
        dataFinal (datetime): data de vencimento do investimento
    """
    # Método criador 
    def __init__(self, tipoInvestimento: str, tipoRendimento: str, valInvestimentoInicial: Decimal, indexador: str, taxa: Decimal, taxaPrefixada: Decimal, dataInicial: datetime, dataFinal: datetime):
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.tipoInvestimento = tipoInvestimento
        self.tipoRendimento = tipoRendimento
        self.valInvestimentoInicial = Decimal(valInvestimentoInicial)
        self.indexador = indexador
        self.taxa = Decimal(taxa)
        self.taxaPrefixada = Decimal(taxaPrefixada)
        self.dataInicial = dataInicial
        self.dataFinal = dataFinal
        # Inicializa demais atributos da classe
        self.valSaldoBruto = Decimal(0)
        self.rentabilidadeBruta = Decimal(0)
        self.percRentabilidadeBruta = Decimal(0)
        self.percRentabilidadeBrutaDiaria = Decimal(0)
        self.percRentabilidadeBrutaMensal = Decimal(0)
        self.percRentabilidadeBrutaAnual = Decimal(0)
        self.rentabilidadeLiquida = Decimal(0)
        self.percRentabilidadeLiquida = Decimal(0)
        self.percRentabilidadeLiquidaDiaria = Decimal(0)
        self.percRentabilidadeLiquidaMensal = Decimal(0)
        self.percRentabilidadeLiquidaAnual = Decimal(0)
        self.percImpostoRenda = Decimal(0)
        self.valImpostoRenda = Decimal(0)
        self.percIOF = Decimal(0)
        self.valIOF = Decimal(0)
        self.qtdDiasCorridos = int(0)
        self.qtdDiasUteis = int(0)
        self.valSaldoLiquido = Decimal(0)
        self.evolucao = []

    def calcular_investimento(self):
        """Realiza o cálculo do investimento em função do período informado.
    
        Retorno:
            Retorna uma lista contendo dictionaries referentes aos valores 
            de saldo e rentabilidade do investimento além de uma sublista 
            da evolução do valor inicial em função do tempo (período informado)
        """
        # Validação - data inicial mínima
        if self.dataInicial < datetime(2001, 1, 1).date():
            mensagem  = "Data inicial do investimento deve ser maior ou igual a 01/01/2001."
            raise BusinessException('BE001', mensagem)
        # Validação - data final máxima
        elif self.dataFinal > datetime(2078, 12, 31).date():
            mensagem  = "Data final do investimento não pode ser maior que 31/12/2078."
            raise BusinessException('BE002', mensagem)
        # Validação - período de investimento
        elif self.dataFinal <= self.dataInicial:
            mensagem  = "Data final do investimento deve ser maior que a data inicial."
            raise BusinessException('BE003', mensagem)
        # Validação - Valor inicial de investimento
        elif self.valInvestimentoInicial <= Decimal(0):
            mensagem  = "Valor inicial do investimento deve ser maior que 0 (zero)."
            raise BusinessException('BE004', mensagem)
        # Validação - Tipo de investimento inválido
        elif self.tipoInvestimento.lower() not in TipoInvestimento.values():
            mensagem  = "Tipo de investimento inválido [{0}]. Tipos esperado: {1}.".format(self.tipoInvestimento.lower(), TipoInvestimento.values())
            raise BusinessException('BE005', mensagem)
        elif self.tipoRendimento.lower() == 'pre':
            if self.taxaPrefixada <= Decimal(0):
                mensagem  = "Você deve informar a taxa prefixada."
                raise BusinessException('BE006', mensagem)
        elif self.tipoRendimento.lower() == 'pos' or self.tipoRendimento.lower() == 'hibrido':
            # Validação - Tipo de indexador inválido
            if self.indexador.lower() not in TipoIndexador.values():
                mensagem  = "Tipo de indexador inválido [{0}]. Tipos esperado: {}.".format(self.indexador.lower(), TipoIndexador.values())
                raise BusinessException('BE007', mensagem)
            elif self.taxa <= Decimal(0):
                mensagem  = "Você deve informar a taxa sobre o indexador pós fixado."
                raise BusinessException('BE008', mensagem)
            elif self.tipoRendimento.lower() == 'hibrido':
                if self.taxaPrefixada <= Decimal(0):
                    mensagem  = "Você deve informar a taxa prefixada."
                    raise BusinessException('BE009', mensagem)        

        
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        getcontext().rounding = ROUND_HALF_UP

        # Inicializa o valor de investimento atualizado onde serão aplicados índices por período
        self.valSaldoBruto = self.valInvestimentoInicial

        objCadastro = GestaoCadastro()
        # Executa a consulta e armazena numa lista
        indices = []
        if self.tipoRendimento.lower() != 'pre':
            indices = objCadastro.list_indices(self.indexador.lower(), self.dataInicial, self.dataFinal)
        
        # Calcula a quantidade de dias corridos do investimento
        self.qtdDiasCorridos = (self.dataFinal - self.dataInicial).days
        
        # Define a variável do dicionário que armazenará a evolução do valor investido de acordo 
        # com a peridicidade do índice (diariamente ou mensalmente)
        resultadoInvestimento = {}
        # Se taxa prefixada foi informada recupera a taxa diária correspondente
        taxaPrefixadaDiaria = 0
        if self.taxaPrefixada > Decimal(0):
            taxaPrefixadaDiaria = self.taxaAnualToDiaria(self.taxaPrefixada)
  
        dtReferencia = self.dataInicial
        # Varre a lista de índices para calcular a evolução
        for indice in indices:
            # Formata a data de referência
            dtReferencia = indice['dt_referencia']
            # Formata o valor do índice
            valIndice = indice['val_indice']
            valIndice = Decimal(valIndice)
            # Se taxa em relação ao índice foi informada aplica sobre o índice obtido
            if self.taxa > Decimal(0):
                valIndice = valIndice * (self.taxa / Decimal(100))
            # Majora a taxa do índice com o valor prefixado
            valIndice = valIndice + taxaPrefixadaDiaria
                
            # Atualizado Saldo Bruto do investimento
            self.valSaldoBruto = self.valSaldoBruto * (1 + (valIndice / Decimal(100)))
            self.valSaldoBruto = Decimal(round(float(self.valSaldoBruto),2))
            self.evolucao.append({'dtReferencia': dtReferencia, 'valIndice': float(valIndice), 'valSaldoBruto': float(self.valSaldoBruto)})

        if len(indices) > 0:
            dtReferencia = dtReferencia + timedelta(days=1)

        if dtReferencia < self.dataFinal:
            # Recupera os dados do indexador
            if self.tipoRendimento.lower() != 'pre':
                objIndexador = objCadastro.get_indexador(self.indexador.lower())
                valIndice = objIndexador.val_ultimo_indice
            else:
                valIndice = Decimal(0)
             # Se taxa em relação ao índice foi informada aplica sobre o índice obtido
            if self.taxa > Decimal(0):
                valIndice = valIndice * (self.taxa / Decimal(100))
            # Majora a taxa do índice com o valor prefixado
            valIndice = valIndice + taxaPrefixadaDiaria
            for dtUtil in Calendario.listDiasUteis(dtReferencia, self.dataFinal):
                # Atualizado Saldo Bruto do investimento
                self.valSaldoBruto = self.valSaldoBruto * (1 + (valIndice / Decimal(100)))
                self.valSaldoBruto = Decimal(round(float(self.valSaldoBruto),2))
                self.evolucao.append({'dtReferencia': dtUtil, 'valIndice': float(valIndice), 'valSaldoBruto': float(self.valSaldoBruto)})


        # Calcula a quantidade de dias úteis considerados no investimentos
        self.qtdDiasUteis = len(self.evolucao)
        ### Atualiza resultados do investimento ###
        # Rentabilidade bruta
        self.rentabilidadeBruta = self.valSaldoBruto - self.valInvestimentoInicial
        self.percRentabilidadeBruta = ((self.valSaldoBruto / self.valInvestimentoInicial)-1) * Decimal(100)
        self.percRentabilidadeBrutaDiaria = self.taxaPeriodo(self.percRentabilidadeBruta, self.qtdDiasUteis)
        self.percRentabilidadeBrutaMensal = self.taxaJuros(self.percRentabilidadeBrutaDiaria, 21)
        self.percRentabilidadeBrutaAnual = self.taxaJuros(self.percRentabilidadeBrutaDiaria, 252)
        # Imposto de renda
        if self.tipoInvestimento.lower() in ['poupanca', 'lci', 'lca']:
            self.percImpostoRenda = Decimal(0)
        else:
            self.percImpostoRenda = self.obterPercIR(self.qtdDiasCorridos)
        self.valImpostoRenda = self.rentabilidadeBruta * (self.percImpostoRenda / Decimal(100))
        # IOF
        # TODO: Incluir obtenção do perc e cálculo de IOF de acordo com a qtdDiasCorridos
        # Rentabilidade Líquida
        self.rentabilidadeLiquida = self.rentabilidadeBruta - self.valImpostoRenda - self.valIOF
        # Saldo Líquido
        self.valSaldoLiquido = self.valInvestimentoInicial + self.rentabilidadeLiquida
        # % Rentabilidade
        self.percRentabilidadeLiquida = ((self.valSaldoLiquido / self.valInvestimentoInicial)-1) * Decimal(100)
        self.percRentabilidadeLiquidaDiaria = self.taxaPeriodo(self.percRentabilidadeLiquida, self.qtdDiasUteis)
        self.percRentabilidadeLiquidaMensal = self.taxaJuros(self.percRentabilidadeLiquidaDiaria, 21)
        self.percRentabilidadeLiquidaAnual = self.taxaJuros(self.percRentabilidadeLiquidaDiaria, 252)

        # for index, item in enumerate(times_ordenados, start=1):
        #     item['class_gols_pro_mand'] = index 

        return self
    
    @classmethod
    def taxaPeriodo(cls, taxa:Decimal, qtdPeriodos:Decimal):
        """Converte uma taxa em sua equivalente na quantidade de períodos informada.
    
        Argumentos: 
            taxa: taxa a ser convertida
            qtdPeriodos: quantidade de períodos (dias, meses, anos)
        Retorno:
            Retorna um decimal representando a taxa calculada equivalente ao período informado.
        """
        taxaInformada = Decimal(1) + (Decimal(taxa) / Decimal(100))
        taxaPeriodo = Decimal(taxaInformada ** Decimal(1 / qtdPeriodos)) - Decimal(1)
        taxaPeriodo = taxaPeriodo * Decimal(100)

        return taxaPeriodo

    @classmethod
    def taxaJuros(cls, taxa:Decimal, qtdPeriodos:Decimal):
        """Converte uma taxa em sua equivalente após aplicada juros sobre juros na quantidade de períodos informada.
    
        Argumentos: 
            taxa: taxa inicial a ser aplicado o cálculo de juros
            qtdPeriodos: quantidade de períodos (dias, meses, anos...)
        Retorno:
            Retorna um decimal representando a taxa calculada equivalente com juros sobre juros na quantidade de períodos informada.
        """
        taxaInformada = Decimal(1) + (Decimal(taxa) / Decimal(100))
        taxaJuros = Decimal(taxaInformada ** Decimal(qtdPeriodos)) - Decimal(1)
        taxaJuros = taxaJuros * Decimal(100)

        return taxaJuros
    
    @classmethod
    def taxaAnualToMensal(cls, taxaAnual:Decimal):
        """Converte uma taxa anual em taxa mensal.

        Argumentos: 
            taxaAnual: taxa Anual a ser convertida
        Retorno:
            Retorna um decimal representando a taxa mensal calculada.
        """
        return cls.taxaPeriodo(taxaAnual, 12)

    @classmethod
    def taxaAnualToDiaria(cls, taxaAnual:Decimal):
        """Converte uma taxa anual em taxa diária.

        Argumentos: 
            taxaAnual: taxa Anual a ser convertida
        Retorno:
            Retorna um decimal representando a taxa diária calculada.
        """
        return cls.taxaPeriodo(taxaAnual, 252)

    def obterPercIR(self, qtdDiasCorridos:int):
        """Identifica o percentual de Imposto de renda aplicável de acordo com a quantidade 
        de dias corridos do investimento.
    
        Retorno:
            Retorna um decimal representando o percentual de IR a ser aplicado sob o rendimento
            do investimento.
        """
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        percIR = Decimal(0)

        # TODO: criar entidade no banco de dados com os intervalos e respectivos % para flexibilizar 
        # manutenção dos intervalos e %s
        if qtdDiasCorridos <= 180:
            percIR = 22.5
        elif qtdDiasCorridos <= 360:
            percIR = 20
        elif qtdDiasCorridos <= 720:
            percIR = 17.5
        else:
            percIR = 15
        
        return Decimal(percIR)

# Enum de tipos de investimento - para evitar buscas excessivas no banco dado que não não mudam tanto
class TipoInvestimento(Enum):
    ''' Enum que define os tipos das investimentos disponíveis para cálculo
    '''
    POUPANCA = 'poupanca'
    CDB = 'cdb'
    LCI = 'lci'
    LCA = 'lca'

    @classmethod
    def values(cls):
        lista = []
        for item in cls.__members__.values():
	        lista.append(item.value)
        lista.sort()
        return lista
