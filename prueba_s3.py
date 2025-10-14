from django.contrib.auth.models import User
from ventas.models import Producto
from django.core.files import File
import traceback

try:
    print(">>> Obteniendo tu usuario...")
    # Reemplaza 'ivonne' con tu nombre de usuario si es diferente
    usuario = User.objects.get(username='ivonne') 

    print(">>> Creando un nuevo objeto Producto en memoria...")
    nuevo_producto = Producto(
        usuario=usuario,
        nombre="Prueba Definitiva desde Shell",
        precio=1.00
    )

    print(">>> Abriendo el archivo de imagen local...")
    with open('test-image.jpg', 'rb') as f:
        # Adjuntamos el archivo al campo 'imagen'
        nuevo_producto.imagen.save('test-image.jpg', File(f))

        print("\n¡¡¡ÉXITO!!! El archivo se ha subido a S3.")
        print(f"URL generada: {nuevo_producto.imagen.url}")

except Exception as e:
    print("\n!!!!!!!!!! ERROR FINAL ATRAPADO !!!!!!!!!!")
    traceback.print_exc()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")