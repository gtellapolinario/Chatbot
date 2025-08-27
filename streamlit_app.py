"""
# Aplicação chatbot usando Streamlit e OpenRouter API
# llm's z.ai - glm4.5
"""
import json

import requests
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Chatbot OpenRouter",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "").strip()
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 Chatbot OpenRouter")
st.markdown("Powered by GLM-4.5-Air")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Insira sua chave API do OpenRouter"
    )
    st.markdown("""
                ##### GT-Medic ®                
                """)
    st.write(
        '- 🛠️ [Chave de API](https://openrouter.ai/z-ai/glm-4.5-air:free/api)')
    st.write(
        '- 🛠️ [Projeto](https://github.com/gtellapolinario/Chatbot/tree/master)')
    st.markdown("---")
    SHORT_MODELS = [
        ("GLM-4.5-Air (free)", "z-ai/glm-4.5-air:free"),
        ("GLM-4.5",           "z-ai/glm-4.5"),
    ]
    labels_r = [n for n, _ in SHORT_MODELS] + ["Custom…"]
    label_to_slug_r = {n: s for n, s in SHORT_MODELS}
    DEFAULT_SLUG_R = "z-ai/glm-4.5-air:free"
    default_idx_r = next((i for i, (_, s) in enumerate(
        SHORT_MODELS) if s == DEFAULT_SLUG_R), 0)
    chosen_label_r = st.radio(
        "Modelo", labels_r, index=default_idx_r, horizontal=True)
    if chosen_label_r == "Custom…":
        model = st.text_input(
            "Slug do modelo (OpenRouter)", value=DEFAULT_SLUG_R)
    else:
        model = label_to_slug_r[chosen_label_r]
    st.markdown("**Provider:** OpenRouter.ai")

    # Botão para limpar conversa
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("💾 Exportar Conversa")

    # Botão de download
    if st.session_state.messages:
        from datetime import datetime
        try:
            conversation_lines = []
            conversation_lines.append("=== CONVERSA CHATBOT OPENROUTER ===")
            conversation_lines.append(
                f"Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            conversation_lines.append(f"Modelo utilizado: {model}")
            conversation_lines.append("=" * 40)
            conversation_lines.append("")

            for i, message in enumerate(st.session_state.messages, 1):
                ROLE = "USUARIO" if message["role"] == "user" else "ASSISTENTE"
                conversation_lines.append(f"[{i}] {ROLE}:")
                CONTENT = str(message['content']).replace(
                    '\r', '').replace('\x00', '')
                conversation_lines.append(CONTENT)
                conversation_lines.append("")
                conversation_lines.append("-" * 40)
                conversation_lines.append("")
            CONVERSATION_CONTENT = "\n".join(conversation_lines)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            FILENAME = f"conversa_chatbot_{timestamp}.txt"

            st.download_button(
                label="📄 Baixar Conversa (TXT)",
                data=CONVERSATION_CONTENT.encode('utf-8'),
                file_name=FILENAME,
                mime="text/plain; charset=utf-8",
                use_container_width=True,
                help="Baixa toda a conversa atual em formato de texto"
            )
        except (OSError, ValueError) as e:
            st.error(f"Erro ao preparar arquivo para download: {str(e)}")

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

if not api_key:
    st.warning("Por favor, insira sua API key do OpenRouter no painel lateral.")
    st.info(
        "Você pode obter uma chave gratuita em [OpenRouter.ai](https://openrouter.ai)")
    st.stop()


def call_openrouter_api(messages, api_key_param, model_param):
    """
    Faz chamada para a API do OpenRouter usando requests
    api_key_param: chave da API
    model_param: modelo a ser usado
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key_param}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model_param,
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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        FULL_RESPONSE = ""
        try:
            with st.spinner("Pensando..."):
                api_response = call_openrouter_api(
                    st.session_state.messages, api_key, model)
            if api_response.status_code == 200:
                response_data = api_response.json()
                FULL_RESPONSE = response_data["choices"][0]["message"]["content"]
                message_placeholder.markdown(FULL_RESPONSE)
            else:
                ERROR_MESSAGE = f"Erro na API (Status {api_response.status_code}): {api_response.text}" # pylint: disable=line-too-long
                message_placeholder.error(ERROR_MESSAGE)
                FULL_RESPONSE = ERROR_MESSAGE
        except requests.exceptions.RequestException as e:
            ERROR_MESSAGE = f"Erro de conexão: {str(e)}"
            message_placeholder.error(ERROR_MESSAGE)
            FULL_RESPONSE = ERROR_MESSAGE
        except json.JSONDecodeError as e:
            ERROR_MESSAGE = f"Erro ao processar resposta: {str(e)}"
            message_placeholder.error(ERROR_MESSAGE)
            FULL_RESPONSE = ERROR_MESSAGE
    st.session_state.messages.append(
        {"role": "assistant", "content": FULL_RESPONSE})

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    Este chatbot utiliza o modelo GLM-4.5-Air através da API do OpenRouter
    </div>
    """,
    unsafe_allow_html=True
)
