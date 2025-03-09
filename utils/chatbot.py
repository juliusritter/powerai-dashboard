import os
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_chatbot_response(query, equipment_data):
    """Get AI response for maintenance queries"""
    try:
        # Convert equipment data to a format suitable for the prompt
        equipment_list = []
        for _, equip in equipment_data.iterrows():
            equipment_list.append({
                "product_id": equip["product_id"],
                "product_name": equip["product_name"],
                "risk_score": float(equip["risk_score"]),
                "customer_impact": int(equip["customer_impact"]),
                "days_since_maintenance": int(equip["days_since_maintenance"]),
                "age": float(equip["age"]),
                "temperature": float(equip["temperature"]),
                "precipitation_forecast": float(equip["precipitation_forecast"]),
                "vegetation_proximity": bool(equip["vegetation_proximity"])
            })

        # Sort equipment by risk and impact
        equipment_list.sort(key=lambda x: (x["risk_score"], x["customer_impact"]), reverse=True)

        # Create the prompt
        prompt = f"""
        You are a utility maintenance advisor. Based on the provided equipment data, analyze and recommend maintenance priorities.
        The equipment data is sorted by risk score and customer impact.

        Current query: {query}

        Consider these key factors when making recommendations:
        1. Risk score (higher means more urgent)
        2. Days since last maintenance
        3. Number of customers impacted
        4. Environmental factors (temperature, precipitation, vegetation)
        5. Equipment age

        Equipment details (top high-risk items):
        {json.dumps(equipment_list[:5], indent=2)}

        Provide specific recommendations including:
        1. Which equipment needs immediate attention
        2. Why it needs maintenance (specific risks)
        3. How many technicians should be deployed (1-5 based on complexity)
        4. Priority level of the maintenance

        Be concise and direct in your response. Just tell me which equipment needs attention and how many technicians to send.
        At the end of your response, state clearly how many technicians should be deployed (as a number between 1-5).
        """

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model released May 13, 2024
            messages=[{"role": "user", "content": prompt}]
        )

        # Get the text response
        recommendation = response.choices[0].message.content

        # Extract the number of technicians needed (look for the last number 1-5 in the text)
        import re
        numbers = re.findall(r'\b[1-5]\b', recommendation)
        technicians_needed = int(numbers[-1]) if numbers else 2  # Default to 2 if no number found

        return {
            "recommendation": recommendation,
            "technicians_needed": technicians_needed
        }

    except Exception as e:
        print(f"Error in chatbot response: {str(e)}")  # Add logging
        raise Exception(f"Error getting chatbot response: {str(e)}")