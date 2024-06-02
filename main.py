import sqlite3
import alunos
import professores

# Função para inscrever um usuário (aluno ou professor)
def inscrever_usuario():
    tipo_usuario = input("Você é um aluno ou professor? ").strip().lower()  # Pergunta o tipo de usuário
    nome = input("Nome: ")
    senha = input("Senha: ")
    email = input("Email: ")
    curso = input("Curso: ")

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    # Insere os dados do usuário no banco de dados, dependendo do tipo de usuário
    if tipo_usuario == 'aluno':
        cursor.execute('INSERT INTO aluno (nome, senha, email, curso, qtd_disciplinas, credito) VALUES (?, ?, ?, ?, ?, ?)',
                       (nome, senha, email, curso, 0, 200))
    elif tipo_usuario == 'professor':
        cursor.execute('INSERT INTO professores (nome, senha, email, curso) VALUES (?, ?, ?, ?)',
                       (nome, senha, email, curso))
    else:
        print("Tipo de usuário inválido.")
        banco.close()  # Fecha a conexão com o banco de dados
        return

    banco.commit()  # Confirma as alterações no banco de dados
    banco.close()  # Fecha a conexão com o banco de dados
    print("Usuário inscrito com sucesso!")

# Função para logar um usuário
def logar_usuario():
    email = input("Email: ")
    senha = input("Senha: ")

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    # Verifica se o usuário é um aluno
    cursor.execute('SELECT * FROM aluno WHERE email = ? AND senha = ?', (email, senha))
    aluno = cursor.fetchone()

    # Verifica se o usuário é um professor
    cursor.execute('SELECT * FROM professores WHERE email = ? AND senha = ?', (email, senha))
    professor = cursor.fetchone()

    if aluno:
        print(f"Bem-vindo, {aluno[1]}! Você está logado como aluno.")
        return ("aluno", aluno)
    elif professor:
        print(f"Bem-vindo, {professor[1]}! Você está logado como professor.")
        return ("professor", professor)
    else:
        print("Email ou senha incorretos.")
        return (None, None)

    banco.close()  # Fecha a conexão com o banco de dados

# Função para visualizar todas as matérias
def ver_materias():
    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM materias')  # Seleciona todas as matérias
    materias = cursor.fetchall()
    banco.close()  # Fecha a conexão com o banco de dados

    print("\nTabela de Matérias:")
    for materia in materias:
        print(materia)  # Imprime todas as matérias

# Função para cadastrar uma nova matéria (para uso do professor)
def cadastrar_materia(professor_id):
    nome = input("Nome da matéria: ")
    creditos = int(input("Créditos: "))
    carga_horaria = int(input("Carga horária: "))
    dia_semana = input("Dia da semana: ")
    horario_entrada = input("Horario de entrada (HH:MM): ")
    horario_saida = input("Horario de saída (HH:MM): ")

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()
    cursor.execute('''INSERT INTO materias (nome, creditos, carga_horaria, id_professor, dia_semana, horario_entrada, horario_saida) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (nome, creditos, carga_horaria, None, dia_semana, horario_entrada, horario_saida))
    banco.commit()  # Confirma as alterações no banco de dados
    banco.close()  # Fecha a conexão com o banco de dados

    print("Matéria cadastrada com sucesso!")

# Menu do aluno com opções específicas para alunos
def menu_aluno(aluno):
    while True:
        print("\nMenu do Aluno:")
        print("1. Ver tabela de matérias")
        print("2. Cadastrar-se em uma matéria")
        print("3. Descadastrar-se de uma matéria")
        print("4. Ver crédito")
        print("5. Ver matérias cadastradas")
        print("6. Visualizar e aceitar recomendações de horários")
        print("7. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            ver_materias()
        elif escolha == '2':
            alunos.cadastrar_aluno_na_materia(aluno[0])  # Chama a função de cadastrar aluno na matéria
        elif escolha == '3':
            alunos.descadastrar_aluno_na_materia(aluno[0])  # Chama a função de descadastrar aluno da matéria
        elif escolha == '4':
            alunos.ver_credito_aluno(aluno[0])  # Chama a função de ver crédito do aluno
        elif escolha == '5':
            alunos.ver_materias_cadastradas_aluno(aluno[0])  # Chama a função de ver matérias cadastradas pelo aluno
        elif escolha == '6':
            print("Visualizando recomendações de horários...")
            recomendacoes = alunos.recomendar_horarios()  # Chama a função de recomendar horários
            alunos.imprimir_recomendacoes(recomendacoes)  # Chama a função de imprimir recomendações
            opcao = input("Deseja se inscrever em todas as matérias recomendadas? (s/n): ").strip().lower()
            if opcao == 's':
                alunos.inscrever_em_recomendacoes(aluno[0], recomendacoes)  # Chama a função de inscrever aluno em recomendações
        elif escolha == '7':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Menu do professor com opções específicas para professores
def menu_professor(professor):
    while True:
        print("\nMenu do Professor:")
        print("1. Ver tabela de matérias")
        print("2. Ver matérias cadastradas")
        print("3. Cadastrar nova matéria")
        print("4. Descadastrar-se de uma matéria")
        print("5. Alterar horário e dia da semana de uma matéria")
        print("6. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            ver_materias()
        elif escolha == '2':
            professores.ver_materias_cadastradas_professor(professor[0])  # Chama a função de ver matérias cadastradas pelo professor
        elif escolha == '3':
            professores.cadastrar_professor_na_materia(professor[0])  # Chama a função de cadastrar professor em uma matéria
        elif escolha == '4':
            professores.descadastrar_professor_na_materia()  # Chama a função de descadastrar professor de uma matéria
        elif escolha == '5':
            professores.alterar_horario_materia()  # Chama a função de alterar horário de uma matéria
        elif escolha == '6':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Menu principal do sistema
def menu_principal():
    while True:
        print("\nMenu Principal:")
        print("1. Inscrever-se")
        print("2. Logar")
        print("3. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            inscrever_usuario()  # Chama a função de inscrever usuário
        elif escolha == '2':
            tipo_usuario, usuario = logar_usuario()  # Chama a função de logar usuário
            if tipo_usuario == 'aluno':
                menu_aluno(usuario)  # Chama o menu do aluno
            elif tipo_usuario == 'professor':
                menu_professor(usuario)  # Chama o menu do professor
        elif escolha == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Inicia o menu principal ao executar o script
if __name__ == "__main__":
    menu_principal()
