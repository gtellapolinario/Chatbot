import streamlit as st
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="Chatbot OpenRouter",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "").strip()

# Inicializar mensagens no session state PRIMEIRO
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    
    st.markdown("""
                ##### GT-Medic ®                
                """)
    st.write('- 🛠️ [Chave de API](https://openrouter.ai/z-ai/glm-4.5-air:free/api)')
    st.write('- 🛠️ [Projeto](https://github.com/gtellapolinario/Chatbot/tree/master)')
    
    st.markdown("---")

    # Seleção de modelos
    SHORT_MODELS = [
        ("GLM-4.5-Air (free)", "z-ai/glm-4.5-air:free"),
        ("GLM-4.5",           "z-ai/glm-4.5"),
    ]
    labels_r = [n for n, _ in SHORT_MODELS] + ["Custom…"]
    label_to_slug_r = {n: s for n, s in SHORT_MODELS}

    default_slug_r = "z-ai/glm-4.5-air:free"
    default_idx_r = next((i for i, (_, s) in enumerate(
        SHORT_MODELS) if s == default_slug_r), 0)

    chosen_label_r = st.radio(
        "Modelo", labels_r, index=default_idx_r, horizontal=True)
    if chosen_label_r == "Custom…":
        model = st.text_input(
            "Slug do modelo (OpenRouter)", value=default_slug_r)
    else:
        model = label_to_slug_r[chosen_label_r]

    st.markdown("**Provider:** OpenRouter.ai")

    # Botão para limpar conversa
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("💾 Exportar Conversa")

    # Botão de download da conversa
    if st.session_state.messages:
        from datetime import datetime

        # Gerar conteúdo da conversa com codificação segura
        try:
            conversation_lines = []
            conversation_lines.append("=== CONVERSA CHATBOT OPENROUTER ===")
            conversation_lines.append(
                f"Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            conversation_lines.append(f"Modelo utilizado: {model}")
            conversation_lines.append("=" * 40)
            conversation_lines.append("")

            for i, message in enumerate(st.session_state.messages, 1):
                role = "USUARIO" if message["role"] == "user" else "ASSISTENTE"
                conversation_lines.append(f"[{i}] {role}:")
                # Sanitizar o conteúdo removendo caracteres problemáticos
                content = str(message['content']).replace(
                    '\r', '').replace('\x00', '')
                conversation_lines.append(content)
                conversation_lines.append("")
                conversation_lines.append("-" * 40)
                conversation_lines.append("")

            conversation_content = "\n".join(conversation_lines)

            # Nome do arquivo seguro
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversa_chatbot_{timestamp}.txt"

            st.download_button(
                label="📄 Baixar Conversa (TXT)",
                data=conversation_content.encode('utf-8'),
                file_name=filename,
                mime="text/plain; charset=utf-8",
                use_container_width=True,
                help="Baixa toda a conversa atual em formato de texto"
            )

        except Exception as e:
            st.error(f"Erro ao preparar arquivo para download: {str(e)}")

        # Mostrar estatísticas da conversa
        total_messages = len(st.session_state.messages)
        user_messages = sum(
            1 for msg in st.session_state.messages if msg["role"] == "user")
        assistant_messages = total_messages - user_messages

        st.info(f"""
        **Estatísticas da Conversa:**
        - Total de mensagens: {total_messages}
        - Perguntas do usuário: {user_messages}
        - Respostas do assistente: {assistant_messages}
        """)
    else:
        st.info("Inicie uma conversa para habilitar a exportação.")

# Verificar se a API key foi fornecida
if not api_key:
    st.warning("Por favor, insira sua API key do OpenRouter no painel lateral.")
    st.info(
        "Você pode obter uma chave gratuita em [OpenRouter.ai](https://openrouter.ai)")
    st.stop()

# Função para fazer chamada à API usando requests


def call_openrouter_api(messages, api_key, model):
    """Faz chamada para a API do OpenRouter usando requests"""
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": (
            [{"role": "system", "content": SYSTEM_PROMPT}] if SYSTEM_PROMPT else []
        ) + messages
    }
    response = requests.post(url, headers=headers,
                             data=json.dumps(data), timeout=30)
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
                response = call_openrouter_api(
                    st.session_state.messages, api_key, model)

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
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

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
