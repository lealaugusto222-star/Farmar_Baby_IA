import re
from datetime import date, datetime

import customtkinter as ctk
from tkinter import messagebox

import banco
import dados_locais
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
        self.prioridade_selecionada = "Todas"

        # Usa os cadastros reais sempre que houver gestantes no banco.
        # Se ainda não houver nenhuma, mantém a demonstração que já existia.
        try:
            usuarios_cadastrados = banco.listar_usuarios("gestante")
        except banco.ErroBanco as erro:
            messagebox.showerror("Falha ao carregar pacientes", str(erro))
            usuarios_cadastrados = None
        self.modo_demo = usuarios_cadastrados is not None and not usuarios_cadastrados

        try:
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
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao carregar dados clínicos", str(erro))
            self.PACIENTES = []
            self.modo_demo = False

        try:
            self.consultas_locais = dados_locais.listar_consultas()
            self.alertas_resolvidos = dados_locais.listar_alertas_resolvidos()
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao carregar dados locais", str(erro))
            self.consultas_locais = []
            self.alertas_resolvidos = []

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
        paciente = {
            "id": usuario.get("id"),
            "nome": usuario.get("nome", "Paciente sem nome"),
            "email": usuario.get("email", ""),
            "telefone": usuario.get("telefone", ""),
            "data_nasc": usuario.get("data_nasc", ""),

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
        email = paciente["email"]
        if email:
            registros = dados_locais.listar_registros(email)
            if registros:
                registro = registros[-1]
                paciente["registro_clinico"] = registro
                paciente["semanas"] = registro.get("semana")
                paciente["peso"] = registro.get("peso")
                paciente["pressao"] = registro.get("pressao")
                paciente["consulta"] = TelaDashboardProfissional.formatar_data(
                    registro.get("proxima_consulta", "")
                )
                correspondencia = re.fullmatch(
                    r"(\d{2,3})/(\d{2,3})",
                    registro.get("pressao", ""),
                )
                if correspondencia:
                    paciente["pa_sis"] = int(correspondencia.group(1))
                    paciente["pa_dia"] = int(correspondencia.group(2))
        paciente["observacoes"] = (
            dados_locais.obter_observacoes(email) if email else ""
        )
        return paciente

    @staticmethod
    def formatar_data(data_iso):
        try:
            return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return data_iso or "Não agendada"

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
            ctk.CTkButton(
                linha,
                text="Detalhes",
                width=80,
                height=30,
                fg_color=self.COR_ATIVO,
                command=lambda p=paciente: self.abrir_detalhes_paciente(p),
            ).grid(
                row=0,
                column=2,
                rowspan=2,
                padx=(0, 12),
            )

    def abrir_detalhes_paciente(self, paciente):
        """Abre os dados cadastrais e as observações locais da paciente."""
        email = paciente.get("email", "")
        try:
            cadastro = banco.obter_usuario(email) if email else None
            observacoes = dados_locais.obter_observacoes(email) if email else ""
        except (banco.ErroBanco, OSError, ValueError) as erro:
            messagebox.showerror("Falha ao carregar detalhes", str(erro))
            return

        dados = cadastro or paciente
        janela = ctk.CTkToplevel(self.master)
        janela.title(f"Detalhes — {dados.get('nome', 'Paciente')}")
        janela.geometry("500x540")
        janela.transient(self.master)
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text=dados.get("nome", "Paciente"),
            font=("Arial", 20, "bold"),
            text_color=self.COR_TITULO,
        ).pack(anchor="w", padx=24, pady=(22, 12))

        for rotulo, chave in (
            ("E-mail", "email"),
            ("Telefone", "telefone"),
            ("Data de nascimento", "data_nasc"),
        ):
            ctk.CTkLabel(
                janela,
                text=f"{rotulo}: {dados.get(chave) or 'Não informado'}",
                font=("Arial", 12),
                anchor="w",
            ).pack(fill="x", padx=24, pady=4)

        registro = paciente.get("registro_clinico")
        if registro:
            resumo = (
                f"Último registro: semana {registro.get('semana', '—')} • "
                f"{registro.get('peso', '—')} kg • "
                f"{registro.get('pressao', '—')} mmHg"
            )
        else:
            resumo = "Sem medições registradas."
        ctk.CTkLabel(
            janela,
            text=resumo,
            font=("Arial", 12),
            anchor="w",
            wraplength=450,
        ).pack(fill="x", padx=24, pady=(12, 8))

        ctk.CTkLabel(
            janela,
            text="Observações",
            font=("Arial", 13, "bold"),
            anchor="w",
        ).pack(fill="x", padx=24, pady=(12, 4))
        campo_observacoes = ctk.CTkTextbox(janela, height=180)
        campo_observacoes.pack(fill="both", expand=True, padx=24)
        campo_observacoes.insert("1.0", observacoes)

        def salvar_observacoes():
            if not email:
                messagebox.showerror(
                    "Cadastro indisponível",
                    "Observações só podem ser salvas para pacientes cadastradas.",
                    parent=janela,
                )
                return
            try:
                dados_locais.salvar_observacoes(
                    email, campo_observacoes.get("1.0", "end")
                )
            except (OSError, ValueError) as erro:
                messagebox.showerror(
                    "Falha ao salvar observações", str(erro), parent=janela
                )
                return
            janela.destroy()

        ctk.CTkButton(
            janela,
            text="Salvar observações",
            fg_color=self.COR_ATIVO,
            hover_color="#b94d70",
            command=salvar_observacoes,
        ).pack(pady=18)
        return janela

    # --- ABA 2: ALERTAS ---
    def carregar_alertas(self):
        self.titulo_aba(
            "Alertas",
            "Alertas gerados pelos dados disponíveis; a prioridade é apenas informativa",
        )
        self.mostrar_aviso_demo()

        alertas = []
        for paciente in self.PACIENTES:
            motivos = []
            if paciente["status"] == "Alerta":
                motivos.append(paciente["motivo"])
            elif (
                paciente.get("pa_sis") is not None
                and paciente.get("pa_dia") is not None
                and (
                    paciente["pa_sis"] >= self.LIMITE_PA_SISTOLICA
                    or paciente["pa_dia"] >= self.LIMITE_PA_DIASTOLICA
                )
            ):
                motivos.append(
                    f'Pressão arterial acima do limite configurado: '
                    f'{paciente["pa_sis"]}/{paciente["pa_dia"]} mmHg'
                )
            if not motivos:
                continue

            registro = paciente.get("registro_clinico", {})
            identidade = paciente.get("email") or paciente.get("nome", "")
            identificador = (
                registro.get("id")
                or paciente.get("motivo", "alerta")
            )
            alertas.append({
                "id": f"{identidade}:{identificador}",
                "paciente": paciente,
                "motivo": "; ".join(motivos),
                "prioridade": (
                    "Alta"
                    if paciente.get("pa_sis", 0) >= 160
                    or paciente.get("pa_dia", 0) >= 110
                    else "Média"
                ),
            })

        opcoes_prioridade = ["Todas", "Alta", "Média", "Baixa"]
        self.filtro_prioridade = ctk.StringVar(
            value=self.prioridade_selecionada
        )
        self.seletor_filtro_prioridade = ctk.CTkOptionMenu(
            self.painel_conteudo,
            values=opcoes_prioridade,
            variable=self.filtro_prioridade,
            command=self.selecionar_prioridade,
            fg_color=self.COR_ATIVO,
            button_color=self.COR_ATIVO,
        )
        self.seletor_filtro_prioridade.pack(
            anchor="e", padx=25, pady=(0, 8)
        )

        alertas = [
            alerta for alerta in alertas
            if alerta["id"] not in self.alertas_resolvidos
            and (
                self.filtro_prioridade.get() == "Todas"
                or alerta["prioridade"] == self.filtro_prioridade.get()
            )
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
                    "Nenhum alerta corresponde ao filtro selecionado."
                )
            elif not any(
                paciente["status"] != "Sem dados"
                for paciente in self.PACIENTES
            ):
                mensagem = (
                    "Ainda não há alertas para o filtro selecionado."
                )
            else:
                mensagem = (
                    "Nenhum alerta ativo corresponde ao filtro selecionado."
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
            dados_paciente = paciente["paciente"]
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
                    f'⚠️ {dados_paciente["nome"]} '
                    f'({self.texto_semanas(dados_paciente)}) '
                    f'• Prioridade {paciente["prioridade"]}'
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
                    f'{self.texto_consulta(dados_paciente)}'
                ),
                font=("Arial", 11),
                text_color=self.COR_TEXTO,
                anchor="w",
            ).pack(
                fill="x",
                padx=15,
                pady=(2, 12),
            )

            ctk.CTkButton(
                card,
                text="Marcar como resolvido",
                width=150,
                height=30,
                fg_color=self.COR_OK,
                hover_color="#276749",
                command=lambda alerta_id=paciente["id"]: self.resolver_alerta(
                    alerta_id
                ),
            ).pack(anchor="e", padx=15, pady=(0, 12))

    def resolver_alerta(self, alerta_id):
        try:
            dados_locais.resolver_alerta(alerta_id)
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao resolver alerta", str(erro))
            return
        if alerta_id not in self.alertas_resolvidos:
            self.alertas_resolvidos.append(alerta_id)
        self.mudar_aba("alertas")

    def selecionar_prioridade(self, prioridade):
        self.prioridade_selecionada = prioridade
        self.mudar_aba("alertas")

    # --- ABA 3: AGENDA DO DIA ---
    def carregar_agenda(self):
        self.titulo_aba(
            "Agenda",
            "Agende novas consultas e acompanhe as consultas registradas",
        )
        self.mostrar_aviso_demo()

        pacientes_reais = [
            paciente for paciente in self.PACIENTES
            if paciente.get("email")
        ]
        opcoes = {
            f'{paciente["nome"]} ({paciente["email"]})': paciente
            for paciente in pacientes_reais
        }

        formulario = self.criar_card(self.painel_conteudo)
        formulario.pack(fill="x", padx=25, pady=(0, 10))
        ctk.CTkLabel(
            formulario,
            text="Agendar consulta",
            font=("Arial", 14, "bold"),
            text_color=self.COR_TITULO,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 4))

        self.paciente_consulta = ctk.StringVar(
            value=next(iter(opcoes), "Nenhuma paciente cadastrada")
        )
        self.seletor_paciente = ctk.CTkOptionMenu(
            formulario,
            values=list(opcoes) or ["Nenhuma paciente cadastrada"],
            variable=self.paciente_consulta,
            fg_color=self.COR_ATIVO,
            button_color=self.COR_ATIVO,
        )
        self.seletor_paciente.grid(
            row=1, column=0, columnspan=2, padx=10, pady=8, sticky="ew"
        )
        if not opcoes:
            self.seletor_paciente.configure(state="disabled")

        self.campo_data_consulta = ctk.CTkEntry(
            formulario,
            placeholder_text="Data (DD/MM/AAAA)",
        )
        self.campo_data_consulta.grid(
            row=2, column=0, padx=10, pady=8, sticky="ew"
        )
        self.campo_horario_consulta = ctk.CTkEntry(
            formulario,
            placeholder_text="Horário (HH:MM)",
        )
        self.campo_horario_consulta.grid(
            row=2, column=1, padx=10, pady=8, sticky="ew"
        )
        self.campo_observacao_consulta = ctk.CTkEntry(
            formulario,
            placeholder_text="Observação (opcional)",
        )
        self.campo_observacao_consulta.grid(
            row=3, column=0, columnspan=2, padx=10, pady=8, sticky="ew"
        )
        self.botao_agendar = ctk.CTkButton(
            formulario,
            text="Agendar",
            fg_color=self.COR_ATIVO,
            command=lambda: self.agendar_consulta(opcoes),
        )
        self.botao_agendar.grid(
            row=4, column=0, columnspan=2, padx=10, pady=(4, 12)
        )
        for coluna in range(2):
            formulario.columnconfigure(coluna, weight=1)

        consultas = []
        email_profissional = (
            self.usuario.get("email", "").strip().lower()
            if isinstance(self.usuario, dict)
            else ""
        )
        for consulta in self.consultas_locais:
            if (
                consulta.get("profissional_email") == email_profissional
                or not email_profissional
            ):
                paciente = next(
                    (
                        item for item in self.PACIENTES
                        if item.get("email") == consulta.get("paciente_email")
                    ),
                    None,
                )
                if paciente:
                    consultas.append((consulta, paciente))

        if self.modo_demo:
            for paciente in self.PACIENTES:
                consulta_demo = self.texto_consulta(paciente)
                if consulta_demo.startswith("Hoje"):
                    consultas.append(({
                        "id": f'demo-{paciente["nome"]}',
                        "data": datetime.now().date().isoformat(),
                        "horario": consulta_demo.replace("Hoje ", "", 1),
                        "observacao": "Consulta de demonstração",
                        "concluida": False,
                        "demonstracao": True,
                    }, paciente))

        consultas.sort(
            key=lambda item: (
                item[0].get("data", ""),
                item[0].get("horario", ""),
            )
        )
        lista = ctk.CTkScrollableFrame(
            self.painel_conteudo,
            fg_color="transparent",
        )
        lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        if not consultas:
            ctk.CTkLabel(
                lista,
                text="Nenhuma consulta agendada.",
                text_color=self.COR_TEXTO,
            ).pack(pady=24)
            return

        for consulta, paciente in consultas:
            card = self.criar_card(lista)
            card.pack(fill="x", pady=5)
            card.columnconfigure(0, weight=1)
            try:
                data = self.formatar_data(consulta.get("data", ""))
            except (TypeError, ValueError):
                data = consulta.get("data", "")
            estado = "Concluída" if consulta.get("concluida") else "Agendada"
            texto = (
                f'{data} às {consulta.get("horario", "")} • '
                f'{paciente["nome"]} • {estado}'
            )
            if consulta.get("observacao"):
                texto += f'\n{consulta["observacao"]}'
            ctk.CTkLabel(
                card,
                text=texto,
                font=("Arial", 12),
                text_color=self.COR_TEXTO,
                anchor="w",
                justify="left",
            ).grid(row=0, column=0, sticky="w", padx=14, pady=12)
            if not consulta.get("concluida"):
                ctk.CTkButton(
                    card,
                    text="Marcar concluída",
                    width=140,
                    command=lambda item=consulta: self.concluir_consulta(item),
                ).grid(row=0, column=1, padx=12, pady=8)

    def agendar_consulta(self, opcoes):
        selecao = self.paciente_consulta.get()
        paciente = opcoes.get(selecao)
        if not paciente:
            messagebox.showerror(
                "Paciente necessária",
                "Cadastre ou selecione uma paciente real para agendar.",
            )
            return
        try:
            data = datetime.strptime(
                self.campo_data_consulta.get().strip(), "%d/%m/%Y"
            ).date()
            horario = self.campo_horario_consulta.get().strip()
            datetime.strptime(horario, "%H:%M")
            if data < date.today():
                raise ValueError("A data da consulta não pode estar no passado.")
        except ValueError:
            messagebox.showerror(
                "Dados inválidos",
                "Informe a data no formato DD/MM/AAAA e o horário em HH:MM.",
            )
            return

        profissional_email = (
            self.usuario.get("email", "").strip().lower()
            if isinstance(self.usuario, dict)
            else ""
        )
        if not profissional_email:
            messagebox.showerror(
                "Conta profissional necessária",
                "Entre em uma conta profissional para registrar a consulta.",
            )
            return
        try:
            consulta = dados_locais.agendar_consulta(
                profissional_email,
                paciente["email"],
                data.isoformat(),
                horario,
                self.campo_observacao_consulta.get().strip(),
            )
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao agendar consulta", str(erro))
            return
        self.consultas_locais.append(consulta)
        self.mudar_aba("agenda")

    def concluir_consulta(self, consulta):
        if consulta.get("demonstracao"):
            messagebox.showinfo(
                "Demonstração",
                "Consultas fictícias não podem ser alteradas.",
            )
            return
        try:
            dados_locais.concluir_consulta(consulta["id"])
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao concluir consulta", str(erro))
            return
        consulta["concluida"] = True
        self.mudar_aba("agenda")