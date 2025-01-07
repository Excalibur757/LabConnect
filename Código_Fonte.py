import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import Calendar
import sqlite3
import datetime

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.master.geometry("350x200")
        # Adicionando cor azul ao fundo
        self.master.configure(bg="blue")

        self.username_label = tk.Label(self.master, text="Usuário:", bg="blue", fg="white")  # Configurando cor do texto e do fundo
        self.username_label.pack()

        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Senha:", bg="blue", fg="white")  # Configurando cor do texto e do fundo
        self.password_label.pack()

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.master, text="Login", command=self.check_login, bg="blue", fg="white")  # Configurando cor do texto e do fundo
        self.login_button.pack(padx=10, pady=10)

        self.login_button = tk.Button(self.master, text="Sair", command=self.sair, bg="blue", fg="white")
        self.login_button.pack(padx=10, pady=10)

        # Conectar ao banco de dados e criar a tabela de usuários se não existir
        self.conn = sqlite3.connect('login_database.db')
        self.create_table()

        #Lista dos professores que seriam cadastrados no código (Apenas Exemplos para melhor entendimento)
        self.add_user("12345", "admin", "Carlos", "Development with Python")
        self.add_user("54321", "admin", "Alberto", "Mathematical Logical")
        self.add_user("01020", "admin", "Marcos", "Linguagem e Comunicação")
        self.add_user("22865", "admin", "André", "Computer Network")

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, username TEXT, password TEXT, professor TEXT, disciplina TEXT)''')
        self.conn.commit()

    def sair(self):
        self.master.destroy()

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:  # Verifica se ambos os campos foram preenchidos
            messagebox.showerror("Falha na autenticação", "Por favor, preencha ambos os campos.")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

            if user:
                self.open_menu()
            else:
                messagebox.showerror("Falha na autenticação", "Usuário ou senha inválida. Tente novamente!")
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro: {e}")

    def open_menu(self):
        self.master.withdraw()  # Esconder a janela de login
        root = tk.Toplevel()
        username = self.username_entry.get()  # Obter o valor do nome de usuário
        password = self.password_entry.get()  # Obter o valor da senha
        app = MenuApp(root, self.conn, username, password)  # Passar os valores de usuário e senha
        root.protocol("WM_DELETE_WINDOW", self.on_menu_close)  # Definir a ação de fechar a janela.
        root.mainloop()

    def on_menu_close(self):
        self.master.destroy()  # Destruir a janela principal ao fechar a janela de menu

    def add_user(self, username, password, professor, disciplina):
        # Para criar um novo usuário e senha, criei esse objeto
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, professor, disciplina) VALUES (?, ?, ?, ?)",
                           (username, password, professor, disciplina))
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro: {e}")

    def close_connection(self):
        self.conn.close()


class MenuApp:
    def __init__(self, master, conn, username, password):
        self.master = master
        self.conn = conn
        self.master.title("Menu")
        self.master.geometry("400x200")
        self.master.configure(bg='light blue')
        self.username = username
        self.password = password
        cursor = self.conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                           (username, password))
            user = cursor.fetchone()
            self.conn.commit()

            self.texto = ttk.Label(self.master, text=f"Bem-vindo Professor: {user[3]}    Disciplina: {user[4]}")
            self.texto.pack(padx=5, pady=5)
            style = ttk.Style()
            style.configure('BemVindo.TLabel', foreground='black',
                            background='light blue')  # Configurar cor do texto e remover o fundo
            self.texto.configure(style='BemVindo.TLabel')  # Aplicar o estilo ao texto



        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro: {e}")

        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), padding=10, background='light green')

        self.schedule_button = tk.Button(self.master, text="Agendar Laboratório", command=self.schedule_lab)
        self.schedule_button.pack(padx=5, pady=5)

        self.view_button = tk.Button(self.master, text="Visualizar Agendamentos", command=self.view_schedule)
        self.view_button.pack(padx=5, pady=5)

        self.quit_button = tk.Button(self.master, text="Sair", command=self.quit_app)
        self.quit_button.pack(padx=5, pady=5)

    def schedule_lab(self):
        self.master.withdraw()  # Esconder a janela de menu
        agendamento = Agendamento(self.master, self.conn)  # Passar o root e a conexão como parâmetros
        self.master.protocol("WM_DELETE_WINDOW", self.on_schedule_close)  # Definir a ação de fechar a janela
        agendamento.mainloop()

    def on_schedule_close(self):
        self.master.destroy()  # Destruir a janela de agendamento ao fechar

    def view_schedule(self):
        # Criar uma nova janela para exibir os agendamentos
        view_window = tk.Toplevel(self.master)
        view_window.title("Agendamentos")
        view_window.configure(bg='white')  # Cor de fundo para a janela de agendamentos

        # Recuperar os agendamentos do banco de dados
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reserva")
        agendamentos = cursor.fetchall()

        # Scrollbar para a lista de agendamentos
        scrollbar = tk.Scrollbar(view_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Exibir os agendamentos
        listbox = tk.Listbox(view_window, yscrollcommand=scrollbar.set, width=50, height=15)
        for agendamento in agendamentos:
            display_text = f"Data: {agendamento[1]}, Início: {agendamento[2]}, Fim: {agendamento[3]}, Lab: {agendamento[4]}"
            listbox.insert(tk.END, display_text)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.config(command=listbox.yview)

        # Obter a posição da janela principal
        x_root = self.master.winfo_rootx()
        y_root = self.master.winfo_rooty()
        width = self.master.winfo_width()

        # Definir a posição da nova janela ao lado da janela principal
        view_window.geometry(f"+{x_root + width + 10}+{y_root}")

    def quit_app(self):
        self.master.destroy()

class Agendamento(tk.Toplevel):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        self.title("Agendamento")
        self.geometry("500x500")
        self.configure(bg='light blue')  # Definir cor de fundo

        self.texto = ttk.Label(self, text="Por favor, escolha uma data")
        self.texto.pack(padx=5, pady=5)
        style = ttk.Style()
        style.configure('BemVindo.TLabel', foreground='black',
                        background='light blue')  # Configurar cor do texto e remover o fundo
        self.texto.configure(style='BemVindo.TLabel')  # Aplicar o estilo ao texto

        self.cal = Calendar(self, selectmode="day", date_pattern="dd/mm/yyyy")
        self.cal.pack(padx=50, pady=20)

        self.btn_selecionar_data = ttk.Button(self, text="Selecionar Data", command=self.selecionar_data)
        self.btn_selecionar_data.pack(pady=10)

        self.btn_voltar = ttk.Button(self, text="Voltar", command=self.voltar)
        self.btn_voltar.pack(pady=10)

    def voltar(self):
        self.destroy()
        self.master.deiconify()

    def selecionar_data(self):
        data_selecionada = self.cal.get_date()
        data_selecionada_dt = datetime.datetime.strptime(data_selecionada, "%d/%m/%Y").date()
        data_atual = datetime.datetime.now().date()

        if data_selecionada_dt < data_atual:
            messagebox.showwarning("Aviso", "Não é possível selecionar uma data anterior à data atual.")
            return

        self.criar_janela_horario(data_selecionada)

    def criar_janela_horario(self, data):
        self.janela_horario = tk.Toplevel(self)
        self.janela_horario.title("Selecionar Horário")

        ttk.Label(self.janela_horario, text="Data Escolhida:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.janela_horario, text=data).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.janela_horario, text="Horário Inicial:").grid(row=1, column=0, padx=5, pady=5)
        self.entrada_inicio = ttk.Entry(self.janela_horario)
        self.entrada_inicio.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.janela_horario, text="Horário Final:").grid(row=2, column=0, padx=5, pady=5)
        self.entrada_fim = ttk.Entry(self.janela_horario)
        self.entrada_fim.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.janela_horario, text="Confirmar", command=self.validar_horario).grid(row=3, column=0,
                                                                                             columnspan=2, padx=5,
                                                                                             pady=5)

        ttk.Button(self.janela_horario, text="Cancelar", command=self.janela_horario.destroy).grid(row=4, column=0,
                                                                                                   columnspan=2, padx=5,
                                                                                                   pady=5)
    def validar_horario(self):
        inicio = self.entrada_inicio.get()
        fim = self.entrada_fim.get()

        # Verificar se os horários estão no formato correto (HH:MM)
        if not self.verificar_formato_horario(inicio) or not self.verificar_formato_horario(fim):
            messagebox.showwarning("Aviso", "Por favor, digite os horários no formato correto (HH:MM).")
            return

        # Verificar se o horário final é maior que o horário inicial
        if self.calcular_minutos(inicio) >= self.calcular_minutos(fim):
            messagebox.showwarning("Aviso", "O horário final deve ser maior que o horário inicial.")
            return

        # Verificar se a diferença entre o horário inicial e final é menor ou igual a 4 horas
        if self.calcular_diferenca_horas(inicio, fim) > 4:
            messagebox.showwarning("Aviso", "O intervalo de reserva não pode ser superior a 4 horas.")
            return

        # Verificar se a data e hora inicial são posteriores à data e hora atuais
        data_selecionada = self.cal.get_date()
        data_selecionada_dt = datetime.datetime.strptime(data_selecionada, "%d/%m/%Y")
        data_hora_inicio = datetime.datetime.combine(data_selecionada_dt,
                                                     datetime.datetime.strptime(inicio, "%H:%M").time())
        data_hora_atual = datetime.datetime.now()

        if data_hora_inicio < data_hora_atual:
            messagebox.showwarning("Aviso", "O horário inicial não pode ser anterior ao horário atual.")
            return

        self.confirmar_horario()
        self.janela_horario.destroy()

    def verificar_formato_horario(self, horario):
        try:
            if datetime.datetime.strptime(horario, "%H:%M"):
                return True
        except ValueError:
            return False

    def calcular_minutos(self, horario):
        horas, minutos = map(int, horario.split(':'))
        return horas * 60 + minutos

    def calcular_diferenca_horas(self, inicio, fim):
        return (self.calcular_minutos(fim) - self.calcular_minutos(inicio)) / 60

    def confirmar_horario(self):
        data = self.cal.get_date()
        inicio = self.entrada_inicio.get()
        fim = self.entrada_fim.get()
        self.cal.destroy()
        self.btn_selecionar_data.destroy()
        self.texto.destroy()
        SelecaoLaboratorioApp(self, data, inicio, fim)


class SelecaoLaboratorioApp:
    def __init__(self, root, data, inicio, fim):
        self.root = root
        self.root.title("Seleção de Laboratório")
        self.data = data
        self.inicio = inicio
        self.fim = fim
        self.confirme = None

        # Definir estilo para os textos
        style = ttk.Style()
        style.configure('BemVindo.TLabel', foreground='black')  # Remover a configuração do fundo

        self.label_instrucao = ttk.Label(root, text="Por favor, escolha o laboratório desejado:")
        self.label_instrucao.pack()
        self.label_instrucao.configure(style='BemVindo.TLabel')

        self.frame_botoes = tk.Frame(root)
        self.frame_botoes.pack()

        self.num_cols = 4
        self.botoes_laboratorios = []
        for i in range(0, len(laboratorios), self.num_cols):
            row_frame = tk.Frame(self.frame_botoes)
            row_frame.pack(side=tk.TOP)
            for lab in laboratorios[i:i + self.num_cols]:
                botao_lab = tk.Button(row_frame, text=lab, command=lambda l=lab: self.selecionar_laboratorio(l))
                botao_lab.pack(side=tk.LEFT)
                self.botoes_laboratorios.append(botao_lab)

        self.label_resultado = tk.Label(root, text="")
        self.label_resultado.pack()

        self.confirmar_botao = tk.Button(root, text="Confirmar", command=self.confirmacao)
        self.cancelar_botao = tk.Button(root, text="Cancelar", command=self.cancelar_selecao)

        self.create_table()

    def create_table(self):
        cursor = self.root.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reserva
                              (id INTEGER PRIMARY KEY, data TEXT, horario_inicio TEXT, horario_fim TEXT, laboratorio TEXT)''')
        self.root.conn.commit()

    def add_lab(self, data, inicio, fim, laboratorio_escolhido):
        cursor = self.root.conn.cursor()
        cursor.execute("INSERT INTO reserva (data, horario_inicio, horario_fim, laboratorio) VALUES (?, ?, ?, ?)",
                       (data, inicio, fim, laboratorio_escolhido))
        self.root.conn.commit()

    def selecionar_laboratorio(self, lab):
        escolha_usuario = lab.split('.')[0].strip()
        self.laboratorio_escolhido = laboratorios[int(escolha_usuario) - 1]
        self.label_resultado.config(text="Laboratório selecionado: " + self.laboratorio_escolhido)
        laboratorio = self.laboratorio_escolhido
        self.confirmar_botao.pack()
        self.cancelar_botao.pack()
        for button in self.botoes_laboratorios:
            button.config(state=tk.DISABLED)

    def cancelar_selecao(self):
        self.label_resultado.config(text="")
        self.confirmar_botao.pack_forget()
        self.cancelar_botao.pack_forget()
        for button in self.botoes_laboratorios:
            button.config(state=tk.NORMAL)

    def verificar_conflito_horario(self):
        cursor = self.root.conn.cursor()
        cursor.execute(
            "SELECT * FROM reserva WHERE laboratorio=? AND data=? AND ((? >= horario_inicio AND ? <= horario_fim) OR (? <= horario_inicio AND ? >= horario_fim))",
            (self.laboratorio_escolhido, self.data, self.inicio, self.inicio, self.fim, self.fim))
        conflitos = cursor.fetchall()
        return len(conflitos) > 0

    def confirmacao(self):
        if self.verificar_conflito_horario():
            messagebox.showerror("Erro", "O horário selecionado está ocupado. Por favor, escolha outro horário.")
            return
        else:
            self.root.destroy()
            self.confirme = tk.Toplevel()
            self.confirme.title("Confirmação") # Aqui é a janela onde tudo que o usuário selecionou retornará na tela

        ttk.Label(self.confirme, text="Data Escolhida:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.confirme, text=self.data).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.confirme, text="Horário Inicial:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(self.confirme, text=self.inicio).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.confirme, text="Horário Final:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(self.confirme, text=self.fim).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.confirme, text="Laboratório: ").grid(row=3, column=0, padx=5, pady=5)
        ttk.Label(self.confirme, text=self.laboratorio_escolhido).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.confirme, text="Confirmar", command=self.avancar).grid(row=4, column=0, columnspan=2, padx=5,
                                                                               pady=5)
        ttk.Button(self.confirme, text="Cancelar", command=self.cancelar).grid(row=5, column=0, columnspan=2, padx=5,
                                                                               pady=5)

    def avancar(self):
        self.add_lab(self.data, self.inicio, self.fim, self.laboratorio_escolhido)
        messagebox.showinfo("Êxito", "Agendamento feito com sucesso!")
        self.confirme.destroy()
        self.root.master.deiconify()  # Mostra a janela de menu novamente

    def cancelar(self):
        self.confirme.destroy()
        self.root.destroy()  # Fecha a janela atual
        self.root.master.deiconify()  # Mostra a janela de menu novamente

laboratorios = [
    '1. Lab I',
    '2. Lab II',
    '3. Lab III',
    '4. Lab IV',
    '5. Lab V',
    '6. Lab VI',
    '7. Lab VII',
    '8. Lab VIII'
]
def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)  # Chamando o método close_connection() quando a janela é fechada
    root.mainloop()

if __name__ == "__main__":
    main()