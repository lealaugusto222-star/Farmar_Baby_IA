import banco


def test_hash_pbkdf2_nao_guarda_senha_em_texto_puro():
    senha = "senha-forte-123"
    hash_gerado = banco._gerar_hash(senha)

    assert hash_gerado != senha
    assert banco._conferir_hash(senha, hash_gerado)
    assert not banco._conferir_hash("senha-incorreta", hash_gerado)


def test_validacoes_de_data():
    assert banco._data_para_banco("10/05/1995") == "1995-05-10"
    assert banco._data_para_banco("1995-05-10") == "1995-05-10"
    assert banco._data_para_tela("1995-05-10") == "10/05/1995"
