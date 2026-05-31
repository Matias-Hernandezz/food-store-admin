from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session


def create_all_tables() -> None:
    import app.modules.dominio_1.Usuarios.models     
    import app.modules.dominio_2.Categoria.models   
    import app.modules.dominio_2.Ingrediente.models   
    import app.modules.dominio_2.Producto.models   
    import app.modules.dominio_3.Pedidos.models
    
    SQLModel.metadata.create_all(engine)
