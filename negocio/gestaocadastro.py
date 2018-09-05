# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model

class GestaoCadastro:
    def __init__(self):
        self.__init__
    
    def criarIndexadores(self):
        # if request.method == 'POST':
        #     data = request.form.to_dict(flat=True)

        #     book = get_model().create(data)

        #     return redirect(url_for('.view', id=book['id']))
        
        # with open('static\json\indicadores.json') as f:
        #     indicadores = f.buffer().json()
        #     # indicadores = list(map(lambda x: dict(x.keys(), x.values()), list(f)))
        # print(indicadores)
        # get_model().update_multi("Indicadores", indicadores)
        keys = []
        # Poupança
        indexador = {}
        indexador.update({'nome': 'Poupança'})
        indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indexador.update({'periodicidade': 'mensal'})
        indexador.update({'serie': '196'})
        indexador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indexadores', indexador, 'poupanca')
        keys.append({key})
        print(indexador)
        # IPCA
        indexador = {}
        indexador.update({'nome': 'IPCA'})
        indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indexador.update({'periodicidade': 'mensal'})
        indexador.update({'serie': '433'})
        indexador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indexadores', indexador, 'ipca')
        keys.append({key})
        # CDI
        indexador = {}
        indexador.update({'nome': 'CDI'})
        indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indexador.update({'periodicidade': 'diario'})
        indexador.update({'serie': '12'})
        indexador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indexadores', indexador, 'cdi')
        keys.append({key})
        # SELIC
        indexador = {}
        indexador.update({'nome': 'SELIC'})
        indexador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indexador.update({'periodicidade': 'diario'})
        indexador.update({'serie': '12'})
        indexador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indexadores', indexador, 'selic')
        keys.append({key})