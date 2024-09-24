import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt


conn = sqlite3.connect('projeto_esportivo.db')
c = conn.cursor()

def create_tables():
    """
    Cria as tabelas 'participantes', 'atividades' e 'frequencia' no banco de dados SQLite.
    
    Se as tabelas já existirem, não serão recriadas.
    
    Returns:
        None
    """
    c.execute('''CREATE TABLE IF NOT EXISTS participantes (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 nome TEXT,
                 idade INTEGER,
                 genero TEXT,
                 escolaridade TEXT,
                 data_inscricao TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS atividades (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 atividade TEXT,
                 descricao TEXT,
                 data_atividade TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS frequencia (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 participante_id INTEGER,
                 atividade_id INTEGER,
                 presenca INTEGER,
                 data_frequencia TEXT,
                 FOREIGN KEY (participante_id) REFERENCES participantes(id),
                 FOREIGN KEY (atividade_id) REFERENCES atividades(id))''')


def add_participante(nome, idade, genero, escolaridade):
    """
    Adiciona um novo participante à tabela 'participantes'.
    
    Args:
        nome (str): Nome do participante.
        idade (int): Idade do participante.
        genero (str): Gênero do participante.
        escolaridade (str): Nível de escolaridade do participante.
    
    Returns:
        None
    """
    c.execute('INSERT INTO participantes (nome, idade, genero, escolaridade, data_inscricao) VALUES (?, ?, ?, ?, ?)',
              (nome, idade, genero, escolaridade, date.today()))
    conn.commit()


def add_atividade(atividade, descricao):
    """
    Adiciona uma nova atividade à tabela 'atividades'.
    
    Args:
        atividade (str): Nome da atividade.
        descricao (str): Descrição da atividade.
    
    Returns:
        None
    """
    c.execute('INSERT INTO atividades (atividade, descricao, data_atividade) VALUES (?, ?, ?)',
              (atividade, descricao, date.today()))
    conn.commit()


def registrar_frequencia(participante_id, atividade_id, presenca, data_frequencia):
    """
    Registra a frequência de um participante em uma atividade.
    
    Args:
        participante_id (int): ID do participante.
        atividade_id (int): ID da atividade.
        presenca (int): 1 para presente, 0 para ausente.
        data_frequencia (str): Data da frequência no formato YYYY-MM-DD.
    
    Returns:
        None
    """
    c.execute('INSERT INTO frequencia (participante_id, atividade_id, presenca, data_frequencia) VALUES (?, ?, ?, ?)',
              (participante_id, atividade_id, presenca, data_frequencia))
    conn.commit()


def visualizar_participantes():
    """
    Retorna todos os participantes cadastrados na tabela 'participantes'.
    
    Returns:
        list: Lista contendo os dados dos participantes.
    """
    c.execute('SELECT * FROM participantes')
    data = c.fetchall()
    return data


def visualizar_atividades():
    """
    Retorna todas as atividades cadastradas na tabela 'atividades'.
    
    Returns:
        list: Lista contendo os dados das atividades.
    """
    c.execute('SELECT * FROM atividades')
    data = c.fetchall()
    return data


def get_participantes_dropdown():
    """
    Retorna os IDs, nomes e idades dos participantes para uso em dropdowns.
    
    Returns:
        list: Lista de tuplas contendo o ID, nome e idade dos participantes.
    """
    c.execute('SELECT id, nome, idade FROM participantes')
    return c.fetchall()


def get_atividades_dropdown():
    """
    Retorna os IDs e nomes das atividades para uso em dropdowns.
    
    Returns:
        list: Lista de tuplas contendo o ID e nome das atividades.
    """
    c.execute('SELECT id, atividade FROM atividades')
    return c.fetchall()


def visualizar_frequencia():
    """
    Retorna a frequência dos participantes nas atividades.
    
    Returns:
        list: Lista contendo os dados de frequência, incluindo nome do participante, atividade, presença e data.
    """
    c.execute('''SELECT f.id, p.nome, a.atividade, f.presenca, f.data_frequencia 
                 FROM frequencia f
                 JOIN participantes p ON f.participante_id = p.id
                 JOIN atividades a ON f.atividade_id = a.id ORDER BY f.data_frequencia''')
    data = c.fetchall()
    return data


def obter_dados_participantes_por_atividade():
    """
    Obtém o número de participantes presentes por atividade e data.
    
    Returns:
        pandas.DataFrame: DataFrame contendo os dados de presença por atividade e data.
    """
    query = '''SELECT a.atividade, f.data_frequencia, COUNT(f.presenca) AS num_presentes
               FROM frequencia f
               JOIN atividades a ON f.atividade_id = a.id
               WHERE f.presenca = 1
               GROUP BY a.atividade, f.data_frequencia
               ORDER BY f.data_frequencia'''
    c.execute(query)
    data = c.fetchall()

    df = pd.DataFrame(data, columns=['Atividade', 'Data', 'Num_Presentes'])
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    return df


def excluir_participante(participante_id):
    """
    Exclui um participante da tabela 'participantes' e remove suas frequências associadas.
    
    Args:
        participante_id (int): ID do participante a ser excluído.
    
    Returns:
        None
    """
    c.execute('DELETE FROM frequencia WHERE participante_id = ?', (participante_id,))
    c.execute('DELETE FROM participantes WHERE id = ?', (participante_id,))
    conn.commit()


def excluir_atividade(atividade_id):
    """
    Exclui uma atividade da tabela 'atividades' e remove as frequências associadas.
    
    Args:
        atividade_id (int): ID da atividade a ser excluída.
    
    Returns:
        None
    """
    c.execute('DELETE FROM frequencia WHERE atividade_id = ?', (atividade_id,))
    c.execute('DELETE FROM atividades WHERE id = ?', (atividade_id,))
    conn.commit()


def excluir_frequencia(frequencia_id):
    """
    Exclui um registro específico de frequência da tabela 'frequencia'.
    
    Args:
        frequencia_id (int): ID do registro de frequência a ser excluído.
    
    Returns:
        None
    """
    c.execute('DELETE FROM frequencia WHERE id = ?', (frequencia_id,))
    conn.commit()



def plotar_grafico_barras(df):
    """
    Gera um gráfico de barras múltiplas para representar o número de participantes presentes por atividade e data.
    
    Args:
        df (pandas.DataFrame): DataFrame contendo os dados de presença por atividade e data.
    
    Returns:
        None
    """
    plt.figure(figsize=(12, 6))

    df_pivot = df.pivot(index='Data', columns='Atividade', values='Num_Presentes')

    ax = df_pivot.plot(kind='bar', width=0.5)

    plt.title('Número de Participantes Presentes por Atividade e Data')
    plt.xlabel('Data')
    plt.ylabel('Número de Presentes')

    ax.set_xticks(ax.get_xticks())
    tick_labels = [x.strftime('%Y-%m-%d') for x in pd.to_datetime(df_pivot.index)]
    ax.set_xticklabels(tick_labels, rotation=90, ha='center')

    plt.grid(axis='y')
    plt.legend(title='Atividade')
    plt.tight_layout()

    st.pyplot(plt)


create_tables()

# Carregar o arquivo de configuração do YAML para os usuários
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Função de login
name, authentication_status, username = authenticator.login('main', fields = {'Form name': 'Login'})

if authentication_status:
    authenticator.logout('logout', 'sidebar')
    st.sidebar.write(f'Bem-vindo, {name}!')

    st.title('Projeto de Incentivo à Prática Esportiva')

    menu = ['Cadastrar Participante', 'Cadastrar Atividade', 'Registrar Frequência', 'Excluir Registro', 'Relatórios']
    choice = st.sidebar.radio('Menu', menu)

    # Cadastrar participante
    if choice == 'Cadastrar Participante':
        st.subheader('Cadastro de Participantes')
        nome = st.text_input('Nome')
        idade = st.number_input('Idade', min_value=9, max_value=12, step=1)
        genero = st.selectbox('Gênero', ['Masculino', 'Feminino'])
        escolaridade = st.text_input('Escolaridade')
        
        if st.button('Cadastrar'):
            add_participante(nome, idade, genero, escolaridade)
            st.success(f'Participante {nome} cadastrado com sucesso!')

    # Cadastrar atividade
    elif choice == 'Cadastrar Atividade':
        st.subheader('Cadastro de Atividades')
        atividade = st.text_input('Atividade')
        descricao = st.text_area('Descrição')
        
        if st.button('Cadastrar'):
            add_atividade(atividade, descricao)
            st.success(f'Atividade {atividade} cadastrada com sucesso!')

    # Registrar Frequência
    elif choice == 'Registrar Frequência':
        st.subheader('Registro de Frequência')

        participantes = get_participantes_dropdown()
        atividades = get_atividades_dropdown()

        if participantes:
            participante_selecionado = st.selectbox(
                'Selecione o Participante',
                [f"ID: {p[0]}, Nome: {p[1]}, Idade: {p[2]}" for p in participantes]
            )
            participante_id = int(participante_selecionado.split(',')[0].split(':')[1].strip())
        else:
            st.warning('Nenhum participante cadastrado!')
            participante_id = None

        if atividades:
            atividade_selecionada = st.selectbox(
                'Selecione a Atividade',
                [f"ID: {a[0]}, Atividade: {a[1]}" for a in atividades]
            )
            atividade_id = int(atividade_selecionada.split(',')[0].split(':')[1].strip())
        else:
            st.warning('Nenhuma atividade cadastrada!')
            atividade_id = None

        presenca_texto = st.selectbox('Presença', ['Presente', 'Ausente'])
        presenca = 1 if presenca_texto == 'Presente' else 0

        data_frequencia = st.date_input('Data da Frequência')

        if st.button('Registrar'):
            if participante_id is not None and atividade_id is not None:
                registrar_frequencia(participante_id, atividade_id, presenca, data_frequencia)
                st.success('Frequência registrada com sucesso!')
            else:
                st.error('Não foi possível registrar a frequência. Verifique se há participantes e atividades cadastrados.')

    elif choice == 'Excluir Registro':
        st.subheader('Exclusão de Registros')

        # Excluir Participante
        if st.checkbox('Excluir Participante'):
            participantes = get_participantes_dropdown()
            if participantes:
                participante_selecionado = st.selectbox(
                    'Selecione o Participante para Exclusão',
                    [f"ID: {p[0]}, Nome: {p[1]}, Idade: {p[2]}" for p in participantes]
                )
                participante_id = int(participante_selecionado.split(',')[0].split(':')[1].strip())

                if st.button('Excluir Participante'):
                    excluir_participante(participante_id)
                    st.success(f'Participante {participante_selecionado} excluído com sucesso!')
            else:
                st.warning('Nenhum participante cadastrado!')

        # Excluir Atividade
        if st.checkbox('Excluir Atividade'):
            atividades = get_atividades_dropdown()
            if atividades:
                atividade_selecionada = st.selectbox(
                    'Selecione a Atividade para Exclusão',
                    [f"ID: {a[0]}, Atividade: {a[1]}" for a in atividades]
                )
                atividade_id = int(atividade_selecionada.split(',')[0].split(':')[1].strip())

                if st.button('Excluir Atividade'):
                    excluir_atividade(atividade_id)
                    st.success(f'Atividade {atividade_selecionada} excluída com sucesso!')
            else:
                st.warning('Nenhuma atividade cadastrada!')

        # Excluir Frequência
        if st.checkbox('Excluir Frequência'):
            frequencias = visualizar_frequencia()
            if frequencias:
                frequencia_selecionada = st.selectbox(
                    'Selecione o Registro de Frequência para Exclusão',
                    [f"ID: {f[0]}, Nome: {f[1]}, Atividade: {f[2]}, Data: {f[3]}" for f in frequencias]
                )
                frequencia_id = int(frequencia_selecionada.split(',')[0].split(':')[1].strip())

                if st.button('Excluir Frequência'):
                    excluir_frequencia(frequencia_id)
                    st.success(f'Frequência {frequencia_selecionada} excluída com sucesso!')
            else:
                st.warning('Nenhum registro de frequência cadastrado!')

    # Exibir relatórios
    elif choice == 'Relatórios':
        st.subheader('Relatórios de Participantes, Atividades e Frequência')

        # Exibir participantes
        if st.checkbox('Visualizar Participantes'):
            st.subheader('Lista de Participantes')
            participantes = visualizar_participantes()
            for participante in participantes:
                st.write(f'ID: {participante[0]}')
                st.write(f'Nome: {participante[1]}')
                st.write(f'Idade: {participante[2]}')
                st.write(f'Gênero: {participante[3]}')
                st.write(f'Escolaridade: {participante[4]}')
                st.write(f'Data de Inscrição: {participante[5]}')
                st.write('---')

        # Exibir atividades
        if st.checkbox('Visualizar Atividades'):
            st.subheader('Lista de Atividades')
            atividades = visualizar_atividades()
            for atividade in atividades:
                st.write(f'ID: {atividade[0]}')
                st.write(f'Atividade: {atividade[1]}')
                st.write(f'Descrição: {atividade[2]}')
                st.write(f'Data da Atividade: {atividade[3]}')
                st.write('---')

        # Exibir frequência
        if st.checkbox('Visualizar Frequência'):
            st.subheader('Registro de Frequência')
            frequencia = visualizar_frequencia()
            for item in frequencia:
                presenca_text = 'Presente' if item[3] == 1 else 'Ausente'
                st.write(f'Nome do Participante: {item[1]}')
                st.write(f'Atividade: {item[2]}')
                st.write(f'Data da Atividade: {item[4]}')
                st.write(f'Presença: {presenca_text}')
                st.write('---')

        if st.checkbox('Visualizar Gráfico de Presença por Atividade e Data'):
            # Obter os dados e plotar o gráfico
            df_presenca = obter_dados_participantes_por_atividade()
            if not df_presenca.empty:
                plotar_grafico_barras(df_presenca)
            else:
                st.warning('Nenhuma frequência registrada com presença!')


elif authentication_status == False:
    st.error('Nome de usuário ou senha incorretos')
elif authentication_status == None:
    st.warning('Por favor, insira o nome de usuário e a senha')
