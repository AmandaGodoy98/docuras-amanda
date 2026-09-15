from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.utils import secure_filename

import os
import pymysql

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


app = Flask(__name__)

app.secret_key = "docuras-amanda-ac-2026"


# =========================================================
# CONFIGURAÇÕES
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "imagens")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# IMAGENS
# =========================================================

def extensao_permitida(nome_arquivo):

    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# CONEXÃO MYSQL
# =========================================================

def conectar_mysql(usar_banco=True):

    dados = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }

    if usar_banco:
        dados["database"] = DB_NAME

    return pymysql.connect(**dados)


# =========================================================
# CRIAR BANCO E TABELA
# =========================================================

def criar_banco_e_tabela():

    conexao = conectar_mysql(usar_banco=False)

    try:

        with conexao.cursor() as cursor:

            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                "CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_unicode_ci"
            )

        conexao.commit()

    finally:

        conexao.close()


    conexao = conectar_mysql()

    try:

        with conexao.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(120) NOT NULL,
                    categoria VARCHAR(60) NOT NULL,
                    descricao VARCHAR(500),
                    preco DECIMAL(10,2) NULL,
                    imagem VARCHAR(255),
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ENGINE=InnoDB
                DEFAULT CHARSET=utf8mb4
                """
            )

            cursor.execute(
                "ALTER TABLE produtos "
                "MODIFY preco DECIMAL(10,2) NULL"
            )

        conexao.commit()

    finally:

        conexao.close()


# =========================================================
# PRODUTOS INICIAIS
# =========================================================

def cadastrar_produtos_iniciais():

    produtos_iniciais = [

        (
            "Bolo Personalizado Rosé",
            "Bolos de Festa",
            "Bolo de festa personalizado. Consulte opções de massa, recheio e decoração pelo WhatsApp.",
            None,
            "bolo-rose.jpeg",
        ),

        (
            "Bolo Personalizado Sonic",
            "Bolos de Festa",
            "Bolo temático personalizado para festas e comemorações.",
            None,
            "bolo-sonic.jpeg",
        ),

        (
            "Bolo Personalizado Stitch",
            "Bolos de Festa",
            "Bolo temático personalizado para festas e comemorações.",
            None,
            "bolo-stich.jpeg",
        ),

        (
            "Docinhos 1",
            "Docinhos",
            "Docinhos para festas e encomendas. Consulte sabores e quantidades pelo WhatsApp.",
            None,
            "docinhos-1.jpeg",
        ),

        (
            "Docinhos 2",
            "Docinhos",
            "Docinhos para festas e encomendas. Consulte sabores e quantidades pelo WhatsApp.",
            None,
            "docinhos-2.jpeg",
        ),

        (
            "Docinhos 3",
            "Docinhos",
            "Docinhos para festas e encomendas. Consulte sabores e quantidades pelo WhatsApp.",
            None,
            "docinhos-3.jpeg",
        ),

        (
            "Casadinho",
            "Bolos de Pote",
            "Bolo de pote artesanal. Consulte disponibilidade pelo WhatsApp.",
            None,
            "pote-casei.jpeg",
        ),

        (
            "Doce de Leite com Ameixa",
            "Bolos de Pote",
            "Bolo de pote artesanal. Consulte disponibilidade pelo WhatsApp.",
            None,
            "pote-dc-amei.jpeg",
        ),

        (
            "Ninho com Morango",
            "Bolos de Pote",
            "Bolo de pote artesanal. Consulte disponibilidade pelo WhatsApp.",
            None,
            "pote-nin-mora.jpeg",
        ),

        (
            "Ninho com Nutella",
            "Bolos de Pote",
            "Bolo de pote artesanal. Consulte disponibilidade pelo WhatsApp.",
            None,
            "pote-nin-nut.jpeg",
        ),

        (
            "Prestígio",
            "Bolos de Pote",
            "Bolo de pote artesanal. Consulte disponibilidade pelo WhatsApp.",
            None,
            "pote-pres.jpeg",
        ),
    ]


    conexao = conectar_mysql()

    try:

        with conexao.cursor() as cursor:

            cursor.execute(
                "DELETE FROM produtos WHERE imagem = %s",
                ("bolo-choc.jpeg",)
            )


            for nome, categoria, descricao, preco, imagem in produtos_iniciais:

                cursor.execute(
                    """
                    SELECT id
                    FROM produtos
                    WHERE imagem = %s
                    LIMIT 1
                    """,
                    (imagem,)
                )

                existente = cursor.fetchone()


                if existente is None:

                    cursor.execute(
                        """
                        INSERT INTO produtos
                        (
                            nome,
                            categoria,
                            descricao,
                            preco,
                            imagem
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            nome,
                            categoria,
                            descricao,
                            preco,
                            imagem
                        )
                    )

                else:

                    cursor.execute(
                        """
                        UPDATE produtos

                        SET nome = %s,
                            categoria = %s,
                            descricao = %s,
                            preco = %s

                        WHERE imagem = %s
                        """,
                        (
                            nome,
                            categoria,
                            descricao,
                            preco,
                            imagem
                        )
                    )

        conexao.commit()

    finally:

        conexao.close()


# =========================================================
# BUSCAR PRODUTOS
# =========================================================

def buscar_produtos(categoria=None):

    conexao = conectar_mysql()

    try:

        with conexao.cursor() as cursor:

            if categoria:

                cursor.execute(
                    """
                    SELECT *
                    FROM produtos
                    WHERE categoria = %s
                    ORDER BY id ASC
                    """,
                    (categoria,)
                )

            else:

                cursor.execute(
                    """
                    SELECT *
                    FROM produtos
                    ORDER BY id ASC
                    """
                )

            return cursor.fetchall()

    finally:

        conexao.close()


# =========================================================
# PÁGINA INICIAL
# =========================================================

@app.route("/")
def inicio():

    return render_template(
        "inicio.html"
    )


# =========================================================
# CATÁLOGO
# =========================================================

@app.route("/catalogo")
def catalogo():

    # Se entrar no catálogo sem escolher uma categoria,
    # começa automaticamente em Bolos de Festa.

    categoria = request.args.get(
        "categoria",
        "Bolos de Festa"
    ).strip()


    # Categorias permitidas
    categorias_validas = [
        "Bolos de Festa",
        "Docinhos",
        "Bolos de Pote",
        "Bolos Caseiros"
    ]


    # Evita uma categoria inválida na URL
    if categoria not in categorias_validas:

        categoria = "Bolos de Festa"


    produtos = buscar_produtos(
        categoria
    )


    return render_template(
        "catalogo.html",
        produtos=produtos,
        categoria_ativa=categoria
    )


# =========================================================
# LOGIN ADMINISTRATIVO
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin_logado"):

        return redirect(
            url_for("admin")
        )


    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        ).strip()


        if usuario == "admin" and senha == "1234":

            session["admin_logado"] = True

            flash(
                "Login realizado com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("admin")
            )


        flash(
            "Usuário ou senha incorretos.",
            "erro"
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "admin_logado",
        None
    )

    flash(
        "Você saiu da área administrativa.",
        "sucesso"
    )

    return redirect(
        url_for("inicio")
    )


# =========================================================
# ADMINISTRATIVO
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logado"):

        flash(
            "Faça login para acessar a área administrativa.",
            "erro"
        )

        return redirect(
            url_for("login")
        )


    produtos = buscar_produtos()


    return render_template(
        "admin.html",
        produtos=produtos
    )


# =========================================================
# CADASTRAR PRODUTO
# =========================================================

@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    if not session.get("admin_logado"):

        return redirect(
            url_for("login")
        )


    nome = request.form.get(
        "nome",
        ""
    ).strip()


    categoria = request.form.get(
        "categoria",
        ""
    ).strip()


    descricao = request.form.get(
        "descricao",
        ""
    ).strip()


    preco = request.form.get(
        "preco",
        ""
    ).strip().replace(",", ".")


    imagem = request.files.get(
        "imagem"
    )


    if not nome or not categoria:

        flash(
            "Preencha nome e categoria.",
            "erro"
        )

        return redirect(
            url_for("admin")
        )


    preco_valor = preco if preco else None

    nome_imagem = ""


    # =====================================================
    # SALVAR IMAGEM
    # =====================================================

    if imagem and imagem.filename:

        if not extensao_permitida(
            imagem.filename
        ):

            flash(
                "Use uma imagem PNG, JPG, JPEG ou WEBP.",
                "erro"
            )

            return redirect(
                url_for("admin")
            )


        nome_imagem = secure_filename(
            imagem.filename
        )


        caminho = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nome_imagem
        )


        base, extensao = os.path.splitext(
            nome_imagem
        )


        contador = 1


        while os.path.exists(caminho):

            nome_imagem = (
                f"{base}_{contador}{extensao}"
            )

            caminho = os.path.join(
                app.config["UPLOAD_FOLDER"],
                nome_imagem
            )

            contador += 1


        imagem.save(
            caminho
        )


    # =====================================================
    # SALVAR NO BANCO
    # =====================================================

    conexao = conectar_mysql()

    try:

        with conexao.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO produtos
                (
                    nome,
                    categoria,
                    descricao,
                    preco,
                    imagem
                )

                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    nome,
                    categoria,
                    descricao,
                    preco_valor,
                    nome_imagem
                )
            )


        conexao.commit()

    finally:

        conexao.close()


    flash(
        "Produto cadastrado com sucesso!",
        "sucesso"
    )


    return redirect(
        url_for("admin")
    )


# =========================================================
# EXCLUIR PRODUTO
# =========================================================

@app.route(
    "/excluir/<int:produto_id>",
    methods=["POST"]
)
def excluir(produto_id):

    if not session.get("admin_logado"):

        return redirect(
            url_for("login")
        )


    conexao = conectar_mysql()

    try:

        with conexao.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM produtos
                WHERE id = %s
                """,
                (produto_id,)
            )


        conexao.commit()

    finally:

        conexao.close()


    flash(
        "Produto excluído.",
        "sucesso"
    )


    return redirect(
        url_for("admin")
    )


# =========================================================
# INICIAR SISTEMA
# =========================================================

if __name__ == "__main__":

    try:

        criar_banco_e_tabela()

        cadastrar_produtos_iniciais()


    except pymysql.MySQLError as erro:

        print(
            "\nERRO AO CONECTAR NO MYSQL"
        )

        print(
            "Confira se o MySQL está iniciado "
            "e se a senha em config.py está correta."
        )

        print(
            f"Detalhes: {erro}\n"
        )

        raise


    app.run(
        debug=True
    )