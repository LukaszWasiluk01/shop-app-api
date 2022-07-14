from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.validators import validate_phone_number


class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)


class Category(models.Model):

    name = models.CharField(max_length=200, unique=True, primary_key=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):

    PROVINCES_CHOICES = (
        ('Lower Silesia', 'Lower Silesia'),
        ('Kuyavia-Pomerania', 'Kuyavia-Pomerania'),
        ('Lodzkie', 'Lodzkie'),
        ('Lublin', 'Lublin'),
        ('Lubusz', 'Lubusz'),
        ('Lesser Poland', 'Lesser Poland'),
        ('Masovia', 'Masovia'),
        ('Subcarpathia', 'Subcarpathia'),
        ('Pomerania', 'Pomerania'),
        ('Silesia', 'Silesia'),
        ('Warmia-Masuria', 'Warmia-Masuria'),
        ('Greater Poland', 'Greater Poland'),
        ('West Pomerania', 'West Pomerania')
    )

    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='products')
    name = models.CharField(max_length=50, db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    province = models.CharField(max_length=64, choices=PROVINCES_CHOICES)
    phone_number = models.CharField(max_length=9,
                                    validators=[validate_phone_number])

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
