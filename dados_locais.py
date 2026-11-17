"""Persistência local para dados clínicos e administrativos dos painéis."""

import json
import math
import os
import re
import tempfile
import uuid
from datetime import date, datetime


CAMINHO_DADOS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dados_clinicos.json",
)


def _registro_valido(registro):
    try:
        semana = registro["semana"]
        peso = registro["peso"]
        pressao = registro["pressao"]
        consulta = registro["proxima_consulta"]
        registrado_em = registro["registrado_em"]
        if (
            not isinstance(pressao, str)
            or re.fullmatch(r"\d{2,3}/\d{2,3}", pressao) is None
        ):
            return False
        sistolica, diastolica = (
            int(valor) for valor in pressao.split("/")
        )
        return (
            isinstance(semana, int)
            and not isinstance(semana, bool)
            and 1 <= semana <= 42
            and isinstance(peso, (int, float))
            and not isinstance(peso, bool)
            and math.isfinite(peso)
            and 20 <= peso <= 300
            and 20 <= sistolica <= 300
            and 20 <= diastolica <= 200
            and isinstance(consulta, str)
            and date.fromisoformat(consulta) is not None
            and isinstance(registrado_em, str)
            and datetime.fromisoformat(registrado_em) is not None
        )
    except (KeyError, TypeError, ValueError):
        return False


def _ler_dados():
    if not os.path.exists(CAMINHO_DADOS):
        return {
            "registros": {},
            "observacoes": {},
            "consultas": [],
            "alertas_resolvidos": [],
        }

    with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, dict):
        raise ValueError("O arquivo local de dados clínicos possui formato inválido.")

    dados.setdefault("registros", {})
    dados.setdefault("observacoes", {})
    dados.setdefault("consultas", [])
    dados.setdefault("alertas_resolvidos", [])

    if not (
        isinstance(dados["registros"], dict)
        and all(
            isinstance(email, str)
            and isinstance(registros, list)
            and all(
                isinstance(registro, dict) and _registro_valido(registro)
                for registro in registros
            )
            for email, registros in dados["registros"].items()
        )
        and isinstance(dados["observacoes"], dict)
        and all(
            isinstance(email, str) and isinstance(texto, str)
            for email, texto in dados["observacoes"].items()
        )
        and isinstance(dados["consultas"], list)
        and all(isinstance(consulta, dict) for consulta in dados["consultas"])
        and isinstance(dados["alertas_resolvidos"], list)
        and all(
            isinstance(alerta_id, str)
            for alerta_id in dados["alertas_resolvidos"]
        )
    ):
        raise ValueError("O arquivo local de dados clínicos possui formato inválido.")

    return dados


def _gravar_dados(dados):
    pasta = os.path.dirname(CAMINHO_DADOS)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=pasta,
            prefix=".dados_clinicos-",
            suffix=".tmp",
            delete=False,
        ) as arquivo:
            temporario = arquivo.name
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        os.replace(temporario, CAMINHO_DADOS)
    finally:
        if temporario and os.path.exists(temporario):
            os.remove(temporario)


def listar_registros(email):
    """Retorna as medições de uma gestante em ordem cronológica."""
    email = email.strip().lower()
    dados = _ler_dados()
    registros = dados["registros"].get(email, [])
    if not isinstance(registros, list):
        raise ValueError("Os registros clínicos da conta possuem formato inválido.")
    if not all(_registro_valido(registro) for registro in registros):
        raise ValueError("Um registro clínico local possui dados inválidos.")
    return sorted(registros, key=lambda registro: registro.get("registrado_em", ""))


def salvar_registro(email, registro):
    """Adiciona uma medição à conta sem modificar o banco de usuários."""
    email = email.strip().lower()
    dados = _ler_dados()
    registros = dados["registros"].setdefault(email, [])
    if not isinstance(registros, list):
        raise ValueError("Os registros clínicos da conta possuem formato inválido.")
    registro = dict(registro)
    if not _registro_valido(registro):
        raise ValueError("Os dados da medição possuem formato ou valores inválidos.")
    registro["id"] = uuid.uuid4().hex
    registros.append(registro)
    _gravar_dados(dados)
    return registro


def obter_observacoes(email):
    return _ler_dados()["observacoes"].get(email.strip().lower(), "")


def salvar_observacoes(email, texto):
    dados = _ler_dados()
    dados["observacoes"][email.strip().lower()] = texto.strip()
    _gravar_dados(dados)


def listar_consultas():
    consultas = _ler_dados()["consultas"]
    if not all(isinstance(consulta, dict) for consulta in consultas):
        raise ValueError("A agenda local possui formato inválido.")
    return consultas


def agendar_consulta(profissional_email, paciente_email, data, horario, observacao):
    dados = _ler_dados()
    consulta = {
        "id": uuid.uuid4().hex,
        "profissional_email": profissional_email.strip().lower(),
        "paciente_email": paciente_email.strip().lower(),
        "data": data,
        "horario": horario,
        "observacao": observacao.strip(),
        "concluida": False,
    }
    dados["consultas"].append(consulta)
    _gravar_dados(dados)
    return consulta


def concluir_consulta(consulta_id):
    dados = _ler_dados()
    for consulta in dados["consultas"]:
        if consulta.get("id") == consulta_id:
            consulta["concluida"] = True
            _gravar_dados(dados)
            return
    raise ValueError("A consulta selecionada não foi encontrada na agenda local.")


def listar_alertas_resolvidos():
    resolvidos = _ler_dados()["alertas_resolvidos"]
    if not all(isinstance(alerta_id, str) for alerta_id in resolvidos):
        raise ValueError("A lista de alertas resolvidos possui formato inválido.")
    return resolvidos


def resolver_alerta(alerta_id):
    dados = _ler_dados()
    resolvidos = dados["alertas_resolvidos"]
    if alerta_id not in resolvidos:
        resolvidos.append(alerta_id)
        _gravar_dados(dados)
