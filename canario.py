import base64
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI

OUTPUT_DIR = Path("outputs")
PERSONA_FILE = Path("persona.txt")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não foi definida."
        )
    return api_key


def get_persona() -> str:
    if PERSONA_FILE.exists():
        return PERSONA_FILE.read_text(encoding="utf-8").strip()
    return (
        "Você é Canário Amarelo, uma inteligência artificial brasileira especializada "
        "em conversar de forma clara, criativa e prática sobre arquitetura, BIM, "
        "projetos, tecnologia e conteúdo multimídia."
    )


def save_persona(text: str) -> None:
    PERSONA_FILE.write_text(text.strip(), encoding="utf-8")


def save_bytes(data: bytes, filename: str) -> Path:
    path = OUTPUT_DIR / filename
    path.write_bytes(data)
    return path


def dictize(item):
    if hasattr(item, "model_dump"):
        return item.model_dump()
    if hasattr(item, "dict"):
        return item.dict()
    if hasattr(item, "to_dict"):
        return item.to_dict()
    return item


def extract_text_from_response(response):
    data = dictize(response)
    if isinstance(data, dict) and "choices" in data:
        choice = data["choices"][0]
        if isinstance(choice, dict) and "message" in choice:
            message = choice["message"]
            return message.get("content") if isinstance(message, dict) else None
    return None


def chat_loop(client: OpenAI) -> None:
    print("Iniciando chat com Canário Amarelo. Digite 'sair' para encerrar.")
    system_prompt = get_persona()
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("Você: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"sair", "quit", "exit"}:
            print("Encerrando chat...")
            break

        messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            text = extract_text_from_response(response)
            if not text:
                raise RuntimeError("Resposta da IA inconsistente.")

            print(f"IA: {text}\n")
            messages.append({"role": "assistant", "content": text})
        except Exception as exc:
            print(f"Erro durante a conversa: {exc}")
            break


def generate_image(client: OpenAI) -> None:
    prompt = input("Digite o prompt de imagem para Canário Amarelo: ").strip()
    if not prompt:
        print("Prompt vazio. Cancelando geração de imagem.")
        return

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json",
        )
        data = dictize(response)
        image_data = None

        if isinstance(data, dict) and "data" in data and data["data"]:
            item = data["data"][0]
            image_data = item.get("b64_json") or item.get("b64_json")

        if not image_data:
            raise RuntimeError("Não foi possível extrair a imagem da resposta.")

        image_bytes = base64.b64decode(image_data)
        filename = f"image_{datetime.now():%Y%m%d_%H%M%S}.png"
        saved = save_bytes(image_bytes, filename)
        print(f"Imagem gerada e salva em: {saved}")
    except Exception as exc:
        print(f"Erro na geração de imagem: {exc}")


def generate_video(client: OpenAI) -> None:
    prompt = input("Digite o prompt de vídeo para Canário Amarelo: ").strip()
    if not prompt:
        print("Prompt vazio. Cancelando geração de vídeo.")
        return

    try:
        response = client.videos.create(
            model="gpt-video-1",
            prompt=prompt,
            size="1024x1024",
            seconds=10,
        )
        data = dictize(response)

        if isinstance(data, dict) and "output" in data and data["output"]:
            first = data["output"][0]
            if isinstance(first, dict):
                if "uri" in first and first["uri"]:
                    print(f"Vídeo criado. Link de download: {first['uri']}")
                    return
                if "b64_json" in first and first["b64_json"]:
                    video_bytes = base64.b64decode(first["b64_json"])
                    filename = f"video_{datetime.now():%Y%m%d_%H%M%S}.mp4"
                    saved = save_bytes(video_bytes, filename)
                    print(f"Vídeo gerado e salvo em: {saved}")
                    return

        raise RuntimeError("Não foi possível extrair o vídeo da resposta.")
    except Exception as exc:
        print(f"Erro na geração de vídeo: {exc}")


def train_canario() -> None:
    print("Defina o estilo e a personalidade de Canário Amarelo.")
    print("Descreva como você quer que a IA responda e quais valores ela deve seguir.")
    text = input("Descrição de treino: ").strip()
    if not text:
        print("Descrição vazia. O treino não foi atualizado.")
        return
    save_persona(text)
    print("Canário Amarelo foi treinado com a nova personalidade.")


def main() -> None:
    try:
        openai_api_key = load_api_key()
    except RuntimeError as exc:
        print(exc)
        return

    client = OpenAI(api_key=openai_api_key)

    while True:
        print("\n=== Canário Amarelo — Assistente Multimodal ===")
        print("1. Conversar com a IA")
        print("2. Criar imagem")
        print("3. Criar vídeo")
        print("4. Treinar / ajustar personalidade")
        print("5. Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            chat_loop(client)
        elif choice == "2":
            generate_image(client)
        elif choice == "3":
            generate_video(client)
        elif choice == "4":
            train_canario()
        elif choice == "5":
            print("Saindo. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
