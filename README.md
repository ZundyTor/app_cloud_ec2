# Conversor de Moneda Flask en la Nube (AWS EC2)

## Descripción

Aplicación web mínima en Flask (Python) que convierte montos entre USD, EUR y COP usando tasas fijas de ejemplo.  
Incluye una interfaz web con listas desplegables, campo de monto, botón Convertir y opción para descargar el código fuente como ZIP (`/download`).  
El objetivo es demostrar el despliegue y funcionamiento en la nube usando AWS EC2.

---

## Tecnologías Utilizadas

- **Python 3.10+**
- **Flask** (microframework web)
- **Gunicorn** (WSGI server para producción en Linux/EC2)
- **Nginx** (reverse proxy para producción)
- **Git / GitHub**
- **AWS EC2** (Ubuntu Server 22.04 LTS — t2.micro/t3.micro Free Tier)

---

## URL / IP Pública

- Página principal: `http://<PUBLIC_IP>/`
- API de conversión: `http://<PUBLIC_IP>/api/convert?from=USD&to=EUR&amount=10`
- Descargar proyecto: `http://<PUBLIC_IP>/download`

> **Nota:** Reemplaza `<PUBLIC_IP>` por la dirección pública de tu instancia EC2.

---

## Requisitos Previos

### Local

- Python 3.x instalado (`python3 --version`)
- Git instalado
- Conocimientos básicos de terminal/Línea de comandos

### AWS

- Cuenta activa en AWS (puedes usar Free Tier)
- Usuario IAM (recomendado, no usar root para tareas rutinarias)
- Key Pair (.pem) para acceso SSH
- Familiaridad con consola AWS y SSH

---

## Instrucciones de Despliegue en AWS EC2

### 1. Crear Instancia EC2

1. Ingresa a [AWS EC2](https://console.aws.amazon.com/ec2/)
2. Haz clic en **Launch Instance**
3. Selecciona **Ubuntu Server 22.04 LTS (Free Tier eligible)**
4. Elige el tipo de instancia **t2.micro** o **t3.micro** (Free Tier)
5. **Key Pair:** Crea o selecciona una existente. Descarga el archivo `.pem` y guárdalo de forma segura.
6. En **Network settings**, configura el **Security Group**:
    - Permite el puerto **22** (SSH) solo para tu IP.
    - Permite el puerto **80** (HTTP) de cualquier origen (`0.0.0.0/0`).
    - Permite el puerto **443** (HTTPS) si planeas usar HTTPS.
7. Lanza la instancia.

### 2. Conectar por SSH

En tu terminal local, navega donde guardaste el `.pem` y conecta usando la IP pública de la instancia:

```bash
chmod 400 tu_clave.pem
ssh -i tu_clave.pem ubuntu@<PUBLIC_IP>
```

---

### 3. Actualizar e Instalar Dependencias  
**(Ejecuta estos comandos FUERA del entorno virtual)**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx -y
```
> Si al ejecutar `sudo nginx -t`, obtienes **nginx: command not found**, es porque Nginx no está instalado. Instálalo con el comando anterior.

---

### 4. Clonar el Proyecto  
```bash
git clone https://github.com/ZundyTor/app_cloud_ec2.git
cd app_cloud_ec2
```

---

### 5. Crear y Activar Entorno Virtual  

```bash
python3 -m venv venv
```
Para activar el entorno virtual:
```bash
source venv/bin/activate
```
> A partir de este punto, todos los comandos de Python, pip, Flask y Gunicorn deben ejecutarse **dentro del entorno virtual**.

---

### 6. Instalar Dependencias Python  
**(DENTRO del entorno virtual)**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 7. Probar la Aplicación Flask (solo para validar)  
**(DENTRO del entorno virtual)**

```bash
python application.py
```
- Accede desde el navegador: `http://<PUBLIC_IP>:5000`
- Para producción, **detén** el servidor con `Ctrl+C`.

---

## 8. Desplegar con Gunicorn y Nginx (Modo Producción)

### 8.1. Ejecutar Gunicorn  
**(DENTRO del entorno virtual)**

- El comando para Gunicorn es:  
  ```bash
  gunicorn --bind 127.0.0.1:8000 application:application
  ```
  > **No pongas `.py` en el nombre del archivo!**

---

### 8.2. Configurar Nginx como Reverse Proxy  
**(TODO lo relacionado con Nginx va FUERA del entorno virtual)**

1. Crea archivo de configuración:

   ```bash
   sudo nano /etc/nginx/sites-available/flaskapp
   ```

2. Agrega lo siguiente:

   ```
   server {
       listen 80;
       server_name <PUBLIC_IP>;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. Habilita el sitio (enlace simbólico) y reinicia Nginx:

   ```bash
   sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/flaskapp
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### Errores comunes y soluciones:
- Si recibes `File exists`, elimina el enlace existente:
  ```bash
  sudo rm /etc/nginx/sites-enabled/flaskapp
  ```
  y vuelve a crear el enlace.
- Si ves `Not a directory`, elimina el archivo y crea el directorio:
  ```bash
  sudo rm /etc/nginx/sites-enabled
  sudo mkdir /etc/nginx/sites-enabled
  ```
  Luego crea el enlace.
- **NO elimines el directorio `/etc/nginx/sites-enabled`, solo el archivo/enlace dentro si es necesario.**

---

## 9. Acceso y Verificación

- Accede a `http://<PUBLIC_IP>/` desde cualquier navegador.
- Prueba los endpoints, conversión y descarga de ZIP.
- Para probar desde la terminal:  
  **(FUERA del entorno virtual)**  
  ```bash
  curl -I http://localhost/
  ```
  Debes ver `HTTP/1.1 200 OK`.

- Para probar Gunicorn directamente:  
  **(DENTRO del entorno virtual, con Gunicorn corriendo)**  
  ```bash
  curl -I http://127.0.0.1:8000/
  ```
  Debes recibir `HTTP/1.1 200 OK`.

---

## 10. Configuración de Security Groups

- **22 (SSH):** Solo para tu IP pública. Elimínalo o restringe tras el despliegue.
- **80 (HTTP):** Abierto para todo el mundo (`0.0.0.0/0`).
- **443 (HTTPS):** Opcional, requiere configuración adicional de SSL.
- Asegúrate de **no exponer otros puertos innecesarios**.

---

## 11. Errores Comunes y Soluciones

- **Ejecutar Gunicorn fuera del venv:**  
  Si no activas el entorno virtual antes de ejecutar Gunicorn, no funcionará y Nginx devolverá un error 502 Bad Gateway.
  **Solución:** Activa el entorno virtual con `source venv/bin/activate` antes de ejecutar Gunicorn.

- **sudo nginx -t: command not found:**  
  Nginx no está instalado. Instálalo con `sudo apt install nginx`.
- **Permiso denegado al conectar por SSH:**  
  Revisa que usas `chmod 400` y el usuario es `ubuntu`.
- **App no responde en el navegador:**  
  Verifica que Gunicorn esté corriendo **dentro del venv** y Nginx esté configurado correctamente.
- **Error 502 Bad Gateway:**  
  Comprueba que Gunicorn corre **en el venv** y el proxy_pass apunta correctamente.
- **sudo ln -s ... File exists:**  
  El enlace ya existe. Elimínalo con `sudo rm /etc/nginx/sites-enabled/flaskapp`.
- **rm: cannot remove ... Is a directory:**  
  Estás intentando eliminar el directorio en vez de un archivo dentro. Usa el nombre completo del archivo/enlace.

---

## 12. Buenas Prácticas

- **Comandos a ejecutar DENTRO del venv:**
  - Activar entorno virtual: `source venv/bin/activate`
  - Instalar dependencias Python: `pip install ...`
  - Ejecutar Flask o Gunicorn

- **Comandos a ejecutar FUERA del venv:**
  - Instalar dependencias del sistema (`sudo apt install ...`)
  - Configuración y administración de Nginx
  - Comandos `sudo` en general
  - Clonado del repositorio

---

## 13. Créditos y Autores

- Desarrollo: [ZundyTor](https://github.com/ZundyTor)

---

## 14. Referencias

- [Documentación Flask](https://flask.palletsprojects.com/)
- [Guía oficial AWS EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [Gunicorn](https://gunicorn.org/)
- [Nginx](https://nginx.org/)

---

> Si tienes dudas, problemas no cubiertos o quieres contribuir, crea un issue en el repositorio.



