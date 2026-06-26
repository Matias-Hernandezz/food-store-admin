from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session


def create_all_tables() -> None:
    import app.modules.dominio_1.auth.models
    import app.modules.dominio_1.usuarios.models
    import app.modules.dominio_1.direcciones.models
    import app.modules.dominio_2.categorias.models   
    import app.modules.dominio_2.ingredientes.models   
    import app.modules.dominio_2.productos.models
    import app.modules.dominio_2.unidad_medida.models
    import app.modules.dominio_3.pedidos.models
    import app.modules.dominio_3.pagos.models

    SQLModel.metadata.create_all(engine)
