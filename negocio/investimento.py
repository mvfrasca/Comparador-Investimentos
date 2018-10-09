# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext, ROUND_HALF_UP
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa a classe base
from negocio.baseobject import BaseObject
from negocio.gestaocadastro import GestaoCadastro
# Import o módulo para cálculos matemáticos
import math

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
    def __init__(self, tipoInvestimento: str, valInvestimentoInicial: Decimal, indexador: str, taxa: Decimal, dataInicial: datetime, dataFinal: datetime):
        # Define a precisão para 7 casas decimais
        getcontext().prec = 17
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.tipoInvestimento = tipoInvestimento.lower()
        self.valInvestimentoInicial = Decimal(valInvestimentoInicial)
        self.indexador = indexador.lower()
        self.taxa = Decimal(taxa)
        self.dataInicial = dataInicial 
        self.dataFinal = dataFinal
        # Inicializa demais atributos da classe
        self.valSaldoBruto = Decimal(0)
        self.rentabilidadeBruta = Decimal(0)
        self.rentabilidadeBrutaAnual = Decimal(0)
        self.rentabilidadeLiquida = Decimal(0)
        self.rentabilidadeLiquidaAnual = Decimal(0)
        self.percImpostoRenda = Decimal(0)
        self.valImpostoRenda = Decimal(0)
        self.percIOF = Decimal(0)
        self.valIOF = Decimal(0)
        self.qtdDiasCorridos = int(0)
        self.valSaldoLiquido = Decimal(0)
        self.evolucao = []

    def calcular_investimento(self):
        """Realiza o cálculo do investimento em função do período informado.
    
        Retorno:
            Retorna uma lista contendo dictionaries referentes aos valores 
            de saldo e rentabilidade do investimento além de uma sublista 
            da evolução do valor inicial em função do tempo (período informado)
        """
        # Define a precisão para 7 casas decimais
        getcontext().prec = 17
        getcontext().rounding = ROUND_HALF_UP

        # Inicializa o valor de investimento atualizado onde serão aplicados índices por período
        self.valSaldoBruto = self.valInvestimentoInicial

        objCadastro = GestaoCadastro()
        # Executa a consulta e armazena num dictionary 
        indices = objCadastro.list_indices(self.indexador, self.dataInicial, self.dataFinal)
        
        # Calcula a quantidade de dias corridos do investimento
        self.qtdDiasCorridos = (self.dataFinal - self.dataInicial).days

        # Define a variável do dicionário que armazenará a evolução do valor investido de acordo 
        # com a peridicidade do índice (diariamente ou mensalmente)
        resultadoInvestimento = {}
        i = 0
        # Varre a lista de índices para aplicar os índices de acordo com a peridicidade do 
        # índice (diariamente ou mensalmente)
        for indice in indices:
            # Formata a data de referência
            data = datetime.strftime(indice['dt_referencia'], "%Y-%m-%d")
            # Formata o valor do índice
            valIndice = indice['val_indice']
            valIndice = Decimal(valIndice)
            # De acordo com o indexador carrega o valor do índice com a taxa informada
            if self.indexador in ['ipca', 'igpm']:
                # Ex.: IPCA + 7%
                taxaMensal = self.taxaAnualToMensal(self.taxa)
                valIndice = valIndice + taxaMensal
            elif self.indexador in ['cdi', 'selic']:
                # Ex.: 130% do CDI
                valIndice = valIndice * (self.taxa / Decimal(100))
            # Atualizado Saldo Bruto do investimento
            self.valSaldoBruto = self.valSaldoBruto * (1 + (valIndice / Decimal(100)))
            self.valSaldoBruto = Decimal(round(float(self.valSaldoBruto),2))

            self.evolucao.append({'data': data, 'indice': float(valIndice), 'valor': float(self.valSaldoBruto)})
            i = i + 1
            #print("Mês/Ano: {0}  |  Indice: {1:03.7}  |  Valor: {2:03.2f}".format(ano_mes, val_indice, val_investimento_atualizado))
        
        ### Atualiza resultados do investimento ###
        # Rentabilidade bruta
        self.rentabilidadeBruta = self.valSaldoBruto - self.valInvestimentoInicial
        # Imposto de renda
        if self.tipoInvestimento in ['poupanca', 'lci', 'lca']:
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

        # Monta o dictionary com o resultado do investimento para retorno do método
        resultadoInvestimento.update({'tipoInvestimento': self.tipoInvestimento.upper()})
        resultadoInvestimento.update({'indexador': self.indexador.upper()})
        resultadoInvestimento.update({'taxa': float(self.taxa)})
        resultadoInvestimento.update({'valInvestimentoInicial': float(self.valInvestimentoInicial)})
        resultadoInvestimento.update({'dataInicial': datetime.strftime(self.dataInicial, "%d/%m/%Y")})
        resultadoInvestimento.update({'dataFinal': datetime.strftime(self.dataFinal, "%d/%m/%Y")})
        resultadoInvestimento.update({'valSaldoBruto': float(self.valSaldoBruto)})
        resultadoInvestimento.update({'rentabilidadeBruta': float(self.rentabilidadeBruta)})
        resultadoInvestimento.update({'percImpostoRenda': float(self.percImpostoRenda)})
        resultadoInvestimento.update({'valImpostoRenda': float(self.valImpostoRenda)})
        resultadoInvestimento.update({'percIOF': float(self.percIOF)})
        resultadoInvestimento.update({'valIOF': float(self.valIOF)})
        resultadoInvestimento.update({'valSaldoLiquido': float(self.valSaldoLiquido)})
        resultadoInvestimento.update({'rentabilidadeLiquida': float(self.rentabilidadeLiquida)})
        resultadoInvestimento.update({'evolucao': self.evolucao})

        # for index, item in enumerate(times_ordenados, start=1):
        #     item['class_gols_pro_mand'] = index 

        return resultadoInvestimento

    def taxaAnualToMensal(self, taxaAnual:Decimal):
        """Converte uma taxa anual em taxa mensal.
    
        Retorno:
            Retorna um decimal representando a taxa mensal.
        """
        taxaAnual = taxaAnual / Decimal(100) 
        taxaMensal = Decimal(0)
        tempTaxaAnual = Decimal(1) + taxaAnual 
        taxaMensal = Decimal(math.pow(tempTaxaAnual, (Decimal(1 / 12))) - 1)
        taxaMensal = taxaMensal * Decimal(100)

        return taxaMensal

    def obterPercIR(self, qtdDiasCorridos:int):
        """Identifica o percentual de Imposto de renda aplicável de acordo com a quantidade 
        de dias corridos do investimento.
    
        Retorno:
            Retorna um decimal representando o percentual de IR a ser aplicado sob o rendimento
            do investimento.
        """
        # Define a precisão para 7 casas decimais
        getcontext().prec = 17
        percIR = Decimal(0)

        # TODO: criar entidade no banco de dados com os intervalos e respectivos % para flixibilizar 
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