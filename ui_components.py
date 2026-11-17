from functools import lru_cache
from importlib.metadata import PackageNotFoundError, distribution

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont


_ICON_GLYPHS = {
    "envelope": "\uf0e0",
    "lock": "\uf023",
    "eye": "\uf06e",
    "eye-slash": "\uf070",
}
_ICON_FONT = (
    "fontawesome-free/static/fontawesome_free/webfonts/fa-solid-900.ttf"
)


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
def icon_image(name, color="#667085", size=20):
    """Renderiza um glifo Font Awesome em alta resolução para o CustomTkinter."""
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
    return ctk.CTkImage(
        light_image=image,
        dark_image=image,
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
