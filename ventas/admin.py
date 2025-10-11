from django.contrib import admin
from .models import Cliente, Producto, Factura, DetalleFactura, Pago, Perfil

admin.site.register(Perfil)

# Esta clase base no cambia
class MultiTenantModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        super().save_model(request, obj, form, change)

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 1

# --- NUEVA FORMA DE REGISTRAR Y CONFIGURAR ---

# El decorador @admin.register es una forma más limpia de hacer admin.site.register()
@admin.register(Cliente)
class ClienteAdmin(MultiTenantModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')
    # EXCLUIMOS EL CAMPO 'usuario' DEL FORMULARIO
    exclude = ('usuario',)

@admin.register(Producto)
class ProductoAdmin(MultiTenantModelAdmin):
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)
    # EXCLUIMOS EL CAMPO 'usuario' DEL FORMULARIO
    exclude = ('usuario',)

@admin.register(Factura)
class FacturaAdmin(MultiTenantModelAdmin):
    inlines = [DetalleFacturaInline]
    list_display = ('id', 'cliente', 'fecha_emision', 'total', 'saldo_pendiente', 'estado')
    list_filter = ('estado', 'fecha_emision')
    # EXCLUIMOS EL CAMPO 'usuario' DEL FORMULARIO
    exclude = ('usuario',)

# Estos modelos no necesitan la lógica multi-inquilino directamente
admin.site.register(DetalleFactura)
admin.site.register(Pago)