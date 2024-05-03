from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comunidadeimpressionadora.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(message='Esse campo é obrigatório.')])
    email_criarconta = StringField('E-mail', validators=[DataRequired(message='Esse campo é obrigatório.'), Email(message='Use um email válido.')])
    senha_criarconta = PasswordField('Senha', validators=[DataRequired(message='Esse campo é obrigatório.'), Length(6, 20, message='A senha deve ter entre 6 e 20 caractéres.')])
    confirmacao = PasswordField('Confirmação da Senha', validators=[DataRequired(message='Esse campo é obrigatório'), EqualTo('senha_criarconta', message='As senhas devem ser iguais.')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email_criarconta(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar')

class FormLogin(FlaskForm):
    email_login = StringField('E-mail', validators=[DataRequired(message='Esse campo é obrigatório.'), Email(message='Use um email válido.')])
    senha_login = PasswordField('Senha', validators=[DataRequired(message='Esse campo é obrigatório.'), Length(6, 20, message='A senha deve ter entre 6 e 20 caractéres')])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')

class FormEditarPerfil(FlaskForm):
    username = StringField('Novo Nome de Usuário', validators=[DataRequired(message='Esse campo é obrigatório.')])
    email = StringField('Novo E-mail', validators=[DataRequired(message='Esse campo é obrigatório.'), Email(message='Use um email válido.')])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'], message='Formato de arquivo não permitido. Os formatos permitidos são: jpg, png.')])

    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Power BI Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_sql = BooleanField('SQL Impressionador')
    curso_ppt = BooleanField('PowerPoint Impressionador')
    curso_dados = BooleanField('Ciência de Dados Impressionador')
    curso_html = BooleanField('HTML & CSS Impressionador')
    curso_js = BooleanField('JavaScript Impressionador')

    botao_submit_confirmar = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com esse e-mail. Cadastre outro e-mail.')

class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(message='Esse campo é obrigatório.'), Length(2, 140, message='O título precisa ter 2 caracteres no mínimo e no máximo 140 caractéres.')])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired(message='Esse campo é obrigatório.')])
    botao_submit = SubmitField('Criar Post')