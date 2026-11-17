import json

import pytest

import dados_locais


def _usar_arquivo_temporario(monkeypatch, tmp_path):
    caminho = tmp_path / "dados_clinicos.json"
    monkeypatch.setattr(dados_locais, "CAMINHO_DADOS", str(caminho))
    return caminho


def test_salva_e_lista_registros_clinicos(monkeypatch, tmp_path):
    caminho = _usar_arquivo_temporario(monkeypatch, tmp_path)

    primeiro = dados_locais.salvar_registro(
        "ANA@example.com",
        {
            "semana": 24,
            "peso": 68.2,
            "pressao": "120/80",
            "proxima_consulta": "2026-11-22",
            "registrado_em": "2026-11-17T10:00:00",
        },
    )
    segundo = dados_locais.salvar_registro(
        "ana@example.com",
        {
            "semana": 25,
            "peso": 68.5,
            "pressao": "118/78",
            "proxima_consulta": "2026-11-29",
            "registrado_em": "2026-11-18T10:00:00",
        },
    )

    assert caminho.exists()
    assert [item["id"] for item in dados_locais.listar_registros(
        "ana@example.com"
    )] == [primeiro["id"], segundo["id"]]
    assert dados_locais.listar_registros("ANA@example.com")[-1]["peso"] == 68.5


def test_persiste_consulta_observacoes_e_alerta_resolvido(monkeypatch, tmp_path):
    _usar_arquivo_temporario(monkeypatch, tmp_path)

    consulta = dados_locais.agendar_consulta(
        "dra@example.com",
        "ana@example.com",
        "2026-11-22",
        "14:30",
        "Retorno",
    )
    dados_locais.salvar_observacoes("ana@example.com", "Acompanhar retorno.")
    dados_locais.concluir_consulta(consulta["id"])
    dados_locais.resolver_alerta("ana:registro-1")

    assert dados_locais.listar_consultas()[0]["concluida"] is True
    assert dados_locais.obter_observacoes("ANA@example.com") == (
        "Acompanhar retorno."
    )
    assert dados_locais.listar_alertas_resolvidos() == ["ana:registro-1"]


def test_rejeita_json_local_corrompido(monkeypatch, tmp_path):
    caminho = _usar_arquivo_temporario(monkeypatch, tmp_path)
    caminho.write_text("{ inválido", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        dados_locais.listar_consultas()


def test_conclusao_de_consulta_inexistente_e_reportada(monkeypatch, tmp_path):
    _usar_arquivo_temporario(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="não foi encontrada"):
        dados_locais.concluir_consulta("inexistente")
