from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import pandas as pd
from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()
# Configuração do banco de dados
user_pg = os.getenv('POSTGRES_USER')
psw_pg = os.getenv('POSTGRES_PSW')
host_pg = os.getenv('POSTGRES_HOST')
db_pg = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL = f"postgresql://{user_pg}:{psw_pg}@{host_pg}:5432/{db_pg}"

# Criação do motor de banco de dados e da sessão
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Definindo o modelo de dados que corresponde à tabela 'usuarios' no banco de dados
class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, index=True)

# Definindo um modelo Pydantic para a resposta (apenas campos que queremos expor na API)
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str

    class Config:
        from_attributes = True

# Criar a aplicação FastAPI
app = FastAPI()


# Endpoint para pegar todos os usuários
@app.get("/usuarios/", response_model=List[UsuarioResponse])
def read_usuarios():
    # Consultando dados da tabela usuarios usando pandas e SQLAlchemy
    usuarios_df = pd.read_sql('SELECT * FROM labdata.usuarios', engine)
    # Convertendo o DataFrame para uma lista de dicionários
    usuarios_list = usuarios_df.to_dict(orient='records')
    # Convertendo cada dicionário para o modelo Pydantic e retornando a resposta
    return [UsuarioResponse(**usuario) for usuario in usuarios_list]

# Endpoint para pegar um usuário específico pelo ID
@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
def read_usuario(usuario_id: int):
    usuario_df = pd.read_sql(f'SELECT * FROM labdata.usuarios WHERE id = {usuario_id}', engine)
    if usuario_df is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario_list = usuario_df.to_dict(orient='records')
    return UsuarioResponse(**usuario_list[0])