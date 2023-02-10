import os

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from PIL import Image

from utils import utils

# Create your models here.


class Produto(models.Model):
    produto_nome = models.CharField(max_length=255, verbose_name='Nome')
    descricao_curta = models.TextField(
        max_length=255, verbose_name='Descrição curta')
    descricao_longa = models.TextField(verbose_name='Descrição longa')
    imagem = models.ImageField(upload_to='produto_imagens/%Y/%m/',
                               blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='Preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='Preço promo')
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variável'),
            ('S', 'Simples'),
        )
    )

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_promo_formatado(self):
        return utils.formata_preco(self.preco_marketing_promocional)
    get_promo_formatado.short_description = 'Preço Promo'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, str(img.name))
        img_pil = Image.open(img_full_path)
        origial_width, original_height = img_pil.size

        if origial_width <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height)/origial_width)

        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            quality=50
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.produto_nome)}'
            self.slug = slug

        super().save(*args, **kwargs)

        max_image_size = 800

        if self.imagem:
            self.resize_image(self.imagem, max_image_size)

    def __str__(self):
        return self.produto_nome


class Variacao(models.Model):
    nome = models.CharField(max_length=50, blank=True, null=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE,
                                default=None)
    preco = models.FloatField(default=None, verbose_name='Preço')
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nome or self.produto.produto_nome

    class Meta:
        verbose_name = 'Variação'
        verbose_name_plural = 'Variações'
