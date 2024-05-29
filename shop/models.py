from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from main.models import Cliente, Direccion, Tarjeta


# Create your models here.
class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    # Para cuando lo reguiste en el django admin aparezca el nombre
    def __str__(self):
        return self.nombre

    # Informacion adiccional de marcas, a la hora de mostrarlo
    class Meta:
        verbose_name_plural = "Marcas"


class Producto(models.Model):
    img = models.CharField(max_length=250)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    unidad = models.IntegerField()
    # Para el campo precio es mejor
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    vip = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.marca} {self.modelo}'

    class Meta:
        unique_together = ['marca', 'modelo']
        verbose_name_plural = "Productos"


class Compra(models.Model):
    # producto = models.ForeignKey(Producto, models.PROTECT)
    cliente = models.ForeignKey(Cliente, models.PROTECT)
    fecha = models.DateTimeField(default=timezone.now)
    unidades = models.PositiveIntegerField()
    importe = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(limit_value=0)])
    iva = models.DecimalField(max_digits=2, decimal_places=2, default=0.21)

    direccion_envio = models.ForeignKey(Direccion, on_delete=models.CASCADE, default=0,
                                        related_name='compras_envio')
    direccion_facturacion = models.ForeignKey(Direccion, on_delete=models.CASCADE, default=0,
                                              related_name='compras_facturacion')
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE, null=False, default=1)

    def _str_(self):
        return f"{self.cliente.user.username}{self.fecha}"

    class Meta:
        unique_together = ["cliente", "fecha"]
        verbose_name_plural = "Compras"
        ordering = ["cliente"]


class ItemCarrito(models.Model):
    producto = models.ForeignKey(Producto, models.PROTECT)
    compra = models.ForeignKey(Compra, models.PROTECT, blank=True, null=True)
    # cliente = models.ForeignKey(Cliente, models.PROTECT)
    cantidad = models.IntegerField()
    importe = models.DecimalField(max_digits=12, decimal_places=2)

    def str(self):
        return f'{self.compra.cliente.user.username} - {self.producto.nombre}'

    def subtotal(self):
        return float(self.cantidad * self.producto.precio)

    def subtotalconiva(self):
        return float(self.cantidad * self.producto.precio) * 1.21

    class Meta:
        verbose_name_plural = "Items Carrito"


class Valoracion(models.Model):
    cliente = models.ForeignKey(Cliente, models.PROTECT)
    producto = models.ForeignKey(Producto, models.PROTECT)
    descripcion = models.TextField()
    puntuacion = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cliente.user.username} - {self.producto.nombre}'

    class Meta:
        verbose_name_plural = "Comentarios"
