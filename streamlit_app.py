import streamlit as st
from openai import OpenAI
import os

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

# Inicializar o cliente OpenAI com OpenRouter
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
except Exception as e:
    st.error(f"Erro ao inicializar cliente: {e}")
    st.stop()

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
            # Fazer chamada para a API
            with st.spinner("Pensando..."):
                completion = client.chat.completions.create(
                    extra_body={},
                    model="z-ai/glm-4.5-air:free",
                    messages=st.session_state.messages,
                    stream=False
                )
            
            # Extrair resposta
            full_response = completion.choices[0].message.content
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_message = f"Erro ao obter resposta: {str(e)}"
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
