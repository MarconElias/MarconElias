import sqlite3
import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk


# Classe para manipular o banco de dados
class BancoDeDados:
    def __init__(self, banco_dados):
        self.conn = sqlite3.connect(banco_dados)
        self.cursor = self.conn.cursor()
        self.criar_tabela()

    def criar_tabela(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estadias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                sobrenome TEXT,
                cor_bicicleta TEXT,
                box INTEGER,
                horario_entrada DATETIME,
                horario_saida DATETIME
            )
        ''')
        self.conn.commit()

    # Função para adicionar cliente no banco de dados
    def adicionar_cliente(self, nome, sobrenome, cor_bicicleta, box, horario_entrada):
        self.cursor.execute('''
            INSERT INTO estadias (nome, sobrenome, cor_bicicleta, box, horario_entrada, horario_saida)
            VALUES (?, ?, ?, ?, ?, NULL)
        ''', (nome, sobrenome, cor_bicicleta, box, horario_entrada))
        self.conn.commit()

    # Função para buscar as entradas de um cliente no banco de dados
    def buscar_todas_entradas_cliente(self, nome, sobrenome):
        self.cursor.execute('''
            SELECT * FROM estadias WHERE nome = ? COLLATE NOCASE AND sobrenome = ? COLLATE NOCASE
        ''', (nome, sobrenome))
        return self.cursor.fetchall()

    # Função para buscar cliente pelo ID (para que seja possível registrar saída pendente)
    def buscar_cliente_por_id(self, id_cliente):
        self.cursor.execute('SELECT * FROM estadias WHERE id = ?', (id_cliente,))
        return self.cursor.fetchone()

    # Função para registrar saída de um cliente no banco de dados
    def registrar_saida_cliente_por_id(self, id_cliente):
        horario_saida = datetime.now().strftime('%d-%m-%Y %H:%M')
        self.cursor.execute('''
            UPDATE estadias SET horario_saida = ? WHERE id = ? AND horario_saida IS NULL
        ''', (horario_saida, id_cliente))
        self.conn.commit()

    # Função para listar estadias dos clientes
    def listar_clientes(self):
        self.cursor.execute('SELECT * FROM estadias')
        return self.cursor.fetchall()

    # Função para exportar e limpar o banco de dados
    def exportar_e_limpar(self, senha):
        senha_correta = "Bicicletable1.5"
        if senha == senha_correta:
            try:
                diretorio = os.path.dirname(os.path.abspath(__file__))
                pasta_exportacao = os.path.join(diretorio, 'exportbkp')
                os.makedirs(pasta_exportacao, exist_ok=True)
                nome_arquivo_export = os.path.join(pasta_exportacao,
                                                   f"bicicletario_export_{datetime.now().strftime('%d%m%Y')}.db")
                with open(nome_arquivo_export, 'wb') as f:
                    for linha in self.conn.iterdump():
                        f.write(f'{linha}\n'.encode('utf-8'))
                self.cursor.execute('DELETE FROM estadias')
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Banco de dados exportado e limpo com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar e limpar o banco de dados: {e}")
        else:
            messagebox.showwarning("Acesso Negado", "Você não tem permissão para esta ação.")

    def fechar_conexao(self):
        self.conn.close()


# Classe principal do aplicativo
class AppBicicletario:
    def __init__(self, rootapp):
        self.bd = BancoDeDados('bicicletario.db')
        self.root = rootapp
        self.interface_grafica()
        self.elementos_interface()

    def interface_grafica(self):
        self.root.title("Bicicletable App")
        self.root.configure(bg='#004d00', borderwidth=10, relief="ridge")
        self.root.geometry("600x710")

        # Carregar a imagem
        def obter_caminho_imagem():
            if getattr(sys, 'frozen', False):
                return os.path.join(sys._MEIPASS, 'logopcn.png')
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logopcn.png')

        caminho_imagem = obter_caminho_imagem()

        if os.path.isfile(caminho_imagem):
            try:
                imagem_cabecalho = Image.open(caminho_imagem)
                imagem_cabecalho = imagem_cabecalho.resize((350, 75))
                self.imagem_cabecalho = ImageTk.PhotoImage(imagem_cabecalho)
            except Exception as e:
                print(f"Um erro inesperado ocorreu ao abrir a imagem: {e}")
        else:
            print(f"Arquivo não encontrado: {caminho_imagem}")

    def elementos_interface(self):

        # Configurações de responsividade e padronização de fonte
        self.root.columnconfigure(1, weight=1)
        fonte_grande = ('Helvetica', 11)

        # Elementos da interface
        label_imagem = tk.Label(self.root, image=self.imagem_cabecalho, bg='#e6e8e6')
        label_imagem.photo = self.imagem_cabecalho
        label_imagem.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Campos de entrada de cliente
        self.entry_nome = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')
        self.entry_sobrenome = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')
        self.entry_cor_bicicleta = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')
        self.entry_box = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')

        # Botão e labels para o layout de entrada de cliente
        tk.Label(self.root, text="Nome", font=fonte_grande, bg='#004d00',
                 fg='white', justify='left').grid(row=1, column=0, padx=10, pady=2)
        self.entry_nome.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Label(self.root, text="Sobrenome", font=fonte_grande, bg='#004d00',
                 fg='white', justify='left').grid(row=2, column=0, padx=10, pady=2)
        self.entry_sobrenome.grid(row=2, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Label(self.root, text="Cor da Bicicleta", font=fonte_grande, bg='#004d00', fg='white', justify='left').grid(
            row=3, column=0, padx=10, pady=2)
        self.entry_cor_bicicleta.grid(row=3, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Label(self.root, text="Número do Box", font=fonte_grande, bg='#004d00',
                 fg='white', justify='left').grid(row=4, column=0, padx=10, pady=2)
        self.entry_box.grid(row=4, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Button(self.root, text="Adicionar Cliente", command=self.adicionar_cliente, font=fonte_grande, bg='#cdd1cd',
                  fg='black', borderwidth=5, relief="raised").grid(row=5, column=0, columnspan=3, pady=5, padx=5,
                                                                   sticky="ew")

        # Botão e labels para o layout de busca de cliente
        self.entry_nome_busca = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')
        self.entry_sobrenome_busca = tk.Entry(self.root, font=fonte_grande, bg='#e6e8e6')
        tk.Label(self.root, text="Nome", font=fonte_grande, bg='#004d00',
                 fg='white').grid(row=6, column=0, padx=10, pady=2)
        self.entry_nome_busca.grid(row=6, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Label(self.root, text="Sobrenome", font=fonte_grande, bg='#004d00', fg='white').grid(row=7, column=0,
                                                                                                padx=10, pady=2)
        self.entry_sobrenome_busca.grid(row=7, column=1, columnspan=2, sticky="ew", padx=10, pady=2)

        tk.Button(self.root, text="Buscar Cliente", command=self.buscar_cliente, font=fonte_grande, bg='#cdd1cd',
                  fg='black', borderwidth=5, relief="raised").grid(row=8, column=0, columnspan=2, pady=5,
                                                                   padx=10, sticky="ew")

        # Tabela para listar clientes
        estilo = ttk.Style()
        estilo.configure("Treeview.Heading", font=('Helvetica', 9, 'bold'))
        colunas = ("Nome", "Sobrenome", "Cor da Bicicleta", "Box", "Horário Entrada", "Horário Saída")
        self.treeview_clientes = ttk.Treeview(self.root, columns=colunas, show='headings', height=6)
        larguras = {
            "Nome": 50,
            "Sobrenome": 50,
            "Cor da Bicicleta": 100,
            "Box": 25,
            "Horário Entrada": 100,
            "Horário Saída": 100
        }
        for coluna in colunas:
            self.treeview_clientes.heading(coluna, text=coluna)
            self.treeview_clientes.column(coluna, width=larguras[coluna], anchor='center')
        self.treeview_clientes.grid(row=9, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

        # Botões e labels para listar clientes e listar clientes por data
        tk.Button(self.root, text="Listar Clientes", command=self.listar_clientes, font=fonte_grande, bg='#cdd1cd',
                  fg='black', borderwidth=5, relief="raised").grid(row=10, column=0, columnspan=2, pady=5, padx=10,
                                                                   sticky="ew")
        tk.Label(self.root, text="Selecione para Listar por Data", font=fonte_grande,
                 bg='#004d00', fg='white').grid(row=11, column=0)
        self.cal_data = DateEntry(self.root, width=12, background='darkgreen', foreground='white', borderwidth=2,
                                  locale='pt_br', font=fonte_grande)
        self.cal_data.grid(row=11, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        tk.Button(self.root, text="Listar Clientes por Data", command=self.listar_clientes_por_data, font=fonte_grande,
                  bg='#cdd1cd', fg='black', borderwidth=5, relief="raised").grid(row=12, column=0, columnspan=2, pady=5,
                                                                                 padx=10, sticky="ew")
        # Botão para limpar lista
        tk.Button(self.root, text="Limpar Lista de Clientes", command=self.limpar_lista_clientes, font=fonte_grande,
                  bg='#cdd1cd', fg='black', borderwidth=5, relief="raised").grid(row=13, column=0, columnspan=2, pady=2,
                                                                                 padx=10, sticky="ew")

        # Botão para abrir as ferramentas administrativas
        tk.Button(self.root, text="Ferramentas Administrativas", font=('Helvetica', 8), bg='#cdd1cd', fg='black',
                  command=self.abrir_ferramentas_administrativas).grid(row=14, column=0, columnspan=2, pady=5, padx=10)
        tk.Label(self.root, text="v1.5", font=('Helvetica', 8), bg='#004d00', fg='#cdd1cd').grid(row=14, column=1,
                                                                                                 sticky='e')

    # Função para adicionar cliente
    def adicionar_cliente(self):
        nome = self.entry_nome.get()
        sobrenome = self.entry_sobrenome.get()
        cor_bicicleta = self.entry_cor_bicicleta.get()
        try:
            box = int(self.entry_box.get())
        except ValueError:
            messagebox.showwarning("Entrada Inválida", "Número do box deve ser um número inteiro.")
            return
        horario_entrada = datetime.now().strftime('%d-%m-%Y %H:%M')

        if not nome or not sobrenome or not cor_bicicleta or not box:
            messagebox.showwarning("Entrada Inválida", "Todos os campos devem ser preenchidos.")
            return

        self.bd.adicionar_cliente(nome, sobrenome, cor_bicicleta, box, horario_entrada)
        messagebox.showinfo("Sucesso", f"Cliente {nome} {sobrenome} adicionado ao Box {box} com sucesso!")
        self.entry_nome.delete(0, tk.END)
        self.entry_sobrenome.delete(0, tk.END)
        self.entry_cor_bicicleta.delete(0, tk.END)
        self.entry_box.delete(0, tk.END)
        self.listar_clientes()

    # Função para buscar cliente
    def buscar_cliente(self):
        nome = self.entry_nome_busca.get()
        sobrenome = self.entry_sobrenome_busca.get()

        if not nome or not sobrenome:
            messagebox.showwarning("Entrada Inválida", "Os campos Nome e Sobrenome devem ser preenchidos.")
            return

        clientes = self.bd.buscar_todas_entradas_cliente(nome, sobrenome)

        if clientes:
            mensagem = ""
            for cliente in clientes:
                mensagem += (f"Nome: {cliente[1]}\nSobrenome: {cliente[2]}\nCor da Bicicleta: {cliente[3]}\n"
                             f"Box: {cliente[4]}\nHorário de Entrada: {cliente[5]}\n")

                if cliente[6] is None:
                    if messagebox.askyesno("Saída Pendente",
                                           f"O cliente {cliente[1]} {cliente[2]} tem uma saída pendente "
                                           f"para a entrada de {cliente[5]}. Deseja registrar a saída?"):
                        self.bd.registrar_saida_cliente_por_id(cliente[0])
                        cliente_atualizado = self.bd.buscar_cliente_por_id(cliente[0])

                        if cliente_atualizado and cliente_atualizado[6]:
                            mensagem += f"Horário de Saída: {cliente_atualizado[6]}\n"
                            messagebox.showinfo("Saída Registrada",
                                                f"Saída registrada com sucesso para a entrada de "
                                                f"{cliente_atualizado[5]}.")
                        else:
                            mensagem += "Não foi possível atualizar o horário de saída.\n"
                else:
                    mensagem += f"Horário de Saída: {cliente[6]}\n"

                mensagem += "\n"

            if mensagem:
                messagebox.showinfo("Busca de Cliente", mensagem)
            else:
                messagebox.showwarning("Busca de Cliente", "Cliente não encontrado.")

            self.limpar_campos_busca()
        else:
            messagebox.showwarning("Busca de Cliente", "Cliente não encontrado.")

    # Função para limpar campos de busca
    def limpar_campos_busca(self):
        self.entry_nome_busca.delete(0, tk.END)
        self.entry_sobrenome_busca.delete(0, tk.END)

    # Função para listar clientes
    def listar_clientes(self):
        for item in self.treeview_clientes.get_children():
            self.treeview_clientes.delete(item)

        clientes = self.bd.listar_clientes()
        for cliente in clientes:
            self.treeview_clientes.insert('', 'end', values=cliente[1:])

    # Função para limpar a lista de clientes
    def limpar_lista_clientes(self):
        for item in self.treeview_clientes.get_children():
            self.treeview_clientes.delete(item)

    # Função para listar clientes por data
    def listar_clientes_por_data(self):
        data_selecionada = self.cal_data.get_date().strftime('%d-%m-%Y')
        for item in self.treeview_clientes.get_children():
            self.treeview_clientes.delete(item)

        clientes = self.bd.listar_clientes()
        for cliente in clientes:
            if cliente[5] and cliente[5].startswith(data_selecionada):
                self.treeview_clientes.insert('', 'end', values=cliente[1:])

    # Função para abrir a janela de ferramentas administrativas
    def abrir_ferramentas_administrativas(self):
        janela_ferramentas = tk.Toplevel(self.root)
        janela_ferramentas.title("Ferramentas Administrativas")
        janela_ferramentas.configure(bg='#004d00')

        # Entrada para senha de administrador
        tk.Label(janela_ferramentas, text="Digite a senha para continuar:",
                 bg='#004d00', fg='white').grid(row=0, column=0, pady=5)
        entry_senha = tk.Entry(janela_ferramentas, show="*")
        entry_senha.grid(row=1, column=0, pady=5)

        # Botão de Exportar e Limpar Banco de Dados
        tk.Button(janela_ferramentas, text="Exportar e Limpar Banco de Dados",
                  command=lambda: self.bd.exportar_e_limpar(entry_senha.get())).grid(row=2, column=0, pady=10)


# Executando o aplicativo principal
if __name__ == "__main__":
    root = tk.Tk()
    app = AppBicicletario(root)
    root.mainloop()
