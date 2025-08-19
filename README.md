Descripción
Aplicación web mínima en Flask (Python) que convierte montos entre USD / EUR / COP usando tasas de ejemplo. Incluye UI con dos listas desplegables, campo de monto y botón Convertir, y botón para descargar un ZIP con todo el proyecto (/download).

Aplicación demostrativa en Flask que:
- Convierte cantidades entre USD, EUR y COP (tasas fijas de     ejemplo).
- Muestra una UI responsiva con dropdowns, input y botones.
- Permite descargar el código completo vía /download para que   otra persona lo ejecute localmente.

Tecnologías
- Python 3.10+
- Flask
- Gunicorn (para Linux/EC2)
- Waitress (opcional para Windows)
- Nginx (reverse proxy)
- systemd (servicio de Gunicorn)
- Git / GitHub
- AWS EC2 (Ubuntu Server 22.04 LTS — t2.micro/t3.micro Free Tier)

URL / IP pública
- Página principal: http://<PUBLIC_IP_O_DNS>/
- API de conversión: http://<PUBLIC_IP_O_DNS>/api/convert?from=USD&to=EUR&amount=10
- Descargar ZIP: http://<PUBLIC_IP_O_DNS>/download

Requisitos previos
Local
- Python 3 instalado (python --version o py -3 --version).
- Git.
- Conocimientos básicos de terminal/PowerShell.
AWS
- Cuenta AWS activa.
- IAM user recomendado (no root) para tareas rutinarias.
- Key Pair (.pem) para SSH.
- Conocer Free Tier (usar t2.micro/t3.micro y vigilar facturación).

Ejecutar localmente
# Windows (Powershell)
cd C:\ruta\a\mi_app_ec2

# crear y activar venv
python -m venv venv

# si PowerShell bloquea scripts (temporal para sesión)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# activar
.\venv\Scripts\Activate.ps1

# instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# ejecutar (dev)
python application.py
# abrir http://localhost:5000

# opcional si falla en Windows
pip install waitress
waitress-serve --port=8000 application:application

# Linux/macOS
cd ~/mi_app_ec2
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python application.py
# abrir http://localhost:5000

Para detener el servidor: Ctrl + C. Para salir del venv: deactivate

Crear y configurar EC2 (consola AWS — pasos)
1. EC2 → Launch instances.
2. AMI: Ubuntu Server 22.04 LTS.
3. Instance type: t2.micro (o t3.micro si está disponible y es elegible Free Tier).
4. Key pair: crea/descarga .pem (guárdalo seguro).
5. Security group inbound (crear/revisar):
    - SSH (22) — Source: tu IP (usar “My IP”)
    - HTTP (80) — Source: 0.0.0.0/0
    - (Opcional) HTTPS (443) — 0.0.0.0/0
6. Launch → obtener Public IPv4 / Public DNS.
Seguridad: restringe SSH a tu IP siempre que sea posible

Despliegue en la instancia (Ubuntu 22.04)
Desde máquina local:
chmod 400 mi_aws_key.pem
ssh -i "mi_aws_key.pem" ubuntu@<PUBLIC_IP_O_DNS>

En la instancia (usuario ubuntu):
# actualizar e instalar paquetes
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx

# (opcional) crear usuario de despliegue
sudo adduser --disabled-password --gecos "" deployer
sudo usermod -aG sudo deployer
sudo mkdir -p /var/www
sudo chown deployer:deployer /var/www

# cambiar a deployer
sudo su - deployer
cd /var/www

# clonar repo (reemplaza TU_USUARIO)
git clone https://github.com/TU_USUARIO/mi_app_ec2.git
cd mi_app_ec2

# crear venv e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# probar con gunicorn (temporal)
gunicorn --bind 0.0.0.0:8000 application:application
# abrir en navegador: http://<PUBLIC_IP_O_DNS>:8000
# Ctrl+C para detener

systemd + Gunicorn + Nginx (archivos y comandos)
