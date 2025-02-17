import ollama

def test_tinyllama():

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
                print("Goodbye!")
                break
        
        # Call the model using ollama
        response = ollama.chat(model="TinyLlama", messages=[{"role": "user", "content": user_input}])
        
        # Print the response from the model
        print(response["message"]["content"])

if __name__ == "__main__":
    test_tinyllama()
