import sqlite3

# Função para cadastrar um professor em uma matéria
def cadastrar_professor_na_materia(professor_id):
    materia_id = int(input("Digite o ID da matéria que deseja se cadastrar: "))  # Solicita ao usuário o ID da matéria

    try:
        banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
        cursor = banco.cursor()

        # Obtém informações sobre a matéria escolhida
        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida 
                          FROM materias 
                          WHERE id = ?''', (materia_id,))
        materia_escolhida = cursor.fetchone()

        # Obtém informações sobre as matérias em que o professor já está cadastrado
        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida
                          FROM materias 
                          WHERE id_professor = ?''', (professor_id,))
        materias_cadastradas = cursor.fetchall()

        conflito = False  # Flag para verificar conflito de horário

        # Verifica se há conflito de horário com matérias já cadastradas pelo professor
        for materia in materias_cadastradas:
            if materia[0] == materia_escolhida[0] and not (materia[2] <= materia_escolhida[1] or materia[1] >= materia_escolhida[2]):
                conflito = True
                break

        if conflito:
            print("Conflito de horário. Você já está inscrito em uma matéria nesse horário.")
        else:
            # Atualiza a matéria com o ID do professor
            cursor.execute('UPDATE materias SET id_professor = ? WHERE id = ?', (professor_id, materia_id))
            banco.commit()  # Confirma as alterações no banco de dados
            print("Professor cadastrado na matéria com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()  # Fecha a conexão com o banco de dados

# Função para descadastrar um professor de uma matéria
def descadastrar_professor_na_materia():
    materia_id = int(input("Digite o ID da matéria que deseja se descadastrar: "))  # Solicita ao usuário o ID da matéria

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    # Remove o ID do professor da matéria
    cursor.execute('UPDATE materias SET id_professor = NULL WHERE id = ?', (materia_id,))
    banco.commit()  # Confirma as alterações no banco de dados
    banco.close()  # Fecha a conexão com o banco de dados

    print("Professor removido da matéria com sucesso!")

# Função para visualizar as matérias cadastradas pelo professor
def ver_materias_cadastradas_professor(professor_id):
    try:
        banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
        cursor = banco.cursor()

        # Obtém informações sobre as matérias em que o professor está cadastrado
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
        banco.close()  # Fecha a conexão com o banco de dados

# Função para alterar o horário de uma matéria
def alterar_horario_materia():
    materia_id = int(input("Digite o ID da matéria que deseja alterar: "))  # Solicita ao usuário o ID da matéria
    dia_semana = input("Novo dia da semana: ")  # Solicita ao usuário o novo dia da semana
    horario_entrada = input("Novo horário de entrada (HH:MM): ")  # Solicita ao usuário o novo horário de entrada
    horario_saida = input("Novo horário de saída (HH:MM): ")  # Solicita ao usuário o novo horário de saída

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    try:
        # Atualiza o dia da semana e os horários da matéria
        cursor.execute('''UPDATE materias 
                          SET dia_semana = ?, horario_entrada = ?, horario_saida = ?
                          WHERE id = ?''', (dia_semana, horario_entrada, horario_saida, materia_id))
        banco.commit()  # Confirma as alterações no banco de dados
        print("Horário e dia da semana da matéria alterados com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()  # Fecha a conexão com o banco de dados
