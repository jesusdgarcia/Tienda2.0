from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic import RedirectView, CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin

from main.forms import LoginForm, SignUpForm, EditProfileForm
from main.models import Cliente, Direccion, Tarjeta
from shop.models import Compra, ItemCarrito


# Create your views here.
class LoginClienteView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('welcome')


class LogoutClienteView(RedirectView):
    permanent = False
    url = reverse_lazy('welcome')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutClienteView, self).get(request, *args, **kwargs)


class SignUpClienteView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('welcome')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        cliente = Cliente()
        cliente.user = self.object
        cliente.saldo = 100000000
        cliente.vip = True
        cliente.save()
        login(self.request, self.object)  # Log the user in after signup
        return response


class ProfileClienteView(LoginRequiredMixin, DetailView):
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        alguien = None
        if not self.request.user.is_superuser:
            alguien = Cliente.objects.get(user=self.request.user)
        return alguien

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compras'] = Compra.objects.filter(cliente=self.request.user.cliente).order_by('-fecha')
        return context


class DetalleCompraView(LoginRequiredMixin, DetailView):
    model = Compra
    context_object_name = 'compra'
    template_name = 'accounts/compra/detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compraContext = get_object_or_404(Compra, pk=self.kwargs.get('pk'))
        context['items'] = ItemCarrito.objects.filter(compra = compraContext)
        return context



class EditClienteView(LoginRequiredMixin, UpdateView):
    form_class = EditProfileForm
    template_name = 'accounts/edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


class EditarDireccionView(LoginRequiredMixin, UpdateView):
    model = Direccion
    template_name = 'accounts/direccion/editarCrearDirecciones.html'
    fields = ["name", "address_one", "address_two", "city", "province", "postal_code"]
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Editar direccion"
        return context


class NuevaDireccionView(LoginRequiredMixin, CreateView):
    model = Direccion
    template_name = 'accounts/direccion/editarCrearDirecciones.html'
    fields = ["name", "address_one", "address_two", "city", "province", "postal_code"]
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        with transaction.atomic():
            direccion = form.save()
            cliente = Cliente.objects.get(user=self.request.user)
            cliente.direcciones.add(direccion)
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Nueva direccion"
        return context


class EliminarDireccionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        with transaction.atomic():
            direccion = get_object_or_404(Direccion, pk=kwargs['pk'])
            cliente = Cliente.objects.get(user=self.request.user)
            cliente.direcciones.remove(direccion)
            direccion.delete()
            return redirect(self.get_success_url())


class EditarTarjetaView(LoginRequiredMixin, UpdateView):
    model = Tarjeta
    template_name = 'accounts/tarjeta/editarCrearTarjeta.html'
    fields = ["tipo", "titular", "numero", "mes_caducidad", "anio_caducidad", "codigo_seguridad"]
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Editar tarjeta"
        return context


class NuevaTarjetaView(LoginRequiredMixin, CreateView):
    model = Tarjeta
    template_name = 'accounts/tarjeta/editarCrearTarjeta.html'
    fields = ["tipo", "titular", "numero", "mes_caducidad", "anio_caducidad", "codigo_seguridad"]
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        with transaction.atomic():
            tarjeta = form.save()
            cliente = Cliente.objects.get(user=self.request.user)
            cliente.tarjetas.add(tarjeta)
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_title'] = "Nueva tarjeta"
        return context


class EliminarTarjetaView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        with transaction.atomic():
            tarjeta = get_object_or_404(Tarjeta, pk=kwargs['pk'])
            cliente = Cliente.objects.get(user=self.request.user)
            cliente.tarjetas.remove(tarjeta)
            tarjeta.delete()
            return redirect('profile')
