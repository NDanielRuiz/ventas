from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
import os
from .models import Cliente, Producto, Factura, DetalleFactura, Pago

# ==============================================================================
# FORMULARIOS PARA CLIENTES
# ==============================================================================

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']


# ==============================================================================
# FORMULARIOS PARA PRODUCTOS
# ==============================================================================

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']

    def clean_imagen(self):
        """
        Añade validaciones de seguridad al campo de la imagen para prevenir
        la subida de archivos maliciosos o inapropiados.
        """
        imagen = self.cleaned_data.get('imagen', False)
        if imagen:
            # 1. Límite de tamaño del archivo (ej. 5MB)
            if imagen.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen no puede pesar más de 5MB.")
            
            # 2. Validar la extensión del archivo
            ext = os.path.splitext(imagen.name)[1]
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if not ext.lower() in valid_extensions:
                raise ValidationError("Tipo de archivo no válido. Solo se permiten imágenes .jpg, .jpeg o .png.")
        
        # Si se pasa la validación, se devuelve el objeto de la imagen
        return imagen


# ==============================================================================
# FORMULARIOS PARA FACTURAS Y PAGOS
# ==============================================================================

class FacturaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        Filtra el queryset del campo 'cliente' para mostrar solo los clientes
        que pertenecen al usuario que está creando la factura.
        """
        usuario = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['cliente'].queryset = Cliente.objects.filter(usuario=usuario)

    class Meta:
        model = Factura
        fields = ['cliente', 'numero_cuotas']


DetalleFacturaFormSet = forms.inlineformset_factory(
    Factura,
    DetalleFactura,
    fields=('producto', 'cantidad'),
    extra=1, # Muestra un formulario vacío para empezar
    can_delete=True # Permite eliminar detalles de una factura existente
)

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo_pago']


# ==============================================================================
# FORMULARIO DE AUTENTICACIÓN
# ==============================================================================

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de login personalizado para añadir clases de Bootstrap y placeholders
    sin necesidad de usar widget_tweaks en la plantilla.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nombre de usuario'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Contraseña'}
        )