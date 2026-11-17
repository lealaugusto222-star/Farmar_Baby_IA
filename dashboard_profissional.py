import customtkinter as ctk
from tkinter import messagebox

import banco
from ui_components import IconEntry, Sidebar


class TelaDashboardProfissional:
    COR_MENU = "#f8eaf0"
    COR_MENU_HOVER = "#fbe7ef"
    COR_ATIVO = "#d7658a"
    COR_TEXTO_MENU = "#624b57"
    COR_FUNDO = "#f7fafc"
    COR_CARD = "white"
    COR_BORDA = "#e2e8f0"
    COR_TITULO = "#284b67"
    COR_TEXTO = "#4a5568"
    COR_ALERTA = "#c53030"
    COR_ALERTA_FUNDO = "#fff5f5"
    COR_OK = "#2f855a"
    COR_OK_FUNDO = "#f0fff4"
    COR_SEM_DADOS = "#718096"
    COR_SEM_DADOS_FUNDO = "#edf2f7"
    COR_DEMO = "#975a16"
    COR_DEMO_FUNDO = "#fffaf0"

    # Limites usados apenas para sinalizar dados registrados no sistema.
    # Eles não substituem avaliação clínica nem orientação profissional.
    LIMITE_PA_SISTOLICA = 140
    LIMITE_PA_DIASTOLICA = 90
    LIMITE_BPM = 100
    LIMITE_SPO2 = 95
    LIMITE_FEBRE = 37.8

    # Pacientes fictícias usadas somente quando ainda não há gestantes cadastradas.
    # pa_sis/pa_dia = pressão arterial, bpm = batimentos, spo2 = oxigênio (%), temp = temperatura (°C).
    PACIENTES_DEMO = [
        {"nome": "Ana Souza", "semanas": 24, "consulta": "22/10 14:00", "bpm": 78, "pa_sis": 110, "pa_dia": 70, "spo2": 98, "temp": 36.6},
        {"nome": "Beatriz Lima", "semanas": 32, "consulta": "Hoje 09:30", "bpm": 84, "pa_sis": 145, "pa_dia": 95, "spo2": 97, "temp": 36.8},
        {"nome": "Carla Mendes", "semanas": 12, "consulta": "24/10 11:00", "bpm": 72, "pa_sis": 105, "pa_dia": 65, "spo2": 99, "temp": 36.5},
        {"nome": "Daniela Rocha", "semanas": 36, "consulta": "Hoje 14:00", "bpm": 118, "pa_sis": 120, "pa_dia": 80, "spo2": 96, "temp": 36.9},
        {"nome": "Elisa Ferreira", "semanas": 28, "consulta": "Hoje 16:30", "bpm": 80, "pa_sis": 115, "pa_dia": 75, "spo2": 98, "temp": 36.7},
        {"nome": "Fernanda Alves", "semanas": 20, "consulta": "27/10 08:00", "bpm": 76, "pa_sis": 108, "pa_dia": 68, "spo2": 98, "temp": 36.6},
    ]

    def __init__(self, master, usuario=None):
        self.master = master
        self.usuario = usuario

        # Usa os cadastros reais sempre que houver gestantes no banco.
        # Se ainda não houver nenhuma, mantém a demonstração que já existia.
        try:
            usuarios_cadastrados = banco.listar_usuarios("gestante")
        except banco.ErroBanco as erro:
            messagebox.showerror("Falha ao carregar pacientes", str(erro))
            usuarios_cadastrados = None
        self.modo_demo = usuarios_cadastrados is not None and not usuarios_cadastrados

        if usuarios_cadastrados is None:
            self.PACIENTES = []
        elif self.modo_demo:
            self.PACIENTES = [
                paciente.copy()
                for paciente in self.PACIENTES_DEMO
            ]
        else:
            self.PACIENTES = [
                self._normalizar_paciente(usuario)
                for usuario in usuarios_cadastrados
            ]

        self.preparar_pacientes()

        # Container principal
        self.container_geral = ctk.CTkFrame(
            self.master,
            fg_color=self.COR_FUNDO,
            corner_radius=0,
        )
        self.container_geral.pack(fill="both", expand=True)

        nome_usuario = (
            self.usuario.get("nome", "Profissional")
            if isinstance(self.usuario, dict)
            else "Profissional"
        )
        itens_menu = (
            (
                "pacientes",
                "Pacientes",
                "users",
                lambda: self.mudar_aba("pacientes"),
            ),
            (
                "alertas",
                "Alertas",
                "exclamation-triangle",
                lambda: self.mudar_aba("alertas"),
            ),
            (
                "agenda",
                "Agenda do Dia",
                "calendar-check",
                lambda: self.mudar_aba("agenda"),
            ),
        )
        self.sidebar = Sidebar(
            self.container_geral,
            nome_usuario=nome_usuario,
            perfil="Profissional",
            itens=itens_menu,
            comando_sair=self.master.abrir_login,
            accent_color=self.COR_ATIVO,
            hover_color=self.COR_MENU_HOVER,
        )
        self.sidebar.pack(side="left", fill="y")
        self.menu_lateral = self.sidebar
        self.btn_pacientes = self.sidebar.buttons["pacientes"]
        self.btn_alertas = self.sidebar.buttons["alertas"]
        self.btn_agenda = self.sidebar.buttons["agenda"]
        self.btn_sair = self.sidebar.btn_sair

        # 2. PAINEL DE CONTEÚDO
        self.painel_conteudo = ctk.CTkFrame(
            self.container_geral,
            fg_color=self.COR_FUNDO,
            corner_radius=0,
        )
        self.painel_conteudo.pack(
            side="right",
            fill="both",
            expand=True,
        )

        self.mudar_aba("pacientes")

    @staticmethod
    def _normalizar_paciente(usuario):
        """Converte o cadastro do banco para o formato usado pelo painel."""
        return {
            "id": usuario.get("id"),
            "nome": usuario.get("nome", "Paciente sem nome"),

            # Estes campos ainda não são solicitados no cadastro atual.
            # Não inventamos semanas, consultas nem medições para pacientes reais.
            "semanas": None,
            "consulta": "Não agendada",
            "bpm": None,
            "pa_sis": None,
            "pa_dia": None,
            "spo2": None,
            "temp": None,
        }

    def avaliar_paciente(self, paciente):
        """Avalia os dados disponíveis e devolve motivos de alerta."""
        campos_vitais = (
            "pa_sis",
            "pa_dia",
            "bpm",
            "spo2",
            "temp",
        )

        # Sem um conjunto completo de medições, não declarar
        # paciente normal ou em alerta.
        if any(
            paciente.get(campo) is None
            for campo in campos_vitais
        ):
            return []

        motivos = []

        if (
            paciente["pa_sis"] >= self.LIMITE_PA_SISTOLICA
            or paciente["pa_dia"] >= self.LIMITE_PA_DIASTOLICA
        ):
            motivos.append(
                f'Pressão arterial elevada: '
                f'{paciente["pa_sis"]}/{paciente["pa_dia"]} mmHg'
            )

        if paciente["bpm"] > self.LIMITE_BPM:
            motivos.append(
                f'Frequência cardíaca alta: {paciente["bpm"]} bpm'
            )

        if paciente["spo2"] < self.LIMITE_SPO2:
            motivos.append(
                f'Oxigenação baixa: {paciente["spo2"]}%'
            )

        if paciente["temp"] >= self.LIMITE_FEBRE:
            temperatura = str(
                paciente["temp"]
            ).replace(".", ",")

            motivos.append(
                f"Temperatura elevada: {temperatura} °C"
            )

        return motivos

    def preparar_pacientes(self):
        """Define status sem tratar ausência de medições como normalidade."""
        campos_vitais = (
            "pa_sis",
            "pa_dia",
            "bpm",
            "spo2",
            "temp",
        )

        for paciente in self.PACIENTES:
            tem_medicoes = all(
                paciente.get(campo) is not None
                for campo in campos_vitais
            )

            if not tem_medicoes:
                paciente["status"] = "Sem dados"
                paciente["motivo"] = (
                    "Ainda não há sinais vitais registrados."
                )
                continue

            motivos = self.avaliar_paciente(paciente)
            paciente["status"] = (
                "Alerta" if motivos else "Normal"
            )
            paciente["motivo"] = "; ".join(motivos)

    @staticmethod
    def texto_semanas(paciente):
        semanas = paciente.get("semanas")

        if semanas is None:
            return "Semanas não informadas"

        return f"{semanas} semanas"

    @staticmethod
    def texto_consulta(paciente):
        return paciente.get("consulta") or "Não agendada"

    # --- NAVEGAÇÃO ---
    def criar_botao_menu(self, texto, nome_aba):
        """Mantém compatibilidade com chamadas antigas de criação de navegação."""
        return self.sidebar.buttons[nome_aba]

    def limpar_painel(self):
        for componente in self.painel_conteudo.winfo_children():
            componente.destroy()

    def mudar_aba(self, nome_aba):
        self.limpar_painel()

        self.sidebar.set_active(nome_aba)

        if nome_aba == "pacientes":
            self.carregar_pacientes()
        elif nome_aba == "alertas":
            self.carregar_alertas()
        elif nome_aba == "agenda":
            self.carregar_agenda()

    # --- COMPONENTES REUTILIZÁVEIS ---
    def titulo_aba(self, titulo, subtitulo):
        ctk.CTkLabel(
            self.painel_conteudo,
            text=titulo,
            font=("Arial", 22, "bold"),
            text_color=self.COR_TITULO,
            anchor="w",
        ).pack(
            fill="x",
            padx=25,
            pady=(25, 0),
        )

        ctk.CTkLabel(
            self.painel_conteudo,
            text=subtitulo,
            font=("Arial", 12),
            text_color=self.COR_TEXTO,
            anchor="w",
        ).pack(
            fill="x",
            padx=25,
            pady=(0, 15),
        )

    def mostrar_aviso_demo(self):
        """Identifica visualmente os dados fictícios quando o painel está em demonstração."""
        if not self.modo_demo:
            return

        ctk.CTkLabel(
            self.painel_conteudo,
            text=(
                "MODO DEMONSTRAÇÃO: pacientes, consultas "
                "e sinais vitais abaixo são fictícios."
            ),
            fg_color=self.COR_DEMO_FUNDO,
            text_color=self.COR_DEMO,
            corner_radius=8,
            font=("Arial", 11, "bold"),
            wraplength=850,
            padx=12,
            pady=9,
        ).pack(
            fill="x",
            padx=25,
            pady=(0, 12),
        )

    def criar_card(self, pai):
        return ctk.CTkFrame(
            pai,
            fg_color=self.COR_CARD,
            border_color=self.COR_BORDA,
            border_width=1,
            corner_radius=10,
        )

    def criar_selo_status(self, pai, status):
        """Selo visual para alerta, normalidade ou ausência de medições."""
        if status == "Alerta":
            fundo, texto = (
                self.COR_ALERTA_FUNDO,
                self.COR_ALERTA,
            )
        elif status == "Normal":
            fundo, texto = (
                self.COR_OK_FUNDO,
                self.COR_OK,
            )
        else:
            fundo, texto = (
                self.COR_SEM_DADOS_FUNDO,
                self.COR_SEM_DADOS,
            )

        return ctk.CTkLabel(
            pai,
            text=status,
            width=90,
            height=24,
            corner_radius=12,
            fg_color=fundo,
            text_color=texto,
            font=("Arial", 11, "bold"),
        )

    # --- ABA 1: PACIENTES ---
    def carregar_pacientes(self):
        self.titulo_aba(
            "Pacientes",
            "Acompanhamento das gestantes sob seu cuidado",
        )
        self.mostrar_aviso_demo()

        total = len(self.PACIENTES)

        em_alerta = sum(
            1 for paciente in self.PACIENTES
            if paciente["status"] == "Alerta"
        )

        consultas_hoje = sum(
            1 for paciente in self.PACIENTES
            if self.texto_consulta(paciente).startswith("Hoje")
        )

        linha_resumo = ctk.CTkFrame(
            self.painel_conteudo,
            fg_color="transparent",
        )
        linha_resumo.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        for coluna in range(3):
            linha_resumo.columnconfigure(coluna, weight=1)

        resumos = [
            ("Total de pacientes", total, self.COR_TITULO),
            ("Em alerta", em_alerta, self.COR_ALERTA),
            ("Consultas hoje", consultas_hoje, self.COR_ATIVO),
        ]

        for coluna, (rotulo, valor, cor) in enumerate(resumos):
            card = self.criar_card(linha_resumo)
            card.grid(
                row=0,
                column=coluna,
                padx=5,
                sticky="nsew",
            )

            ctk.CTkLabel(
                card,
                text=str(valor),
                font=("Arial", 26, "bold"),
                text_color=cor,
            ).pack(pady=(10, 0))

            ctk.CTkLabel(
                card,
                text=rotulo,
                font=("Arial", 11),
                text_color=self.COR_TEXTO,
            ).pack(pady=(0, 10))

        self.entrada_busca = IconEntry(
            self.painel_conteudo,
            icon="search",
            placeholder_text="Buscar paciente pelo nome...",
            height=46,
        )
        self.entrada_busca.pack(
            fill="x",
            padx=25,
            pady=(5, 10),
        )
        self.entrada_busca.bind(
            "<KeyRelease>",
            lambda event: self.desenhar_lista_pacientes(),
        )

        self.lista_pacientes = ctk.CTkScrollableFrame(
            self.painel_conteudo,
            fg_color="transparent",
        )
        self.lista_pacientes.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15),
        )

        self.desenhar_lista_pacientes()

    def desenhar_lista_pacientes(self):
        for componente in self.lista_pacientes.winfo_children():
            componente.destroy()

        filtro = self.entrada_busca.get().strip().casefold()

        encontrados = [
            paciente for paciente in self.PACIENTES
            if filtro in paciente["nome"].casefold()
        ]

        if not encontrados:
            ctk.CTkLabel(
                self.lista_pacientes,
                text="Nenhuma paciente encontrada.",
                text_color=self.COR_TEXTO,
            ).pack(pady=20)
            return

        for paciente in encontrados:
            linha = self.criar_card(self.lista_pacientes)
            linha.pack(fill="x", pady=4)
            linha.columnconfigure(0, weight=1)

            ctk.CTkLabel(
                linha,
                text=paciente["nome"],
                font=("Arial", 13, "bold"),
                text_color=self.COR_TITULO,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=15,
                pady=(10, 0),
            )

            resumo = (
                f"{self.texto_semanas(paciente)} • "
                f"Consulta: {self.texto_consulta(paciente)}"
            )

            ctk.CTkLabel(
                linha,
                text=resumo,
                font=("Arial", 11),
                text_color=self.COR_TEXTO,
                anchor="w",
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=15,
                pady=(0, 10),
            )

            self.criar_selo_status(
                linha,
                paciente["status"],
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=15,
            )

    # --- ABA 2: ALERTAS ---
    def carregar_alertas(self):
        self.titulo_aba(
            "Alertas",
            "Pacientes com sinais vitais registrados fora dos limites configurados",
        )
        self.mostrar_aviso_demo()

        alertas = [
            paciente for paciente in self.PACIENTES
            if paciente["status"] == "Alerta"
        ]

        lista = ctk.CTkScrollableFrame(
            self.painel_conteudo,
            fg_color="transparent",
        )
        lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15),
        )

        if not alertas:
            if self.modo_demo:
                mensagem = (
                    "Nenhum alerta na demonstração neste momento."
                )
            elif not any(
                paciente["status"] != "Sem dados"
                for paciente in self.PACIENTES
            ):
                mensagem = (
                    "Ainda não há sinais vitais registrados para avaliar."
                )
            else:
                mensagem = (
                    "Nenhum alerta gerado pelos dados registrados."
                )

            ctk.CTkLabel(
                lista,
                text=mensagem,
                text_color=self.COR_TEXTO,
                font=("Arial", 14),
                wraplength=800,
            ).pack(pady=30)
            return

        for paciente in alertas:
            card = ctk.CTkFrame(
                lista,
                fg_color=self.COR_ALERTA_FUNDO,
                border_color=self.COR_ALERTA,
                border_width=1,
                corner_radius=10,
            )
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(
                card,
                text=(
                    f'⚠️ {paciente["nome"]} '
                    f'({self.texto_semanas(paciente)})'
                ),
                font=("Arial", 14, "bold"),
                text_color=self.COR_ALERTA,
                anchor="w",
            ).pack(
                fill="x",
                padx=15,
                pady=(12, 2),
            )

            ctk.CTkLabel(
                card,
                text=paciente["motivo"],
                font=("Arial", 12),
                text_color=self.COR_TEXTO,
                anchor="w",
                wraplength=850,
            ).pack(fill="x", padx=15)

            ctk.CTkLabel(
                card,
                text=(
                    f'Próxima consulta: '
                    f'{self.texto_consulta(paciente)}'
                ),
                font=("Arial", 11),
                text_color=self.COR_TEXTO,
                anchor="w",
            ).pack(
                fill="x",
                padx=15,
                pady=(2, 12),
            )

    # --- ABA 3: AGENDA DO DIA ---
    def carregar_agenda(self):
        self.titulo_aba(
            "Agenda do Dia",
            "Consultas marcadas para hoje",
        )
        self.mostrar_aviso_demo()

        consultas = [
            paciente for paciente in self.PACIENTES
            if self.texto_consulta(paciente).startswith("Hoje")
        ]

        consultas.sort(
            key=lambda paciente: self.texto_consulta(paciente)
        )

        lista = ctk.CTkScrollableFrame(
            self.painel_conteudo,
            fg_color="transparent",
        )
        lista.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15),
        )

        if not consultas:
            ctk.CTkLabel(
                lista,
                text="Nenhuma consulta registrada para hoje.",
                text_color=self.COR_TEXTO,
            ).pack(pady=30)
            return

        for paciente in consultas:
            hora = self.texto_consulta(paciente).replace(
                "Hoje ", "", 1
            )

            card = self.criar_card(lista)
            card.pack(fill="x", pady=5)
            card.columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card,
                text=hora,
                font=("Arial", 20, "bold"),
                text_color=self.COR_ATIVO,
                width=80,
            ).grid(
                row=0,
                column=0,
                rowspan=2,
                padx=(15, 10),
                pady=12,
            )

            ctk.CTkLabel(
                card,
                text=paciente["nome"],
                font=("Arial", 14, "bold"),
                text_color=self.COR_TITULO,
                anchor="w",
            ).grid(
                row=0,
                column=1,
                sticky="w",
                pady=(12, 0),
            )

            ctk.CTkLabel(
                card,
                text=f'{self.texto_semanas(paciente)} • Pré-natal',
                font=("Arial", 11),
                text_color=self.COR_TEXTO,
                anchor="w",
            ).grid(
                row=1,
                column=1,
                sticky="w",
                pady=(0, 12),
            )

            self.criar_selo_status(
                card,
                paciente["status"],
            ).grid(
                row=0,
                column=2,
                rowspan=2,
                padx=15,
            )