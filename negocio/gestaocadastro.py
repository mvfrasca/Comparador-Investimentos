# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa módulo para tratamento de arquivos json
import json
# Importa módulo para tratamento de arquivos csv
import csv
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
from utils.helper import _strdate_to_int
from utils.helper import _date_to_int
from utils.helper import _intdate_to_str
from utils.helper import InputException
from utils.helper import BusinessException
from utils.helper import ServerException
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject
# Importa outras classes de negócio
from negocio.bancocentral import BancoCentral
from negocio.indice import Indice

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe GestaoCadastro')
logger.setLevel(logging.INFO)

class GestaoCadastro(BaseObject):
    """Classe que gerencia os cadastros que dão suporte aos cálculos de investimento.
    """
    def __init__(self):
       pass
    
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
            indexadores = list(map(lambda item: _converter_datas_dict(item, datas_converter), indexadores))
            # Loga os estado atual do indicador
            logger.info("Carga inicial de indexadores")
            logger.info('indexadores = {}'.format(indexadores))
            # Inclui/atualiza a base de dados com os indexadores
            tipoEntidade = get_model().TipoEntidade.INDEXADORES
            get_model().update_multi(tipoEntidade, indexadores)

        return
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
    
    def criar_feriados(self):
        """Realiza a carga inicial das entidades que representarão os feriados bancários.
           CSV extraído de http://www.anbima.com.br/feriados/feriados.asp
        Retorno:
            Quantidade de feriados incluidos.
        """
        # Carrega arquivo CSV que contém a carga inicial dos feriados
        with open(r'''static\json\feriados.csv''',encoding='UTF8') as f:
            reader = csv.reader(f, delimiter=';')
            feriados = []
            
            for linha in reader:
                # Recupera atributo data da linha do arquivo e formata com padrão de data inteiro
                dt_feriado = _strdate_to_int(linha[0], "%d/%m/%Y")
                # Prepara o dicionário com os atributos da entidade feriado
                feriado = {'id': dt_feriado, 'dt_feriado': dt_feriado, 'descricao': linha[2]}
                feriados.append(feriado)

            # Loga os estado atual do indicador
            logger.info("Carga inicial de feriados. Qtd. feriados carregada: {}".format(len(feriados)))
            # Inclui/atualiza a base de dados com os indexadores
            tipoEntidade = get_model().TipoEntidade.FERIADOS
            get_model().update_multi(tipoEntidade, feriados)

        return len(feriados)

    def list_indexadores(self, dataReferencia: int=None):
        """Obtém a lista de indexadores disponíveis cuja data de última atualização é anterior ao argumento dataReferencia.
        
        Argumentos:
            - dataReferencia: data de referencia que limita a consulta aos indexadores cuja data de última 
            atualização seja anterior ao referido argumento. Quando não informada ou for informada como None,
            todos os indexadores cadastrados são retornados.
        """
        # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à dt_referencia)
        return get_model().list_indexadores(dataReferencia)
        # TODO: Avaliar para transformar em lista de objetos indexador

    def get_indexador(self, id: str):
        """Retorna o indexador de acordo com o id solicitado

        Argumentos:
            id: código identificador do indexador. Ex.: ipca, cdi, poupanca.
        """
        # Obtém os dados do indexador solicitado
        tipoEntidade = get_model().TipoEntidade.INDEXADORES
        return get_model().read(tipoEntidade, id.lower())
    
    def list_indices(self, indexador: str, dataInicial: int, dataFinal: int ):
        """Retorna o indexador de acordo com o id solicitado

        Argumentos:
            indexador: código identificador do indexador. Ex.: ipca, cdi, poupanca.
            dataInicial: data inicial do período de índices a ser consultado.
            dataFinal: data final do período de índices a ser consultado.
        """
        # Obtém os dados dos índices solicitados 
        # Executa a consulta e armazena num dictionary 
        indices = get_model().list_indices(indexador, dataInicial, dataFinal)

        return indices

    def atualizar_indices(self):
        """Atualiza os índices dos indexadores cadastrados. Obtém os índices atualizados desde a 
        última data de referência importada da API do Banco Central.
        """
        try:
            # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
            # zerados caso contrário datastore não reconhece)
            #dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
            dataAtual = _date_to_int(datetime.now())
            # Inicializa o contador geral de registros atualizados
            contadorTotal = 0
            # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à data atual)
            indexadores = self.list_indexadores(dataAtual)
            # TODO: Converter para lista de objetos Indexador
        except BusinessException as be:
            raise be
        except Exception as e:
            raise ServerException(e)

        # Percorre os indexadores para consulta e atualização
        for indexador in indexadores:
            # Loga os estado atual do indexador
            logger.info('Indexador a receber atualização de índices: {}'.format(indexador))
            # Obtém os dados do indexador
            serie = indexador['serie']
            tipoIndice = indexador['id']
            dataUltReferencia = indexador['dt_ult_referencia']
            periodicidade = indexador['periodicidade']
            # Caso o índicador seja de peridicidade mensal e o mês da última atualização é igual ao 
            # mês atual pula para o próximo indexador
            # if (periodicidade.lower() == 'mensal') and (datetime.strftime(dataAtual, "%Y%m") == datetime.strftime(dataUltReferencia, "%Y%m")):
            #     # Pula para o próximo indexador
            #     continue
            # Instancia a classe de negócios responsável pela consulta à API do Banco Central
            objBC = BancoCentral()
            # Recupera indices disponíveis do indexador desde a última atualização até hoje 
            indicesAPI = objBC.list_indices(serie, dataUltReferencia, dataAtual)

            # Inicializa coleção e contadores
            indicesConsistir = []
            contadorParcial = 0
            contador = 0
            
            # Varre a lista de índices retornadas pela API
            for indiceAPI in indicesAPI:
                logger.info('Índice a ser atualizado: {0}, dados: {1}'.format(tipoIndice, indiceAPI))
                # Recupera as propriedades do índice (data e valor)
                dataReferencia = indiceAPI['data']
                valorIndice = float(indiceAPI['valor'])
                # Verifica se data de referência do índice é anterior à data da última atualização 
                # e caso positivo pula para o próximo (API do BC retornar sempre um dia pra tras)]
                # if (dataReferencia.isocalendar() <= dataUltReferencia.isocalendar()):
                #     logger.info('Índice descartado por ser anterior a última atualização')
                #     continue
        
                # Popula uma instancia de índice a ser consistida
                indice = Indice(tp_indice = tipoIndice, dt_referencia = dataReferencia, val_indice = valorIndice, dt_inclusao = datetime.now())

                # Inclui o índice na coleção de índices a ser consistida em banco de dados
                indicesConsistir.append(indice)

                # Atualiza contadores
                contadorParcial = contadorParcial + 1
                contador = contador + 1

                # Caso coleção chegou em 100 itens libera a gravação em lote em banco de dados 
                # para não sobrecarregar chamada à API do banco de dados
                if contadorParcial == 100:
                    # TODO: Ajustar para atualizar a partir de GestaoCadastro
                    tipoEntidade = get_model().TipoEntidade.INDICES
                    get_model().update_multi(tipoEntidade, indicesConsistir)
                    indicesConsistir = []
                    contadorParcial = 0
                    # Atualiza a data do último índice armazanado na entidade do indexador correspondente 
                    # para controle de próximas atualizações
                    # TODO: Ajustar para atualizar a partir de GestaoCadastro utilizando objeto Indexador
                    indexador['dt_ult_referencia'] = dataReferencia
                    indexador['dt_ult_atualiz'] = datetime.now()
                    indexador['qtd_regs_ult_atualiz'] = contador
                    tipoEntidade = get_model().TipoEntidade.INDEXADORES
                    get_model().update(tipoEntidade, indexador, tipoIndice)

            # Realiza a gravação em lote dos índices no banco de dados caso algum registro tenha
            # sido tratado
            if contadorParcial > 0:
                # TODO: Ajustar para atualizar a partir de GestaoCadastro
                tipoEntidade = get_model().TipoEntidade.INDICES
                get_model().update_multi(tipoEntidade, indicesConsistir)
                # Atualiza a data do último índice armazanado na entidade do indexador correspondente 
                # para controle de próximas atualizações
                # TODO: Ajustar para atualizar a partir de GestaoCadastro utilizando objeto Indexador
                indexador['dt_ult_referencia'] = dataReferencia
                indexador['dt_ult_atualiz'] = datetime.now()
                indexador['qtd_regs_ult_atualiz'] = contador
                tipoEntidade = get_model().TipoEntidade.INDEXADORES
                get_model().update(tipoEntidade, indexador, tipoIndice)

            contadorTotal = contadorTotal + contador

        return contadorTotal