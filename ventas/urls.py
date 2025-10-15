# ventas/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

# El nombre 'ventas' se define en el archivo urls.py principal del proyecto.
# Todas las URL definidas aquí tendrán el prefijo 'ventas:', por ejemplo: 'ventas:dashboard'
app_name = 'ventas'

urlpatterns = [
    # ==========================================================================
    # URL PRINCIPAL (DASHBOARD)
    # ==========================================================================
    path('', views.dashboard, name='dashboard'),

    # ==========================================================================
    # URLS DE AUTENTICACIÓN
    # ==========================================================================
    path('login/', auth_views.LoginView.as_view(
        template_name='ventas/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # ==========================================================================
    # URLS DE CLIENTES
    # ==========================================================================
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/borrar/', views.borrar_cliente, name='borrar_cliente'),

    # ==========================================================================
    # URLS DE PRODUCTOS
    # ==========================================================================
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/borrar/', views.borrar_producto, name='borrar_producto'),

    # ==========================================================================
    # URLS DE FACTURAS Y PAGOS
    # ==========================================================================
    path('facturas/', views.lista_facturas, name='lista_facturas'),
    path('facturas/crear/', views.crear_factura, name='crear_factura'),
    path('facturas/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('facturas/<int:factura_id>/editar/', views.editar_factura, name='editar_factura'),
    path('facturas/<int:factura_id>/borrar/', views.borrar_factura, name='borrar_factura'),
    path('facturas/<int:factura_id>/pago/', views.añadir_pago, name='añadir_pago'),
    path('facturas/<int:factura_id>/comprobante/', views.vista_comprobante, name='vista_comprobante'),
]