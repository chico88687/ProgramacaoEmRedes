from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from .models import *
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from django.core.files.storage import FileSystemStorage

from django.core.paginator import Paginator

from .code.pages import *
import datetime

contexto = {
    'list_pages': Page.pages,
}


# dá as funções de url e path os botões a colocar no lado direito do ecrã
def contexto_direita(request):
    if request.user.is_authenticated:
        return PageRightLogado.pages
    else:
        return PageRight.pages


def index(request):  # pag inicial
    contexto['titulo_pagina'] = "Pagina Principal"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    return render(request, 'duvidasemcasa/index.html', contexto)


def contactanos(request):  # pag contactanos
    contexto['titulo_pagina'] = "Contacta-nos"
    contexto['list_right'] = contexto_direita(request)
    contexto['opcoes'] = ['Aluno', 'Professor']
    contexto['cor'] = Escola.objects.get(pk='iscte')
    return render(request, 'duvidasemcasa/contactanos.html', contexto)


def envia_contactus(request):  # para enviar a mensagem escrita no contactanos
    assunto = request.POST['assunto']
    email = request.POST['email']
    texto = request.POST['mensagem']
    nome = request.POST['nome']
    if nome != "":
        nome += " - "
    opcao = request.POST['opcao']
    if opcao == "Outro":
        opcao = request.POST['outro']
    if opcao != "":
        opcao = opcao + " "
    if 'enviar' in request.POST:
        send_mail(opcao + nome + assunto, texto, settings.EMAIL_HOST_USER, [email])

    texto += "\n" + email
    send_mail(opcao + nome + assunto, texto, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
    return HttpResponseRedirect(reverse('duvidasemcasa:contactanos'))


def forum(request):  # pag principal do forum
    escola = []  # criação de uma lista de dicionarios com os posts de cada escola ordenados de 3 formas diferentes
    for e in Escola.objects.all():
        recente = {
            't': 'Mais Recentes',
            'disp': 'novo',
            'posts': e.mais_recentes()[:3],
        }

        update = {
            't': 'Ultimos Updates',
            'disp': 'update',
            'posts': e.ultimo_update()[:3],
        }

        votacao = {
            't': 'Melhores Notas',
            'disp': 'votacao',
            'posts': e.melhores_notas()[:3],
        }

        escola.append({
            'sigla': e.sigla,
            'nome': e.nome,
            'ordens': [recente, update, votacao],
        })
    contexto['titulo_pagina'] = "Forum"
    contexto['list_right'] = contexto_direita(request)
    contexto['escolas'] = Escola.objects.all()
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['escolas'] = escola
    return render(request, 'duvidasemcasa/forum.html', contexto)


def escolaordem(request, e, disp):  # pag com os posts da escola e ordenados de forma disp
    contexto['list_right'] = contexto_direita(request)
    if request.user.is_authenticated:
        contexto['logado'] = True
    else:
        contexto['logado'] = False
    eobj = get_object_or_404(Escola, pk=e)
    contexto['titulo_pagina'] = "Forum " + e.capitalize()
    contexto['classe'] = eobj
    contexto['cor'] = eobj
    contexto['disp'] = disp
    if disp == "novo":
        contexto['top_tabela'] = "Mais Recentes"
        paginator = Paginator(eobj.mais_recentes(), 10)
    elif disp == "update":
        contexto['top_tabela'] = "Ultimos Updates"
        paginator = Paginator(eobj.ultimo_update(), 10)
    elif disp == "votacao":
        contexto['top_tabela'] = "Melhores Notas"
        paginator = Paginator(eobj.melhores_notas(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto['page_obj'] = page_obj
    contexto['disp'] = disp
    return render(request, 'duvidasemcasa/escola.html', contexto)


def escola(request,
           e):  # redirecciona para a pag com os posts da escola e ordenados por ordem de publicação mais recente
    return HttpResponseRedirect(reverse('duvidasemcasa:escolaordem', args=(e, 'novo')))


def loginview(request):  # pag login
    contexto['titulo_pagina'] = "Log In"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['erro'] = Mensagem.e
    Mensagem.e = ""
    return render(request, 'duvidasemcasa/login.html', contexto)


def login2(request):  # para realizar o login
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))
    else:
        Mensagem.e = "Username/Password errados"
        return HttpResponseRedirect(reverse('duvidasemcasa:login'))


def logoutview(request):  # faz logout
    contexto['list_right'] = contexto_direita(request)
    logout(request)
    return HttpResponseRedirect(reverse('duvidasemcasa:login'))


def registate(request):  # pag de registo
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))
    contexto['titulo_pagina'] = "Regista-te"
    contexto['list_right'] = contexto_direita(request)
    contexto['escolas'] = Escola.objects.all()
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['erro'] = Mensagem.e
    Mensagem.e = ""
    return render(request, 'duvidasemcasa/registate.html', contexto)


def registate_registo(request):  # para efectuar o registo
    username = request.POST['username']
    password = request.POST['pass']
    email = request.POST['email']
    if Conta.objects.filter(user__email=email).exists():
        Mensagem.e = "Email já registado"
        return HttpResponseRedirect(reverse('duvidasemcasa:registate'))
    try:
        user = User.objects.create_user(username, email, password)
        assunto = 'Bem vindo a duvidas em casa!'
        msg = 'Olá, ' + username + '! Sê bem vindo ao duvidas em casa. Um forum feito por alunos do 2º ano de Engenharia Informática para todos os alunos do iscte em que os professores são também bem vindos.'
        send_mail(assunto, msg, settings.EMAIL_HOST_USER, [email])
    except IntegrityError:
        Mensagem.e = "Username já registado"
        return HttpResponseRedirect(reverse('duvidasemcasa:registate'))
    user.first_name = request.POST['proprio']
    user.last_name = request.POST['apelido']
    user.save()
    conta = Conta()
    conta.user = user
    conta.tipo = request.POST['tipo']
    conta.escola = Escola.objects.get(pk=request.POST['escola'])
    conta.curso_departamento = request.POST['curso']
    conta.save()
    new_user = authenticate(username=username, password=password)
    if new_user is not None:
        login(request, new_user)
        return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))
    return HttpResponseRedirect(reverse('duvidasemcasa:registate'))


def sobrenos(request):  # ppag sobre nós
    contexto['titulo_pagina'] = "Sobre nós"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    return render(request, 'duvidasemcasa/sobrenos.html', contexto)


def perfil(request):  # pag de perfil do utilizador
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('duvidasemcasa:login'))
    contexto['titulo_pagina'] = "Perfil"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['user'] = request.user
    contexto['logado'] = request.user.username
    contexto['opcoes'] = ["Aluno", "Professor"]
    contexto['escolas'] = Escola.objects.all()
    contexto['erro'] = Mensagem.e
    Mensagem.e = ""
    contexto['sucesso'] = Mensagem.s
    Mensagem.s = ""
    return render(request, 'duvidasemcasa/perfil.html', contexto)


def perfil_user(request, pfl):  # pag de um qualquer utilizador
    contexto['cor'] = Escola.objects.get(pk='iscte')
    try:
        user = User.objects.get(username=pfl)
        contexto['user'] = user
        contexto['logado'] = request.user.username
        contexto['titulo_pagina'] = "Perfil"
        contexto['list_right'] = contexto_direita(request)
        return render(request, 'duvidasemcasa/perfil_outro.html', contexto)
    except User.DoesNotExist:
        return Http404("Perfil Não Encontrado")


def change(request):  # para alterar a informação do utilizador
    if not request.user.check_password(request.POST['pass']):
        Mensagem.e = "Password inválida"
        return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))
    email = request.POST['mail']
    if email != request.user.email and Conta.objects.filter(user__email=email).exists():
        Mensagem.e = "Email já registado!"
        return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))
    else:
        request.user.email = email
    request.user.email = email
    newpass = request.POST['nova']
    request.user.last_name = request.POST['apelido']
    request.user.first_name = request.POST['primeiro']
    request.user.conta.tipo = request.POST['tipo']
    request.user.conta.escola = Escola.objects.get(pk=request.POST['escola'])
    request.user.conta.curso_departamento = request.POST['curso']
    request.user.save()
    if request.method == 'POST' and request.FILES.getlist('imagem'):
        imagem = request.FILES['imagem']
        fs = FileSystemStorage()
        filename = fs.save(imagem.name, imagem)
        uploaded_file_url = fs.url(filename)
        aux = request.user.conta.imagem_perfil
        request.user.conta.imagem_perfil = uploaded_file_url
        if aux != "/duvidasemcasa/static/media/default.png":
            fs.delete(aux.split("/")[-1])
    publicos = request.POST.getlist('publico[]')
    request.user.conta.p_email = '0' in publicos
    request.user.conta.p_proprio = '1' in publicos
    request.user.conta.p_apelido = '2' in publicos
    request.user.conta.save()
    Mensagem.s = "Perfil editado com sucesso"
    if newpass:
        request.user.set_password(newpass)
        user = authenticate(username=request.user.username, password=newpass)
        if user is not None:
            login(request, user)
    return HttpResponseRedirect(reverse('duvidasemcasa:perfil'))


def noticias(request):  # pag de noticias
    contexto['titulo_pagina'] = "Noticias"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['staff'] = request.user.is_staff
    noticias = Noticia.objects.order_by('-data_publicacao')
    paginator = Paginator(noticias, 10)
    page_number = request.GET.get('page')
    contexto['page_obj'] = paginator.get_page(page_number)
    return render(request, 'duvidasemcasa/noticias.html', contexto)


def novanoticia(request):  # pag para criar uma nova noticia
    contexto['titulo_pagina'] = "Publicar Noticia"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'duvidasemcasa/novanoticia.html', contexto)
    else:
        return HttpResponseRedirect(reverse('duvidasemcasa:noticias'))


def criarnoticia(request):  # cria a nova noticia
    noticia = Noticia(user=request.user)
    noticia.titulo = request.POST['titulo']
    noticia.texto = request.POST['texto']
    noticia.data_publicacao = datetime.datetime.now()
    noticia.save()
    if request.method == 'POST' and request.FILES.getlist('img'):
        imagem = request.FILES['img']
        fs = FileSystemStorage()
        filename = fs.save(imagem.name, imagem)
        uploaded_file_url = fs.url(filename)
        noticia.imagem_noticia = uploaded_file_url
    noticia.save()
    return HttpResponseRedirect(reverse('duvidasemcasa:noticias'))


def pesquisa(request):  # pag de pesquisa
    contexto['titulo_pagina'] = "Pesquisa"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto["previous_search"] = "Search"
    contexto["perfils"] = ""
    contexto["c_perfil"] = ""
    contexto["perfil_mensagem"] = ""
    contexto["check_posts"] = ""
    contexto["c_post"] = ""
    contexto["post_mensagem"] = ""
    contexto["news"] = ""
    contexto["c_news"] = ""
    contexto["news_mensagem"] = ""
    return render(request, 'duvidasemcasa/pesquisa.html', contexto)


def manda_procura(request):  # realiza a pesquisa
    contexto['titulo_pagina'] = "Pesquisa"
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')

    search = request.GET.get("search")
    filter_t = request.GET.getlist("filter_search")
    fperfil_escola = request.GET.get("perfil_escola")
    fperfil_tipo = request.GET.get("perfil_tipo")
    fpost_escola = request.GET.get("post_escola")
    fpost_tipo = request.GET.get("post_tipo")
    fpost_file = request.GET.get("file")
    fpost_comentario = request.GET.getlist("comentario")
    contexto["previous_search"] = search
    escolas = Escola.objects.all()
    contexto["escola"] = escolas
    contexto["fperfil_escola"] = fperfil_escola
    contexto["fperfil_tipo"] = fperfil_tipo
    contexto["fpost_escola"] = fpost_escola
    contexto["fpost_tipo"] = fpost_tipo
    contexto["fpost_file"] = fpost_file

    if fpost_comentario:
        contexto["fpost_comentario"] = "checked"

    if not filter_t:
        filter_t = ["s_perfil", "s_post", "s_news"]

    if "s_perfil" in filter_t:
        perfils = filter_perfil(search, fperfil_escola, fperfil_tipo)
        contexto["perfils"] = perfils
        contexto["c_perfil"] = "checked"
        contexto["perfil_mensagem"] = "Não foi obtido nenhum perfil na pesquisa"
    else:
        contexto["perfils"] = ""
        contexto["c_perfil"] = ""

    if "s_post" in filter_t:
        posts = filter_post(search, fpost_escola, fpost_tipo)
        posts = filter_file(posts, fpost_file)
        posts = filter_comment(posts, search, fpost_comentario)
        contexto["check_posts"] = posts
        contexto["c_post"] = "checked"
        contexto["post_mensagem"] = "Não foi obtido nenhum post na pesquisa"
    else:
        contexto["check_posts"] = ""
        contexto["c_post"] = ""

    if "s_news" in filter_t:
        news = Noticia.objects.filter(Q(titulo__icontains=search) | Q(texto__icontains=search))
        contexto["news"] = news
        contexto["c_news"] = "checked"
        contexto["news_mensagem"] = "Não foi obtido nenhuma notícia na pesquisa"
    else:
        contexto["news"] = ""
        contexto["c_news"] = ""

    return render(request, 'duvidasemcasa/pesquisa.html', contexto)


def filter_perfil(search, fperfil_escola, fperfil_tipo):  # pesquisa em perfil
    if fperfil_escola is None:
        fperfil_escola == ""
    if fperfil_tipo is None:
        fperfil_tipo = ""

    if fperfil_escola == "" and fperfil_tipo == "":
        perfils = Conta.objects.filter(Q(user__username__startswith=search))
    elif fperfil_escola == "":
        perfils = Conta.objects.filter(Q(user__username__startswith=search) & Q(tipo=fperfil_tipo))
    elif fperfil_tipo == "":
        perfils = Conta.objects.filter(Q(user__username__startswith=search) & Q(escola__sigla=fperfil_escola))
    else:
        perfils = Conta.objects.filter(
            Q(user__username__startswith=search) & Q(escola__sigla=fperfil_escola) & Q(tipo=fperfil_tipo))
    return perfils


def filter_post(search, fpost_escola, fpost_tipo):  # pesquisa em posts
    print(fpost_escola)
    if fpost_escola is None:
        fpost_escola = ""
    if fpost_tipo is None:
        fpost_tipo = ""
    if fpost_escola == "" and fpost_tipo == "":
        post = Post.objects.filter(
            Q(titulo__contains=search) | Q(autor__user__username__contains=search) | Q(texto__icontains=search))
    elif fpost_escola == "":
        post = Post.objects.filter(
            (Q(titulo__contains=search) | Q(autor__user__username__contains=search) | Q(texto__icontains=search)) & Q(
                tipo=fpost_tipo))
    elif fpost_tipo == "":
        print("ola")
        post = Post.objects.filter(
            (Q(titulo__contains=search) | Q(autor__user__username__contains=search) | Q(texto__icontains=search)) & Q(
                escola__sigla=fpost_escola))
    else:
        post = Post.objects.filter(
            (Q(titulo__contains=search) | Q(autor__user__username__contains=search) | Q(texto__icontains=search)) & Q(
                escola__sigla=fpost_escola) & Q(tipo=fpost_tipo))
    return post


def filter_file(post, fpost_file):  # filtra pesquisa se for para os post terem/não terem ficheiros
    if fpost_file is None or fpost_file == "":
        return post
    else:
        post2 = []
        for x in post:
            if fpost_file == "has_file" and Imagem.objects.filter(Q(post=x)):
                post2.append(x)
            elif fpost_file == "no_file" and not Imagem.objects.filter(Q(post=x)):
                post2.append(x)
        return post2


def filter_comment(post, search, fpost_comentario):  # se for para pesquisar em comentarios, faz essa pesquisa
    if not fpost_comentario:
        return post
    else:
        new_posts = []
        for x in post:
            new_posts.append(x)
        comments = Comentario.objects.filter(Q(texto__icontains=search))
        for x in comments:
            new_posts.append(x.post)
        return new_posts


def novopost(request, e):  # pag para criar um novo post
    contexto['escola'] = get_object_or_404(Escola, pk=e)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('duvidasemcasa:login'))
    contexto['titulo_pagina'] = 'Novo post'
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = contexto['escola']
    return render(request, 'duvidasemcasa/novopost.html', contexto)


def criapost(request, e):  # cria novo post
    titulo_post = request.POST['titulo']
    texto_post = request.POST['texto']
    imagens_post = []
    post = Post()
    post.escola = get_object_or_404(Escola, pk=e)
    if request.method == 'POST' and request.FILES.getlist('myfile'):
        for myfile in request.FILES.getlist('myfile'):
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            imagens_post.append(uploaded_file_url)
    post.titulo = titulo_post
    post.texto = texto_post
    post.data_publicacao = datetime.datetime.now()
    post.autor = request.user.conta
    post.data_update = post.data_publicacao
    post.cursos = request.POST['curso']
    post.cadeiras = request.POST['cadeira']
    post.save()
    for f in imagens_post:
        imagem = Imagem()
        imagem.endereco = f
        imagem.post = post
        imagem.save()
    return HttpResponseRedirect(reverse('duvidasemcasa:post', args=(post.escola.sigla, post.id)))


def postid(request, e, i):  # pag do post i da escola e
    escola = get_object_or_404(Escola, pk=e)
    post = get_object_or_404(Post, pk=i)
    if post.escola != escola:
        raise Http404("Page not found")
    contexto['titulo_pagina'] = "Forum - " + escola.sigla + " - " + post.titulo
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = escola
    contexto['escola'] = escola
    contexto['post'] = post
    if request.user.is_authenticated:
        contexto['autorcomentario'] = request.user.conta
        contexto['avaliou'] = []
        for c in request.user.conta.ratingcomentario_set.all():  # lista para o html não deixar avaliar o mesmo comentario mais que uma vez
            contexto['avaliou'].append(c.comentario)
        if post.autor == request.user.conta:  # notifica o html para não deixar o utilizador avaliar o post porque é o autor
            contexto['avalia'] = 2
        elif post.votos > 0: # se o post já tiver avaliações
            if post.ratingpost_set.filter(autor=request.user.conta):  # se o utilizador já o tiver avaliado, não o pode fazer outra vez
                contexto['avalia'] = 1
                contexto['avaliacao'] = post.ratingpost_set.get(autor=request.user.conta).nota
            else:
                contexto['avalia'] = 0  # deixa o utilizador avaliar o post
        else:
            contexto['avalia'] = 0  # deixa o utilizador avaliar o post
    else:  # notifica o html que não é para deixar o utilizador fazer avaliações nem permitir comentarios
        contexto['avalia'] = 3
    paginator = Paginator(post.comentario_set.all(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto['page_obj'] = page_obj
    contexto['pdf'] = []
    contexto['pic'] = []
    for f in post.imagem_set.all():
        if f.endereco.split('.')[-1] == 'pdf':
            contexto['pdf'].append(f)
        else:
            contexto['pic'].append(f)
    return render(request, 'duvidasemcasa/post.html', contexto)


def avaliapost(request, e, i):  # cria avaliação de post (RatingPost)
    rating = RatingPost()
    rating.autor = request.user.conta
    rating.post = get_object_or_404(Post, pk=i)
    rating.nota = request.POST['nota']
    rating.save()
    rating.post.atualiza_nota_votos()
    rating.post.autor.atualiza_nota_votos()
    return HttpResponseRedirect(reverse('duvidasemcasa:post', args=(e, i)))


def comenta(request, e, i):  # cria comentario
    texto = request.POST['texto']
    if texto != "":
        comentario = Comentario()
        comentario.texto = texto
        comentario.post = get_object_or_404(Post, pk=i)
        comentario.autor = request.user.conta
        comentario.data_publicacao = datetime.datetime.now()
        comentario.post.data_update = comentario.data_publicacao
        if request.method == 'POST' and request.FILES.getlist('ficheiro'):
            ficheiro = request.FILES['ficheiro']
            fs = FileSystemStorage()
            filename = fs.save(ficheiro.name, ficheiro)
            uploaded_file_url = fs.url(filename)
            comentario.endereco = uploaded_file_url
        comentario.save()
        comentario.post.save()
    return HttpResponseRedirect(reverse('duvidasemcasa:post', args=(e, i)))


def avaliacomentario(request, e, i, c):  # cria avaliação de comentario (RatingComentario)
    rating = RatingComentario()
    rating.autor = request.user.conta
    rating.comentario = get_object_or_404(Comentario, pk=c)
    rating.nota = request.POST['nota']
    rating.save()
    rating.comentario.atualiza_nota()
    rating.comentario.autor.atualiza_nota_votos()
    return HttpResponseRedirect(reverse('duvidasemcasa:post', args=(e, i)))


def noticia_especifica(request, i):  # pag com 1 unica noticia
    noticia = get_object_or_404(Noticia, pk=i)
    contexto['titulo_pagina'] = "Noticia - " + noticia.titulo
    contexto['list_right'] = contexto_direita(request)
    contexto['cor'] = Escola.objects.get(pk='iscte')
    contexto['noticia'] = noticia
    return render(request, 'duvidasemcasa/noticia.html', contexto)
