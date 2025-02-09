from transformers import BartForConditionalGeneration, BartTokenizer
from aioredis import Redis
import health_metrics   

# Initialize pre-trained BART model and tokenizer
model_name = 'facebook/bart-large-cnn'
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

async def generate_bot_response(user_message: str, session_id: str, redis_client: Redis) -> dict:
    # Default response
    bot_response = "I'm sorry, I don't understand. Can you please rephrase?"

    # Fetch user details from Redis
    user_email = await redis_client.get(f"session:{session_id}")
    if not user_email:
        return {"bot_response": "Session expired or invalid. Please log in again."}

    user_email = user_email.decode("utf-8")

    personal_details = await redis_client.hgetall(f"personal_details:{user_email}")
    preferences = await redis_client.hgetall(f"preferences:{user_email}")
    health_conditions = await redis_client.hgetall(f"health_conditions:{user_email}")

    if not personal_details:
        return {"bot_response": "Your profile details are missing. Please update your profile."}

    try:
        weight = float(personal_details[b'weight'].decode("utf-8"))
        height = float(personal_details[b'height'].decode("utf-8"))
        dob = personal_details[b'date_of_birth'].decode("utf-8")
        gender = personal_details[b'gender'].decode("utf-8")
        age = health_metrics.calculate_age(dob)
        diet_preference = preferences[b'diet_preference'].decode("utf-8")
        allergies = health_conditions[b'allergies'].decode("utf-8")
        # fasting_glucose = float(personal_details[b'fasting_glucose'].decode("utf-8"))
        # post_meal_glucose = float(personal_details[b'post_meal_glucose'].decode("utf-8"))
        # vitamin_d = float(personal_details[b'vitamin_d'].decode("utf-8"))
        # calcium = float(personal_details[b'calcium'].decode("utf-8"))
        # sodium = float(personal_details[b'sodium'].decode("utf-8"))
        # potassium = float(personal_details[b'potassium'].decode("utf-8"))
        # waist = float(personal_details[b'waist'].decode("utf-8"))
    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}

    # Build the chat context using the last few messages from Redis
    chat_history = await redis_client.lrange(f"chat_history:{user_email}", 0, -1)
    context = ''
    for chat in chat_history[-5:]:  # Limit context to the last 5 exchanges
        chat_data = await redis_client.hgetall(chat)
        user_msg = chat_data.get(b"user_message", b"").decode('utf-8')
        bot_resp = chat_data.get(b"bot_response", b"").decode('utf-8')
        context += f"User: {user_msg}\nBot: {bot_resp}\n"

    # Add the current user message to the context
    context += f"User: {user_message}\nBot:"

    # Tokenize and generate the response using BART
    inputs = tokenizer.encode(context, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, num_beams=5, early_stopping=True)

    bot_response = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return {"bot_response": bot_response}
