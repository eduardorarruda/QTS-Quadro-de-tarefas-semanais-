import sqlite3

# Função para cadastrar um aluno em uma matéria
def cadastrar_aluno_na_materia(aluno_id):
    materia_id = int(input("Digite o ID da matéria que deseja se cadastrar: "))  # Solicita ao usuário o ID da matéria

    try:
        banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
        cursor = banco.cursor()

        # Verifica o número de disciplinas já cadastradas pelo aluno
        cursor.execute('SELECT qtd_disciplinas FROM aluno WHERE id = ?', (aluno_id,))
        qtd_disciplinas = cursor.fetchone()[0]

        # Limite máximo de disciplinas é 10
        if qtd_disciplinas >= 10:
            print("Você já está cadastrado no número máximo de disciplinas (10).")
            return

        # Obtém informações sobre a matéria escolhida
        cursor.execute('''SELECT dia_semana, horario_entrada, horario_saida 
                          FROM materias 
                          WHERE id = ?''', (materia_id,))
        materia_escolhida = cursor.fetchone()

        # Obtém informações sobre as matérias em que o aluno já está cadastrado
        cursor.execute('''SELECT materias.dia_semana, materias.horario_entrada, materias.horario_saida
                          FROM materias 
                          JOIN relacaoAlunoMateria ON materias.id = relacaoAlunoMateria.id_materia 
                          WHERE relacaoAlunoMateria.id_aluno = ?''', (aluno_id,))
        materias_cadastradas = cursor.fetchall()

        conflito = False  # Flag para verificar conflito de horário
        materias_no_dia = 0  # Contador de matérias no mesmo dia

        for materia in materias_cadastradas:
            if materia[0] == materia_escolhida[0]:  # Verifica se é o mesmo dia
                materias_no_dia += 1
                if not (materia[2] <= materia_escolhida[1] or materia[1] >= materia_escolhida[2]):  # Verifica conflito de horário
                    conflito = True
                    break

        if conflito:
            print("Conflito de horário. Você já está inscrito em uma matéria nesse horário.")
        elif materias_no_dia >= 2:
            print("Você já está inscrito no número máximo de matérias (2) para esse dia.")
        else:
            # Insere a relação aluno-matéria na tabela relacaoAlunoMateria
            cursor.execute('INSERT INTO relacaoAlunoMateria (id_materia, id_aluno) VALUES (?, ?)', (materia_id, aluno_id))

            # Obtém o nome da matéria para feedback ao usuário
            cursor.execute('SELECT nome FROM materias WHERE id = ?', (materia_id,))
            materia_nome = cursor.fetchone()[0]

            # Atualiza os créditos e o número de disciplinas do aluno
            cursor.execute('UPDATE aluno SET credito = credito - 40 WHERE id = ?', (aluno_id,))
            cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas + 1 WHERE id = ?', (aluno_id,))

            # Atualiza o número de alunos cadastrados na matéria
            cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados + 1 WHERE id = ?', (materia_id,))

            banco.commit()  # Confirma as alterações no banco de dados
            print("Aluno cadastrado na matéria com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
    finally:
        banco.close()  # Fecha a conexão com o banco de dados
        
# Função para descadastrar um aluno de uma matéria
def descadastrar_aluno_na_materia(aluno_id):
    materia_id = int(input("Digite o ID da matéria: "))  # Solicita ao usuário o ID da matéria

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    # Remove a relação aluno-matéria da tabela relacaoAlunoMateria
    cursor.execute('DELETE FROM relacaoAlunoMateria WHERE id_materia = ? AND id_aluno = ?', (materia_id, aluno_id))

    # Atualiza o número de alunos cadastrados na matéria
    cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados - 1 WHERE id = ?', (materia_id,))

    # Atualiza os créditos e o número de disciplinas do aluno
    cursor.execute('UPDATE aluno SET credito = credito + 40 WHERE id = ?', (aluno_id,))
    cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas - 1 WHERE id = ?', (aluno_id,))

    banco.commit()  # Confirma as alterações no banco de dados
    banco.close()  # Fecha a conexão com o banco de dados

    print("Aluno removido da matéria com sucesso!")
    
# Função para visualizar os créditos do aluno
def ver_credito_aluno(aluno_id):
    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    # Obtém os créditos do aluno
    cursor.execute('SELECT credito FROM aluno WHERE id = ?', (aluno_id,))
    credito = cursor.fetchone()[0]

    banco.close()  # Fecha a conexão com o banco de dados

    print(f"Seu crédito atual é: {credito}")

# Função para visualizar as matérias cadastradas pelo aluno
def ver_materias_cadastradas_aluno(aluno_id):
    try:
        banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
        cursor = banco.cursor()

        # Obtém informações sobre as matérias em que o aluno está cadastrado
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
        banco.close()  # Fecha a conexão com o banco de dados

# Função para recomendar horários de matérias sem conflitos
def recomendar_horarios():
    dias_semana = ['segunda', 'terça', 'quarta', 'quinta', 'sexta']  # Lista de dias da semana

    recomendacoes = {dia: [] for dia in dias_semana}  # Dicionário para armazenar recomendações por dia

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    try:
        for dia in dias_semana:

            # Obtém matérias disponíveis para o dia especificado
            cursor.execute('''SELECT nome, horario_entrada, horario_saida 
                              FROM materias 
                              WHERE dia_semana = ?''', (dia,))
            materias_do_dia = cursor.fetchall()

            materias_adicionadas = 0  # Contador de matérias adicionadas

            for nome, horario_entrada, horario_saida in materias_do_dia:

                if materias_adicionadas >= 2:  # Limite máximo de 2 matérias por dia
                    break

                conflito = False  # Flag para verificar conflito de horário

                # Verifica se há conflito de horário com matérias já recomendadas
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
        banco.close()  # Fecha a conexão com o banco de dados

    return recomendacoes

# Função para imprimir as recomendações de horários
def imprimir_recomendacoes(recomendacoes):
    for dia, materias_horarios in recomendacoes.items():
        print(f"Recomendações para {dia.capitalize()}:")
        for nome, hora_entrada, hora_saida in materias_horarios:
            print(f"- {nome}: {hora_entrada} - {hora_saida}")
        print()
        
# Função para inscrever o aluno nas matérias recomendadas
def inscrever_em_recomendacoes(aluno_id, recomendacoes):

    banco = sqlite3.connect('bancoDeDados.db')  # Conecta ao banco de dados
    cursor = banco.cursor()

    try:
        for dia, materias_horarios in recomendacoes.items():
            for nome, _, _ in materias_horarios:

                # Obtém o ID da matéria a partir do nome
                cursor.execute('SELECT id FROM materias WHERE nome = ?', (nome,))
                materia_id = cursor.fetchone()[0]

                # Verifica se o aluno já está inscrito na matéria
                cursor.execute('''SELECT COUNT(*) FROM relacaoAlunoMateria 
                                  WHERE id_materia = ? AND id_aluno = ?''', (materia_id, aluno_id))
                if cursor.fetchone()[0] == 0:

                    # Insere a relação aluno-matéria na tabela relacaoAlunoMateria
                    cursor.execute('INSERT INTO relacaoAlunoMateria (id_materia, id_aluno) VALUES (?, ?)', (materia_id, aluno_id))

                    # Atualiza os créditos e o número de disciplinas do aluno
                    cursor.execute('UPDATE aluno SET credito = credito - 40 WHERE id = ?', (aluno_id,))
                    cursor.execute('UPDATE aluno SET qtd_disciplinas = qtd_disciplinas + 1 WHERE id = ?', (aluno_id,))

                    # Atualiza o número de alunos cadastrados na matéria
                    cursor.execute('UPDATE materias SET qtd_alunos_cadastrados = qtd_alunos_cadastrados + 1 WHERE id = ?', (materia_id,))

        banco.commit()  # Confirma as alterações no banco de dados
        print("Aluno inscrito nas matérias recomendadas com sucesso!")
    except sqlite3.Error as e:
        print("Erro ao acessar o banco de dados:", e)
        banco.rollback()  # Desfaz as alterações em caso de erro
    finally:
        banco.close()  # Fecha a conexão com o banco de dados
