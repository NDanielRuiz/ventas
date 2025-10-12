import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar las variables de entorno desde el archivo .env
print(">>> Cargando variables desde el archivo .env...")
load_dotenv()

# Leer las credenciales y configuración
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_storage_bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
aws_s3_region_name = os.environ.get('AWS_S3_REGION_NAME')

# --- VERIFICACIÓN INICIAL ---
print("--- Verificando variables leídas ---")
if aws_access_key_id:
    print(f"Access Key ID: {aws_access_key_id[:4]}... (OK)")
else:
    print("Access Key ID: NO ENCONTRADO")

print(f"Bucket Name: {aws_storage_bucket_name} (leído)")
print(f"Region Name: {aws_s3_region_name} (leído)")
print("------------------------------------\n")

# Crear un cliente de S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_s3_region_name
)

try:
    file_content = b"Este es un archivo de prueba."
    file_name = "test-directo-desde-terminal.txt"

    print(f"Intentando subir '{file_name}' al bucket '{aws_storage_bucket_name}'...")

    # Subir el archivo
    s3_client.put_object(
        Bucket=aws_storage_bucket_name,
        Key=f"media/{file_name}",
        Body=file_content,
        ACL='public-read'
    )

    print("\n¡¡¡ÉXITO!!! El archivo se subió correctamente a S3.")
    print("Puedes verificarlo en tu bucket en la consola de AWS.")

except ClientError as e:
    # Atrapamos específicamente los errores de AWS
    print("\n!!!!!!!!!! ERROR DE AWS ATRAPADO !!!!!!!!!!")
    print(f"Código de error: {e.response['Error']['Code']}")
    print(f"Mensaje de error: {e.response['Error']['Message']}")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")