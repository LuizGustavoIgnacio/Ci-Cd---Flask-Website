import pandas as pd
from datetime import timedelta
from flask import Flask, flash, render_template, request, redirect, url_for, session

import csv

app = Flask(__name__)
app.secret_key = 'mydude'
app.permanent_session_lifetime = timedelta(minutes=2)

try:
    pd.read_excel('banco_excel.xlsx')
except:
    banco_produtos = pd.DataFrame({"PRODUTOS": [], "ID": [],
                                   "PREÇO": [], "VALIDADE": []})
    banco_users = pd.DataFrame({'cpf': [], 'nome': [], 'data_nascimento': [],
                                'email': [], 'senha': []})

    with pd.ExcelWriter('banco_excel.xlsx') as writer:
        banco_produtos.to_excel(writer, sheet_name='banco_produtos', index=False)
        banco_users.to_excel(writer, sheet_name='banco_users', index=False)

banco_produtos = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
banco_users = pd.read_excel('banco_excel.xlsx', sheet_name='banco_users')

@app.route("/")
def home():
    return render_template("index.html")

# Parte LOGIN --- Inicio
@app.route('/login', methods=['POST', 'GET'])
def login():    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # verificar se a conta existe no formulário csv
        with open("usuarios.csv", mode="r") as f:
            reader = csv.reader(f,delimiter=",")
            for row in reader:
                if row == [username, password]:
                    session.permanent = True
                    user = request.form["username"]
                    session["user"] = user
                    flash("Login realizado com sucesso!")
                    return redirect(url_for("user"))
                else:
                    if "user" in session:
                        flash("Você já está logado!")
                        return redirect(url_for("user"))
            else:
                flash("Email ou senha incorretos. Tente novamente!")
        

    return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        flash("Você não está logado")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"Você foi desconectado, {user}", "info")
    session.pop('user', None)
    return redirect (url_for('login'))

# PARTE LOGIN -- Fim



# Parte Funcionalidades Cadastrar|Editar|Remover Produtos -- Inicio

# df=df.append({'Name' : 'Apple' , 'Price' : 23, 'Stock' : 'No'} , ignore_index=True)
@app.route('/cadastrar_produtos', methods=["POST", "GET"])
def receber_produtos():
    # resp = 'sim'
    # while resp == 'sim':
        if request.method == "POST":
            df = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')

            # print(df)

            addProd = request.form["nome_produto"]
            addID = request.form["id_produto"]
            addVal = request.form["val_produto"]
            addPrice = request.form["price_produto"]

            df.loc[len(df)] = [addProd, addID, addPrice, str(addVal)]

            with pd.ExcelWriter("banco_excel.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name='banco_produtos', index=False)
            
            flash("Produto Cadastrado com sucesso!")
            return render_template("sucesso.html")
        else:
            return render_template("cadastrar_produtos.html")
            # print(df)
            # resp = input("\nDeseja adicionar mais algum produto? Digite Sim ou Não:  ").lower().strip()

@app.route('/produtos')
def sucesso_produto():
    data = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
    return render_template("produtos.html",data=data.to_html(classes="my-table").replace('<th>','<th style="text-align:center">'))

# def cadastrar_usuario():
#     nome_user = str(input('Digite seu nome: '))
#     nascimento = str(input('Digite sua data de nascimento: '))
#     email = str(input('Digite o email: '))
#     senha = str(input('Digite sua senha: '))
#     cpf = str(input('Digite seu CPF: '))

#     banco_user = pd.DataFrame(banco_users)
#     banco_user = banco_user.append({'nome': nome_user, 'data_nascimento': nascimento,
#                                     'email': email, 'senha': senha, 'cpf': cpf}, ignore_index=True)

#     df_usuarios = pd.DataFrame(banco_user)
#     with pd.ExcelWriter("banco_excel.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
#         df_usuarios.to_excel(writer, sheet_name='banco_users', index=False)

#     return df_usuarios.head()

@app.route('/editar_produtos', methods=["POST", "GET"])
def editar_produtos():
    # resp = 'sim'
    # while resp == 'sim':

    if request.method == "POST":    

        df = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
        # print("\n", df)
        editLine = request.form["id_edit_produto"]
        prodShow = df.loc[df['ID'] == int(editLine)]
        # print('\n', prodShow)

        addProd = request.form["new_nome_produto"]
        addID = request.form["new_id_produto"]
        addPrice = request.form["new_price_produto"]
        addVal = request.form["new_val_produto"]
        df.loc[df['ID'] == int(editLine)] = [addProd, addID, addPrice, str(addVal)]

        with pd.ExcelWriter("banco_excel.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name='banco_produtos', index=False)
        # print("\n", df)

        flash("Produto editado com sucesso!")
        return render_template("sucesso.html")
        # resp = input("\nDeseja editar mais algum produto? Digite Sim ou Não:  ").lower().strip()
    else:
        data = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
        return render_template("editar_produto.html",data=data.to_html(classes="my-table").replace('<th>','<th style="text-align:center">'))



@app.route('/remover_produtos', methods=["POST", "GET"])
def remover_produto():
    # resp = 'sim'
    # while resp == 'sim':

    if request.method == "POST":   
        df = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
        # print("\n", df)
        delLine = request.form["id_remov_produto"]
        df.drop(df.loc[df['ID'] == int(delLine)].index, inplace=True)
        # print("\n", df)
        with pd.ExcelWriter("banco_excel.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name='banco_produtos', index=False)

        flash("Produto removido com sucesso!")
        return render_template("sucesso.html")
    else:
        data = pd.read_excel('banco_excel.xlsx', sheet_name='banco_produtos')
        return render_template("remover_produto.html",data=data.to_html(classes="my-table").replace('<th>','<th style="text-align:center">'))
        # resp = input("\nDeseja remover mais algum produto? Digite Sim ou Não:  ").lower().strip()


# def show_bd():
#     df = pd.read_excel('banco_excel.xlsx')
#     print(df)

app.run()