# Descripción
Aplicación web mínima en Flask (Python) que convierte montos entre USD / EUR / COP usando tasas de ejemplo. Incluye UI con dos listas desplegables, campo de monto y botón Convertir, y botón para descargar un ZIP con todo el proyecto (/download).

Aplicación en Flask que:
- Convierte cantidades entre USD, EUR y COP (tasas fijas).
- Muestra una UI responsiva con dropdowns, input y botones.
- Permite descargar el código completo vía /download para que otra persona lo ejecute localmente.

# Tecnologías
- Python 3.10+
- Flask
- Gunicorn (para Linux/EC2)
- Waitress (opcional para Windows)
- Nginx (reverse proxy)
- systemd (servicio de Gunicorn)
- Git / GitHub
- AWS EC2 (Ubuntu Server 22.04 LTS — t2.micro/t3.micro Free Tier)

# URL / IP pública
- Página principal: http://<PUBLIC_IP_O_DNS>/
- API de conversión: http://<PUBLIC_IP_O_DNS>/api/convert?from=USD&to=EUR&amount=10
- Descargar ZIP: http://<PUBLIC_IP_O_DNS>/download

# Requisitos previos
Local
- Python 3 instalado (python --version o py -3 --version).
- Git.
- Conocimientos básicos de terminal/PowerShell.
AWS
- Cuenta AWS activa.
- IAM user recomendado (no root) para tareas rutinarias.
- Key Pair (.pem) para SSH.
- Conocer Free Tier (usar t2.micro/t3.micro y vigilar facturación).

# Ejecutar localmente
Windows (Powershell)
```
cd C:\ruta\a\mi_app_ec2
```

# Crear y activar venv
Windows (Powershell)
```
python -m venv venv
```

# Si PowerShell bloquea scripts (temporal para sesión)
Windows (Powershell)
``Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process``

# Activar
Windows (Powershell)
```
.\venv\Scripts\Activate.ps1
```

# Instalar dependencias
Windows (Powershell)
```
pip install --upgrade pip
pip install -r requirements.txt
```

# Ejecutar (dev)
Windows (Powershell)
```
python application.py
```
- Abrir http://localhost:5000

# Opcional si falla en Windows
Windows (Powershell)
```
pip install waitress
waitress-serve --port=8000 application:application
```

# Linux/macOS
```
cd ~/mi_app_ec2
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python application.py
```
- Abrir http://localhost:5000
- Para detener el servidor: Ctrl + C. Para salir del venv: deactivate

# Crear y configurar EC2 (consola AWS — pasos)
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

# Despliegue en la instancia (Ubuntu 22.04)
Desde máquina local:
```
chmod 400 mi_aws_key.pem
ssh -i "mi_aws_key.pem" ubuntu@<PUBLIC_IP_O_DNS>
```

# En la instancia (usuario ubuntu):
- Actualizar e instalar paquetes
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx
```

# (Opcional) crear usuario de despliegue
```
sudo adduser --disabled-password --gecos "" deployer
sudo usermod -aG sudo deployer
sudo mkdir -p /var/www
sudo chown deployer:deployer /var/www
```

# Cambiar a deployer
```
sudo su - deployer
cd /var/www
```

# Clonar repo (reemplaza TU_USUARIO)
```
git clone https://github.com/TU_USUARIO/mi_app_ec2.git
cd mi_app_ec2
```

# Crear venv e instalar dependencias
```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Probar con gunicorn (temporal)
``gunicorn --bind 0.0.0.0:8000 application:application``
- Abrir en navegador: http://<PUBLIC_IP_O_DNS>:8000
- Ctrl+C para detener

# systemd + Gunicorn + Nginx (archivos y comandos)
Ejecutar como root o con sudo:
``sudo tee /etc/systemd/system/mi_app_gunicorn.service > /dev/null <<'EOF'``
[Unit]
Description=Gunicorn instance to serve mi_app_ec2
After=network.target

[Service]
User=deployer
Group=www-data
WorkingDirectory=/var/www/mi_app_ec2
Environment="PATH=/var/www/mi_app_ec2/venv/bin"
ExecStart=/var/www/mi_app_ec2/venv/bin/gunicorn --workers 3 --bind unix:/var/www/mi_app_ec2/mi_app.sock application:application

[Install]
WantedBy=multi-user.target
EOF

# Activar y arrancar:
```
sudo systemctl daemon-reload
sudo systemctl start mi_app_gunicorn
sudo systemctl enable mi_app_gunicorn
sudo systemctl status mi_app_gunicorn
```

# Configurar Nginx
Crear archivo /etc/nginx/sites-available/mi_app:
```
sudo tee /etc/nginx/sites-available/mi_app > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/mi_app_ec2/mi_app.sock;
    }

    location /static/ {
        alias /var/www/mi_app_ec2/static/;
    }
}
EOF
```

# Habilitar y reiniciar Nginx:
```
sudo ln -s /etc/nginx/sites-available/mi_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
- Verifica en navegador: http://<PUBLIC_IP_O_DNS>/

# Verificación y pruebas
Comprobaciones recomendadas:
1. UI: abrir http://<PUBLIC_IP_O_DNS>/ — la interfaz debe mostrarse con dropdowns, input y botones.

Problemas comunes y soluciones
- 502 Bad Gateway (Nginx)
    - Causa: Gunicorn no está corriendo o socket incorrecto.
    - Comandos de depuración:
        sudo systemctl status mi_app_gunicorn
        sudo journalctl -u mi_app_gunicorn -n 200
        sudo tail -n 200 /var/log/nginx/error.log
    - Solución: revisar ExecStart y rutas de socket, reiniciar servicio.
- Permisos .pem / SSH
    - Ejecuta: chmod 400 mi_aws_key.pem y usa el usuario correcto (ubuntu@...).
- gunicorn: command not found
    - Asegúrate de activar el venv antes: source venv/bin/activate y pip install gunicorn
- WSGI: callable 'application' no encontrado
    - Verificar que tu archivo sea application.py y contenga application = Flask(...). En systemd/Gunicorn se usa application:application
- PowerShell - ejecución de scripts bloqueada
    - Para la sesión actual: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    - Alternativa para activar: usar activate.bat en Windows o CMD:
        .\venv\Scripts\activate.bat
- Cargos inesperados
    - Revisa EC2 Instances, EBS Volumes, S3 Buckets. Termina instancias y borra volúmenes. Consulta Billing & Cost Explorer.

# Limpieza / evitar cobros
Consola (GUI):
- EC2 → Instances → seleccionar → Actions → Instance State → Terminate
- EC2 → Volumes → eliminar volúmenes no usados 
- EC2 → Key Pairs → eliminar si no se usará
- S3 → eliminar buckets (si se crearon)

AWS CLI (si configurado):
aws ec2 terminate-instances --instance-ids i-XXXXXXXXXXXXX
aws ec2 delete-key-pair --key-name mi-key-name
aws s3 rb s3://mi-bucket --force

Espera que el estado sea terminated y revisa Cost Explorer para confirmar que no haya cargos residuales.














