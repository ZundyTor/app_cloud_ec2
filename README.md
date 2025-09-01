# Conversor de Moneda Flask en la Nube (AWS EC2)
![Python Tests](https://github.com/ZundyTor/app_cloud_ec2/workflows/Python%20Tests/badge.svg)

Aplicación web mínima en Flask (Python) que convierte montos entre USD, EUR y COP usando tasas fijas de ejemplo.  
Incluye una interfaz web con listas desplegables, campo de monto, botón Convertir y opción para descargar el código fuente como ZIP (`/download`).  
El objetivo es demostrar el despliegue y funcionamiento en la nube usando AWS EC2.

---

## 🚀 Automatización con GitHub Actions

Este proyecto incorpora un workflow básico de integración continua utilizando **GitHub Actions**.  
Cada vez que se realiza un `push` a la rama principal (`main`), se ejecutan automáticamente los siguientes pasos:

- Instalación del entorno Python y dependencias del proyecto (`requirements.txt`)
- Ejecución de tests automáticos (ubicados en `tests/`)
- Validación básica del funcionamiento de la aplicación (status HTTP y pruebas unitarias)

Esto permite detectar errores y asegurar la calidad del código antes de realizar despliegues manuales.

### 📋 Instrucciones para desarrolladores

1. Al realizar un cambio en el código, asegúrate de que los tests pasen localmente:
   ```bash
   python -m unittest discover
   ```
2. Haz commit y push a la rama principal (`main`). El workflow se ejecutará automáticamente en GitHub.
3. Si algún test falla, visualiza el log en la pestaña *Actions* de GitHub para identificar el error.

### 📝 Descripción del Workflow

El archivo `.github/workflows/python.yml` define el proceso de validación automática:

```yaml
name: Python Tests
on:
  push:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m unittest discover
```

---

## Tecnologías Utilizadas

### 🟩 Forma Fácil (solo con Python y Flask)
- **Python 3.10+**
- **Flask** (framework web ligero)
- **JavaScript** (interactividad en el navegador)
- **HTML + CSS** (interfaz web, diseño responsivo)
- **Git / GitHub**
- **AWS EC2** (Ubuntu Server 22.04 LTS — t2.micro/t3.micro Free Tier)

### ⚡ Forma Profesional (producción con Gunicorn y Nginx)
- **Gunicorn** (WSGI server para producción en Linux/EC2)
- **Nginx** (reverse proxy para producción)
- *(Incluye todas las tecnologías anteriores)*

---

## Requisitos Previos para el Desarrollo

Es necesario tener:

- **Sistema Operativo:** Ubuntu 22.04 LTS (recomendado) o cualquier sistema basado en Linux.
- **Python:** Versión 3.10 o superior.
- **pip:** Gestor de paquetes para Python.
- **Git:** Para clonar el repositorio.
- **Acceso a una instancia EC2 de AWS:** (o entorno local compatible)
- **Key Pair de AWS EC2:** Para acceder por SSH a la instancia.
- **Conexión a internet:** Para instalar dependencias y clonar el proyecto.

> Para el despliegue profesional, también necesitarás instalar Gunicorn y Nginx (ver instrucciones más abajo).

---

# 🟢 Despliegue solo con Python y Flask

Esta es la manera más sencilla de desplegar la aplicación, ideal si no se quiere configurar servidores adicionales.  
La app funcionará directamente en la instancia EC2 y será accesible desde el navegador.

---

## 1. Crear Instancia EC2

1. Ingresa a [AWS EC2](https://console.aws.amazon.com/ec2/)
2. Haz clic en **Launch Instance**
3. Selecciona **Ubuntu Server 22.04 LTS (Free Tier eligible)**
4. Elige el tipo de instancia **t2.micro** o **t3.micro** (Free Tier)
5. **Key Pair:** Crea o selecciona una existente. Descarga el archivo `.pem` y guárdalo de forma segura.
6. En **Network settings**, configura el **Security Group**:
    - Permite el puerto **22** (SSH) solo para tu IP.
    - Permite el puerto **5000** (TCP) para todo el mundo (`0.0.0.0/0`). *(Así podrás acceder por el navegador)*
7. Lanza la instancia.

---

## 2. Conectar por SSH

En tu terminal local, navega donde guardaste el `.pem` y conecta usando la IP pública de la instancia:

```bash
chmod 400 tu_clave.pem // Linux
ssh -i tu_clave.pem ubuntu@<PUBLIC_IP> // Windows
```

---

## 3. Instalar Python y Git

```bash
sudo apt update
sudo apt install python3-pip git -y
```

---

## 4. Instalar Flask

```bash
pip3 install flask
```

---

## 5. Clonar el Proyecto

```bash
git clone https://github.com/ZundyTor/app_cloud_ec2.git
cd app_cloud_ec2
```

---

## 6. Ejecutar la Aplicación Flask

```bash
python3 application.py
```

---

## 7. Acceder desde el Navegador

- Ve a **http://<PUBLIC_IP>:5000/** en tu navegador (donde `<PUBLIC_IP>` es la IP pública de tu instancia EC2).
- ¡Ya puedes usar el conversor y descargar el ZIP!

---

## 8. Detener la Aplicación

- Para detener la app presiona `Ctrl+C` en la terminal.

---

## 9. Notas y Recomendaciones

- **Esta forma NO es recomendada para producción** (es perfecta para pruebas, aprendizaje y demos).
- Si cierras la terminal, la app se detiene.
- Si necesitas que la app esté siempre disponible y sea segura, usa la forma profesional (ver abajo).

---

# ⚡ Despliegue con Gunicorn y Nginx

Esta es la manera recomendada para producción, ya que es más segura, robusta y escalable.

---

## 1. Crear Instancia EC2

(Son los mismos pasos que arriba, pero para producción se recomienda abrir solo los puertos 22 y 80).

---

## 2. Conectar por SSH

```bash
chmod 400 tu_clave.pem
ssh -i tu_clave.pem ubuntu@<PUBLIC_IP>
```

---

## 3. Actualizar e Instalar Dependencias  
**(Ejecuta estos comandos FUERA del entorno virtual)**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx -y
```
> Si al ejecutar `sudo nginx -t`, obtienes **nginx: command not found**, es porque Nginx no está instalado. Instálalo con el comando anterior.

---

## 4. Clonar el Proyecto  
**(FUERA del entorno virtual)**
```bash
git clone https://github.com/ZundyTor/app_cloud_ec2.git
cd app_cloud_ec2
```

---

## 5. Crear y Activar Entorno Virtual  
**(FUERA para crear, DENTRO para activar)**

```bash
python3 -m venv venv
```
Para activar el entorno virtual:
```bash
source venv/bin/activate
```
> A partir de este punto, todos los comandos de Python, pip, Flask y Gunicorn deben ejecutarse **dentro del entorno virtual**.

---

## 6. Instalar Dependencias Python  
**(DENTRO del entorno virtual)**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 7. Probar la Aplicación Flask (solo para validar)  
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










