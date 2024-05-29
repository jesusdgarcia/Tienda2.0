from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class Tarjeta(models.Model):
    TIPO_CHOICES = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'MasterCard'),
        ('AMERICAN EXPRESS', 'American Express'),
        ('OTRO', 'Otro'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='VISA')
    titular = models.CharField(max_length=255)
    numero = models.CharField(max_length=255)
    mes_caducidad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    anio_caducidad = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2999)])
    codigo_seguridad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)])

    def __str__(self):
        return f"{self.tipo} - {self.titular} - {self.numero}"

    class Meta:
        verbose_name_plural = "Tarjetas"


class Direccion(models.Model):
    name = models.CharField(max_length=400, null=True, blank=True)
    address_one = models.CharField(max_length=300, default="")
    address_two = models.CharField(max_length=300, default="")
    city = models.CharField(max_length=200, default="")
    province = models.CharField(max_length=200, default="")
    postal_code = models.CharField(max_length=5, default=00000)

    def __str__(self):
        return f"{self.address_one} - {self.address_two} - {self.city} - {self.postal_code}"

    def save(self, *args, **kwargs):
        super().save()


class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tarjetas = models.ManyToManyField(Tarjeta, related_name='clientes', blank=True)
    direcciones = models.ManyToManyField(Direccion, related_name='clientes', blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    vip = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        verbose_name_plural = "Clientes"
