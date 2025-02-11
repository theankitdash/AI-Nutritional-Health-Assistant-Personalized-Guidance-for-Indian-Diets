import ollama

# Test TinyLlama in Python
response = ollama.chat(model="tinyllama", messages=[{"role": "user", "content": "What are the health benefits of eating spinach?"}])
print(response["message"]["content"])
