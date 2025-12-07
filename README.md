# Proyecto DEVS - Creado para el trabajo final del INFORMATORIO 2025
# Team: Leiva Gonzalo y Fernadez Gabriel

Este es un proyecto desarrollado en Django que incluye autenticación de usuarios, perfiles y publicaciónes con comentarios, ademas de la administración(AdminPanel) que cuenta con sistema de reportes y bloqueo de usuarios.

---

## 🚀 Características principales

- Registro e inicio de sesión de usuarios  
- Perfiles personalizables  
- Sistema de mensajería privada  
- Listado de conversaciones entre usuarios  
- Envío y recepción de mensajes  
- Integración opcional con **Django Channels** para chat en tiempo real  
- Panel de administración con gestión de usuarios  
- Código organizado y listo para escalar  

---

## 📦 Requisitos

Asegurate de tener instalado:

- Python 3.10 o superior  
- pip  
- Git  

---

## 🛠 Instalación

Clonar el repositorio:

```bash
git clone https://github.com/LeivaGonzaloM/devs-informatorio.git
cd mi-proyecto-django
```

Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Crear superusuario:

```bash
python manage.py createsuperuser
```

Ejecutar servidor:

```bash
python manage.py runserver
```

---

## ⚙️ Variables de entorno

Crear un archivo `.env` (no se sube al repositorio):

```
SECRET_KEY=tu-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

## 📁 Estructura del proyecto

```
backend/
│
├── core/                  # Core + Aplicaciones Django(Misma altura)
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── templates/            # HTML
├── static/               # Archivos estáticos
├── media/                # Archivos de usuario (Gitignore)
│
├── requirements.txt
├── manage.py
└── README.md
```

---

## 💬 Funciones principales del chat

- Bandeja de entrada con todas las conversaciones  
- Carga ordenada por último mensaje  
- Chat entre usuarios  
- Envío y recepción de texto  
- (Opcional) WebSockets para mensajes en tiempo real  

---

## 🧑‍🤝‍🧑 Flujo de trabajo en equipo

Antes de trabajar:

```bash
git pull
```

Para crear una funcionalidad nueva:

```bash
git checkout -b nombre-de-la-rama
```

Cuando terminás:

```bash
git add .
git commit -m "Descripción de lo realizado"
git push -u origin nombre-de-la-rama
```

Crear un **Pull Request** en GitHub para revisión.

Para volver a `main`:

```bash
git checkout main
git pull
```

---

## 🧪 Comandos útiles

Ejecutar tests:

```bash
python manage.py test
```

Crear migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

Recopilar estáticos (producción):

```bash
python manage.py collectstatic
```

---

## 🛡 Licencia

Este proyecto es de uso educativo. Podés utilizarlo, modificarlo y adaptarlo libremente.

---

## ✨ Contribuciones

Los PRs son bienvenidos.  
Por favor crear una rama por cada feature o fix antes de enviar un Pull Request.

---

## 📫 Contacto

Si tenés dudas o ideas para mejorar el proyecto, podés abrir un **Issue** o realizar un **Pull Request**.
