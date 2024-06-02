import sqlite3

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
