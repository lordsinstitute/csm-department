from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
MODEL_CACHE_DIR = "local_llm_cache" 

print(f"1. Attempting to download and initialize {MODEL_NAME}...")
print(f"   (This may take several minutes and download several GBs)")

try:
    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=MODEL_CACHE_DIR)
    print("   Tokenizer loaded.")
    
    # 2. Load Model (Force CPU usage for stability, unless you have a strong GPU)
    # This is the step that downloads the large file (approx 4-5 GB)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, 
        trust_remote_code=True, 
        cache_dir=MODEL_CACHE_DIR,
        torch_dtype=torch.float32, # Use float32 for CPU compatibility
    ).to('cpu')
    print("   Model loaded successfully to CPU.")
    
    # 3. Test a quick prediction
    test_prompt = "You are a medical consultant. What are the key symptoms of late-stage CKD?"
    input_ids = tokenizer.encode(test_prompt, return_tensors="pt")
    
    output = model.generate(input_ids, max_length=150, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    print("\n--- Test Prediction Output ---")
    print(response)
    print("------------------------------")
    
    print("\n✅ Success! Model is ready for Django integration.")

except Exception as e:
    print(f"\n❌ ERROR during model download/test: {e}")
    print("   Check your internet connection and ensure your torch installation is correct.")
