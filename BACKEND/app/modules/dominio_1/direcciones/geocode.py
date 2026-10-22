from sqlmodel import Session

from app.core.geocoding import geocode_address
from app.modules.dominio_1.direcciones.models import DireccionEntrega


def ensure_direccion_coords(session: Session, direccion: DireccionEntrega) -> bool:
    """Completa lat/lng si faltan. Devuelve True si hay coordenadas al final."""
    if direccion.latitud is not None and direccion.longitud is not None:
        return True

    coords = geocode_address(
        linea1=direccion.linea1,
        linea2=direccion.linea2,
        ciudad=direccion.ciudad,
        provincia=direccion.provincia,
    )
    if not coords:
        return False

    direccion.latitud, direccion.longitud = coords
    session.add(direccion)
    session.commit()
    session.refresh(direccion)
    return True
