from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Cliente, Producto, Factura, Pago # Importar Pago
from .forms import ClienteForm, ProductoForm, FacturaForm, DetalleFacturaFormSet, PagoForm # Importar PagoForm
from django.contrib import messages # <-- 1. IMPORTAMOS LOS MENSAJES
from django.db.models import Sum, Count # Importamos herramientas de agregación


# --- Vistas de Clientes (sin cambios) ---
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_clientes(request):
    clientes = Cliente.objects.filter(usuario=request.user)
    return render(request, 'ventas/lista_clientes.html', {'clientes': clientes})

# ... (las otras vistas de cliente no cambian, pero las incluyo para que copies todo el archivo) ...

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario = request.user
            cliente.save()
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
            return redirect('detalle_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'ventas/editar_cliente.html', {'form': form, 'cliente': cliente})

@login_required
def borrar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'ventas/borrar_cliente.html', {'cliente': cliente})

# --- NUEVAS VISTAS PARA PRODUCTOS ---

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_productos(request):
    productos = Producto.objects.filter(usuario=request.user)
    return render(request, 'ventas/lista_productos.html', {'productos': productos})

@login_required
def crear_producto(request):
    if request.method == 'POST':
        # ANTES: form = ProductoForm(request.POST)
        # AHORA:
        form = ProductoForm(request.POST, request.FILES) # <-- Añadimos request.FILES
        if form.is_valid():
            producto = form.save(commit=False)
            producto.usuario = request.user
            producto.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'ventas/producto_form.html', {'form': form})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    return render(request, 'ventas/detalle_producto.html', {'producto': producto})

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    if request.method == 'POST':
        # ANTES: form = ProductoForm(request.POST, instance=producto)
        # AHORA:
        form = ProductoForm(request.POST, request.FILES, instance=producto) # <-- Añadimos request.FILES
        if form.is_valid():
            form.save()
            return redirect('detalle_producto', producto_id=producto.id)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'ventas/producto_form.html', {'form': form, 'producto': producto})

@login_required
def borrar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, usuario=request.user)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'ventas/borrar_producto.html', {'producto': producto})

# --- NUEVA VISTA PARA CREAR FACTURAS ---
@login_required
def crear_factura(request):
    if request.method == 'POST':
        # Si se envía el formulario, crea instancias con los datos POST
        form = FacturaForm(request.POST)
        formset = DetalleFacturaFormSet(request.POST)

        # Valida ambos
        if form.is_valid() and formset.is_valid():
            # Guarda la factura principal (sin confirmar en la DB)
            factura = form.save(commit=False)
            factura.usuario = request.user # Asigna el usuario
            factura.save() # Ahora guarda en la DB para obtener un ID

            # Asocia el formset con la factura recién creada
            formset.instance = factura
            formset.save() # Guarda todos los detalles de la factura

            # Nuestra lógica en los modelos se encargará de calcular el total
            
            # Redirigir a una página de éxito (aún no la creamos, usamos la lista de clientes)
            return redirect('lista_clientes')
    else:
        # Si se visita por primera vez, muestra formularios vacíos
        form = FacturaForm()
        formset = DetalleFacturaFormSet()

    contexto = {
        'form': form,
        'formset': formset
    }
    return render(request, 'ventas/factura_form.html', contexto)

# --- AÑADE ESTA NUEVA VISTA PARA LISTAR FACTURAS ---
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_facturas(request):
    # Filtramos las facturas por el usuario y las ordenamos por fecha, de la más nueva a la más antigua
    facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_emision')

    return render(request, 'ventas/lista_facturas.html', {'facturas': facturas})

# --- AÑADE ESTA NUEVA VISTA ---
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_factura(request, factura_id):
    # Obtenemos la factura específica, asegurándonos de que pertenezca al usuario logueado
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    
    # Pasamos la factura a la plantilla
    return render(request, 'ventas/detalle_factura.html', {'factura': factura})

# ventas/views.py
# ... (otras importaciones) ...
from .models import Cliente, Producto, Factura, Pago # Importar Pago
from .forms import ClienteForm, ProductoForm, FacturaForm, DetalleFacturaFormSet, PagoForm # Importar PagoForm

# ... (otras vistas no cambian) ...

# --- AÑADE ESTA NUEVA VISTA ---
@login_required
def añadir_pago(request, factura_id):
    # Obtenemos la factura a la que se le añadirá el pago
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.factura = factura # Asignamos la factura al pago
            pago.save() # Al guardar, la lógica del modelo recalculará el saldo
            return redirect('detalle_factura', factura_id=factura.id)
    else:
        form = PagoForm()

    return render(request, 'ventas/pago_form.html', {'form': form, 'factura': factura})

# ventas/views.py
# ... (otras vistas) ...

# --- AÑADE ESTA NUEVA VISTA ---
@login_required
def vista_comprobante(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    return render(request, 'ventas/comprobante.html', {'factura': factura})

# ventas/views.py
# ... (otras vistas)

# --- AÑADE ESTA NUEVA VISTA ---
@login_required
def editar_factura(request, factura_id):
    # Obtenemos la factura que se va a editar
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    if request.method == 'POST':
        # Rellenamos el form y el formset con los datos enviados y la instancia existente
        form = FacturaForm(request.POST, user=request.user, instance=factura)
        formset = DetalleFacturaFormSet(request.POST, instance=factura)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            # La lógica de los modelos se encarga de recalcular totales
            return redirect('detalle_factura', factura_id=factura.id)
    else:
        # Mostramos el form y el formset con los datos actuales de la factura
        form = FacturaForm(user=request.user, instance=factura)
        formset = DetalleFacturaFormSet(instance=factura)

    contexto = {
        'form': form,
        'formset': formset,
        'factura': factura # Pasamos la factura para usarla en el título
    }
    return render(request, 'ventas/factura_form.html', contexto)


@login_required
def borrar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)

    # --- 2. AÑADIMOS NUESTRA REGLA DE NEGOCIO ---
    if factura.saldo_pendiente > 0:
        # Si hay saldo, creamos un mensaje de error
        messages.error(request, '¡Acción no permitida! No se puede borrar una factura con saldo pendiente.')
        # Y redirigimos al detalle de la factura
        return redirect('detalle_factura', factura_id=factura.id)

    # Si el saldo es cero, el resto de la función se ejecuta como antes
    if request.method == 'POST':
        factura.delete()
        messages.success(request, f'La factura #{factura.id} ha sido eliminada con éxito.') # Mensaje de éxito
        return redirect('lista_facturas')

    return render(request, 'ventas/borrar_factura.html', {'factura': factura})

# --- AÑADE ESTA NUEVA VISTA PARA EL DASHBOARD ---
@login_required
def dashboard(request):
    # Contar el total de clientes del usuario
    total_clientes = Cliente.objects.filter(usuario=request.user).count()

    # Contar facturas pendientes
    facturas_pendientes = Factura.objects.filter(usuario=request.user, estado='PENDIENTE').count()

    # Sumar el saldo pendiente de todas las facturas pendientes
    total_por_cobrar = Factura.objects.filter(usuario=request.user, estado='PENDIENTE').aggregate(Sum('saldo_pendiente'))['saldo_pendiente__sum'] or 0

    # Obtener las últimas 5 facturas
    ultimas_facturas = Factura.objects.filter(usuario=request.user).order_by('-fecha_emision')[:5]

    contexto = {
        'total_clientes': total_clientes,
        'facturas_pendientes': facturas_pendientes,
        'total_por_cobrar': total_por_cobrar,
        'ultimas_facturas': ultimas_facturas,
    }
    return render(request, 'ventas/dashboard.html', contexto)