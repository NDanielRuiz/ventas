# Django Imports
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.db.models import Sum, Count, ProtectedError
from django.http import HttpResponse
from django.conf import settings

# AWS SDK
import boto3

# Local Imports
from .models import Cliente, Producto, Factura, Pago, DetalleFactura
from .forms import ClienteForm, ProductoForm, FacturaForm, DetalleFacturaFormSet, PagoForm

# ==============================================================================
# VISTA PRINCIPAL (DASHBOARD)
# ==============================================================================
@login_required
def dashboard(request):
    total_clientes = Cliente.objects.filter(usuario=request.user).count()
    facturas_pendientes = Factura.objects.filter(usuario=request.user, estado='PENDIENTE').count()
    total_por_cobrar = Factura.objects.filter(usuario=request.user, estado='PENDIENTE').aggregate(Sum('saldo_pendiente'))['saldo_pendiente__sum'] or 0
    ultimas_facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_emision')[:5]

    contexto = {
        'total_clientes': total_clientes,
        'facturas_pendientes': facturas_pendientes,
        'total_por_cobrar': total_por_cobrar,
        'ultimas_facturas': ultimas_facturas,
    }
    return render(request, 'ventas/dashboard.html', contexto)

# ==============================================================================
# VISTAS DE CLIENTES
# ==============================================================================
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_clientes(request):
    clientes = Cliente.objects.filter(usuario=request.user)
    return render(request, 'ventas/lista_clientes.html', {'clientes': clientes})

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario = request.user
            cliente.save()
            messages.success(request, f'Cliente "{cliente.nombre}" creado con éxito.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'ventas/crear_cliente.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)
    return render(request, 'ventas/detalle_cliente.html', {'cliente': cliente})

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado con éxito.')
            return redirect('detalle_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'ventas/editar_cliente.html', {'form': form, 'cliente': cliente})

@login_required
def borrar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)
    if request.method == 'POST':
        try:
            nombre_cliente = cliente.nombre
            cliente.delete()
            messages.success(request, f'Cliente "{nombre_cliente}" eliminado con éxito.')
            return redirect('lista_clientes')
        except ProtectedError:
            messages.error(request, f'Error: No se puede eliminar "{cliente.nombre}" porque tiene facturas asociadas.')
            return redirect('detalle_cliente', cliente_id=cliente.id)
    return render(request, 'ventas/borrar_cliente.html', {'cliente': cliente})

# ==============================================================================
# VISTAS DE PRODUCTOS (CON SEGURIDAD DE REKOGNITION)
# ==============================================================================
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_productos(request):
    productos = Producto.objects.filter(usuario=request.user)
    return render(request, 'ventas/lista_productos.html', {'productos': productos})

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = request.FILES.get('imagen')
            if imagen:
                # --- INICIO: VERIFICACIÓN CON AWS REKOGNITION ---
                rekognition = boto3.client('rekognition', region_name=settings.AWS_S3_REGION_NAME)
                imagen.seek(0)
                image_bytes = imagen.read()
                try:
                    response = rekognition.detect_moderation_labels(Image={'Bytes': image_bytes})
                    if response.get('ModerationLabels'):
                        form.add_error('imagen', 'La imagen contiene contenido inapropiado y fue rechazada.')
                        return render(request, 'ventas/producto_form.html', {'form': form})
                except Exception as e:
                    form.add_error(None, f'Hubo un error al analizar la imagen: {e}')
                    return render(request, 'ventas/producto_form.html', {'form': form})
                # --- FIN: VERIFICACIÓN CON AWS REKOGNITION ---

            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            messages.success(request, '¡Producto creado con éxito!')
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'ventas/producto_form.html', {'form': form})

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            imagen = request.FILES.get('imagen')
            if imagen:
                # --- INICIO: VERIFICACIÓN CON AWS REKOGNITION ---
                rekognition = boto3.client('rekognition', region_name=settings.AWS_S3_REGION_NAME)
                imagen.seek(0)
                image_bytes = imagen.read()
                try:
                    response = rekognition.detect_moderation_labels(Image={'Bytes': image_bytes})
                    if response.get('ModerationLabels'):
                        form.add_error('imagen', 'La imagen contiene contenido inapropiado y fue rechazada.')
                        return render(request, 'ventas/producto_form.html', {'form': form, 'producto': producto})
                except Exception as e:
                    form.add_error(None, f'Hubo un error al analizar la imagen: {e}')
                    return render(request, 'ventas/producto_form.html', {'form': form, 'producto': producto})
                # --- FIN: VERIFICACIÓN CON AWS REKOGNITION ---
            
            form.save()
            messages.success(request, 'Producto actualizado con éxito.')
            return redirect('detalle_producto', producto_id=producto.id)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'ventas/producto_form.html', {'form': form, 'producto': producto})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    return render(request, 'ventas/detalle_producto.html', {'producto': producto})

@login_required
def borrar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    if request.method == 'POST':
        try:
            nombre_producto = producto.nombre
            producto.delete()
            messages.success(request, f'El producto "{nombre_producto}" ha sido eliminado con éxito.')
            return redirect('lista_productos')
        except ProtectedError:
            messages.error(request, f'Error: No se puede eliminar "{producto.nombre}" porque ya está siendo usado en una o más facturas.')
            return redirect('detalle_producto', producto_id=producto.id)
    return render(request, 'ventas/borrar_producto.html', {'producto': producto})

# ==============================================================================
# VISTAS DE FACTURAS Y PAGOS
# ==============================================================================
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_facturas(request):
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_emision')
    return render(request, 'ventas/lista_facturas.html', {'facturas': facturas})

@login_required
def crear_factura(request):
    # Pasamos el usuario al formulario para filtrar los clientes
    form = FacturaForm(request.POST or None, user=request.user)
    formset = DetalleFacturaFormSet(request.POST or None)

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        factura = form.save(commit=False)
        factura.usuario = request.user
        factura.save()
        formset.instance = factura
        formset.save()
        messages.success(request, f'Factura #{factura.id} creada con éxito.')
        return redirect('detalle_factura', factura_id=factura.id)

    contexto = {'form': form, 'formset': formset}
    return render(request, 'ventas/factura_form.html', contexto)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    return render(request, 'ventas/detalle_factura.html', {'factura': factura})

@login_required
def editar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    if request.method == 'POST':
        form = FacturaForm(request.POST, user=request.user, instance=factura)
        formset = DetalleFacturaFormSet(request.POST, instance=factura)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Factura #{factura.id} actualizada con éxito.')
            return redirect('detalle_factura', factura_id=factura.id)
    else:
        form = FacturaForm(user=request.user, instance=factura)
        formset = DetalleFacturaFormSet(instance=factura)
    contexto = {'form': form, 'formset': formset, 'factura': factura}
    return render(request, 'ventas/factura_form.html', contexto)

@login_required
def borrar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    if factura.pagos.exists():
        messages.error(request, '¡Acción no permitida! No se puede borrar una factura que ya tiene pagos registrados.')
        return redirect('detalle_factura', factura_id=factura.id)
    if request.method == 'POST':
        factura.delete()
        messages.success(request, f'La factura #{factura.id} ha sido eliminada con éxito.')
        return redirect('lista_facturas')
    return render(request, 'ventas/borrar_factura.html', {'factura': factura})

@login_required
def añadir_pago(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.factura = factura
            pago.save()
            messages.success(request, 'Pago registrado con éxito.')
            return redirect('detalle_factura', factura_id=factura.id)
    else:
        form = PagoForm()
    return render(request, 'ventas/pago_form.html', {'form': form, 'factura': factura})

@login_required
def vista_comprobante(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    return render(request, 'ventas/comprobante.html', {'factura': factura})