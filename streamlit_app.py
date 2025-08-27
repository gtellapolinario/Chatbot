import streamlit as st
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Chatbot OpenRouter",
    page_icon="🤖",
    layout="centered"
)

# Título principal
st.title("🤖 Chatbot OpenRouter")
st.markdown("Powered by GLM-4.5-Air")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Input para API key
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Insira sua chave API do OpenRouter"
    )
    
    st.markdown("---")
    
    # Informações sobre o modelo
    st.markdown("**Modelo:** z-ai/glm-4.5-air:free")
    st.markdown("**Provider:** OpenRouter.ai")
    
    # Botão para limpar conversa
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Verificar se a API key foi fornecida
if not api_key:
    st.warning("Por favor, insira sua API key do OpenRouter no painel lateral.")
    st.info("Você pode obter uma chave gratuita em [OpenRouter.ai](https://openrouter.ai)")
    st.stop()

# Função para fazer chamada à API usando requests
def call_openrouter_api(messages, api_key):
    """Faz chamada para a API do OpenRouter usando requests"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-streamlit-app.com",
        "X-Title": "Streamlit Chatbot"
    }
    
    data = {
        "model": "z-ai/glm-4.5-air:free",
        "messages": messages
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response

# Inicializar mensagens no session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibir mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Exibir resposta do assistente
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Fazer chamada para a API usando requests
            with st.spinner("Pensando..."):
                response = call_openrouter_api(st.session_state.messages, api_key)
            
            if response.status_code == 200:
                response_data = response.json()
                full_response = response_data["choices"][0]["message"]["content"]
                message_placeholder.markdown(full_response)
            else:
                error_message = f"Erro na API (Status {response.status_code}): {response.text}"
                message_placeholder.error(error_message)
                full_response = error_message
            
        except requests.exceptions.RequestException as e:
            error_message = f"Erro de conexão: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
        except json.JSONDecodeError as e:
            error_message = f"Erro ao processar resposta: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
        except Exception as e:
            error_message = f"Erro inesperado: {str(e)}"
            message_placeholder.error(error_message)
            full_response = error_message
    
    # Adicionar resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Rodapé informativo
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    Este chatbot utiliza o modelo GLM-4.5-Air através da API do OpenRouter
    </div>
    """,
    unsafe_allow_html=True
)
