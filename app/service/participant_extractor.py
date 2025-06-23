import json

def extract_participants_from_transcript(transcript: str, model="gpt-3.5-turbo"):
    #Loading it here after faving env loaded.
    from openai import OpenAI  
    client = OpenAI()          

    prompt = (
        "You are analyzing a sales demo transcript.\n\n"
        "Your task is to extract the list of participants and assign each one a role:\n"
        "- \"SE\" → Sales Engineer (only one person should be labeled SE)\n"
        "- \"Customer\" → someone from the buying organization\n"
        "- \"Partner\" → any other internal team member (Account Exec, BDR, SA, etc.)\n\n"
        "If more than one person seems like an SE, choose the one who speaks most and label them as SE. Others become Partners.\n\n"
        "Return only a JSON array like:\n"
        '[{"name": "Alice", "role": "SE"}, {"name": "Bob", "role": "Customer"}, {"name": "Charlie", "role": "Partner"}]\n\n'
        f"Here is the transcript:\n{transcript}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    reply = response.choices[0].message.content
    try:
        #Debug gpt response
        #print("GPT raw response:\n", reply)
        return json.loads(reply)
    except json.JSONDecodeError:
        print("GPT returned invalid JSON:\n", reply)
        return None
