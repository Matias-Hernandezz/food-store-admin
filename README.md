# 🍔 FOODSTORE - FastAPI + React

[📹 Video de presentación](https://drive.google.com/file/d/1DOZpkd6W3HFCy_E5-I_rS0YFutu8IU3i/view?usp=drive_link)

Una aplicación full-stack moderna para gestionar un catálogo de productos alimenticios con categorías e ingredientes. Construida con **FastAPI** en el backend y **React + TypeScript** en el frontend.

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Ejecución](#ejecución)
- [API Endpoints](#api-endpoints)
- [Desarrollo](#desarrollo)

---

## ✨ Características

- ✅ Gestión completa de **Categorías**
- ✅ Gestión completa de **Ingredientes**
- ✅ Gestión completa de **Productos**
- ✅ Carga de imágenes para productos
- ✅ API RESTful bien documentada
- ✅ Interface de administración intuitiva
- ✅ Base de datos PostgreSQL
- ✅ TypeScript en frontend y backend
- ✅ Validación con Pydantic (backend) y TypeScript (frontend)

---

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Python 3.x** - Lenguaje de programación
- **SQLModel** - ORM basado en SQLAlchemy con soporte Pydantic
- **PostgreSQL** - Base de datos relacional
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validación de datos

### Frontend
- **React 19** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool moderno
- **Tailwind CSS** - Framework CSS
- **TanStack Query** - State management de datos
- **Axios** - Cliente HTTP
- **React Router** - Enrutamiento
- **ESLint** - Linter

---

## 📦 Requisitos Previos

- **Python 3.9+** (para backend)
- **Node.js 18+** (para frontend)
- **pnpm** o **npm** (gestor de paquetes)
- **PostgreSQL 12+** (base de datos)
- **Git** (control de versiones)

---

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/usuario/FOODSTORE-FASTAPI+REACT.git
cd FOODSTORE-FASTAPI+REACT
```

### 2️⃣ Configurar Backend

#### Crear entorno virtual

```bash
cd BACKEND
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

#### Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Configurar variables de entorno

Crear archivo `.env` en `BACKEND/`:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/foodstore
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Crear base de datos

```bash
# Conectarse a PostgreSQL y ejecutar:
createdb foodstore
```

### 3️⃣ Configurar Frontend

#### Instalar dependencias

```bash
cd FRONTEND
pnpm install
# o
npm install
```

#### Configurar variables de entorno

Crear archivo `.env` en `FRONTEND/`:

```env
VITE_API_URL=http://localhost:8000/api
```

---

## 📁 Estructura del Proyecto

```
FOODSTORE-FASTAPI+REACT/
├── BACKEND/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Aplicación principal FastAPI
│   │   ├── core/
│   │   │   ├── config.py          # Configuración
│   │   │   ├── db.py              # Conexión a BD
│   │   │   ├── repository.py      # Base repository
│   │   │   ├── unit_of_work.py    # Patrón UoW
│   │   ├── modules/
│   │   │   ├── Categoria/
│   │   │   │   ├── models.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── routers.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   ├── Ingrediente/
│   │   │   ├── Producto/
│   │   │   │   ├── models_shared.py
│   │   │   └── ...
│   │   ├── routers/
│   │   │   └── uploads.py         # Manejo de cargas
│   ├── tests/
│   │   └── test.http              # Pruebas HTTP
│   ├── uploads/                   # Archivos cargados
│   ├── requirements.txt           # Dependencias Python
│   ├── docker-compose.yml         # Configuración Docker
│   └── README                     # Instrucciones backend
├── FRONTEND/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/                   # Clientes API
│   │   ├── components/            # Componentes React
│   │   ├── hooks/                 # Custom hooks
│   │   ├── pages/                 # Páginas
│   │   ├── types/                 # Tipos TypeScript
│   ├── public/                    # Archivos estáticos
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── images/                        # Imágenes del proyecto
└── README.md                      # Este archivo
```

---

## ⚙️ Ejecución

### Opción 1: Docker Compose (Recomendado)

```bash
cd BACKEND
docker-compose up -d
```

Esto inicia:
- PostgreSQL en puerto `5432`
- Backend FastAPI en puerto `8000`

### Opción 2: Ejecución Manual

#### Terminal 1 - Backend

```bash
cd BACKEND
.venv\Scripts\activate        # Windows
# source .venv/bin/activate  # macOS/Linux

python -m fastapi dev app/main.py
```

Backend disponible en: `http://localhost:8000`

Documentación interactiva:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Terminal 2 - Frontend

```bash
cd FRONTEND
pnpm dev
# o
npm run dev
```

Frontend disponible en: `http://localhost:5173`

---

## 🔌 API Endpoints

### Categorías

```
GET    /api/categorias              # Listar todas
POST   /api/categorias              # Crear nueva
GET    /api/categorias/{id}         # Obtener por ID
PUT    /api/categorias/{id}         # Actualizar
DELETE /api/categorias/{id}         # Eliminar
```

### Ingredientes

```
GET    /api/ingredientes            # Listar todas
POST   /api/ingredientes            # Crear nuevo
GET    /api/ingredientes/{id}       # Obtener por ID
PUT    /api/ingredientes/{id}       # Actualizar
DELETE /api/ingredientes/{id}       # Eliminar
```

### Productos

```
GET    /api/productos               # Listar todos
POST   /api/productos               # Crear nuevo
GET    /api/productos/{id}          # Obtener por ID
PUT    /api/productos/{id}          # Actualizar
DELETE /api/productos/{id}          # Eliminar
```

### Uploads

```
POST   /api/uploads                 # Cargar archivo
GET    /api/uploads/{filename}      # Descargar archivo
```

---

## 📝 Desarrollo

### Backend

#### Ejecutar tests

```bash
cd BACKEND
pytest tests/
```

#### Format code

```bash
black app/
isort app/
```

### Frontend

#### Lint

```bash
cd FRONTEND
pnpm lint
```

#### Build para producción

```bash
pnpm build
```

#### Preview de producción

```bash
pnpm preview
```

---

## 🔧 Troubleshooting

### Puerto 8000 ya en uso

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Error de conexión a PostgreSQL

Verificar:
1. PostgreSQL está ejecutándose
2. Credenciales en `.env`
3. Base de datos existe

### Error CORS en Frontend

Verificar en `BACKEND/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📄 Licencia

MIT License - Ver LICENSE para más detalles

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/MiFeature`)
3. Commit cambios (`git commit -am 'Add MiFeature'`)
4. Push a la rama (`git push origin feature/MiFeature`)
5. Abre un Pull Request

---

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Hecho con ❤️ usando FastAPI y React**
