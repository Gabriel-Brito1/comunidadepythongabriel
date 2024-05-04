from flask import render_template, url_for, redirect, flash, request, abort
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from comunidadeimpressionadora.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route("/contato")
def contato():
    return render_template('contato.html')

@app.route("/usuarios")
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email_login.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login. E-mail ou Senha incorretos', 'alert-danger')
        
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        # criar usuario
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha_criarconta.data).decode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email_criarconta.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario)
        flash(f'Conta criada com sucesso no e-mail: {form_criarconta.email_criarconta.data}', 'alert-success')
        par_next = request.args.get('next')
        if par_next:
            return redirect(par_next)
        else:
            return redirect(url_for('home'))
    
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f'Logout feito com sucesso', 'alert-primary')
    return redirect(url_for('home'))

@app.route("/perfil")
@login_required
def perfil():
    lista_cursos = current_user.cursos.split(';')
    if lista_cursos[0] == 'Não Informado':
        quantidade_cursos = 0
    else:
        quantidade_cursos = len(lista_cursos)
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil, quantidade_cursos=quantidade_cursos)

def salvar_imagem(imagem):
    cod = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + cod + extensao

    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem).convert('RGB')
    imagem_reduzida.thumbnail(tamanho)

    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name and campo.data:
            lista_cursos.append(campo.label.text)
    if lista_cursos:
        return ';'.join(lista_cursos)
    else:
        return 'Não Informado'

@app.route("/perfil/editar", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = imagem
        current_user.cursos = atualizar_cursos(form)
        database.session.commit()
        flash(f'Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
        lista_cursos = current_user.cursos.split(';')
        if lista_cursos[0] != 'Não Informado':
            for curso in lista_cursos:
                for campo in form:
                    if campo.label.text == curso:
                        campo.data = True

    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)

@app.route("/post/criar", methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

@app.route("/post/<post_id>", methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        form.botao_submit.label.text = 'Editar Post'
        form.corpo.label.text = 'Novo Texto do Post'
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit() and 'botao_submit' in request.form:
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)

@app.route("/post/<post_id>/excluir", methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
