import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from .config_loader import load_config


class ModelLoader:
    def __init__(self, provider: str = "groq"):
        print("Loading config...")
        self.config = load_config()
        self.provider = provider.lower()

    def load_llm(self):
        """Return a fully configured LangChain LLM."""

        if self.provider == "groq":
            return self._load_groq()

        elif self.provider == "openai":
            return self._load_openai()

        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _load_groq(self):
        cfg = self.config["llm"]["groq"]

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY missing in environment variables")

        return ChatGroq(
            api_key=api_key,
            model=cfg["model_name"],
            temperature=cfg["temperature"],
            max_tokens=cfg["max_tokens"],
            timeout=cfg["timeout"],
            model_kwargs={
                "top_p": cfg["top_p"],
                "frequency_penalty": cfg["frequency_penalty"],
                "presence_penalty": cfg["presence_penalty"],
            },
        )

    def _load_openai(self):
        cfg = self.config["llm"]["openai"]

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY missing in environment variables")

        return ChatOpenAI(
            api_key=api_key,
            model=cfg["model_name"],
            temperature=cfg["temperature"],
            max_tokens=cfg["max_tokens"],
            timeout=cfg["timeout"],
            model_kwargs={
                "top_p": cfg["top_p"],
                "frequency_penalty": cfg["frequency_penalty"],
                "presence_penalty": cfg["presence_penalty"],
            },
        )
