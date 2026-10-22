# Snapshot pre-rediseño estético

**Fecha:** 2026-10-22  
**Carpeta:** `e:\mati\programacion\PROYECTOS\FOOD-STORE-SNAPSHOT-PRE-ESTETICA-2026-10-22`

Copia del workspace **antes** de cambiar la estética de la tienda/admin hacia el moodboard Bad Burgers (u otro tema).

## Qué incluye

- Los tres repos bajo `FOOD-STORE` (backend, admin-panel, client)
- `docs/` (auditoría, plan, referencias, etc.)
- Historial `.git` de cada repo (si existía en el momento de la copia)

## Qué se excluyó (para ahorrar espacio)

- `node_modules`, `.venv`, `__pycache__`, `dist`, cachés de test

## Restaurar dependencias

En cada repo del snapshot:

```powershell
# Backend
cd Food-store-admin\BACKEND
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# Admin / Cliente
cd food-store-admin-panel   # o Food-Store-client\store
npm install
```

## Nota

Este snapshot **no** reemplaza tags en GitHub. Para un respaldo versionado, hacé tag o branch en cada remoto cuando commitees el estado actual.
