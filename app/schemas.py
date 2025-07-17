from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from enum import Enum

class PerfilUsuario(str, Enum):
    VISUALIZADOR = "VISUALIZADOR"
    EDITOR       = "EDITOR"
    APROVADOR    = "APROVADOR"

class UsuarioCreate(BaseModel):
    nm_responsavel: str
    email: EmailStr
    senha: str
    tp_perfil: PerfilUsuario

class UsuarioOut(BaseModel):
    id_responsavel: int
    nm_responsavel: str
    email: EmailStr
    tp_perfil: PerfilUsuario

    class Config:
        orm_mode = True

class EmailCreate(BaseModel):
    cd_sei: Optional[str]
    remetente: str
    assunto: Optional[str]
    conteudo: Optional[str]
    tp_status: Optional[str]
    resposta: Optional[str]
    prazo_resposta: Optional[date]
    id_setor: Optional[int]
    id_responsavel: Optional[int]
    tp_email: Optional[str]

class EmailOut(BaseModel):
    id_email: int
    cd_sei: Optional[str]
    remetente: str
    assunto: Optional[str]
    conteudo: Optional[str]
    tp_status: str
    resposta: Optional[str]
    prazo_resposta: Optional[date]
    id_setor: Optional[int]
    id_responsavel: Optional[int]
    tp_email: Optional[str]

    class Config:
        orm_mode = True

class ObrigacaoCreate(BaseModel):
    nm_tarefa: str
    tp_item: str
    tp_status: Optional[str]
    id_setor_atribuido: int
    id_area_condicionamento: Optional[int]
    periodicidade: Optional[str]
    dt_inicio: Optional[date]
    dt_termino: Optional[date]
    duracao: Optional[int]
    dt_limite: Optional[date]
    id_email: Optional[int]

    class Config:
        orm_mode = True
