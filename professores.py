import sqlite3

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
        
def descadastrar_professor_na_materia():
    materia_id = int(input("Digite o ID da matéria que deseja se descadastrar: "))

    banco = sqlite3.connect('bancoDeDados.db')
    cursor = banco.cursor()
    cursor.execute('UPDATE materias SET id_professor = NULL WHERE id = ?', (materia_id,))
    banco.commit()
    banco.close()

    print("Professor removido da matéria com sucesso!")

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
        