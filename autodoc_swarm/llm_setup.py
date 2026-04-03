import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm(provider: str, model: str) -> BaseChatModel:
    """
    Returns the appropriate Langchain ChatModel based on provider.
    Supported providers: openrouter, anthropic, openai, google.
    """
    provider = provider.lower()

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set.")
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        return ChatAnthropic(
            api_key=api_key,
            model_name=model
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        return ChatOpenAI(
            api_key=api_key,
            model=model
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")
