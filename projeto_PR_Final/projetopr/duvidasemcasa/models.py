from django.db import models
from django.contrib.auth.models import User


class Escola(models.Model):
    sigla = models.CharField(max_length=20, primary_key=True, unique=True)
    nome = models.CharField(max_length=200)

    def mais_recentes(self):
        return self.post_set.order_by('-data_publicacao')

    def ultimo_update(self):
        return self.post_set.order_by('-data_update')

    def melhores_notas(self):
        return self.post_set.order_by('-rating')


class Conta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    escola = models.ForeignKey(Escola, on_delete=models.PROTECT, default='iscte')
    curso_departamento = models.CharField(max_length=200)
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=0.0)
    votos = models.IntegerField(default=0)
    imagem_perfil = models.CharField(max_length=20000, default="/duvidasemcasa/static/media/default.png")
    p_email = models.BooleanField(default=False)
    p_proprio = models.BooleanField(default=False)
    p_apelido = models.BooleanField(default=False)

    def atualiza_nota_votos(self):
        auxn = 0
        auxv = 0
        for n in self.post_set.all():
            for r in n.ratingpost_set.all():
                auxn += r.nota
                auxv += 1
        for n in self.comentario_set.all():
            for r in n.ratingcomentario_set.all():
                auxn += r.nota
                auxv += 1
        if auxv > 0:
            self.rating = auxn / auxv
            self.votos = auxv
            self.save()


class Post(models.Model):
    autor = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True)
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
    data_publicacao = models.DateTimeField('data de publicacao')
    escola = models.ForeignKey(Escola, on_delete=models.PROTECT, default='iscte')
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=0.0)
    votos = models.IntegerField(default=0)
    data_update = models.DateTimeField('data de update')
    tipo = models.CharField(max_length=100, default="Convivio")
    cursos = models.CharField(max_length=500, blank=True)
    cadeiras = models.CharField(max_length=200, blank=True)

    def atualiza_nota_votos(self):
        auxn = 0
        if self.ratingpost_set.all().count() > 0:
            for n in self.ratingpost_set.all():
                auxn += n.nota
            self.rating = auxn/self.ratingpost_set.all().count()
            self.votos = self.ratingpost_set.all().count()
            self.save()

    def preview_texto(self):
        if len(self.texto) > 500:
            return self.texto[:500]+"(...)"
        else:
            return self.texto[:500]

    def melhor_comentario(self):
        return self.comentario_set.order_by('-rating')[0]

    def comentario_mais_recente(self):
        return self.comentario_set.order_by('-data_publicacao')[0]

    def media_notas_comentarios(self):
        auxn = 0
        auxv = 0
        for c in self.comentario_set.all():
            if c.ratingcomentario_set.all().count() > 0:
                auxn += c.rating
                auxv += 1
        if auxv > 0:
            return auxn/auxv
        else:
            return 99



class Imagem(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    endereco = models.CharField(max_length=20000)


class RatingPost(models.Model):
    autor = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    nota = models.IntegerField('nota')


class Comentario(models.Model):
    autor = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    texto = models.TextField()
    data_publicacao = models.DateTimeField('data de publicacao')
    rating = models.DecimalField(decimal_places=1, max_digits=3, default=0.0)
    endereco = models.CharField(max_length=20000, blank=True)
    
    def atualiza_nota(self):
        auxn = 0
        if self.ratingcomentario_set.all().count() > 0:
            for n in self.ratingcomentario_set.all():
                auxn += n.nota
            self.rating = auxn / self.ratingcomentario_set.all().count()
            self.save()


class RatingComentario(models.Model):
    autor = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)
    nota = models.IntegerField('nota')


class Noticia(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
    data_publicacao = models.DateTimeField()
    imagem_noticia = models.CharField(max_length=20000, default="")
