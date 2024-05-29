from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    # ruta para establecer idioma
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('shop.urls'), name='welcome'),

    # Accounts
    path('accounts/login/', LoginClienteView.as_view(), name='login'),
    path('accounts/logout/', LogoutClienteView.as_view(), name='logout'),
    path('accounts/signup/', SignUpClienteView.as_view(), name='signup', ),
    path('accounts/profile/', ProfileClienteView.as_view(), name='profile'),
    path('accounts/profile/edit', EditClienteView.as_view(), name='profileEdit'),

    # Accounts/Direcciones
    path('accounts/profile/direccion/editar/<int:pk>', EditarDireccionView.as_view(), name='editarDireccion'),
    path('accounts/profile/direccion/nueva', NuevaDireccionView.as_view(), name='nuevaDireccion'),
    path('accounts/profile/direccion/eliminar/<int:pk>', EliminarDireccionView.as_view(), name='eliminarDireccion'),

    # Accounts/Tarjetas
    path('accounts/profile/tarjeta/editar/<int:pk>', EditarTarjetaView.as_view(), name='editarTarjeta'),
    path('accounts/profile/tarjeta/nueva', NuevaTarjetaView.as_view(), name='nuevaTarjeta'),
    path('accounts/profile/tarjeta/eliminar/<int:pk>', EliminarTarjetaView.as_view(), name='eliminarTarjeta'),

    # Accounts/Compras
    path('accounts/profile/detalleCompra/<int:pk>', DetalleCompraView.as_view(), name='detalleCompra')
]
