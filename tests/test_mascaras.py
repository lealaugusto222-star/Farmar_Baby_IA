import pytest

from ui_components import aplicar_mascara_digitos


class CampoSimulado:
    def __init__(self, texto=""):
        self.texto = texto
        self.cursor = len(texto)

    def get(self):
        return self.texto

    def delete(self, inicio, fim):
        self.texto = ""
        self.cursor = 0

    def insert(self, indice, texto):
        self.texto = texto + self.texto[indice:]
        self.cursor = indice + len(texto)

    def index(self, indice):
        assert indice == "insert"
        return self.cursor

    def icursor(self, indice):
        self.cursor = indice


class EventoSimulado:
    def __init__(self, widget, keysym="1"):
        self.widget = widget
        self.keysym = keysym


def _digitar(campo, texto, grupos):
    for caractere in texto:
        campo.texto = (
            campo.texto[:campo.cursor]
            + caractere
            + campo.texto[campo.cursor:]
        )
        campo.cursor += len(caractere)
        aplicar_mascara_digitos(
            EventoSimulado(campo), campo, grupos
        )


def test_mascara_data_formata_dia_mes_ano():
    campo = CampoSimulado()

    _digitar(campo, "17112026", (2, 2, 4))

    assert campo.get() == "17/11/2026"
    assert campo.cursor == len("17/11/2026")


@pytest.mark.parametrize(
    ("digitacao", "resultado"),
    [
        ("12080", "120/80"),
        ("10070", "100/70"),
    ],
)
def test_mascara_pressao_formata_e_backspace_apaga_normalmente(
    digitacao, resultado
):
    campo = CampoSimulado()

    _digitar(campo, digitacao, (3, 2))
    assert campo.get() == resultado

    campo.texto = campo.texto[:-1]
    campo.cursor = len(campo.texto)
    aplicar_mascara_digitos(
        EventoSimulado(campo, "BackSpace"), campo, (3, 2)
    )
    assert campo.get() == resultado[:-1]


def test_mascara_horario_formata_hora_e_minutos():
    campo = CampoSimulado()

    for caractere in "1430":
        campo.texto += caractere
        campo.cursor = len(campo.texto)
        aplicar_mascara_digitos(
            EventoSimulado(campo),
            campo,
            (2, 2),
            separador=":",
        )

    assert campo.get() == "14:30"


def test_mascara_remove_letras_e_limita_quantidade_de_digitos():
    campo = CampoSimulado()

    _digitar(campo, "a1711202699", (2, 2, 4))

    assert campo.get() == "17/11/2026"


def test_mascara_preserva_posicao_do_cursor_ao_digitar_no_meio():
    campo = CampoSimulado("12/34")
    campo.cursor = 1

    campo.texto = campo.texto[:1] + "9" + campo.texto[1:]
    campo.cursor += 1
    aplicar_mascara_digitos(EventoSimulado(campo), campo, (2, 2))

    assert campo.get() == "19/23"
    assert campo.cursor == 2
