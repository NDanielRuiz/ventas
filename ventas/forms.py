from django import forms
from .models import Cliente, Producto, Factura, DetalleFactura, Pago
from django.contrib.auth.forms import AuthenticationForm

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

# --- AÑADE ESTE NUEVO FORMULARIO ---
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# ... (ClienteForm y ProductoForm no cambian) ...
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
        # ... widgets ...

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']
        # ... widgets ...

# --- NUEVOS FORMULARIOS PARA FACTURAS ---
# ventas/forms.py

class FacturaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # 1. SACAMOS el argumento 'user' ANTES de hacer cualquier otra cosa.
        usuario = kwargs.pop('user', None)

        # 2. AHORA llamamos al constructor padre con los argumentos restantes.
        super().__init__(*args, **kwargs)

        # 3. Si el usuario existe, filtramos el queryset del campo 'cliente'.
        if usuario:
            self.fields['cliente'].queryset = Cliente.objects.filter(usuario=usuario)

    class Meta:
        model = Factura
        fields = ['cliente', 'numero_cuotas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'numero_cuotas': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Usamos una factory para crear un FormSet para los detalles de la factura
DetalleFacturaFormSet = forms.inlineformset_factory(
    Factura,
    DetalleFactura,
    fields=('producto', 'cantidad'),
    extra=1, # Muestra un formulario vacío para empezar
    widgets={
        'producto': forms.Select(attrs={'class': 'form-select'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cant.'}),
    }
)

# --- AÑADE ESTE NUEVO FORMULARIO ---
class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo_pago']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

# --- AÑADE ESTE FORMULARIO PERSONALIZADO ---
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos la clase 'form-control' de Bootstrap a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})