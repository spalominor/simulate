from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

simulacion_escenario = Table(
    'Simulacion_Escenario',
    Base.metadata,
    Column('simulacion_id', Integer, ForeignKey('Simulaciones.id', ondelete='CASCADE'), primary_key=True),
    Column('escenario_id', Integer, ForeignKey('Escenarios.id', ondelete='CASCADE'), primary_key=True)
)

class Usuario(Base):
    __tablename__ = 'Usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    
    # Relación: un usuario puede crear muchas simulaciones
    simulaciones = relationship("Simulacion", back_populates="creado_por_usuario")
    
    def __repr__(self):
        return f"{self.nombre}"

class Escenario(Base):
    __tablename__ = 'Escenarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    capital = Column(Float, nullable=False)
    tasa = Column(Float, nullable=False)
    plazo = Column(Integer, nullable=False)
    cuota = Column(Float, nullable=False)
    creado_por = Column(Integer, ForeignKey('Usuarios.id', ondelete='SET NULL'), nullable=True)
    
    # Relaciones
    abonos = relationship("Abono", back_populates="escenario", cascade="all, delete-orphan")
    usuario_creador = relationship("Usuario", foreign_keys=[creado_por])

    # Relación con Simulación (N escenarios pertenecen a 1 simulación)
    simulaciones = relationship(
        "Simulacion", 
        secondary=simulacion_escenario, 
        back_populates="escenarios"
    )

    
    def __repr__(self):
        return f"{self.nombre}"

class Abono(Base):
    __tablename__ = 'Abonos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    escenario_id = Column(Integer, ForeignKey('Escenarios.id', ondelete='CASCADE'), nullable=False)
    mes = Column(Integer, nullable=False)
    monto = Column(Float, nullable=False)
    
    # Relación inversa
    escenario = relationship("Escenario", back_populates="abonos")

class Simulacion(Base):
    __tablename__ = 'Simulaciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    fecha = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    creado_por = Column(Integer, ForeignKey('Usuarios.id', ondelete='SET NULL'), nullable=True)
    
    # Relaciones inversas
    # N Simulaciones tiene N Escenarios
    escenarios = relationship(
        "Escenario", 
        secondary=simulacion_escenario, 
        back_populates="simulaciones"
    )
    creado_por_usuario = relationship("Usuario", back_populates="simulaciones", foreign_keys=[creado_por])
    
    def __repr__(self):
        return f"{self.id} - {self.nombre}"
    