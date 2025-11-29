from utils.model_loader import ModelLoader

loader = ModelLoader(provider="groq")
llm = loader.load_llm()

response = llm.invoke("Explain quantum computing in 3 lines.")
print(response.content)
