import aioredis

# Redis Database Connection
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
}

# Initialize Redis connection
redis_client = aioredis.from_url(f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}")

# Bot logic for generating responses and extracting key points
async def generate_bot_response(user_message: str, session_id: str) -> dict:
    # Basic responses based on the user's input to test the connection
    if "hello" in user_message.lower():
        bot_response = "Hello! How can I help you today?"
    elif "how are you" in user_message.lower():
        bot_response = "I'm just a simple bot, but I'm doing great! How about you?"
    elif "bye" in user_message.lower():
        bot_response = "Goodbye! Have a nice day!"
    else:
        # Default response if no specific keyword is found
        bot_response = "I'm sorry, I don't understand. Can you please rephrase?"

    # Extract and store important points in Redis if not a simple greeting
    important_points = []
    if bot_response not in ["Hello! How can I help you today?", "I'm just a simple bot, but I'm doing great! How about you?", "Goodbye! Have a nice day!"]:
        important_points = extract_important_points(user_message, bot_response)
        email = await redis_client.get(f"session:{session_id}")
        if email:
            email_key = email.decode("utf-8")
            for point in important_points:
                await redis_client.sadd(f"important_points:{email_key}", point)  # Store as a set to avoid duplicates
    
    # Return bot response and extracted points
    return {"bot_response": bot_response, "important_points": important_points}    

# Function to extract key information from messages
def extract_important_points(user_message: str, bot_response: str) -> list:
    key_points = []
    
    # Example parsing for specific keywords or phrases
    if "nutrition" in user_message.lower() or "diet" in user_message.lower():
        key_points.append("Discussed nutrition or diet recommendations.")
    if "goal" in user_message.lower():
        key_points.append("User mentioned goals or objectives.")
    
    # Custom logic to identify key points from the bot response
    if "suggests" in bot_response:
        key_points.append("Bot provided a recommendation.")
    
    return key_points