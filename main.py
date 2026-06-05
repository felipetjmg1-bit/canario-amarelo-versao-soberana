"""
Chat-GPT Aurora - Speckle Automate Function
Integrando IA (Aurora) para análise inteligente de dados BIM no Speckle.
"""

import os
from pydantic import Field, SecretStr
from flatten import flatten_base

try:
    from speckle_automate import (
        AutomateBase,
        AutomationContext,
        execute_automate_function,
    )
except ImportError:
    from speckle_automate_stub import (
        AutomateBase,
        AutomationContext,
        execute_automate_function,
    )

class FunctionInputs(AutomateBase):
    """Parâmetros de entrada para a função Aurora AI."""
    
    openai_api_key: SecretStr = Field(
        title="OpenAI API Key",
        description="Chave para acessar o modelo Aurora/GPT para análise."
    )
    analysis_prompt: str = Field(
        default="Realize uma auditoria técnica rigorosa. Verifique se há duplicidade de IDs, inconsistências de materiais e se a hierarquia espacial faz sentido para um modelo de construção.",
        title="Prompt de Análise Avançada",
        description="Instruções específicas para a auditoria de IA."
    )

def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """
    Função que recebe dados do Speckle e os envia para análise via IA Aurora.
    """
    # 1. Receber dados do Speckle
    version_root_object = automate_context.receive_version()
    flat_objects = list(flatten_base(version_root_object))
    
    # 2. Preparar sumário detalhado e validação de regras
    object_types = {}
    missing_params = []
    for obj in flat_objects[:150]:
        t = obj.speckle_type
        object_types[t] = object_types.get(t, 0) + 1
        
        # Regra de negócio: Objetos estruturais devem ter material definido
        if "Structure" in t and not hasattr(obj, "material"):
            missing_params.append(f"Objeto {obj.id} ({t}) sem material definido.")

    data_summary = f"Relatório de Dados BIM:\n"
    data_summary += f"- Total de objetos: {len(flat_objects)}\n"
    data_summary += f"- Amostra para análise profunda: {len(flat_objects[:150])}\n"
    data_summary += "Distribuição de tipos:\n"
    for t, count in object_types.items():
        data_summary += f"  * {t}: {count}\n"
    
    if missing_params:
        data_summary += "\nInconsistências detectadas por regras locais:\n"
        data_summary += "\n".join(missing_params[:10])

    if not function_inputs.openai_api_key or not function_inputs.openai_api_key.get_secret_value().strip():
        analysis_result = (
            "Nenhuma chave de API OpenAI foi fornecida. "
            "O relatório local foi gerado com base nos dados disponíveis."
        )
        automate_context.mark_run_success(
            "Análise Aurora concluída (modo local, sem OpenAI)."
        )
        with open("relatorio_aurora.md", "w") as f:
            f.write(f"# Relatório de Análise Aurora AI\n\n{analysis_result}")
        automate_context.store_file_result("relatorio_aurora.md")
        return

    try:
        from openai import OpenAI

        client = OpenAI(api_key=function_inputs.openai_api_key.get_secret_value())
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Usando um modelo eficiente
            messages=[
                {"role": "system", "content": "Você é a Aurora, uma especialista em análise de dados BIM e Speckle."},
                {"role": "user", "content": f"{function_inputs.analysis_prompt}\n\nDados do Modelo:\n{data_summary}"}
            ]
        )

        choice = response.choices[0]
        message = getattr(choice, "message", None)
        if message is None:
            raise ValueError("Resposta inválida da OpenAI: campo 'message' ausente.")

        analysis_result = (
            message.content
            if hasattr(message, "content")
            else message.get("content", "")
        )

        if not analysis_result:
            raise ValueError("Resposta da OpenAI não contém conteúdo de análise.")

        automate_context.mark_run_success(f"Análise Aurora concluída: {analysis_result[:200]}...")

        with open("relatorio_aurora.md", "w") as f:
            f.write(f"# Relatório de Análise Aurora AI\n\n{analysis_result}")

        automate_context.store_file_result("relatorio_aurora.md")

    except ImportError as e:
        automate_context.mark_run_failed(
            f"Biblioteca OpenAI não está instalada: {str(e)}"
        )
    except Exception as e:
        automate_context.mark_run_failed(f"Falha na integração com Aurora AI: {str(e)}")

if __name__ == "__main__":
    execute_automate_function(automate_function, FunctionInputs)
