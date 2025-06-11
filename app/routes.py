from flask import Flask, render_template, request, redirect, url_for, session
from app.config import criar_conexao

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões

# Credenciais fixas
USERNAME = 'admin'
PASSWORD = 'senha123'

@app.route('/menu')
def menu():
    return render_template('index.html')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('exibir_dados'))
    else:
        return "Credenciais inválidas! <a href='/'>Tente novamente</a>"
    
@app.route('/dados')
def exibir_dados():
    # Verifica se o usuário está logado
    if not session.get('logged_in') or session.get('username') != USERNAME:
        return redirect(url_for('login'))
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        
        # Consultar dados da tabela vendedores
        cursor.execute("SELECT * FROM vendedores")
        vendedores = cursor.fetchall()
        
        # Consultar dados da tabela pedidos com o nome do vendedor
        cursor.execute("""
            SELECT pedidos.id, pedidos.cliente, pedidos.descricao, pedidos.pago, vendedores.nome AS vendedor_nome
            FROM pedidos
            JOIN vendedores ON pedidos.id_vendedor = vendedores.id
        """)
        pedidos = cursor.fetchall()
        
        cursor.close()
        conexao.close()
        
        return render_template('dados.html', vendedores=vendedores, pedidos=pedidos)
    else:
        return "Erro ao conectar ao banco de dados."

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))
@app.route('/editar_vendedor', methods=['POST'])
def editar_vendedor():
    id_vendedor = request.form.get('id_vendedor')
    nome = request.form.get(f'nome_{id_vendedor}')
    chave = request.form.get(f'chave_{id_vendedor}')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE vendedores SET nome = %s, chave = %s WHERE id = %s",
            (nome, chave, id_vendedor)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return "Vendedor atualizado com sucesso! <a href='/dados'>Voltar</a>"
    else:
        return "Erro ao conectar ao banco de dados."

@app.route('/editar_pedido', methods=['POST'])
def editar_pedido():
    id_pedido = request.form.get('id_pedido')
    descricao = request.form.get(f'descricao_{id_pedido}')
    pago = request.form.get(f'pago_{id_pedido}')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "UPDATE pedidos SET descricao = %s, pago = %s WHERE id = %s",
            (descricao, pago, id_pedido)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return "Pedido atualizado com sucesso! <a href='/dados'>Voltar</a>"
    else:
        return "Erro ao conectar ao banco de dados."
    
@app.route('/excluir_pedido', methods=['POST'])
def excluir_pedido():
    id_pedido = request.form.get('id_pedido')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id = %s", (id_pedido,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return "Pedido excluído com sucesso! <a href='/dados'>Voltar</a>"
    else:
        return "Erro ao conectar ao banco de dados."
    
@app.route('/excluir_vendedor', methods=['POST'])
def excluir_vendedor():
    id_vendedor = request.form.get('id_vendedor')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM vendedores WHERE id = %s", (id_vendedor,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return "Vendedor excluído com sucesso! <a href='/dados'>Voltar</a>"
    else:
        return "Erro ao conectar ao banco de dados."

@app.route('/adicionar_vendedor', methods=['POST'])
def adicionar_vendedor():
    nome = request.form.get('nome')
    chave = request.form.get('chave')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO vendedores (nome, chave) VALUES (%s, %s)",
            (nome, chave)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return "Vendedor adicionado com sucesso! <a href='/dados'>Voltar</a>"
    else:
        return "Erro ao conectar ao banco de dados."
    
@app.route('/login_venda')
def login_venda():
    return render_template('login_venda.html')

@app.route('/autenticar_venda', methods=['POST'])
def autenticar_venda():
    chave = request.form.get('chave')
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id FROM vendedores WHERE chave = %s", (chave,))
        vendedor = cursor.fetchone()
        cursor.close()
        conexao.close()
        
        if vendedor:
            session['vendedor_id'] = vendedor['id']
            return redirect(url_for('registrar_venda'))
        else:
            return "Chave inválida! <a href='/login_venda'>Tente novamente</a>"
    else:
        return "Erro ao conectar ao banco de dados."

@app.route('/registrar_venda', methods=['GET', 'POST'])
def registrar_venda():
    if not session.get('vendedor_id'):
        return redirect(url_for('login_venda'))
    
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        ingredientes = request.form.getlist('ingredientes')
        todos_ingredientes = ['iscas de carne', 'tomate', 'cebola', 'milho', 'ervilha', 'alface', 'ketchup', 'mostarda', 'maionese', 'ovo']
        
        # Ingredientes desmarcados
        desmarcados = [f"S/ {ing}" for ing in todos_ingredientes if ing not in ingredientes]
        descricao = " ".join(desmarcados)
        
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO pedidos (cliente, descricao, id_vendedor) VALUES (%s, %s, %s)",
                (cliente, descricao, session['vendedor_id'])
            )
            conexao.commit()
            cursor.close()
            conexao.close()
            return "Venda registrada com sucesso! <a href='/registrar_venda'>Registrar outra venda</a>"
        else:
            return "Erro ao conectar ao banco de dados."
    
    return render_template('registrar_venda.html')

@app.route('/calcular_lucro', methods=['POST'])
def calcular_lucro():
    gastos = float(request.form.get('gastos'))
    valor_venda = float(request.form.get('valor_venda'))
    
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) AS total_vendas FROM pedidos")
        total_vendas = cursor.fetchone()[0]  # Acessa o primeiro elemento da tupla
        cursor.close()
        conexao.close()
        
        lucro = (valor_venda * total_vendas) - gastos
        return render_template('dados.html', lucro=lucro, vendedores=[], pedidos=[])
    else:
        return "Erro ao conectar ao banco de dados."
    
@app.route('/ranking_vendedores')
def ranking_vendedores():
    conexao = criar_conexao()
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT vendedores.nome, COUNT(pedidos.id) AS total_vendas
            FROM vendedores
            LEFT JOIN pedidos ON vendedores.id = pedidos.id_vendedor
            GROUP BY vendedores.nome
            ORDER BY total_vendas DESC
        """)
        ranking = cursor.fetchall()
        cursor.close()
        conexao.close()
        
        return render_template('ranking.html', ranking=ranking)
    else:
        return "Erro ao conectar ao banco de dados."