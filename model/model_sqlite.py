# @app.route('/api/v1/resources/percursos', methods=['GET'])
# def api_filter():
#     query_parameters = request.args

#     id = query_parameters.get('id')
#     nome = query_parameters.get('published')
#     descricao = query_parameters.get('author')

#     query = "SELECT * FROM percursos WHERE"
#     to_filter = []

#     if id:
#         query += ' id=? AND'
#         to_filter.append(id)
#     if nome:
#         query += ' nome=? AND'
#         to_filter.append(nome)
#     if descricao:
#         query += ' descricao=? AND'
#         to_filter.append(descricao)
#     if not (id or nome or descricao):
#         return page_not_found(404)

#     query = query[:-4] + ';'

#     conn = sqlite3.connect('twt.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()

#     results = cur.execute(query, to_filter).fetchall()

#     return jsonify(results)

# @app.route('/api/v1/resources/percursos/all', methods=['GET'])
# def api_all():
#     conn = sqlite3.connect('twt.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     all_books = cur.execute('SELECT * FROM percursos;').fetchall()

#     return jsonify(all_books)

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d