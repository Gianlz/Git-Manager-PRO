import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json

# First try to import git with error handling
try:
    import git
except ImportError as e:
    # Store the original error message
    GIT_IMPORT_ERROR = str(e)
    git = None

class GitManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.load_config()
        
        self.window = ctk.CTk()
        self.window.title("Git Manager Pro")
        self.window.geometry("1200x900")
        ctk.set_appearance_mode("system")
        # Apply saved theme if exists
        if hasattr(self, 'current_theme'):
            theme_path = os.path.join(os.path.dirname(__file__), "themes", f"{self.current_theme}.json")
            if os.path.exists(theme_path):
                ctk.set_default_color_theme(theme_path)
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 1200) // 2
        y = (screen_height - 900) // 2
        self.window.geometry(f"+{x}+{y}")
        
    
   
        
        # Repositório atual
        self.current_repo = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configuração do grid principal
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo
        self.left_panel = ctk.CTkFrame(self.window, width=300)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Área principal
        self.main_area = ctk.CTkFrame(self.window)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.create_left_panel()
        self.create_main_area()
        
        # Add new tabs to your tabview creation
        self.tab_config = self.tabview.add("Config")
        self.tab_branches = self.tabview.add("Branches")
        
        # Call the setup methods
        self.setup_config_tab()
        self.setup_branches_tab()
        
    def create_left_panel(self):
        # Título REPOSITÓRIO
        repo_label = ctk.CTkLabel(
            self.left_panel,
            text="REPOSITÓRIO",
            font=("Arial", 14, "bold")
        )
        repo_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Botão Clonar Repositório
        clone_btn = ctk.CTkButton(
            self.left_panel,
            text="Clonar Repositório",
            command=self.clone_repository,
            height=32
        )
        clone_btn.pack(pady=5, padx=10, fill="x")
        
        # Frame para caminho do repositório
        path_frame = ctk.CTkFrame(self.left_panel)
        path_frame.pack(pady=5, padx=10, fill="x")
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="C:/Users/skyla/Pictures/teste/Git"
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="📁",
            width=32,
            height=32,
            command=self.browse_repository
        )
        browse_btn.pack(side="right", padx=(5, 0))
        
        # STATUS com mini console
        status_label = ctk.CTkLabel(
            self.left_panel,
            text="STATUS",
            font=("Arial", 14, "bold")
        )
        status_label.pack(pady=(20, 5), padx=10, anchor="w")
        
        # Frame para mini console
        self.mini_console = ctk.CTkFrame(self.left_panel)
        self.mini_console.pack(pady=5, padx=10, fill="x")
        
        # Labels para informações
        self.info_labels = {
            "projeto": ctk.CTkLabel(
                self.mini_console,
                text="📁 Projeto: Nenhum",
                anchor="w",
                justify="left"
            ),
            "branch": ctk.CTkLabel(
                self.mini_console,
                text="🔀 Branch: -",
                anchor="w",
                justify="left"
            ),
            "arquivos_modificados": ctk.CTkLabel(
                self.mini_console,
                text="📝 Modificados: 0",
                anchor="w",
                justify="left"
            ),
            "arquivos_untracked": ctk.CTkLabel(
                self.mini_console,
                text="❓ Não rastreados: 0",
                anchor="w",
                justify="left"
            ),
            "commits_ahead": ctk.CTkLabel(
                self.mini_console,
                text="⬆️ Commits para push: 0",
                anchor="w",
                justify="left"
            ),
            "commits_behind": ctk.CTkLabel(
                self.mini_console,
                text="⬇️ Commits para pull: 0",
                anchor="w",
                justify="left"
            )
        }
        
        # Adicionar labels ao mini console
        for label in self.info_labels.values():
            label.pack(pady=2, padx=5, fill="x")
        
        # AÇÕES RÁPIDAS
        actions_label = ctk.CTkLabel(
            self.left_panel,
            text="AÇÕES RÁPIDAS",
            font=("Arial", 14, "bold")
        )
        actions_label.pack(pady=(20, 5), padx=10, anchor="w")
        
        # Botões de ações
        actions = [
            ("⬇️ Pull", self.pull_changes),
            ("⬆️ Push", self.push_changes),
            ("📝 Commit", self.show_commit_view),
            ("🔀 Branches", self.show_branches)
        ]
        
        for text, command in actions:
            btn = ctk.CTkButton(
                self.left_panel,
                text=text,
                command=command,
                height=32
            )
            btn.pack(pady=5, padx=10, fill="x")
            
    def create_main_area(self):
        # Título ÁREA DE TRABALHO
        title_frame = ctk.CTkFrame(self.main_area)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        work_label = ctk.CTkLabel(
            title_frame,
            text="ÁREA DE TRABALHO",
            font=("Arial", 14, "bold")
        )
        work_label.pack(side="left")
        
        # TabView
        self.tabview = ctk.CTkTabview(self.main_area)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Criar as tabs
        self.tab_alteracoes = self.tabview.add("Alterações")
        self.tab_historico = self.tabview.add("Histórico")
        self.tab_estatisticas = self.tabview.add("Estatísticas")
        
        # Configurar conteúdo da tab Alterações
        self.setup_alteracoes_tab()
        
        # Configurar conteúdo da tab Histórico
        self.setup_historico_tab()
        
        # Configurar conteúdo da tab Estatísticas
        self.setup_estatisticas_tab()
        
    def setup_alteracoes_tab(self):
        # Botões de ação
        actions_frame = ctk.CTkFrame(self.tab_alteracoes)
        actions_frame.pack(fill="x", pady=5)
        
        actions = [
            ("🔄 Atualizar", self.refresh),
            ("➕ Add Selecionados", self.add_selected),
            ("📥 Add Todos", self.add_all)
        ]
        
        for text, command in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                height=32,
                width=120
            )
            btn.pack(side="left", padx=2)
        
        # Área de arquivos
        self.files_frame = ctk.CTkScrollableFrame(self.tab_alteracoes)
        self.files_frame.pack(fill="both", expand=True, pady=5)
        
        # Dicionário para armazenar as checkboxes
        self.file_checkboxes = {}
        
        # Atualizar lista de arquivos
        self.update_file_list()
        
        # Status do Git com estilo de console
        self.git_status_frame = ctk.CTkFrame(self.tab_alteracoes)
        self.git_status_frame.pack(fill="both", expand=True, pady=5)
        
        status_label = ctk.CTkLabel(
            self.git_status_frame,
            text="Console Git",
            font=("Arial", 12, "bold")
        )
        status_label.pack(anchor="w", padx=10, pady=5)
        
        # Textbox com estilo de console
        self.status_text = ctk.CTkTextbox(
            self.git_status_frame,
            font=("Consolas", 12),  # Fonte monoespaçada
            height=400
        )
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configurar cores de fundo para parecer um console
        self.status_text.configure(
            fg_color="#1a1a1a",  # Fundo mais escuro
            text_color="#ffffff"  # Texto branco
        )
        
        # Adicione após a criação do tab_alteracoes
        self.setup_branch_sync_frame()
        
    def setup_historico_tab(self):
        # Main container
        main_frame = ctk.CTkFrame(self.tab_historico)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="HISTÓRICO DE COMMITS",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(5,10), anchor="w")
        
        # Filters frame
        filters_frame = ctk.CTkFrame(main_frame)
        filters_frame.pack(fill="x", pady=5)
        
        # Branch filter
        branch_frame = ctk.CTkFrame(filters_frame)
        branch_frame.pack(side="left", padx=5)
        
        branch_label = ctk.CTkLabel(branch_frame, text="Branch:", font=("Arial", 12))
        branch_label.pack(side="left", padx=5)
        
        self.history_branch_var = ctk.StringVar(value="all")
        self.branch_combobox = ctk.CTkComboBox(
            branch_frame,
            values=["all"],
            variable=self.history_branch_var,
            width=150,
            command=self.update_historico
        )
        self.branch_combobox.pack(side="left", padx=5)
        
        # Date filter
        date_frame = ctk.CTkFrame(filters_frame)
        date_frame.pack(side="left", padx=20)
        
        date_label = ctk.CTkLabel(date_frame, text="Period:", font=("Arial", 12))
        date_label.pack(side="left", padx=5)
        
        self.date_filter_var = ctk.StringVar(value="All time")
        date_combobox = ctk.CTkComboBox(
            date_frame,
            values=["All time", "Today", "Last 7 days", "Last 30 days", "Last 90 days"],
            variable=self.date_filter_var,
            width=150,
            command=self.update_historico
        )
        date_combobox.pack(side="left", padx=5)
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=10)
        
        search_label = ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 14))
        search_label.pack(side="left", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search commits...",
            width=300
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<Return>', lambda e: self.update_historico())
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.update_historico
        )
        search_button.pack(side="left", padx=5)
        
        # Commits list
        self.commits_frame = ctk.CTkScrollableFrame(main_frame)
        self.commits_frame.pack(fill="both", expand=True, pady=10)
        
        # Initial update
        self.update_historico()

    def update_historico(self, *args):
        if not self.current_repo:
            return
        
        # Clear previous commits
        for widget in self.commits_frame.winfo_children():
            widget.destroy()
        
        try:
            # Update branch list
            branches = ["all"] + [b.name for b in self.current_repo.heads]
            self.branch_combobox.configure(values=branches)
            
            # Get commits based on filters
            commits = self.get_filtered_commits()
            
            if not commits:
                no_commits_label = ctk.CTkLabel(
                    self.commits_frame,
                    text="No commits found",
                    font=("Arial", 12),
                    text_color="gray"
                )
                no_commits_label.pack(pady=20)
                return
            
            # Display commits
            for commit in commits:
                commit_frame = self.create_commit_widget(commit)
                commit_frame.pack(fill="x", pady=2, padx=5)
                
        except git.GitCommandError as e:
            error_label = ctk.CTkLabel(
                self.commits_frame,
                text=f"Error: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=10)

    def get_filtered_commits(self):
        # Build git log command based on filters
        log_args = ['--pretty=format:%H']  # Get full hashes
        
        # Branch filter
        if self.history_branch_var.get() != "all":
            log_args.append(self.history_branch_var.get())
        
        # Date filter
        date_filter = self.date_filter_var.get()
        if date_filter != "All time":
            if date_filter == "Today":
                log_args.append('--since=midnight')
            elif date_filter == "Last 7 days":
                log_args.append('--since=7.days.ago')
            elif date_filter == "Last 30 days":
                log_args.append('--since=30.days.ago')
            elif date_filter == "Last 90 days":
                log_args.append('--since=90.days.ago')
        
        # Search filter
        search_text = self.search_entry.get().strip()
        if search_text:
            log_args.append(f'--grep={search_text}')
            log_args.append('--regexp-ignore-case')
        
        # Get commit hashes
        commit_hashes = self.current_repo.git.log(*log_args).split('\n')
        
        # Convert hashes to commit objects
        return [self.current_repo.commit(hash) for hash in commit_hashes if hash]

    def create_commit_widget(self, commit):
        frame = ctk.CTkFrame(self.commits_frame)
        
        # Header frame
        header_frame = ctk.CTkFrame(frame)
        header_frame.pack(fill="x", padx=5, pady=2)
        
        # Commit hash
        hash_label = ctk.CTkLabel(
            header_frame,
            text=commit.hexsha[:8],
            font=("Consolas", 12),
            text_color="#ffaa00"
        )
        hash_label.pack(side="left", padx=5)
        
        # Author
        author_label = ctk.CTkLabel(
            header_frame,
            text=f"by {commit.author.name}",
            font=("Arial", 11)
        )
        author_label.pack(side="left", padx=5)
        
        # Date
        date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M")
        date_label = ctk.CTkLabel(
            header_frame,
            text=date,
            font=("Arial", 11),
            text_color="gray"
        )
        date_label.pack(side="right", padx=5)
        
        # Commit message
        msg_frame = ctk.CTkFrame(frame)
        msg_frame.pack(fill="x", padx=5, pady=2)
        
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=commit.message.strip(),
            font=("Arial", 12),
            justify="left",
            anchor="w"
        )
        msg_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Actions frame
        actions_frame = ctk.CTkFrame(frame)
        actions_frame.pack(fill="x", padx=5, pady=2)
        
        # Show changes button
        def show_commit_changes():
            self.show_commit_details(commit)
        
        changes_btn = ctk.CTkButton(
            actions_frame,
            text="Show Changes",
            command=show_commit_changes,
            width=100,
            height=24
        )
        changes_btn.pack(side="left", padx=5)
        
        # Checkout button
        def checkout_commit():
            try:
                self.current_repo.git.checkout(commit.hexsha)
                messagebox.showinfo("Success", f"Checked out commit {commit.hexsha[:8]}")
                self.refresh()
            except git.GitCommandError as e:
                messagebox.showerror("Error", str(e))
        
        checkout_btn = ctk.CTkButton(
            actions_frame,
            text="Checkout",
            command=checkout_commit,
            width=100,
            height=24
        )
        checkout_btn.pack(side="left", padx=5)
        
        return frame

    def show_commit_details(self, commit):
        # Create details window
        details_window = ctk.CTkToplevel(self.window)
        details_window.title(f"Commit Details - {commit.hexsha[:8]}")
        details_window.geometry("800x600")
        details_window.transient(self.window)
        details_window.grab_set()
        
        # Center window
        x = self.window.winfo_x() + (self.window.winfo_width() - 800) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 600) // 2
        details_window.geometry(f"+{x}+{y}")
        
        # Commit info frame
        info_frame = ctk.CTkFrame(details_window)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Basic info
        ctk.CTkLabel(
            info_frame,
            text=f"Commit: {commit.hexsha}",
            font=("Consolas", 12)
        ).pack(anchor="w", padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Author: {commit.author.name} <{commit.author.email}>",
            font=("Arial", 12)
        ).pack(anchor="w", padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}",
            font=("Arial", 12)
        ).pack(anchor="w", padx=5)
        
        # Commit message
        msg_frame = ctk.CTkFrame(details_window)
        msg_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            msg_frame,
            text="Message:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=5)
        
        msg_text = ctk.CTkTextbox(msg_frame, height=60)
        msg_text.pack(fill="x", padx=5, pady=5)
        msg_text.insert("1.0", commit.message)
        msg_text.configure(state="disabled")
        
        # Changes
        changes_frame = ctk.CTkFrame(details_window)
        changes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            changes_frame,
            text="Changes:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=5)
        
        # Show diff in a textbox
        diff_text = ctk.CTkTextbox(changes_frame, font=("Consolas", 12))
        diff_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        try:
            # Get the diff
            diff = self.current_repo.git.show(
                commit.hexsha,
                '--color=never',
                '--patch'
            )
            
            # Insert diff with syntax highlighting
            diff_text.insert("1.0", diff)
            
            # Apply basic syntax highlighting
            for pattern, color in [
                (r'diff --git.*\n', '#00ff00'),  # File headers in green
                (r'\+.*\n', '#00ff00'),          # Additions in green
                (r'-.*\n', '#ff0000'),           # Deletions in red
                (r'@@ .*\n', '#00ffff')          # Chunk headers in cyan
            ]:
                start = "1.0"
                while True:
                    start = diff_text.search(pattern, start, "end", regexp=True)
                    if not start:
                        break
                    line_end = diff_text.search('\n', start)
                    if not line_end:
                        line_end = "end"
                    else:
                        line_end = f"{line_end}+1c"
                    diff_text.tag_add(f"color_{color}", start, line_end)
                    diff_text.tag_config(f"color_{color}", foreground=color)
                    start = line_end
            
            diff_text.configure(state="disabled")
            
        except git.GitCommandError as e:
            diff_text.insert("1.0", f"Error getting diff: {str(e)}")
            diff_text.configure(state="disabled")

    def setup_estatisticas_tab(self):
        # Frame para período
        period_frame = ctk.CTkFrame(self.tab_estatisticas)
        period_frame.pack(fill="x", pady=5)
        
        period_label = ctk.CTkLabel(period_frame, text="Período:")
        period_label.pack(side="left", padx=5)
        
        self.period_combobox = ctk.CTkComboBox(
            period_frame,
            values=["Última semana", "Último mês", "Último ano", "Todo o projeto"],
            width=150
        )
        self.period_combobox.pack(side="left", padx=5)
        
        # Frame para estatísticas
        stats_container = ctk.CTkFrame(self.tab_estatisticas)
        stats_container.pack(fill="both", expand=True, pady=5)
        
        # Grid para estatísticas
        stats = [
            ("Total de commits:", "0"),
            ("Contribuidores:", "0"),
            ("Arquivos alterados:", "0"),
            ("Linhas adicionadas:", "0"),
            ("Linhas removidas:", "0")
        ]
        
        for i, (label_text, value) in enumerate(stats):
            label = ctk.CTkLabel(
                stats_container,
                text=label_text,
                font=("Arial", 12, "bold")
            )
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            value_label = ctk.CTkLabel(
                stats_container,
                text=value
            )
            value_label.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
    def update_mini_console(self):
        if not self.current_repo:
            for label in self.info_labels.values():
                label.configure(fg_color="transparent")
            return
            
        try:
            # Atualizar nome do projeto
            projeto_nome = os.path.basename(self.current_repo.working_dir)
            self.info_labels["projeto"].configure(
                text=f"📁 Projeto: {projeto_nome}"
            )
            
            # Atualizar branch atual
            branch_atual = self.current_repo.active_branch.name
            self.info_labels["branch"].configure(
                text=f"🔀 Branch: {branch_atual}"
            )
            
            # Contar arquivos modificados e não rastreados
            status = self.current_repo.git.status('--porcelain').split('\n')
            modificados = len([f for f in status if f.startswith(' M') or f.startswith('M ')])
            untracked = len([f for f in status if f.startswith('??')])
            
            self.info_labels["arquivos_modificados"].configure(
                text=f"📝 Modificados: {modificados}"
            )
            self.info_labels["arquivos_untracked"].configure(
                text=f"❓ Não rastreados: {untracked}"
            )
            
            # Verificar commits ahead/behind
            try:
                remote = self.current_repo.active_branch.tracking_branch()
                if remote:
                    ahead = len(list(self.current_repo.iter_commits(f'{remote.name}..HEAD')))
                    behind = len(list(self.current_repo.iter_commits(f'HEAD..{remote.name}')))
                    
                    self.info_labels["commits_ahead"].configure(
                        text=f"⬆️ Commits para push: {ahead}"
                    )
                    self.info_labels["commits_behind"].configure(
                        text=f"⬇️ Commits para pull: {behind}"
                    )
                else:
                    self.info_labels["commits_ahead"].configure(
                        text="⬆️ Sem remote configurado"
                    )
                    self.info_labels["commits_behind"].configure(
                        text="⬇️ Sem remote configurado"
                    )
            except git.GitCommandError:
                self.info_labels["commits_ahead"].configure(
                    text="⬆️ Erro ao verificar commits"
                )
                self.info_labels["commits_behind"].configure(
                    text="⬇️ Erro ao verificar commits"
                )
                
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def update_file_list(self):
        # Limpar checkboxes anteriores
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()
        
        if not self.current_repo:
            return
            
        try:
            # Obter status dos arquivos
            status = self.current_repo.git.status('--porcelain').split('\n')
            
            # Agrupar arquivos por status
            modified_files = []
            untracked_files = []
            staged_files = []
            
            for line in status:
                if not line:
                    continue
                status_code = line[:2]
                file_path = line[3:]
                
                if status_code == 'M ' or status_code == 'A ':
                    staged_files.append(file_path)
                elif status_code == ' M':
                    modified_files.append(file_path)
                elif status_code == '??':
                    untracked_files.append(file_path)
            
            # Função para criar seção de arquivos
            def create_section(title, files, color):
                if files:
                    section_label = ctk.CTkLabel(
                        self.files_frame,
                        text=title,
                        font=("Arial", 12, "bold"),
                        text_color=color
                    )
                    section_label.pack(pady=(10,5), anchor="w")
                    
                    for file in files:
                        file_frame = ctk.CTkFrame(self.files_frame)
                        file_frame.pack(fill="x", pady=2)
                        
                        checkbox = ctk.CTkCheckBox(
                            file_frame,
                            text=file,
                            font=("Arial", 11)
                        )
                        checkbox.pack(side="left", padx=5)
                        
                        self.file_checkboxes[file] = checkbox
            
            # Criar seções para cada tipo de arquivo
            create_section("📦 Staged Files", staged_files, "green")
            create_section("📝 Modified Files", modified_files, "orange")
            create_section("❓ Untracked Files", untracked_files, "red")
            
            if not (staged_files or modified_files or untracked_files):
                no_changes_label = ctk.CTkLabel(
                    self.files_frame,
                    text="✨ No changes detected",
                    font=("Arial", 12),
                    text_color="gray"
                )
                no_changes_label.pack(pady=20)
                
        except git.GitCommandError as e:
            error_label = ctk.CTkLabel(
                self.files_frame,
                text=f"Error: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=10)

    # Métodos de ação
    def browse_repository(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            self.open_repository(path)
            
    def open_repository(self, path):
        if git is None:
            messagebox.showerror("Error", "Git is not properly configured. Please install Git and restart the application.")
            return
            
        try:
            self.current_repo = git.Repo(path)
            self.update_status()
            self.update_mini_console()
        except git.InvalidGitRepositoryError:
            messagebox.showerror("Error", "Selected directory is not a valid Git repository!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open repository: {str(e)}")
            
    def update_status(self):
        if not self.current_repo:
            return
            
        try:
            # Limpar status anterior
            self.status_text.configure(state="normal")
            self.status_text.delete("1.0", "end")
            
            # Configurar cores
            self.status_text.tag_config("header", foreground="#00ff00")  # Verde
            self.status_text.tag_config("branch", foreground="#00ffff")  # Ciano
            self.status_text.tag_config("modified", foreground="#ff9900")  # Laranja
            self.status_text.tag_config("untracked", foreground="#ff0000")  # Vermelho
            self.status_text.tag_config("staged", foreground="#00ff00")  # Verde
            self.status_text.tag_config("clean", foreground="#888888")  # Cinza
            self.status_text.tag_config("remote", foreground="#ff00ff")  # Magenta
            
            # Cabeçalho
            self.status_text.insert("end", "=== Status do Git ===\n\n", "header")
            
            # Branch atual
            branch = self.current_repo.active_branch.name
            self.status_text.insert("end", f"📍 Branch: ", "header")
            self.status_text.insert("end", f"{branch}\n", "branch")
            
            # Status do repositório
            status = self.current_repo.git.status('--porcelain')
            staged_files = []
            modified_files = []
            untracked_files = []
            
            for line in status.split('\n'):
                if line:
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code == 'M ' or status_code == 'A ':
                        staged_files.append(file_path)
                    elif status_code == ' M':
                        modified_files.append(file_path)
                    elif status_code == '??':
                        untracked_files.append(file_path)
            
            # Arquivos staged
            if staged_files:
                self.status_text.insert("end", "\n📦 Alterações preparadas para commit:\n", "header")
                for file in staged_files:
                    self.status_text.insert("end", f"    ✓ {file}\n", "staged")
                    
            # Arquivos modificados
            if modified_files:
                self.status_text.insert("end", "\n📝 Arquivos modificados:\n", "header")
                for file in modified_files:
                    self.status_text.insert("end", f"    • {file}\n", "modified")
                    
            # Arquivos untracked
            if untracked_files:
                self.status_text.insert("end", "\n❓ Arquivos não rastreados:\n", "header")
                for file in untracked_files:
                    self.status_text.insert("end", f"    + {file}\n", "untracked")
                    
            # Status do remote
            try:
                remote = self.current_repo.active_branch.tracking_branch()
                if remote:
                    self.status_text.insert("end", "\n🌐 Status do Remote:\n", "header")
                    
                    # Commits ahead/behind
                    ahead = len(list(self.current_repo.iter_commits(f'{remote.name}..HEAD')))
                    behind = len(list(self.current_repo.iter_commits(f'HEAD..{remote.name}')))
                    
                    if ahead > 0:
                        self.status_text.insert("end", f"    ⬆️ {ahead} commit(s) para push\n", "remote")
                    if behind > 0:
                        self.status_text.insert("end", f"    ⬇️ {behind} commit(s) para pull\n", "remote")
                    if ahead == 0 and behind == 0:
                        self.status_text.insert("end", "    ✓ Sincronizado com remote\n", "clean")
                else:
                    self.status_text.insert("end", "\n⚠️ Sem remote configurado\n", "remote")
                    
            except git.GitCommandError:
                self.status_text.insert("end", "\n❌ Erro ao verificar remote\n", "untracked")
                
            # Se não houver alterações
            if not (staged_files or modified_files or untracked_files):
                self.status_text.insert("end", "\n✨ Working tree clean\n", "clean")
                
            # Último commit
            try:
                last_commit = self.current_repo.head.commit
                self.status_text.insert("end", "\n📅 Último commit:\n", "header")
                self.status_text.insert("end", f"    Hash: {last_commit.hexsha[:7]}\n", "clean")
                self.status_text.insert("end", f"    Autor: {last_commit.author.name}\n", "clean")
                self.status_text.insert("end", f"    Data: {last_commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n", "clean")
                self.status_text.insert("end", f"    Mensagem: {last_commit.message.strip()}\n", "clean")
            except:
                pass
                
            self.status_text.configure(state="disabled")
            
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def add_selected(self):
        if not self.current_repo:
            messagebox.showerror("Error", "No repository open!")
            return
            
        try:
            # Get selected files
            selected_files = [
                file for file, checkbox in self.file_checkboxes.items()
                if checkbox.get() == 1
            ]
            
            if not selected_files:
                messagebox.showwarning("Warning", "No files selected!")
                return
                
            # Add selected files
            for file in selected_files:
                self.current_repo.git.add(file)
                
            messagebox.showinfo("Success", f"Added {len(selected_files)} file(s) to staging area!")
            
            # Update UI
            self.refresh()
            
        except git.GitCommandError as e:
            messagebox.showerror("Error", str(e))

    def add_all(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
            
        try:
            self.current_repo.git.add('.')
            messagebox.showinfo("Sucesso", "Todos os arquivos foram adicionados!")
            self.update_status()
            self.update_mini_console()
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def clone_repository(self):
        if git is None:
            messagebox.showerror("Error", "Git is not properly configured. Please install Git and restart the application.")
            return
            
        clone_window = ctk.CTkToplevel(self.window)
        clone_window.title("Clonar Repositório")
        # UI for 1920x1080
        clone_window.geometry("400x240")
        clone_window.transient(self.window)
        clone_window.grab_set()
        
        # Centralizar a janela
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 200) // 2
        clone_window.geometry(f"+{x}+{y}")
        
        # URL do repositório
        url_label = ctk.CTkLabel(clone_window, text="URL do Repositório:")
        url_label.pack(pady=5)
        
        url_entry = ctk.CTkEntry(clone_window, width=300)
        url_entry.pack(pady=5)
        
        # Diretório de destino
        path_label = ctk.CTkLabel(clone_window, text="Diretório de Destino:")
        path_label.pack(pady=5)
        
        path_frame = ctk.CTkFrame(clone_window)
        path_frame.pack(pady=5)
        
        path_entry = ctk.CTkEntry(path_frame, width=240)
        path_entry.pack(side="left", padx=5)
        
        def browse_path():
            path = filedialog.askdirectory()
            if path:
                path_entry.delete(0, "end")
                path_entry.insert(0, path)
        
        browse_button = ctk.CTkButton(path_frame, text="Browse", command=browse_path, width=50)
        browse_button.pack(side="left")
        
        def do_clone():
            url = url_entry.get().strip()
            path = path_entry.get().strip()
            
            if not url or not path:
                messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
                return
                
            try:
                git.Repo.clone_from(url, path)
                messagebox.showinfo("Sucesso", "Repositório clonado com sucesso!")
                clone_window.destroy()
                self.open_repository(path)
            except git.GitCommandError as e:
                messagebox.showerror("Erro", str(e))
        
        clone_button = ctk.CTkButton(clone_window, text="Clonar", command=do_clone)
        clone_button.pack(pady=20)

    def pull_changes(self):
        if git is None:
            messagebox.showerror("Error", "Git is not properly configured. Please install Git and restart the application.")
            return
            
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
            
        try:
            self.current_repo.git.pull()
            messagebox.showinfo("Sucesso", "Pull realizado com sucesso!")
            self.update_status()
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def push_changes(self):
        if git is None:
            messagebox.showerror("Error", "Git is not properly configured. Please install Git and restart the application.")
            return
            
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
            
        try:
            self.current_repo.git.push()
            messagebox.showinfo("Sucesso", "Push realizado com sucesso!")
            self.update_status()
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def show_commit_view(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
            
        commit_window = ctk.CTkToplevel(self.window)
        commit_window.title("Fazer Commit")
        commit_window.geometry("500x300")
        commit_window.transient(self.window)
        commit_window.grab_set()
        
        # Centralizar a janela
        x = self.window.winfo_x() + (self.window.winfo_width() - 500) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 300) // 2
        commit_window.geometry(f"+{x}+{y}")
        
        # Mensagem do commit
        msg_label = ctk.CTkLabel(commit_window, text="Mensagem do Commit:")
        msg_label.pack(pady=5)
        
        msg_text = ctk.CTkTextbox(commit_window, height=100)
        msg_text.pack(pady=5, padx=10, fill="x")
        
        def do_commit():
            message = msg_text.get("1.0", "end-1c").strip()
            if not message:
                messagebox.showerror("Erro", "Por favor, insira uma mensagem para o commit!")
                return
                
            try:
                self.current_repo.git.commit('-m', message)
                messagebox.showinfo("Sucesso", "Commit realizado com sucesso!")
                commit_window.destroy()
                self.update_status()
            except git.GitCommandError as e:
                messagebox.showerror("Erro", str(e))
        
        commit_button = ctk.CTkButton(commit_window, text="Commit", command=do_commit)
        commit_button.pack(pady=20)

    def show_branches(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
            
        # Criar janela de branches
        branch_window = ctk.CTkToplevel(self.window)
        branch_window.title("Gerenciar Branches")
        branch_window.geometry("500x600")
        branch_window.transient(self.window)  # Faz a janela ser modal
        branch_window.grab_set()  # Força foco na janela
        
        # Centralizar a janela
        x = self.window.winfo_x() + (self.window.winfo_width() - 500) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 600) // 2
        branch_window.geometry(f"+{x}+{y}")
        
        # Frame para criar novo branch
        create_frame = ctk.CTkFrame(branch_window)
        create_frame.pack(pady=10, padx=10, fill="x")
        
        new_branch_label = ctk.CTkLabel(create_frame, text="Novo Branch:", font=("Arial", 12, "bold"))
        new_branch_label.pack(side="left", padx=5)
        
        new_branch_entry = ctk.CTkEntry(create_frame, width=200)
        new_branch_entry.pack(side="left", padx=5)
        
        def create_branch():
            branch_name = new_branch_entry.get().strip()
            if not branch_name:
                messagebox.showerror("Erro", "Digite um nome para o branch!")
                return
                
            try:
                self.current_repo.git.branch(branch_name)
                messagebox.showinfo("Sucesso", f"Branch '{branch_name}' criado!")
                
                self.update_mini_console()
                self.update_branches_list(branches_frame)  # Atualiza a lista de branches
                new_branch_entry.delete(0, 'end')
            except git.GitCommandError as e:
                messagebox.showerror("Erro", str(e))
        
        create_btn = ctk.CTkButton(
            create_frame,
            text="Criar Branch",
            command=create_branch,
            width=100
        )
        create_btn.pack(side="left", padx=5)
        
        # Separador
        separator = ctk.CTkFrame(branch_window, height=2)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Lista de branches
        branches_label = ctk.CTkLabel(
            branch_window,
            text="Branches Existentes:",
            font=("Arial", 12, "bold")
        )
        branches_label.pack(pady=5)
        
        branches_frame = ctk.CTkScrollableFrame(branch_window)
        branches_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.update_branches_list(branches_frame)

    def update_branches_list(self, frame):
        # Limpar frame
        for widget in frame.winfo_children():
            widget.destroy()
            
        try:
            current_branch = self.current_repo.active_branch.name
            
            for branch in self.current_repo.heads:
                branch_frame = ctk.CTkFrame(frame)
                branch_frame.pack(fill="x", pady=2, padx=5)
                
                # Indicador de branch atual
                is_current = branch.name == current_branch
                name_text = f"➤ {branch.name}" if is_current else branch.name
                
                name_label = ctk.CTkLabel(
                    branch_frame,
                    text=name_text,
                    font=("Arial", 11, "bold") if is_current else ("Arial", 11)
                )
                name_label.pack(side="left", padx=5)
                
                if not is_current:
                    # Botão de checkout
                    checkout_btn = ctk.CTkButton(
                        branch_frame,
                        text="Checkout",
                        command=lambda b=branch: self.checkout_branch(b.name, frame),
                        width=80
                    )
                    checkout_btn.pack(side="right", padx=5)
                    
                    # Botão de deletar
                    delete_btn = ctk.CTkButton(
                        branch_frame,
                        text="Deletar",
                        command=lambda b=branch: self.delete_branch(b.name, frame),
                        width=80,
                        fg_color="darkred",
                        hover_color="#800000"
                    )
                    delete_btn.pack(side="right", padx=5)
        
        except git.GitCommandError as e:
            error_label = ctk.CTkLabel(frame, text=f"Erro: {str(e)}")
            error_label.pack(pady=10)

    def checkout_branch(self, branch_name, frame=None):
        try:
            self.current_repo.git.checkout(branch_name)
            messagebox.showinfo("Sucesso", f"Mudou para o branch '{branch_name}'")
            self.update_status()
            self.update_mini_console()
            if frame:
                self.update_branches_list(frame)
            
            # Verificar se tem upstream configurado
            branch = self.current_repo.active_branch
            if not branch.tracking_branch():
                self.show_upstream_button(branch_name)
            
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def show_upstream_button(self, branch_name):
        # Criar botão de upstream no frame de sync
        self.upstream_button = ctk.CTkButton(
            self.sync_frame,
            text="Configurar Upstream",
            command=lambda: self.setup_upstream(branch_name),
            fg_color="orange",
            hover_color="#c17702"
        )
        self.upstream_button.pack(side="right", padx=5)
        
        # Atualizar label de status
        self.branch_status_label.configure(
            text="⚠ Branch sem upstream configurado",
            text_color="orange"
        )

    def setup_upstream(self, branch_name):
        try:
            remote_name = "origin"
            self.current_repo.git.push('--set-upstream', remote_name, branch_name)
            messagebox.showinfo("Sucesso", "Upstream configurado com sucesso!")
            
            # Remover botão e atualizar status
            if hasattr(self, 'upstream_button'):
                self.upstream_button.pack_forget()
                
            self.update_branch_status()
            self.refresh()
            
        except git.GitCommandError as e:
            messagebox.showerror("Erro", f"Erro ao configurar upstream: {str(e)}")

    def delete_branch(self, branch_name, frame):
        if messagebox.askyesno("Confirmar", 
            f"Tem certeza que deseja deletar o branch '{branch_name}'?"):
            try:
                self.current_repo.git.branch('-D', branch_name)
                messagebox.showinfo("Sucesso", f"Branch '{branch_name}' deletado!")
                self.update_branches_list(frame)
                self.update_mini_console()
            except git.GitCommandError as e:
                messagebox.showerror("Erro", str(e))

    def check_branch_status(self):
        try:
            current = self.current_repo.active_branch  # Get the branch object directly
            upstream = current.tracking_branch()  # Get tracking branch from the branch object
            
            if not upstream:
                return False, "Branch não tem upstream configurado"
            
            # Fetch para atualizar referências remotas
            self.current_repo.remotes.origin.fetch()
            
            # Verifica commits ahead/behind
            commits_behind = len(list(self.current_repo.iter_commits(f'HEAD..{upstream.name}')))
            commits_ahead = len(list(self.current_repo.iter_commits(f'{upstream.name}..HEAD')))
            
            if commits_behind > 0 or commits_ahead > 0:
                return False, f"Branch desatualizada (ahead: {commits_ahead}, behind: {commits_behind})"
            return True, "Branch sincronizada"
            
        except git.GitCommandError as e:
            return False, f"Erro ao verificar status da branch: {str(e)}"
        except Exception as e:
            return False, str(e)

    def setup_branch_sync_frame(self):
        self.sync_frame = ctk.CTkFrame(self.tab_alteracoes)
        self.sync_frame.pack(fill="x", padx=10, pady=5)
        
        self.branch_status_label = ctk.CTkLabel(
            self.sync_frame,
            text="",
            font=("Arial", 12)
        )
        self.branch_status_label.pack(side="left", padx=5)
        
        self.sync_button = ctk.CTkButton(
            self.sync_frame,
            text="Sincronizar Branch",
            command=self.sync_branch,
            fg_color="orange",
            hover_color="#c17702"
        )
        # Não empacotamos o botão inicialmente - ele estará oculto
        # self.sync_button.pack(side="right", padx=5)

    def update_branch_status(self):
        if not self.current_repo:
            return
            
        is_synced, message = self.check_branch_status()
        
        if is_synced:
            self.branch_status_label.configure(text="✓ " + message, text_color="green")
            self.sync_button.pack_forget()  # Esconde o botão
        else:
            self.branch_status_label.configure(text="⚠ " + message, text_color="orange")
            # Mostra o botão apenas se ele não estiver já visível
            if not self.sync_button.winfo_ismapped():
                self.sync_button.pack(side="right", padx=5)

    def sync_branch(self):
        try:
            current = self.current_repo.active_branch
            upstream = current.tracking_branch()
            
            if not upstream:
                # Configura o upstream se não existir
                remote_name = "origin"
                self.current_repo.git.push('--set-upstream', remote_name, current.name)
                messagebox.showinfo("Sucesso", "Branch configurada com upstream!")
            else:
                # Tenta fazer pull primeiro
                try:
                    self.current_repo.git.pull()
                except git.GitCommandError as e:
                    if "conflict" in str(e).lower():
                        messagebox.showerror("Erro", "Conflitos detectados! Resolva os conflitos manualmente.")
                        return
                    
                # Se não houver conflitos, tenta push
                try:
                    self.current_repo.git.push()
                    messagebox.showinfo("Sucesso", "Branch sincronizada com sucesso!")
                except git.GitCommandError as e:
                    messagebox.showerror("Erro", f"Erro ao fazer push: {str(e)}")
                    return
                    
            self.update_branch_status()
            self.refresh()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao sincronizar: {str(e)}")

    def setup_config_tab(self):
        # Frame for theme selection
        theme_frame = ctk.CTkFrame(self.tab_config)
        theme_frame.pack(fill="x", pady=10, padx=10)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=("Arial", 12, "bold")
        )
        theme_label.pack(side="left", padx=5)
        
        # Get available themes
        themes_dir = os.path.join(os.path.dirname(__file__), "themes")
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        theme_files = [f[:-5] for f in os.listdir(themes_dir) if f.endswith('.json')]
        if not theme_files:
            # Create default theme if no themes exist
            default_theme = {
                "CTk": {
                    "fg_color": ["gray92", "gray14"]
                },
                "CTkFrame": {
                    "corner_radius": 6,
                    "border_width": 0,
                    "fg_color": ["gray86", "gray17"],
                    "top_fg_color": ["gray81", "gray20"],
                    "border_color": ["gray65", "gray28"]
                }
            }
            
            with open(os.path.join(themes_dir, "default.json"), "w") as f:
                json.dump(default_theme, f, indent=4)
            theme_files = ["default"]
        
    def load_theme(self, theme_name):
        try:
            theme_path = os.path.join(themes_dir, f"{theme_name}.json")
            with open(theme_path, "r") as f:
                theme_data = json.load(f)
            
            # Save theme selection to config
            self.current_theme = theme_name
            self.save_config()
            
            # Apply theme
            ctk.set_default_color_theme(theme_path)
            messagebox.showinfo("Success", f"Theme '{theme_name}' loaded!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load theme: {str(e)}")
            
            # Theme selector
            self.theme_option = ctk.CTkOptionMenu(
                theme_frame,
                values=theme_files,
                command=load_theme,
                width=200
            )
            self.theme_option.pack(side="left", padx=10)
        
        # Set initial theme selection to match current theme
        if hasattr(self, 'current_theme') and self.current_theme in theme_files:
            self.theme_option.set(self.current_theme)
        elif theme_files:
            self.theme_option.set(theme_files[0])
        
        # Button to refresh theme list
        refresh_btn = ctk.CTkButton(
            theme_frame,
            text="🔄",
            width=32,
            height=32,
            command=lambda: self.refresh_theme_list()
        )
        refresh_btn.pack(side="left", padx=5)

    def refresh_theme_list(self):
        themes_dir = os.path.join(os.path.dirname(__file__), "themes")
        theme_files = [f[:-5] for f in os.listdir(themes_dir) if f.endswith('.json')]
        
        self.theme_option.configure(values=theme_files)
        if theme_files:
            self.theme_option.set(theme_files[0])

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'default')
            else:
                self.current_theme = 'default'
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.current_theme = 'default'

    def save_config(self):
        try:
            config = {
                'theme': self.current_theme
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def show_git_error_message(self):
        """Show error message and instructions when Git is not properly configured"""
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Git Configuration Error")
        error_window.geometry("600x400")
        error_window.transient(self.window)
        error_window.grab_set()
        
        # Center the error window
        x = self.window.winfo_x() + (self.window.winfo_width() - 600) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 400) // 2
        error_window.geometry(f"+{x}+{y}")
        
        # Error message
        msg_frame = ctk.CTkFrame(error_window)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            msg_frame,
            text="Git Configuration Required",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        error_text = ctk.CTkTextbox(msg_frame, height=200)
        error_text.pack(fill="both", padx=10, pady=10)
        error_text.insert("1.0", 
            "Git executable not found. Please ensure Git is:\n\n"
            "1. Installed on your system\n"
            "2. Added to your system's PATH environment variable\n\n"
            "To fix this:\n"
            "1. Download and install Git from https://git-scm.com/downloads\n"
            "2. During installation, choose 'Add to PATH' option\n"
            "3. Restart your computer\n"
            "4. Restart this application\n\n"
            f"Technical details:\n{GIT_IMPORT_ERROR}"
        )
        error_text.configure(state="disabled")
        
        def open_git_download():
            import webbrowser
            webbrowser.open("https://git-scm.com/downloads")
        
        download_btn = ctk.CTkButton(
            msg_frame,
            text="Download Git",
            command=open_git_download
        )
        download_btn.pack(pady=10)
        
        quit_btn = ctk.CTkButton(
            msg_frame,
            text="Quit Application",
            command=self.window.quit
        )
        quit_btn.pack(pady=10)

    def setup_branches_tab(self):
        # Frame for branch operations
        branch_frame = ctk.CTkFrame(self.tab_branches)
        branch_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Branch list with title
        title_label = ctk.CTkLabel(
            branch_frame,
            text="BRANCHES",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(5,10), anchor="w")
        
        # Branch list with scrollbar
        list_frame = ctk.CTkFrame(branch_frame)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        self.branch_listbox = ctk.CTkTextbox(
            list_frame,
            height=300,
            font=("Consolas", 12)
        )
        self.branch_listbox.pack(fill="both", expand=True, side="left")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(branch_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        # Branch operations buttons
        buttons = [
            ("🔄 Fetch", self.fetch_changes),
            ("🔀 Merge", self.merge_branch),
            ("⬇️ Pull", self.pull_changes),
            ("⬆️ Push", self.push_changes),
            ("➕ New Branch", self.create_new_branch)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=120,
                height=32
            )
            btn.pack(side="left", padx=5)
        
        # Initial update
        self.update_branch_list()

    def create_new_branch(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
        
        # Create branch dialog
        branch_window = ctk.CTkToplevel(self.window)
        branch_window.title("Create New Branch")
        branch_window.geometry("400x200")
        branch_window.transient(self.window)
        branch_window.grab_set()
        
        # Center window
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 200) // 2
        branch_window.geometry(f"+{x}+{y}")
        
        # Branch name input
        name_label = ctk.CTkLabel(branch_window, text="New Branch Name:")
        name_label.pack(pady=10)
        
        name_entry = ctk.CTkEntry(branch_window, width=200)
        name_entry.pack(pady=10)
        
        # Checkbox for checkout
        checkout_var = ctk.BooleanVar(value=True)
        checkout_check = ctk.CTkCheckBox(
            branch_window,
            text="Checkout new branch",
            variable=checkout_var
        )
        checkout_check.pack(pady=10)
        
        def do_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a branch name")
                return
            
            try:
                # Create new branch
                new_branch = self.current_repo.create_head(name)
                
                # Checkout if requested
                if checkout_var.get():
                    new_branch.checkout()
                
                messagebox.showinfo("Success", f"Branch '{name}' created successfully!")
                branch_window.destroy()
                self.refresh()
                
            except git.GitCommandError as e:
                messagebox.showerror("Error", str(e))
        
        create_button = ctk.CTkButton(
            branch_window,
            text="Create Branch",
            command=do_create
        )
        create_button.pack(pady=20)

    def update_branch_list(self):
        if not self.current_repo:
            return
        
        try:
            self.branch_listbox.configure(state="normal")
            self.branch_listbox.delete("1.0", "end")
            
            current = self.current_repo.active_branch.name
            
            # Add local branches
            self.branch_listbox.insert("end", "📁 Local Branches:\n", "header")
            for branch in self.current_repo.heads:
                prefix = "➤ " if branch.name == current else "  "
                self.branch_listbox.insert("end", f"{prefix}{branch.name}\n")
            
            # Add remote branches
            self.branch_listbox.insert("end", "\n🌐 Remote Branches:\n", "header")
            for ref in self.current_repo.remote().refs:
                name = ref.name.split('/', 1)[1]  # Remove 'origin/' prefix
                self.branch_listbox.insert("end", f"  {name}\n")
            
            # Configure tags for styling
            self.branch_listbox.tag_config("header", foreground="#00ff00")
            
            self.branch_listbox.configure(state="disabled")
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))
        except AttributeError:
            # No remote configured
            pass

    def fetch_changes(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
        
        try:
            self.current_repo.git.fetch()
            messagebox.showinfo("Sucesso", "Alterações buscadas com sucesso.")
            self.refresh()
        except git.GitCommandError as e:
            messagebox.showerror("Erro", str(e))

    def merge_branch(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum repositório aberto!")
            return
        
        # Create merge dialog
        merge_window = ctk.CTkToplevel(self.window)
        merge_window.title("Merge Branch")
        merge_window.geometry("400x250")
        merge_window.transient(self.window)
        merge_window.grab_set()
        
        # Center window
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 250) // 2
        merge_window.geometry(f"+{x}+{y}")
        
        # Branch selection
        branch_label = ctk.CTkLabel(
            merge_window,
            text="Select branch to merge:",
            font=("Arial", 12, "bold")
        )
        branch_label.pack(pady=10)
        
        # Get list of branches (both local and remote)
        local_branches = [b.name for b in self.current_repo.heads 
                         if b.name != self.current_repo.active_branch.name]
        remote_branches = []
        try:
            remote_branches = [
                ref.name for ref in self.current_repo.remote().refs
                if not ref.name.endswith('/HEAD')
            ]
        except (git.GitCommandError, AttributeError):
            pass
        
        all_branches = local_branches + remote_branches
        
        if not all_branches:
            messagebox.showinfo("Info", "No other branches available for merge")
            merge_window.destroy()
            return
        
        branch_var = ctk.StringVar(value=all_branches[0])
        branch_menu = ctk.CTkOptionMenu(
            merge_window,
            values=all_branches,
            variable=branch_var,
            width=250
        )
        branch_menu.pack(pady=10)
        
        # Merge options
        options_frame = ctk.CTkFrame(merge_window)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ff_var = ctk.BooleanVar(value=True)
        ff_check = ctk.CTkCheckBox(
            options_frame,
            text="Fast-forward if possible",
            variable=ff_var
        )
        ff_check.pack(pady=5)
        
        squash_var = ctk.BooleanVar(value=False)
        squash_check = ctk.CTkCheckBox(
            options_frame,
            text="Squash merge",
            variable=squash_var
        )
        squash_check.pack(pady=5)
        
        def do_merge():
            try:
                target_branch = branch_var.get()
                
                # Build merge command options
                merge_args = []
                if not ff_var.get():
                    merge_args.append('--no-ff')
                if squash_var.get():
                    merge_args.append('--squash')
                
                # Perform merge
                self.current_repo.git.merge(target_branch, *merge_args)
                
                messagebox.showinfo("Success", f"Branch '{target_branch}' merged successfully!")
                merge_window.destroy()
                self.refresh()
                
            except git.GitCommandError as e:
                if "CONFLICT" in str(e):
                    messagebox.showerror(
                        "Error",
                        "Merge conflicts detected! Please resolve conflicts manually."
                    )
                else:
                    messagebox.showerror("Error", str(e))
        
        merge_button = ctk.CTkButton(
            merge_window,
            text="Merge",
            command=do_merge,
            width=200
        )
        merge_button.pack(pady=20)

    def update_estatisticas(self):
        if not self.current_repo:
            return
        
        try:
            period = self.period_combobox.get()
            since_arg = None
            
            if period == "Última semana":
                since_arg = "--since='1 week ago'"
            elif period == "Último mês":
                since_arg = "--since='1 month ago'"
            elif period == "Último ano":
                since_arg = "--since='1 year ago'"
            
            stats = {}
            
            log_args = ['--pretty=format:%H']
            if since_arg:
                log_args.append(since_arg)
            
            commit_count = len(self.current_repo.git.log(*log_args).split('\n'))
            stats["Total de commits:"] = str(commit_count)
            
            authors = set()
            for commit in self.current_repo.iter_commits():
                authors.add(f"{commit.author.name} <{commit.author.email}>")
            stats["Contribuidores:"] = str(len(authors))
            
            diff_args = ['--shortstat']
            if since_arg:
                diff_args.append(since_arg)
            
            try:
                diff_stats = self.current_repo.git.diff(*diff_args)
                
                files_changed = "0"
                insertions = "0"
                deletions = "0"
                
                if diff_stats:
                    parts = diff_stats.strip().split(', ')
                    for part in parts:
                        if 'files changed' in part:
                            files_changed = part.split()[0]
                        elif 'insertions' in part:
                            insertions = part.split()[0]
                        elif 'deletions' in part:
                            deletions = part.split()[0]
                
                stats["Arquivos alterados:"] = files_changed
                stats["Linhas adicionadas:"] = insertions
                stats["Linhas removidas:"] = deletions
                
            except git.GitCommandError as e:
                messagebox.showerror("Erro", f"Falha ao obter estatísticas de diferenças: {str(e)}")
                stats["Arquivos alterados:"] = "N/A"
                stats["Linhas adicionadas:"] = "N/A"
                stats["Linhas removidas:"] = "N/A"
            
            for widget in self.tab_estatisticas.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            label_text = child.cget("text")
                            if label_text in stats:
                                child.configure(text=stats[label_text])
        
        except git.GitCommandError as e:
            messagebox.showerror("Erro", f"Falha ao atualizar estatísticas: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao atualizar estatísticas: {str(e)}")

    def refresh(self):
        """Refresh all UI components"""
        if not self.current_repo:
            return
        
        try:
            self.update_status()
            self.update_historico()
            self.update_estatisticas()
            self.update_mini_console()
            self.update_file_list()
            self.update_branch_status()
            self.update_branch_list()
        except git.GitCommandError as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = GitManager()
    app.run() 
