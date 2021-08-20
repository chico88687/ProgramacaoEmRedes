from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# significados de nomes de variaveis dos path
# e) sigla da escola
# i) nº id do post
# pfl) username da conta cujo perfil publico se quer ver
# disp) mode de ordenar os posts na pagina

app_name = 'duvidasemcasa'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contactanos/$', views.contactanos, name='contactanos'),
    url(r'^envia_contactus/$', views.envia_contactus, name='envia_contactus'),
    url(r'^forum/$', views.forum, name='forum'),
    path('forum/<str:e>', views.escola, name='escola'),
    path('forum/<str:e>/ordem/<str:disp>', views.escolaordem, name='escolaordem'),
    url(r'^login/$', views.loginview, name='login'),
    url(r'^login2/$', views.login2, name='login2'),
    url(r'^noticias/$', views.noticias, name='noticias'),
    url(r'noticias/novanoticia/$', views.novanoticia, name='novanoticia'),
    url(r'^noticia/novanoticia/criarnoticia/$', views.criarnoticia, name='criarnoticia'),
    url(r'^perfil/$', views.perfil, name='perfil'),
    url(r'^registate/$', views.registate, name='registate'),
    url(r'^registate_registo/$', views.registate_registo, name='registate_registo'),
    url(r'^sobrenos/$', views.sobrenos, name='sobrenos'),
    url(r'^logout/$', views.logoutview, name='logout'),
    path('forum/<str:e>/novopost', views.novopost, name='novopost'),
    path('forum/<str:e>/criapost', views.criapost, name='criapost'),
    path('forum/<str:e>/post/<int:i>', views.postid, name='post'),
    path('avalia/post/<str:e>/<int:i>', views.avaliapost, name='avaliapost'),
    path('forum/<str:e>/post/<int:i>/comenta', views.comenta, name='post_comentario'),
    path('perfil/<str:pfl>', views.perfil_user, name='perfil_user'),
    path('change', views.change, name='change'),
    path('forum/<str:e>/post/<int:i>/<int:c>', views.avaliacomentario, name='avaliacomentario'),
    path('noticias/<int:i>', views.noticia_especifica, name='noticia_especifica'),
    url(r'^pesquisa/$', views.pesquisa, name='pesquisa'),
    url(r'^manda_procurar/$', views.manda_procura, name='manda_procurar'),
    path('manda_procurar/<str:pfl>', views.perfil_user),
    path('manda_procurar/<str:e>/<int:i>', views.postid, name='post'),
]
