# Projeto de Incentivo à Prática ESportiva para Crianças e Adolescentes

Instale os pacotes necessários com

```bash
pip install -r requirements.txt 
```

altere o arquivo `config.yaml` de credenciais se necessário, onde as senhas podem ser geradas por:

```python
stauth.Hasher(['suasenha']).generate()
```

rode o projeto com:

```bash
streamlit run app.py
```