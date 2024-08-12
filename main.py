import os
from supabase import create_client, Client
import folium
from folium.plugins import MarkerCluster
from flask import  Flask, request, render_template, jsonify
from flask import request, redirect, url_for, session
from flask import Flask, render_template, request, render_template_string
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from flask_cors import CORS
import datetime



# Classe BancoDeDados para interação com Supabase
class BancoDeDados:
    def __init__(self):
        self.url = "https://fgvqqqgcyujztipjpsta.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZndnFxcWdjeXVqenRpcGpwc3RhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTkzNDQ3MTYsImV4cCI6MjAzNDkyMDcxNn0.d0uL6yzSavALzO76gXopEdJ0fPVW6FVL9SUCQr1p0A4"
        self.client = create_client(self.url, self.key)
        self.session=None

    def pegar_coletivos(self):
        response = self.client.table("coletivo").select("*").execute()
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao buscar dados: {response.error.message}")
            return None
        return response.data

    def inserir_coletivo(self, dados_formulario):
        # Inserir na tabela do Supabase
        response = self.client.table("coletivo").insert([
            {
                "nome": dados_formulario.get("nome_projeto", ""),
                "email": dados_formulario.get("email", ""),
                "senha": dados_formulario.get("senha", ""),
                "descricao": dados_formulario.get("DescColetivo", ""),
                "sigla": dados_formulario.get("sigla", ""),
                "latitude": dados_formulario.get("latitude", ""),
                "longitude": dados_formulario.get("longitude", ""),
                "data_fundacao": dados_formulario.get("data_fundacao", ""),
                "link": dados_formulario.get("link", ""),
                "nome_resp": dados_formulario.get("nome_resp", ""),
                "created_at": datetime.datetime.now().isoformat(),
                # Você pode adicionar mais campos como coordenadas, latitude, longitude, etc.
            }
        ]).execute()
        if 'data' in str(response):
            self.session=self.consultar_coletivo(dados_formulario.get("email"), dados_formulario.get("senha"))
            return True
    def atualizar_coletivo(self, dados_formulario, id_coletivo):
        # Atualizar na tabela do Supabase
        response = self.client.table("coletivo").update({
            "nome": dados_formulario.get("nome_projeto", ""),
            "email": dados_formulario.get("email", ""),
            "senha": dados_formulario.get("senha", ""),
            "descricao": dados_formulario.get("descricao", ""),
            "sigla": dados_formulario.get("sigla", ""),
            "latitude": dados_formulario.get("latitude", ""),
            "longitude": dados_formulario.get("longitude", ""),
            "data_fundacao": dados_formulario.get("data_fundacao", ""),
            "link": dados_formulario.get("link", ""),
            "nome_resp": dados_formulario.get("nome_resp", ""),
            # Adicione mais campos conforme necessário
        }).eq('id', id_coletivo).execute()
        
        if response.data:
            self.session = self.consultar_coletivo(dados_formulario.get("email"), dados_formulario.get("senha"))
            return True
        else:
            return False

    
    def consultar_coletivo(self, email, senha):
        # Consultar na tabela do Supabase usando email e senha
        response = self.client.table("coletivo").select("*").eq("email", email).eq("senha", senha).execute()

        if response.data:
            
            # Se os dados forem encontrados, retornar as informações do coletivo
            return response.data
        else:
            # Se nenhum dado for encontrado, retornar None ou uma mensagem de erro
            return None

# Inicializa o aplicativo Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = 'afldfwerlw4342'
CORS(app)

@app.route('/')

def index():
    sigla_coletivo = session.get('coletivos', {})[0].get('nome_resp', 'Login')
    if sigla_coletivo=="":
        link_login='/login'
        sigla_coletivo='Login'
    else:
        link_login='/adm'
    

    # Instancia a classe BancoDeDados e pega os dados dos coletivos
    db = BancoDeDados()
    dados_coletivo = db.pegar_coletivos()

    # Cria um mapa com Folium
    mapa = folium.Map(location=[-22.789812291778134, -43.31623672627236], zoom_start=13)
    marker_cluster = MarkerCluster(maxClusterRadius=20).add_to(mapa)

    # Adiciona os marcadores com ícones personalizados ao mapa
    if dados_coletivo:
        for coletivo in dados_coletivo:
            lat = coletivo.get('latitude')
            long = coletivo.get('longitude')
            nome = coletivo.get('nome', 'Sem nome')
            link = coletivo.get('link', '')
            descricao = coletivo.get('descricao', 'Sem descrição')
            email = coletivo.get('email', 'Email não informado')
            if lat and long:
                # Exemplo de ícone personalizado local
                icon_url = 'static/src/icon_.ico'  # Substitua com o caminho para o seu ícone local
                icon = folium.features.CustomIcon(icon_url, icon_size=(20, 20))

                # HTML para o Popup
                popup_html = f"""
                <a href="{link}" target="_blank">
                    <link rel="stylesheet" href="static/css/index.css">                
                    <div class="card">
                        <h3 class="card__title">{nome}</h3>
                        <p class="card__content">{descricao[:250]}...</p>
                        <div class="card__date">{email}</div>
                        <div class="card__arrow">
                        <a href="{link}" target="_blank">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" height="15" width="15">
                                <path fill="#fff" d="M13.4697 17.9697C13.1768 18.2626 13.1768 18.7374 13.4697 19.0303C13.7626 19.3232 14.2374 19.3232 14.5303 19.0303L20.3232 13.2374C21.0066 12.554 21.0066 11.446 20.3232 10.7626L14.5303 4.96967C14.2374 4.67678 13.7626 4.67678 13.4697 4.96967C13.1768 5.26256 13.1768 5.73744 13.4697 6.03033L18.6893 11.25H4C3.58579 11.25 3.25 11.5858 3.25 12C3.25 12.4142 3.58579 12.75 4 12.75H18.6893L13.4697 17.9697Z"></path>
                            </svg>
                        </a>
                        </div>
                    </div>
                    </a>
                    """
                marker = folium.Marker(
                    location=[lat, long],
                    popup=folium.Popup(popup_html, max_width=400),
                    icon=icon,
                    tooltip="<p>Clique para saber Mais!</p>"  # Adiciona um Tooltip com o nome do coletivo
                )
                marker.add_to(marker_cluster)

    # Gera o HTML do mapa
    mapa_html = mapa._repr_html_()

    # Template HTML para renderizar o mapa
    template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Mapa de Coletivos</title>
        <link rel="stylesheet" href="static/css/index.css">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="static/js/coletivos.js"></script> <!-- Inclua o arquivo coletivos.js -->
    </head>
    <body>
        <header class="header">
            <div class="logoBox">
                <img class="logo" src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/bxdMaps.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL2J4ZE1hcHMucG5nIiwiaWF0IjoxNzE5MzU2MDI5LCJleHAiOjE3NTA4OTIwMjl9.lRqtIWFLXUY803SddFO_aiO4V5pBPlTXbuOadmAn2rA&t=2024-06-25T22%3A53%3A49.278Z" alt="logo">
            </div>
            <a href="/API">API</a>
            <a href="/cadastro">Cadastro</a>
            <a href="/#roll">Mapa Cultural</a>
            <a class="buttonLink" id="buttonLink" href="/adm" target="">Gerenciar</a>
            <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const buttonLink = document.getElementById('buttonLink');

            if (buttonLink) {{
                fetch('static/coletivos.json')
                    .then(response => response.json())
                    .then(data => {{
                        // Verifica se a variável data é um array e tem pelo menos um item
                        if (Array.isArray(data) && data.length > 0) {{
                            buttonLink.textContent = 'Gerenciar';
                            buttonLink.href = '/adm';
                        }} else {{
                            buttonLink.textContent = 'Login';
                            buttonLink.href = '/login';
                        }}
            }})
                    .catch(error => {{
                        console.error('Erro ao carregar o JSON:', error);
                        // Caso ocorra um erro ao carregar o JSON, exibe uma mensagem padrão
                        buttonLink.textContent = 'Login';
                        buttonLink.href = '/login';
                    }});
            }}
        }});
    </script>
        </header>

        <script>
            // Função para centralizar o mapa ao abrir o popup
            function centralizarMapa(lat, long) {{
                var map = L.map('map');
                map.setView([lat, long], 15);  // Ajuste o zoom (neste exemplo, 15) para o nível desejado
            }}
        </script>

        <main class="mainContainer">
            <div class="nav" style="display: flex; flex-direction: row">
                <section class="mapDescriptionSection">
                    <div class="titleContainer">
                        <h2 class="descTitle">Você realmente conhece a Baixada?</h2>
                        <p class="descParagraph">
                            O Mapa da Baixada promove a cultura, história e a arte local
                            valorizando o território. Se você é artista, representa um espaço ou
                            é agente de turismo, cadastre-se em nosso mapa e nos ajude a
                            divulgar a Baixada Fluminense.
                        </p>
                        <p class="descParagraph">
                            Aqui, você encontrará um pouco da história dos municípios e detalhes
                            sobre artistas incluindo sua biografia, obras, além de espaços
                            culturais, agentes de turismo, agenda de shows e atividades. O
                            MapaBXd é história, cultura, turismo e o que faz a Baixada
                            Fluminense tão incrível, a sua gente.
                        </p>
                        <a class="buttonLink" href="/cadastro" target="">Cadastre-se</a>
                    </div>
                </section>
                <img class="geo_bxd" src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/Design_sem_nome__9_.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL0Rlc2lnbl9zZW1fbm9tZV9fOV8ucG5nIiwiaWF0IjoxNzE5MzU4MDI2LCJleHAiOjE3NTA4OTQwMjZ9.9_YSQAN8xAVdlHpOarUTBTOndPvN84KmUlaPurzjZ8U&t=2024-06-25T23%3A27%3A06.274Z">
            </div>
            <div class="filtros" id="roll"></div>
            <section class="mapDescriptionSectionRight">
                <div class="cemPorCento" style="width: 100vw; max-height:70vh; padding: 15vh;padding-top: 0;">
                    <div class="map-container" style="margin:auto;" id="map">
                        {mapa_html}
                    </div>
                </div>
            </section>
            <span style="visibility:hidden;"></span>
        </main>
         <div class="nav" style="display: flex; flex-direction: row">
                <section class="mapDescriptionSection">
                    <div class="titleContainer">
                        <h2 class="descTitle">Conheça a nossa API!</h2>
                        <p class="descParagraph">
                           Para acessar todos os dados disponíveis pelo Mapas BXD em formato JSON, realize uma requisição HTTP utilizando o método GET para o endpoint acima. Isso permitirá que você recupere as informações necessárias de maneira eficiente e padronizada para alimentar seu sistema, ou outro fim.
                        </p>
                       
                        <a class="buttonLink" href="/API" target="">Conhecer a API</a>
                    </div>
                </section>
                <img class="geo_bxd" style="width:30%;"src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/api.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL2FwaS5wbmciLCJpYXQiOjE3MTk2MTAzOTUsImV4cCI6MTc1MTE0NjM5NX0.ik6m7FyL8G9WRX_Zp-7mTd9euK9zujxlAQ6qH-25cJM&t=2024-06-28T21%3A33%3A15.695Z">
            </div>
        <footer class="footer">
            <ul class="footerContatcsList">
                <li>
                    <a class="footerContatcsLink" target="_blank" href="https://www.instagram.com/infocria/">
                        <span> InfoCria </span>
                        <img class="footerContatcsLogo" src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/instagram.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL2luc3RhZ3JhbS5wbmciLCJpYXQiOjE3MTk1NTQzMzAsImV4cCI6MTc1MTA5MDMzMH0.Hx6qB-bbhOsWMEQOAlSvbf45hBtbGAVotaswgmQg6OI&t=2024-06-28T05%3A58%3A50.993Z" alt="instagram logo">
                    </a>
                </li>
                <li>
                    <a class="footerContatcsLink" target="_blank" href="https://www.instagram.com/eca.aworan/">
                        <span> ECA Àwòrán </span>
                        <img class="footerContatcsLogo" src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/instagram.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL2luc3RhZ3JhbS5wbmciLCJpYXQiOjE3MTk1NTQzMzAsImV4cCI6MTc1MTA5MDMzMH0.Hx6qB-bbhOsWMEQOAlSvbf45hBtbGAVotaswgmQg6OI&t=2024-06-28T05%3A58%3A50.993Z" alt="instagram logo">
                    </a>
                </li>
                <li>
                    <a class="footerContatcsLink" target="_blank" href="https://www.instagram.com/eca.aworan/">
                        <span> GCD Na Baixada Fluminense</span>
                        <img class="footerContatcsLogo" src="https://fgvqqqgcyujztipjpsta.supabase.co/storage/v1/object/sign/foto_coletivo/instagram.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJmb3RvX2NvbGV0aXZvL2luc3RhZ3JhbS5wbmciLCJpYXQiOjE3MTk1NTQzMzAsImV4cCI6MTc1MTA5MDMzMH0.Hx6qB-bbhOsWMEQOAlSvbf45hBtbGAVotaswgmQg6OI&t=2024-06-28T05%3A58%3A50.993Z" alt="instagram logo">
                    </a>
                </li>
            </ul>
            <p class="footerText" id="footer">
                Para mais informações, entre em contato conosco!
                <a href="mailto:conscienciadecria@gmail.com">conscienciadecria@gmail.com</a>
            </p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(template)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    banco = BancoDeDados()
    if request.method == 'POST':
        dados_formulario = request.form  # Ajuste se necessário para request.json ou request.form
        inserido = banco.inserir_coletivo(dados_formulario)
        if inserido:
            return redirect(url_for('index'))
        return "Erro ao inserir dados.", 500

@app.route('/login_form', methods=['POST'])
def login_form():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        db = BancoDeDados()
        coletivos = db.consultar_coletivo(email, senha)
        if coletivos:
            session['coletivos'] = coletivos
            # Atualiza ou cria o arquivo coletivos.json
            atualizar_coletivos_json(coletivos)
            return redirect(url_for('adm'))
        else:
            return render_template('failure.html', message="Credenciais inválidas. Tente novamente.")
        
@app.route('/atualizar_coletivo', methods=['POST'])
def atualizar_coletivo():
    if request.method == 'POST':
        dados_formulario = request.json
        id_coletivo = dados_formulario.get('id')

        db = BancoDeDados()
        sucesso = db.atualizar_coletivo(dados_formulario, id_coletivo)
        atualizar_coletivos_json(db.consultar_coletivo(dados_formulario.get('email'), dados_formulario.get('senha')))
        if sucesso:
            
            return {'success': True}, 200
        else:
            return {'success': False, 'message': 'Erro ao atualizar o coletivo'}, 400

def atualizar_coletivos_json(coletivos):
    # Caminho do arquivo onde os coletivos serão salvos
    caminho_arquivo = os.path.join('static', 'coletivos.json')

    # Converte os coletivos para JSON
    coletivos_json = json.dumps(coletivos, indent=4, ensure_ascii=False)

    # Escreve o conteúdo no arquivo coletivos.json
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(coletivos_json)


@app.route('/adm')
def adm():
    
    return render_template('adm.html')

@app.route('/API')
def API():
    return render_template('API.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/_api')
def api():
    db = BancoDeDados()
    dados_coletivo = db.pegar_coletivos()
    return jsonify(dados_coletivo)


@app.route('/clear-coletivos', methods=['POST'])
def clear_coletivos():
    try:
        # Caminho para o arquivo JSON
        file_path = 'static/coletivos.json'
        
        # Limpa o conteúdo do arquivo JSON
        with open(file_path, 'w') as file:
            json.dump([], file)  # Escreve um array vazio

        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)