from django import forms

from main.models import Direccion, Tarjeta
from .models import Producto, Marca, Cliente


class CantidadProductosForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, max_value=20, required=True, initial=1)


class FilterForm(forms.Form):
    nombre = forms.CharField(required=False)
    marca = forms.ModelMultipleChoiceField(queryset=Marca.objects.all(), required=False,
                                           widget=forms.CheckboxSelectMultiple)


class CompraForm(forms.Form):
    direccion_envio = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True,
                                             label="Direccion de envio")
    direccion_facturacion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=True,
                                                   label="Direccion de facturacion")
    tarjeta = forms.ModelChoiceField(queryset=Tarjeta.objects.all(), required=True, label="Tarjeta")

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)

        if cliente:
            self.fields['direccion_envio'].queryset = cliente.direcciones.all()
            self.fields['direccion_facturacion'].queryset = cliente.direcciones.all()
            self.fields['tarjeta'].queryset = cliente.tarjetas.all()


class FilterClienteForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), required=False, label="Seleccione un cliente")


class FilterMarcaForm(forms.Form):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all(), required=False, label="Seleccione una marca")
