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
                "location": f"lat: {equip['latitude']}, long: {equip['longitude']}"
            })

        # Create the prompt
        prompt = f"""
        You are a utility maintenance advisor. Analyze the following equipment data and {query}
        
        Consider these factors when making recommendations:
        1. Risk score (higher means more urgent)
        2. Days since last maintenance
        3. Number of customers impacted
        
        Equipment data:
        {json.dumps(equipment_list, indent=2)}
        
        Provide a response in this JSON format:
        {{
            "recommendation": "Your detailed recommendation here",
            "selected_equipment": "product_id of the recommended equipment",
            "urgency_level": "high/medium/low",
            "technicians_needed": number between 1 and 5
        }}
        """

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model released May 13, 2024
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        raise Exception(f"Error getting chatbot response: {str(e)}")
