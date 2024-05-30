import sqlite3

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

def cadastrar_aluno_na_materia(aluno_id):
    materia_id = int(input("Digite o ID da matéria que deseja se cadastrar: "))

    try:
        banco = sqlite3.connect('bancoDeDados.db')
        cursor = banco.cursor()


        cursor.execute('SELECT qtd_disciplinas FROM aluno WHERE id = ?', (aluno_id,))
        qtd_disciplinas = cursor.fetchone()[0]

        if qtd_disciplinas >= 10:
            print("Você já está cadastrado no número máximo de disciplinas (10).")
            return

        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida 
                          FROM materias 
                          WHERE id = ?''', (materia_id,))
        materia_escolhida = cursor.fetchone()

        cursor.execute('''SELECT materias.dia_semana, materias.horario_entrada, materias.horario_saida
                          FROM materias 
                          JOIN relacaoAlunoMateria ON materias.id = relacaoAlunoMateria.id_materia 
                          WHERE relacaoAlunoMateria.id_aluno = ?''', (aluno_id,))
        materias_cadastradas = cursor.fetchall()

        conflito = False
        materias_no_dia = 0
        for materia in materias_cadastradas:
            if materia[0] == materia_escolhida[0]:
                materias_no_dia += 1
                if not (materia[2] <= materia_escolhida[1] or materia[1] >= materia_escolhida[2]):
                    conflito = True
                    break

        if conflito:
            print("Conflito de horário. Você já está inscrito em uma matéria nesse horário.")
        elif materias_no_dia >= 2:
            print("Você já está inscrito no número máximo de matérias (2) para esse dia.")
        else:
            cursor.execute('INSERT INTO relacaoAlunoMateria (id_materia, id_aluno) VALUES (?, ?)', (materia_id, aluno_id))

            cursor.execute('SELECT nome FROM materias WHERE id = ?', (materia_id,))
            materia_nome = cursor.fetchone()[0]

            cursor.execute('UPDATE aluno SET credito = credito - 40 WHERE id = ?', (aluno_id,))
            cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas + 1 WHERE id = ?', (aluno_id,))
            cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados + 1 WHERE id = ?', (materia_id,))

            banco.commit()
            print("Aluno cadastrado na matéria com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()

def cadastrar_professor_na_materia(professor_id):
    materia_id = int(input("Digite o ID da matéria que deseja se cadastrar: "))

    try:
        banco = sqlite3.connect('bancoDeDados.db')
        cursor = banco.cursor()


        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida 
                          FROM materias 
                          WHERE id = ?''', (materia_id,))
        materia_escolhida = cursor.fetchone()

        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida
                          FROM materias 
                          WHERE id_professor = ?''', (professor_id,))
        materias_cadastradas = cursor.fetchall()

        conflito = False
        for materia in materias_cadastradas:
            if materia[0] == materia_escolhida[0] and not (materia[2] <= materia_escolhida[1] or materia[1] >= materia_escolhida[2]):
                conflito = True
                break

        if conflito:
            print("Conflito de horário. Você já está inscrito em uma matéria nesse horário.")
        else:
            cursor.execute('UPDATE materias SET id_professor = ? WHERE id = ?', (professor_id, materia_id))
            banco.commit()
            print("Professor cadastrado na matéria com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()

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

def descadastrar_aluno_na_materia(aluno_id):
    materia_id = int(input("Digite o ID da matéria: "))

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()
    cursor.execute('DELETE FROM relacaoAlunoMateria WHERE id_materia = ? AND id_aluno = ?', (materia_id, aluno_id))
    cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados - 1 WHERE id = ?', (materia_id,))
    cursor.execute('UPDATE aluno SET credito = credito + 40 WHERE id = ?', (aluno_id,))
    cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas - 1 WHERE id = ?', (aluno_id,))
    banco.commit()
    banco.close()

    print("Aluno removido da matéria com sucesso!")

def descadastrar_professor_na_materia():
    materia_id = int(input("Digite o ID da matéria que deseja se descadastrar: "))

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()
    cursor.execute('UPDATE materias SET id_professor = NULL WHERE id = ?', (materia_id,))
    banco.commit()
    banco.close()

    print("Professor removido da matéria com sucesso!")

def ver_credito_aluno(aluno_id):
    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    cursor.execute('SELECT credito FROM aluno WHERE id = ?', (aluno_id,))
    credito = cursor.fetchone()[0]

    banco.close()

    print(f"Seu crédito atual é: {credito}")

def ver_materias_cadastradas_aluno(aluno_id):
    try:
        banco = sqlite3.connect('bancoDeDados.db')
        cursor = banco.cursor()

        cursor.execute('''SELECT materias.nome, materias.dia_semana, materias.horario_entrada, materias.horario_saida 
                          FROM materias 
                          JOIN relacaoAlunoMateria ON materias.id = relacaoAlunoMateria.id_materia 
                          WHERE relacaoAlunoMateria.id_aluno = ?''', (aluno_id,))
        materias_cadastradas = cursor.fetchall()

        if materias_cadastradas:
            print("\nMatérias cadastradas pelo aluno:")
            for materia in materias_cadastradas:
                nome, dia_semana, horario_entrada, horario_saida = materia
                print(f"Nome: {nome}, Dia da Semana: {dia_semana}, Horário: {horario_entrada} - {horario_saida}")
        else:
            print("Nenhuma matéria cadastrada para este aluno.")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()

def ver_materias_cadastradas_professor(professor_id):
    try:
        banco = sqlite3.connect('bancoDeDados.db')
        cursor = banco.cursor()

        cursor.execute('''SELECT materias.nome, materias.dia_semana, materias.horario_entrada, materias.horario_saida 
                          FROM materias 
                          WHERE id_professor = ?''', (professor_id,))
        materias_cadastradas = cursor.fetchall()

        if materias_cadastradas:
            print("\nMatérias cadastradas pelo professor:")
            for materia in materias_cadastradas:
                nome, dia_semana, horario_entrada, horario_saida = materia
                print(f"Nome: {nome}, Dia da Semana: {dia_semana}, Horário: {horario_entrada} - {horario_saida}")
        else:
            print("Nenhuma matéria cadastrada para este professor.")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()

def alterar_horario_materia():
    materia_id = int(input("Digite o ID da matéria que deseja alterar: "))
    dia_semana = input("Novo dia da semana: ")
    horario_entrada = input("Novo horário de entrada (HH:MM): ")
    horario_saida = input("Novo horário de saída (HH:MM): ")

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    try:
        cursor.execute('''UPDATE materias 
                          SET dia_semana = ?, horario_entrada = ?, horario_saida = ?
                          WHERE id = ?''', (dia_semana, horario_entrada, horario_saida, materia_id))
        banco.commit()
        print("Horário e dia da semana da matéria alterados com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()
        


def recomendar_horarios():
    dias_semana = ['segunda', 'terça', 'quarta', 'quinta', 'sexta']


    recomendacoes = {dia: [] for dia in dias_semana}


    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    try:
        for dia in dias_semana:

            cursor.execute('''SELECT nome, horario_entrada, horario_saida 
                              FROM materias 
                              WHERE dia_semana = ?''', (dia,))
            materias_do_dia = cursor.fetchall()

            materias_adicionadas = 0


            for nome, horario_entrada, horario_saida in materias_do_dia:

                if materias_adicionadas >= 2:
                    break


                conflito = False
                for _, hora_entrada, hora_saida in recomendacoes[dia]:
                    if hora_entrada < horario_saida and hora_saida > horario_entrada:
                        conflito = True
                        break


                if not conflito:
                    recomendacoes[dia].append((nome, horario_entrada, horario_saida))
                    materias_adicionadas += 1

    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:

        banco.close()

    return recomendacoes

def imprimir_recomendacoes(recomendacoes):
    for dia, materias_horarios in recomendacoes.items():
        print(f"Recomendações para {dia.capitalize()}:")
        for nome, hora_entrada, hora_saida in materias_horarios:
            print(f"- {nome}: {hora_entrada} - {hora_saida}")
        print()
        
        
def inscrever_em_recomendacoes(aluno_id, recomendacoes):

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()

    try:
        for dia, materias_horarios in recomendacoes.items():
            for nome, _, _ in materias_horarios:

                cursor.execute('SELECT id FROM materias WHERE nome = ?', (nome,))
                materia_id = cursor.fetchone()[0]

                cursor.execute('''SELECT COUNT(*) FROM relacaoAlunoMateria 
                                  WHERE id_materia = ? AND id_aluno = ?''', (materia_id, aluno_id))
                if cursor.fetchone()[0] == 0:

                    cursor.execute('INSERT INTO relacaoAlunoMateria (id_materia, id_aluno) VALUES (?, ?)', (materia_id, aluno_id))

                    cursor.execute('UPDATE aluno SET credito = credito - 40 WHERE id = ?', (aluno_id,))
                    cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas + 1 WHERE id = ?', (aluno_id,))
                    cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados + 1 WHERE id = ?', (materia_id,))

        banco.commit()
        print("Aluno inscrito nas matérias recomendadas com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
        banco.rollback()
    finally:
        banco.close()

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
            cadastrar_aluno_na_materia(aluno[0])
        elif escolha == '3':
            descadastrar_aluno_na_materia(aluno[0])
        elif escolha == '4':
            ver_credito_aluno(aluno[0])
        elif escolha == '5':
            ver_materias_cadastradas_aluno(aluno[0])
        elif escolha == '6':
            print("Visualizando recomendações de horários...")
            recomendacoes = recomendar_horarios()
            imprimir_recomendacoes(recomendacoes)
            opcao = input("Deseja se inscrever em todas as matérias recomendadas? (s/n): ").strip().lower()
            if opcao == 's':
                inscrever_em_recomendacoes(aluno[0], recomendacoes)
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
            ver_materias_cadastradas_professor(professor[0])
        elif escolha == '3':
            cadastrar_materia(professor[0])
        elif escolha == '4':
            descadastrar_professor_na_materia()
        elif escolha == '5':
            alterar_horario_materia()
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
