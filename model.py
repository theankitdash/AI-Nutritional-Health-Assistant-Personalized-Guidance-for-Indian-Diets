# Simple chatbot logic for testing without external libraries
def generate_bot_response(user_message: str) -> str:
    # Basic responses based on the user's input
    if "hello" in user_message.lower():
        return "Hello! How can I help you today?"
    elif "how are you" in user_message.lower():
        return "I'm just a simple bot, but I'm doing great! How about you?"
    elif "bye" in user_message.lower():
        return "Goodbye! Have a nice day!"
    else:
        return "I'm sorry, I don't understand. Can you please rephrase?"

if __name__ == "__main__":
    # Example: Testing the chatbot with a sample user message
    user_input = input()
    response = generate_bot_response(user_input)
    print(f"Bot: {response}")
