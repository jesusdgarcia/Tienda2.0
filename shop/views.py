from datetime import datetime
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.serializers import deserialize, serialize
from django.core.serializers.base import DeserializationError
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, RedirectView
from django.views.generic.edit import ModelFormMixin, FormMixin

from main.models import Cliente, Direccion, Tarjeta
from shop.forms import FilterForm, FilterClienteForm, FilterMarcaForm, CantidadProductosForm, CompraForm
from shop.models import Producto, Compra, ItemCarrito, Valoracion


# Create your views here.
def cliente_check(user):
    return Cliente.objects.filter(user=user).exists()


# CRUD
class ListadoProductosView(ListView):
    model = Producto
    template_name = 'admin/listadoProductos.html'

    def get_queryset(self):
        return Producto.objects.all()


class DetalleProductoView(DetailView):
    model = Producto
    template_name = 'admin/detalleProducto.html'


class EditarProductoView(UpdateView):
    model = Producto
    template_name = 'admin/editarCrearProducto.html'
    fields = ["marca", "nombre", "modelo", "unidad", "precio", "vip"]
    success_url = reverse_lazy('listaProductos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Nuevo producto"
        return context


class NuevoProductoView(CreateView):
    model = Producto
    template_name = 'admin/editarCrearProducto.html'
    fields = ["marca", "nombre", "modelo", "unidad", "precio", "vip"]
    success_url = reverse_lazy('listaProductos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Nuevo producto"
        return context


class EliminarProductoView(DeleteView, DetailView):
    model = Producto
    context_object_name = 'producto'
    template_name = 'admin/eliminarProducto.html'

    def post(self, request, **kwargs):
        producto = get_object_or_404(Producto, pk=kwargs['pk'])
        producto.delete()
        return redirect('listaProductos')

    def get_object(self, queryset=None):
        return get_object_or_404(Producto, pk=self.kwargs['pk'])


# Compra
class ListaProductosFiltroCompraView(FormMixin, ListView):
    model = Producto
    form_class = FilterForm
    context_object_name = 'productos'
    template_name = 'compra/listadoProductosFormulario.html'

    def get_queryset(self):
        queryset = Producto.objects.all().order_by('marca')
        form = self.form_class(self.request.GET)

        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            marca = form.cleaned_data.get('marca')

            queryset = queryset.filter(nombre__contains=nombre).order_by('marca')
            if marca:
                queryset = queryset.filter(marca__id__in=marca).order_by('marca')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        return context


class DetallesProductoCompraView(DetailView):
    model = Producto
    context_object_name = 'producto'
    template_name = 'compra/detalleProducto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productoContext = get_object_or_404(Producto, pk=self.kwargs.get('pk'))
        context['comentarios'] = Valoracion.objects.filter(producto=productoContext)
        return context


# class DetallesCompraView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
#     model = Producto
#     form_class = CompraForm
#     context_object_name = 'producto'
#     template_name = 'compra/detalleCompra.html'
#
#     def post(self, request, *args, **kwargs):
#         cantidad = 0
#         producto = get_object_or_404(Producto, pk=kwargs['pk'])
#         formulario = CantidadProductosForm(request.POST)
#         # Ejecutamos la validacion
#         if formulario.is_valid():
#             # Los datos se cogen del diccionario cleaned_data
#             cantidad = formulario.cleaned_data['cantidad']
#         total = cantidad * producto.precio
#         return render(request, self.template_name,
#                       {'producto': producto, 'cantidad': cantidad, 'total': total})
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CompraForm(self.request.GET)
#         return context
#
#     def test_func(self):
#         return cliente_check(self.request.user)
#
#
# class CheckoutCompraProductosView(LoginRequiredMixin, UserPassesTestMixin, View):
#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         direccion_envio = None
#         direccion_facturacion = None
#         tarjeta = None
#         formulario = CompraForm(request.POST)
#         # Ejecutamos la validacion
#         if formulario.is_valid():
#             # Los datos se cogen del diccionario cleaned_data
#             direccion_envio = formulario.cleaned_data['direccion_envio']
#             direccion_facturacion = formulario.cleaned_data['direccion_facturacion']
#             tarjeta = formulario.cleaned_data['tarjeta']
#         cantidad = kwargs['cantidad']
#         producto = get_object_or_404(Producto, pk=kwargs['pk'])
#
#         if cantidad <= producto.unidad:
#             cliente = Cliente.objects.get(user=request.user)
#             producto.unidad -= cantidad
#             producto.save()
#             compra = Compra()
#             compra.producto = producto
#             compra.user = cliente
#             compra.unidades = cantidad
#             compra.importe = cantidad * producto.precio
#             compra.fecha = datetime.now()
#             compra.direccion_envio = direccion_envio
#             compra.direccion_facturacion = direccion_facturacion
#             compra.tarjeta = tarjeta
#             compra.save()
#             cliente.saldo -= compra.importe
#             cliente.save()
#         return redirect('listaProductosCompra')
#
#     def test_func(self):
#         return cliente_check(self.request.user)


# Carrito

def deserializer(itemSession):
    itemsCarrito = []

    for item in itemSession:
        try:
            item_deserializado = list(deserialize('json', item))
            item_instance = item_deserializado[0].object
            itemsCarrito.append(item_instance)
        except DeserializationError as e:
            print("Error de deserialización:", e)
    return itemsCarrito


def actualizar(request, producto_id, cantidad):
    if cantidad == 0:
        borrar(request, producto_id)
    else:
        lista_carrito = request.session.get('carrito', [])
        carrito_deserializado = deserializer(lista_carrito)

        for index, carrito in enumerate(carrito_deserializado):
            if producto_id == carrito.producto.id:
                carrito.cantidad = cantidad
                carrito_serializado = serialize('json', [carrito])
                request.session['carrito'][index] = carrito_serializado
                request.session.modified = True
    return


def aniadir(request, producto, cantidad):
    res = False
    item = ItemCarrito(producto=producto, cantidad=cantidad)
    item_json = serialize('json', [item])

    # Si la session no se encuentra, devuelve true y crea la session
    if request.session.get('carrito') is None:
        request.session['carrito'] = []
        print(request.session['carrito'])

    # Añade el item al carrito
    if 'carrito' in request.session and isinstance(request.session['carrito'], list):
        request.session['carrito'].append(item_json)
        request.session.modified = True
        res = True
    return res


def borrar(request, producto_id):
    lista_carrito = request.session.get('carrito', [])
    carrito_deserializado = deserializer(lista_carrito)
    for index, carrito in enumerate(carrito_deserializado):
        if producto_id == carrito.producto.id:
            request.session['carrito'].pop(index)
            request.session.modified = True
    return


class ListaProductosCarritoView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, ListView):
    model = ItemCarrito
    form_class = CantidadProductosForm
    template_name = 'compra/carrito/listadoProductosCarrito.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items_session = self.request.session.get('carrito', [])
        items_carrito = deserializer(items_session)
        context['itemsCarrito'] = items_carrito
        context['form'] = CantidadProductosForm(self.request.GET)
        return context

    def test_func(self):
        return cliente_check(self.request.user)


class DetalleProductoCarritoView(FormMixin, DetailView):
    model = Producto
    form_class = CantidadProductosForm
    context_object_name = 'producto'
    template_name = 'compra/carrito/detalleProducto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CantidadProductosForm(self.request.GET)
        return context


class DetalleCompraCarritoView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, ListView):
    model = ItemCarrito
    form_class = CompraForm
    template_name = 'compra/carrito/detalleCompra.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items_session = self.request.session.get('carrito', [])
        items_carrito = deserializer(items_session)
        cliente = self.request.user.cliente
        context['itemsCarrito'] = items_carrito
        context['total'] = float(sum([item.producto.precio * item.cantidad for item in items_carrito])) * 1.21
        context['form'] = CompraForm(self.request.POST, cliente=cliente)
        return context

    def test_func(self):
        return cliente_check(self.request.user)


class AniadirProductosCarritoView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        cantidad = 0
        producto = get_object_or_404(Producto, pk=kwargs['pk'])
        formulario = CantidadProductosForm(request.POST)
        # Ejecutamos la validacion
        if formulario.is_valid():
            # Los datos se cogen del diccionario cleaned_data
            cantidad = formulario.cleaned_data['cantidad']
        # Serializamos el item carrito
        # item = ItemCarrito(cliente=request.user.cliente, producto=producto, cantidad=cantidad)
        # item_json = serialize('json', [item])
        #
        # # Si la session no se encuentra, devuelve true y crea la session
        # if request.session.get('carrito') is None:
        #     request.session['carrito'] = []
        #     print(request.session['carrito'])
        #
        # # Añade el item al carrito
        if aniadir(request, producto, cantidad):
            return redirect('listaCarrito')
        else:
            return redirect('listaProductosCompra')

    def test_func(self):
        return cliente_check(self.request.user)


class BorrarItemCarritoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        producto_id = self.kwargs.get('pk')
        borrar(request, producto_id)
        # lista_carrito = request.session.get('carrito', [])
        # carrito_deserializado = deserializer(lista_carrito)
        # for index, carrito in enumerate(carrito_deserializado):
        #     if producto_id == carrito.producto.id:
        #         request.session['carrito'].pop(index)
        #         request.session.modified = True
        return redirect('listaCarrito')


class ActualizarItemCarritoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Obtener el producto correspondiente al pk de la URL
        cantidad = 0
        producto_id = self.kwargs.get('pk')
        formulario = CantidadProductosForm(request.POST)
        # Ejecutamos la validacion
        if formulario.is_valid():
            # Los datos se cogen del diccionario cleaned_data
            cantidad = formulario.cleaned_data['cantidad']
        # Obtener el carrito actual de la sesión
        # lista_carrito = request.session.get('carrito', [])
        #
        # carrito_deserializado = deserializer(lista_carrito)
        #
        # for index, carrito in enumerate(carrito_deserializado):
        #     if producto_id == carrito.producto.id:
        #         carrito.cantidad = cantidad
        #         carrito_serializado = serialize('json', [carrito])
        #         request.session['carrito'][index] = carrito_serializado
        #         request.session.modified = True
        actualizar(request, producto_id, cantidad)
        return redirect('listaCarrito')


class CheckoutCompraCarritoView(LoginRequiredMixin, UserPassesTestMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        direccion_envio = Direccion()
        direccion_facturacion = Direccion()
        tarjeta = Tarjeta()
        # Declaramos la compra
        compra = Compra()
        cliente = request.user.cliente
        importeTotal = 0
        formulario = CompraForm(request.POST)
        # Ejecutamos la validacion
        if formulario.is_valid():
            # Los datos se cogen del diccionario cleaned_data
            direccion_envio = formulario.cleaned_data['direccion_envio']
            direccion_facturacion = formulario.cleaned_data['direccion_facturacion']
            tarjeta = formulario.cleaned_data['tarjeta']

        # Desserializamos para comprar
        items_session = self.request.session.get('carrito', [])
        items_carrito = deserializer(items_session)

        # Instanciamos la compra
        compra.cliente = cliente
        compra.fecha = datetime.now()
        compra.direccion_envio = direccion_envio
        compra.direccion_facturacion = direccion_facturacion
        compra.tarjeta = tarjeta
        compra.unidades = sum(item.cantidad for item in items_carrito)
        compra.save()

        for item in items_carrito:
            if item.cantidad <= item.producto.unidad:
                producto = item.producto
                cantidad = item.cantidad

                itemCompra = ItemCarrito()
                itemCompra.compra = compra
                itemCompra.producto = producto
                itemCompra.cantidad = cantidad
                itemCompra.importe = item.cantidad * item.producto.precio * Decimal(1.21)
                itemCompra.save()

                producto.unidad -= cantidad
                producto.save()

                importeTotal += itemCompra.importe

        compra.importe = importeTotal
        compra.save()

        cliente.saldo -= Decimal(compra.importe)
        cliente.save()

        request.session['carrito'] = []
        request.session.modified = True
        return redirect('comprafinalizada')

    def test_func(self):
        return cliente_check(self.request.user)


# Valoracion
class HacerValoracionProducto(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Valoracion
    template_name = 'valoracion/editarCrearValoracion.html'
    fields = ["descripcion", "puntuacion"]
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=self.kwargs.get('pk'))
        valoracion_existente = Valoracion.objects.filter(cliente=get_object_or_404(Cliente, user=request.user), producto=producto).exists()
        if valoracion_existente:
            return redirect(reverse('editarValorarProducto', kwargs={'pk': producto.pk}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valoracion = form.save(commit=False)
        valoracion.cliente = get_object_or_404(Cliente, user=self.request.user)
        valoracion.producto = get_object_or_404(Producto, pk=self.kwargs.get('pk'))
        valoracion.fecha_creacion = datetime.now()
        valoracion.save()
        return super().form_valid(form)

    def test_func(self):
        return cliente_check(self.request.user)


class EditarValoracionProducto(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Valoracion
    template_name = 'valoracion/editarCrearValoracion.html'
    fields = ["descripcion", "puntuacion"]
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        valoracion = get_object_or_404(Valoracion, cliente__user=self.request.user, producto__pk=self.kwargs.get('pk'))
        return valoracion

    def test_func(self):
        return cliente_check(self.request.user)


# Informes
class InformeTop10VendidosView(ListView):
    model = Producto
    template_name = 'informes/top10vendidos.html'

    def get_queryset(self):
        return Producto.objects.annotate(sumVentas=Sum('compra__unidades'),
                                         sumImportes=Sum('compra__importe')).order_by('sumVentas')[:10]


class InformeTop10ClientesView(ListView):
    model = Cliente
    template_name = 'informes/top10clientes.html'

    def get_queryset(self):
        return Cliente.objects.annotate(sumImportes=Sum('compra__importe')).order_by('-sumImportes')[:10]


class InformeComprasClienteView(FormMixin, ListView):
    model = Compra
    form_class = FilterClienteForm
    context_object_name = 'compras'
    template_name = 'informes/comprasCliente.html'

    def get_queryset(self):
        queryset = Compra.objects.all()
        form = self.form_class(self.request.GET)

        if form.is_valid():
            cliente = form.cleaned_data.get('cliente')
            queryset = queryset.filter(user=cliente)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)
        return context


class InformeProductosMarcaView(FormMixin, ListView):
    http_method_names = ['get']
    model = Producto
    form_class = FilterMarcaForm
    context_object_name = 'productos'
    template_name = 'informes/productosMarca.html'
    form = None

    def get_queryset(self):
        queryset = Producto.objects.all()
        self.form = self.form_class(self.request.GET)

        if self.form.is_valid() and self.form.cleaned_data.get('marca'):
            marca = self.form.cleaned_data.get('marca')
            queryset = queryset.filter(marca=marca)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context
