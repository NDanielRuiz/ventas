from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.contrib.auth.models import User
import decimal

# --- NUEVAS IMPORTACIONES PARA MANEJAR IMÁGENES ---
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
import os
import uuid
from django.utils.text import slugify

class Cliente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.nombre} {self.apellido}"

class Producto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Si hay una imagen, la procesamos ANTES de guardar el modelo
        if self.imagen:
            img = Image.open(self.imagen)
            max_width = 640
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            slug_nombre = slugify(self.nombre)
            unique_id = uuid.uuid4()
            nuevo_nombre = f"{slug_nombre}-{unique_id}.jpg"
            
            # 2. Reemplazamos el archivo en memoria, sin guardar el modelo todavía (save=False)
            self.imagen.save(nuevo_nombre, ContentFile(buffer.read()), save=False)

        # 3. Llamamos al método de guardado original UNA SOLA VEZ.
        # En este momento, Django-storages ve que hay una nueva imagen y la sube a S3.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Factura(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ESTADO_CHOICES = [('PENDIENTE', 'Pendiente de Pago'), ('PAGADA', 'Pagada'), ('ATRASADA', 'Atrasada'), ('CANCELADA', 'Cancelada')]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT) 
    fecha_emision = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    numero_cuotas = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    def actualizar_totales(self):
        total_detalles = self.detalles.aggregate(total=Sum(F('cantidad') * F('precio_unitario')))['total'] or decimal.Decimal('0.00')
        total_pagos = self.pagos.aggregate(total=Sum('monto'))['total'] or decimal.Decimal('0.00')
        self.total = total_detalles
        self.saldo_pendiente = self.total - total_pagos
        if self.saldo_pendiente <= 0 and self.total > 0: self.estado = 'PAGADA'
        else: self.estado = 'PENDIENTE'
        self.save()
    def __str__(self): return f"Factura #{self.id} a {self.cliente} - Saldo: ${self.saldo_pendiente}"

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    def save(self, *args, **kwargs):
        if self.precio_unitario is None: self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)
        self.factura.actualizar_totales()
    def __str__(self): return f"{self.cantidad} x {self.producto.nombre}"

class Pago(models.Model):
    METODO_CHOICES = [('EFECTIVO', 'Efectivo'), ('TRANSFERENCIA', 'Transferencia'), ('OTRO', 'Otro')]
    factura = models.ForeignKey(Factura, related_name='pagos', on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(decimal.Decimal('0.01'))])
    metodo_pago = models.CharField(max_length=15, choices=METODO_CHOICES, default='EFECTIVO')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.factura.actualizar_totales()
    def __str__(self): return f"Pago de ${self.monto} para Factura #{self.factura.id}"

# ventas/models.py
# ... (al final del archivo, después de la clase Pago) ...

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_almacen = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"    