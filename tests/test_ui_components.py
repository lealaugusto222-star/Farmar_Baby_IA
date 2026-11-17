import pytest

from ui_components import PasswordField, icon_image


@pytest.mark.parametrize(
    "name",
    [
        "envelope",
        "lock",
        "eye",
        "eye-slash",
        "user",
        "phone",
        "calendar",
        "key",
        "shield",
    ],
)
def test_icon_image_renders_supported_icons(name):
    image = icon_image(name, size=20)

    assert image._size == (20, 20)
    assert image._light_image.size == (80, 80)
    assert image._light_image.getbbox() is not None


def test_icon_image_rejects_unknown_icon():
    with pytest.raises(ValueError, match="Ícone não suportado"):
        icon_image("unknown")


class ElementoFalso:
    def __init__(self):
        self.configuracao = {}

    def configure(self, **kwargs):
        self.configuracao.update(kwargs)


def _campo_senha_sem_tela():
    campo = PasswordField.__new__(PasswordField)
    campo._hovered = False
    campo._pinned = False
    campo._visible = False
    campo.entry = ElementoFalso()
    campo.eye_button = ElementoFalso()
    return campo


def test_icone_temporario_revela_senha_apenas_enquanto_hover():
    campo = _campo_senha_sem_tela()

    campo._pointer_enter(None)
    assert campo.entry.configuracao["show"] == ""

    campo._pointer_leave(None)
    assert campo.entry.configuracao["show"] == "*"


def test_clique_mantem_visibilidade_ate_novo_clique():
    campo = _campo_senha_sem_tela()

    campo._toggle_pinned()
    assert campo.entry.configuracao["show"] == ""

    campo._pointer_enter(None)
    campo._pointer_leave(None)
    assert campo.entry.configuracao["show"] == ""

    campo._toggle_pinned()
    assert campo.entry.configuracao["show"] == "*"
