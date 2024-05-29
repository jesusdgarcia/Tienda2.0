from django.urls import path
from django.views.generic import TemplateView

from shop.views import *

urlpatterns = [
    # CRUD
    path('admin/producto/listado', ListadoProductosView.as_view(), name='listaProductos'),
    path('admin/producto/detalles/<int:pk>', DetalleProductoView.as_view(), name='detalleProducto'),
    path('admin/producto/edicion/<int:pk>', staff_member_required(EditarProductoView.as_view()), name='editarProducto'),
    path('admin/producto/nuevo', staff_member_required(NuevoProductoView.as_view()), name='nuevoProducto'),
    path('admin/producto/eliminar/<int:pk>', staff_member_required(EliminarProductoView.as_view()), name='eliminarProducto'),

    # TIENDA
    path('', ListaProductosFiltroCompraView.as_view(), name='welcome'),
    path('detalleProducto/<int:pk>', DetallesProductoCompraView.as_view(), name='detalleProducto'),
    path('compraFinalizada', TemplateView.as_view(template_name="compra/compraRealizada.html"), name='comprafinalizada'),
    # path('detalleCompra/<int:pk>', DetallesCompraView.as_view(), name='detalleCompra'),
    # path('compra/<int:pk>/<int:cantidad>', CheckoutCompraProductosView.as_view(), name='comprarProductos'),

    # COMPRA CARRITO
    path('carrito', ListaProductosCarritoView.as_view(), name='listaCarrito'),
    path('carrito/detalleProducto/<int:pk>', DetalleProductoCarritoView.as_view(), name='detalleProductoCompraCarrito'),
    path('carrito/detalleItemCarrito/<int:pk>', AniadirProductosCarritoView.as_view(), name='aniadirProductoCompraCarrito'),
    path('carrito/borrar/<int:pk>', BorrarItemCarritoView.as_view(), name='borrarItemCarrito'),
    path('carrito/actualizar/<int:pk>', ActualizarItemCarritoView.as_view(), name='actualizarItemCarrito'),
    path('carrito/confirmacion', DetalleCompraCarritoView.as_view(), name='comprarItemsConfirmacion'),
    path('carrito/comprar', CheckoutCompraCarritoView.as_view(), name='comprarItemsCheckout'),

    # VALORACION
    path('valorar/<int:pk>', HacerValoracionProducto.as_view(), name='valorarProducto'),
    path('valorar/editar/<int:pk>', EditarValoracionProducto.as_view(), name='editarValorarProducto'),

    # INFORMES
    path('informes', staff_member_required(TemplateView.as_view(template_name='informes/informes.html')), name='informes'),
    path('informes/top10vendidos', staff_member_required(InformeTop10VendidosView.as_view()), name='topTenVendidos'),
    path('informes/top10clientes', staff_member_required(InformeTop10ClientesView.as_view()), name='topTenClientes'),
    path('informes/comprasClientes', staff_member_required(InformeComprasClienteView.as_view()), name='comprasCliente'),
    path('informes/productosMarca', staff_member_required(InformeProductosMarcaView.as_view()), name='productosMarca')


]
