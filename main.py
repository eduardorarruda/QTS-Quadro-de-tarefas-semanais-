import sqlite3
import alunos
import professores 


def inscrever_usuario():
    tipo_usuario = input("Você é um aluno ou professor? ").strip().lower()
    nome = input("Nome: ")
    senha = input("Senha: ")
    email = input("Email: ")
    curso = input("Curso: ")

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    if tipo_usuario == 'aluno':
        cursor.execute('INSERT INTO aluno (nome, senha, email, curso, qtd_disciplinas, credito) VALUES (?, ?, ?, ?, ?, ?)',
                       (nome, senha, email, curso, 0, 200))
    elif tipo_usuario == 'professor':
        cursor.execute('INSERT INTO professores (nome, senha, email, curso) VALUES (?, ?, ?, ?)',
                       (nome, senha, email, curso))
    else:
        print("Tipo de usuário inválido.")
        banco.close()
        return

    banco.commit()
    banco.close()
    print("Usuário inscrito com sucesso!")

def logar_usuario():
    email = input("Email: ")
    senha = input("Senha: ")

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    cursor.execute('SELECT * FROM aluno WHERE email = ? AND senha = ?', (email, senha))
    aluno = cursor.fetchone()

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

    banco.close()

def ver_materias():
    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()
    cursor.execute('SELECT * FROM materias')
    materias = cursor.fetchall()
    banco.close()

    print("\nTabela de Matérias:")
    for materia in materias:
        print(materia)

def cadastrar_materia(professor_id):
    nome = input("Nome da matéria: ")
    creditos = int(input("Créditos: "))
    carga_horaria = int(input("Carga horária: "))
    dia_semana = input("Dia da semana: ")
    horario_entrada = input("Horario de entrada (HH:MM): ")
    horario_saida = input("Horario de saída (HH:MM): ")

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()
    cursor.execute('''INSERT INTO materias (nome, creditos, carga_horaria, id_professor, dia_semana, horario_entrada, horario_saida) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (nome, creditos, carga_horaria, None, dia_semana, horario_entrada, horario_saida))
    banco.commit()
    banco.close()

    print("Matéria cadastrada com sucesso!")

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
          alunos.cadastrar_aluno_na_materia(aluno[0])
        elif escolha == '3':
            alunos.descadastrar_aluno_na_materia(aluno[0])
        elif escolha == '4':
            alunos.ver_credito_aluno(aluno[0])
        elif escolha == '5':
            alunos.ver_materias_cadastradas_aluno(aluno[0])
        elif escolha == '6':
            print("Visualizando recomendações de horários...")
            recomendacoes = alunos.recomendar_horarios()
            alunos.imprimir_recomendacoes(recomendacoes)
            opcao = input("Deseja se inscrever em todas as matérias recomendadas? (s/n): ").strip().lower()
            if opcao == 's':
                alunos.inscrever_em_recomendacoes(aluno[0], recomendacoes)
        elif escolha == '7':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
            
            
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
            professores.ver_materias_cadastradas_professor(professor[0])
        elif escolha == '3':
            professores.cadastrar_professor_na_materia(professor[0])
        elif escolha == '4':
            professores.descadastrar_professor_na_materia()
        elif escolha == '5':
            professores.alterar_horario_materia()
        elif escolha == '6':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_principal():
    while True:
        print("\nMenu Principal:")
        print("1. Inscrever-se")
        print("2. Logar")
        print("3. Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == '1':
            inscrever_usuario()
        elif escolha == '2':
            tipo_usuario, usuario = logar_usuario()
            if tipo_usuario == 'aluno':
                menu_aluno(usuario)
            elif tipo_usuario == 'professor':
                menu_professor(usuario)
        elif escolha == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()
