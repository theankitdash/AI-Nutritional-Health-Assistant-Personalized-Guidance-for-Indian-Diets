import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from aioredis import Redis
import health_metrics

# Load TinyLlama model and tokenizer
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def generate_llm_response(prompt: str) -> str:
    """Generates a response using TinyLlama."""
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

async def generate_bot_response(user_message: str, session_id: str, redis_client: Redis) -> dict:
    """Generates chatbot response dynamically using TinyLlama."""
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
        weight = float(personal_details.get(b'weight', b'0').decode("utf-8"))
        height = float(personal_details.get(b'height', b'0').decode("utf-8"))
        dob = personal_details.get(b'date_of_birth', b'').decode("utf-8")
        gender = personal_details.get(b'gender', b'').decode("utf-8")
        age = health_metrics.calculate_age(dob)
        diet_preference = preferences.get(b'diet_preference', b'').decode("utf-8")
        allergies = health_conditions.get(b'allergies', b'').decode("utf-8")
    except KeyError:
        return {"bot_response": "Some details are missing in your profile. Please update your weight, height, date of birth, and gender."}
    
    # Create a structured prompt for LLM
    prompt = (
        f"User: {user_message}\n"
        f"User Profile: Weight: {weight} kg, Height: {height} cm, Age: {age}, Gender: {gender}, "
        f"Diet Preference: {diet_preference}, Allergies: {allergies}\n"
        f"Bot: "
    )
    
    # Get response from TinyLlama
    bot_response = generate_llm_response(prompt)
    
    return {"bot_response": bot_response}