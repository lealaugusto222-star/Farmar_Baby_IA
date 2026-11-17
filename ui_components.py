from functools import lru_cache
from importlib.metadata import PackageNotFoundError, distribution
import os

import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageFont


_ICON_GLYPHS = {
    "envelope": "\uf0e0",
    "lock": "\uf023",
    "eye": "\uf06e",
    "eye-slash": "\uf070",
    "user": "\uf007",
    "phone": "\uf095",
    "calendar": "\uf073",
    "key": "\uf084",
    "shield": "\uf3ed",
}
_ICON_FONT = (
    "fontawesome-free/static/fontawesome_free/webfonts/fa-solid-900.ttf"
)


def preparar_logo(caminho, altura_desejada):
    """Recorta margens claras do logo e calcula seu tamanho proporcional."""
    imagem = Image.open(caminho).convert("RGBA")
    fundo = Image.new("RGBA", imagem.size, (255, 255, 255, 255))
    fundo.alpha_composite(imagem)
    imagem = fundo.convert("RGB")
    diferenca = ImageChops.difference(
        imagem,
        Image.new("RGB", imagem.size, (255, 255, 255)),
    )
    caixa = diferenca.convert("L").point(
        lambda pixel: 255 if pixel > 15 else 0
    ).getbbox()
    if caixa:
        imagem = imagem.crop(caixa)
    proporcao = imagem.width / imagem.height
    return imagem, int(altura_desejada * proporcao), altura_desejada


class PainelInstitucional(ctk.CTkFrame):
    """Painel de marca compartilhado pelas telas de acesso e cadastro."""

    def __init__(self, master, mensagem):
        super().__init__(master, fg_color="#f8eaf0", corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        conteudo = ctk.CTkFrame(self, fg_color="transparent")
        conteudo.grid(row=1, column=0, sticky="ew", padx=24, pady=24)
        conteudo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            conteudo,
            text="CUIDADO QUE ACOLHE",
            font=("Arial", 10, "bold"),
            text_color="#9e536c",
        ).pack(pady=(0, 14))

        altura_logo = min(
            max(int(master.winfo_screenheight() * 0.16), 135),
            185,
        )
        caminho_logo = os.path.join(
            os.path.dirname(__file__),
            "foto_login.png",
        )
        try:
            imagem, largura, altura = preparar_logo(
                caminho_logo,
                altura_logo,
            )
            self.imagem_logo = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(largura, altura),
            )
            ctk.CTkLabel(
                conteudo,
                image=self.imagem_logo,
                text="",
            ).pack(pady=(0, 12))
        except FileNotFoundError:
            ctk.CTkLabel(
                conteudo,
                text="FARMAR BABY",
                font=("Arial", 22, "bold"),
                text_color="#b84f73",
            ).pack(pady=(12, 24))

        ctk.CTkLabel(
            conteudo,
            text="Cuidando de quem\ngera o futuro.",
            font=("Arial", 21, "bold"),
            text_color="#284b67",
            justify="center",
        ).pack(pady=(4, 8))
        ctk.CTkLabel(
            conteudo,
            text=mensagem,
            font=("Arial", 12),
            text_color="#66758a",
            justify="center",
            wraplength=310,
        ).pack()


@lru_cache(maxsize=1)
def _icon_font_path():
    try:
        font_path = distribution("fontawesome-free").locate_file(_ICON_FONT)
    except PackageNotFoundError as erro:
        raise RuntimeError(
            "Instale as dependências do projeto com "
            "'python -m pip install -r requirements.txt'."
        ) from erro

    if not font_path.is_file():
        raise RuntimeError(f"Arquivo de ícones não encontrado: {font_path}")
    return str(font_path)


@lru_cache(maxsize=32)
def _render_icon(name, color, size):
    if name not in _ICON_GLYPHS:
        raise ValueError(f"Ícone não suportado: {name}")

    scale = 4
    image = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(_icon_font_path(), size * scale)
    draw.text(
        (size * scale / 2, size * scale / 2),
        _ICON_GLYPHS[name],
        font=font,
        fill=color,
        anchor="mm",
    )
    return image


def icon_image(name, color="#667085", size=20):
    """Renderiza um glifo vetorial em alta resolução para o CustomTkinter."""
    return ctk.CTkImage(
        light_image=_render_icon(name, color, size),
        dark_image=_render_icon(name, color, size),
        size=(size, size),
    )


class IconEntry(ctk.CTkFrame):
    """Campo de entrada com ícone e borda de foco integrados."""

    def __init__(
        self,
        master,
        icon,
        placeholder_text,
        width=380,
        height=50,
        **entry_options,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            fg_color="#ffffff",
            border_color="#d0d5dd",
            border_width=1,
            corner_radius=12,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            image=icon_image(icon, "#8492a6", 18),
            width=42,
        )
        self.icon_label.grid(row=0, column=0, sticky="ns")
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            text_color="#263445",
            placeholder_text_color="#98a2b3",
            **entry_options,
        )
        self.entry.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)

    def _focus_in(self, _event):
        self.configure(border_color="#d7658a", border_width=2)

    def _focus_out(self, _event):
        self.configure(border_color="#d0d5dd", border_width=1)

    def get(self):
        return self.entry.get()

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, string):
        self.entry.insert(index, string)

    def bind(self, sequence=None, command=None, add=None):
        if hasattr(self, "entry"):
            return self.entry.bind(
                sequence,
                command,
                "+" if add is None else add,
            )
        return super().bind(sequence, command, add)

    def focus_set(self):
        self.entry.focus_set()


class PasswordField(ctk.CTkFrame):
    """Campo de senha com ícone ocular e revelação temporária ou fixada."""

    def __init__(
        self,
        master,
        placeholder_text="Senha",
        width=380,
        height=50,
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            fg_color="#ffffff",
            border_color="#d0d5dd",
            border_width=1,
            corner_radius=12,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self._hovered = False
        self._pinned = False
        self._visible = False

        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            image=icon_image("lock", "#8492a6", 18),
            width=42,
        )
        self.icon_label.grid(row=0, column=0, sticky="ns")
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
            show="*",
            border_width=0,
            corner_radius=0,
            fg_color="transparent",
            text_color="#263445",
            placeholder_text_color="#98a2b3",
        )
        self.entry.grid(row=0, column=1, sticky="nsew")
        self.eye_button = ctk.CTkButton(
            self,
            text="",
            image=icon_image("eye-slash", "#8492a6", 18),
            width=42,
            height=42,
            fg_color="transparent",
            hover_color="#f8eef2",
            command=self._toggle_pinned,
        )
        self.eye_button.grid(row=0, column=2, padx=(0, 4), pady=3)

        self.entry.bind("<FocusIn>", self._focus_in)
        self.entry.bind("<FocusOut>", self._focus_out)
        self.eye_button.bind("<Enter>", self._pointer_enter)
        self.eye_button.bind("<Leave>", self._pointer_leave)
        self.eye_button.bind("<FocusIn>", self._focus_in)
        self.eye_button.bind("<FocusOut>", self._focus_out)
        self._set_entry_visibility()

    def _set_entry_visibility(self):
        self._visible = self._pinned or self._hovered
        self.entry.configure(show="" if self._visible else "*")
        self.eye_button.configure(
            image=icon_image(
                "eye" if self._visible else "eye-slash",
                "#d7658a" if self._visible else "#8492a6",
                18,
            )
        )

    def _toggle_pinned(self):
        self._pinned = not self._pinned
        self._set_entry_visibility()

    def _pointer_enter(self, _event):
        self._hovered = True
        self._set_entry_visibility()

    def _pointer_leave(self, _event):
        self._hovered = False
        self._set_entry_visibility()

    def _focus_in(self, _event):
        self.configure(border_color="#d7658a", border_width=2)

    def _focus_out(self, _event):
        self.configure(border_color="#d0d5dd", border_width=1)

    def get(self):
        return self.entry.get()

    def bind(self, sequence=None, command=None, add=None):
        if hasattr(self, "entry"):
            return self.entry.bind(
                sequence,
                command,
                "+" if add is None else add,
            )
        return super().bind(sequence, command, add)

    def focus_set(self):
        self.entry.focus_set()
