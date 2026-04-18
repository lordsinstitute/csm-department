# users/utility/llm_setup.py
from langchain.llms import LlamaCpp
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

class LLMInitializer:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME", "TheBloke/Llama-2-7B-Chat-GGML")
        self.model_file = os.getenv("MODEL_FILE", "llama-2-7b-chat.ggmlv3.q4_0.bin")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    
    def initialize_llm(self):
        if not self.model_name or not self.model_file:
            raise ValueError("MODEL_NAME and MODEL_FILE must be set in environment variables")
        
        print(f"Loading quantized model: {self.model_name}")
        
        from huggingface_hub import hf_hub_download
        model_path = hf_hub_download(
            repo_id=self.model_name,
            filename=self.model_file,
            resume_download=True
        )
        
        # Updated configuration
        n_gpu_layers = 40  # Use GPU if available
        n_batch = 512
        return LlamaCpp(
            model_path=model_path,
            n_gpu_layers=0,       # CPU only
            n_batch=64,           # Safe for CPU
            n_ctx=2048,           # Reasonable context
            f16_kv=True,          # Can stay enabled
            temperature=0.8,
            top_k=50,
            max_tokens=600,       # Longer responses
            streaming=True,
            verbose=False
        )
        
    def initialize_embeddings(self):
        return HuggingFaceEmbeddings(model_name=self.embedding_model)


