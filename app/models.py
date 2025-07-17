from app import db
from sqlalchemy import Table, Column, Integer, String, Text, Date, ForeignKey, Enum as PgEnum
from enum import Enum

class PerfilUsuario(Enum):
    VISUALIZADOR = "VISUALIZADOR"
    EDITOR       = "EDITOR"
    APROVADOR    = "APROVADOR"

class StatusEmail(Enum):
    RECEBIDO     = "RECEBIDO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    RESPONDIDO   = "RESPONDIDO"
    ATRASADO     = "ATRASADO"

class TipoObrigacao(Enum):
    PERIODICA    = "PERIODICA"
    UNICA        = "UNICA"
    EMERGENCIAL  = "EMERGENCIAL"
    CONDICIONADA = "CONDICIONADA"

class StatusObrigacao(Enum):
    EM_ANDAMENTO = "EM_ANDAMENTO"
    PENDENTE     = "PENDENTE"
    CONCLUIDO    = "CONCLUIDO"
    ATRASADA     = "ATRASADA"

# Tabela responsavel
class Responsavel(db.Model):
    __tablename__   = "responsavel"
    id_responsavel  = Column(Integer, primary_key=True)
    nm_responsavel  = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, nullable=False)
    senha           = Column(String(255), nullable=False)
    tp_perfil       = Column(
        PgEnum(PerfilUsuario, name="perfilusuario"),
        nullable=False
    )

# Tabela setor
class Setor(db.Model):
    __tablename__   = "setor"
    id_setor        = Column(Integer, primary_key=True)
    nm_setor        = Column(String(255), nullable=False)
    id_responsavel  = Column(
        Integer,
        ForeignKey("responsavel.id_responsavel"),
        nullable=False
    )

# Tabela email
class Email(db.Model):
    __tablename__   = "email"
    id_email        = Column(Integer, primary_key=True)
    cd_sei          = Column(String(100))
    titulo          = Column(String(255))
    assunto         = Column(String(255))
    tp_status       = Column(
        PgEnum(StatusEmail, name="statusemail"),
        default=StatusEmail.RECEBIDO
    )
    resposta        = Column(Text)
    prazo_resposta  = Column(Date)
    id_setor        = Column(
        Integer,
        ForeignKey("setor.id_setor")
    )
    id_responsavel  = Column(
        Integer,
        ForeignKey("responsavel.id_responsavel")
    )
    tp_email        = Column(String(50))

# Tabela obrigacao
class Obrigacao(db.Model):
    __tablename__             = "obrigacao"
    id_obrigacao              = Column(Integer, primary_key=True)
    nm_tarefa                 = Column(String(255), nullable=False)
    tp_item                   = Column(
        PgEnum(TipoObrigacao, name="tipoobrigacao"),
        nullable=False
    )
    tp_status                 = Column(
        PgEnum(StatusObrigacao, name="statusobrigacao"),
        default=StatusObrigacao.PENDENTE
    )
    id_setor_atribuido        = Column(
        Integer,
        ForeignKey("setor.id_setor"),
        nullable=False
    )
    id_area_condicionamento   = Column(
        Integer,
        ForeignKey("setor.id_setor")
    )
    periodicidade             = Column(String(100))
    dt_inicio                 = Column(Date)
    dt_termino                = Column(Date)
    duracao                   = Column(Integer)
    dt_limite                 = Column(Date)
    id_email                  = Column(
        Integer,
        ForeignKey("email.id_email")
    )

rl_obrigacoes_correspondencia = Table(
    'rl_obrigacoes_correspondencia',
    db.metadata,
    Column('id_email',     Integer, ForeignKey('email.id_email'),      primary_key=True),
    Column('id_obrigacao', Integer, ForeignKey('obrigacao.id_obrigacao'), primary_key=True)
)

Obrigacao.correspondencias = db.relationship(
    "Email",
    secondary=rl_obrigacoes_correspondencia,
    backref="obrigacoes"
)