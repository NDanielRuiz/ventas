# ventas/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # URLs de Clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('clientes/<int:cliente_id>/borrar/', views.borrar_cliente, name='borrar_cliente'),

    # URLs de Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:producto_id>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/borrar/', views.borrar_producto, name='borrar_producto'),

    # URLs de Facturas
    path('facturas/', views.lista_facturas, name='lista_facturas'),
    path('facturas/crear/', views.crear_factura, name='crear_factura'),
    path('facturas/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('facturas/<int:factura_id>/editar/', views.editar_factura, name='editar_factura'), # <-- AÑADE ESTA LÍNEA
    path('facturas/<int:factura_id>/pago/', views.añadir_pago, name='añadir_pago'),
    path('facturas/<int:factura_id>/comprobante/', views.vista_comprobante, name='vista_comprobante'),
    path('facturas/<int:factura_id>/borrar/', views.borrar_factura, name='borrar_factura'),

    path('login/', auth_views.LoginView.as_view(
        template_name='ventas/login.html',
        authentication_form=CustomAuthenticationForm # Le decimos que use nuestro formulario
    ), name='login'),

    

    path('', views.dashboard, name='dashboard'),

    # URLs de Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='ventas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]