import os

from openai import OpenAI


def load_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key.strip():
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não foi definida."
        )
    return api_key


def main() -> None:
    openai_api_key = load_api_key()
    client = OpenAI(api_key=openai_api_key)
    conversation = [
        {
            "role": "system",
            "content": (
                "Você é uma assistente de conversa em português. Responda de forma clara, "
                "educada e útil."
            ),
        }
    ]

    print("Chat com IA iniciado. Escreva 'sair' ou 'quit' para encerrar.")

    while True:
        try:
            user_input = input("Você: ").strip()
        except KeyboardInterrupt:
            print("\nEncerrando chat...")
            break

        if not user_input:
            continue
        if user_input.lower() in {"sair", "quit", "exit"}:
            print("Encerrando chat...")
            break

        conversation.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            max_tokens=500,
        )

        choice = response.choices[0]
        message = getattr(choice, "message", None)
        if message is None:
            print("Erro: resposta inválida da IA.")
            break

        text = (
            message.content
            if hasattr(message, "content")
            else message.get("content", "")
        )
        print(f"IA: {text}\n")
        conversation.append({"role": "assistant", "content": text})


if __name__ == "__main__":
    main()
