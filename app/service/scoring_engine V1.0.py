import json


# Build the GPT scoring prompt
def build_scoring_prompt(transcript, metric_list, chunks, framework_key, se_name, framework_context, quote_mode="post", scoring_guide=None):
    prompt = (
        f"You are a sales engineering coach evaluating a demo transcript.\n"
        f"The evaluation is based on the framework: {framework_context}.\n"
        f"The main Sales Engineer in this conversation is: {se_name}.\n"
        f"Evaluate the demo transcript focusing on the performance of {se_name}. "
        "Consider the full conversation and how others interacted with them, "
        "but base your scores only on how effectively this person demonstrated the best practices.\n\n"
        )



    prompt += "Reference best practices:\n"
    for i, chunk in enumerate(chunks):
        prompt += f"[{i+1}] {chunk.strip()}\n"

    prompt += "\nTranscript:\n" + transcript.strip() + "\n\n"

    prompt += "Evaluate based on these criteria:\n"
    for metric in metric_list:
        prompt += f"- {metric['name']}: {metric['description']}\n"

    if scoring_guide:
        prompt += "\nScoring guide (1–5 scale):\n"
        for line in scoring_guide.get("scale", []):
            prompt += f"- {line}\n"
        note = scoring_guide.get("strictness_note", "")
        if note:
            prompt += "\n" + note.strip() + "\n"

    if quote_mode == "post":
        prompt += (
            "\nFor each metric, include:\n"
            "- score (1 to 5)\n"
            "- explanation\n"
            "- best_quote, best_quote_author, best_quote_reason\n"
            "- worst_quote, worst_quote_author, worst_quote_reason\n"
        )
    prompt += "No quote should be shorter than 10 words\n"
    prompt += "\nRespond in JSON format like:\n"
    prompt += '''{
        "clarity": {
            "score": 4,
            "explanation": "...",
            "best_quote": "...",
            "best_quote_author": "Sales Engineer",
            "best_quote_reason": "...",
            "worst_quote": "...",
            "worst_quote_author": "Customer",
            "worst_quote_reason": "..."
        },
        ...
    }'''

    return prompt

# Call GPT and parse response
def call_gpt(prompt, model="gpt-4", parse_json=True):
    #Once env is loaded
    from openai import OpenAI
    client = OpenAI()
    
    print("Calling GPT with model:", model)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    reply = response.choices[0].message.content
    
    if not parse_json:
        return reply.strip()
    
    try:
        return json.loads(reply)
    except json.JSONDecodeError:
        print("GPT returned invalid JSON:\n", reply)
        return None


# Summary feedback
def build_summary_feedback_prompt(explanations, overall_score):
    prompt = (
        "You are a sales engineering coach.\n\n"
        "Here are the metric-level evaluation results for a sales demo:\n"
    )

    for metric, data in explanations.items():
        score = data.get("score", "")
        explanation = data.get("explanation", "")
        prompt += f"\n{metric.title()} (score: {score})\n{explanation.strip()}\n"

    prompt += "\n\nBased on the above:\n"
    prompt += "Write a short, clear summary paragraph in HTML format. Highlighting the best thing the Sales Engineer did overall.\n"
    prompt += "Use <strong> to emphasize the Sales Engineer’s biggest strength. \n"
    prompt += "Also mention one key area where they can improve.\n"

    prompt += "Write it as if you're a coach giving supportive feedback. Keep it concise, about 3–4 sentences."

    return prompt

# Main scoring function
def score_transcript(transcript, config, collections, participants):
    print("score_transcript debug 1")

    framework = config["coaching_frameworks"][0]  # assume one for now
    model=config["settings"].get("model", "gpt-4")
    print(framework)
    scoring_keys = framework.get("scoring_framework_keys", [])
    metrics = config["metrics"]
    quote_mode = config["settings"].get("quote_mode", "post")
    scoring_guide = config["settings"].get("scoring_guide")
    framework_name = framework["name"]
    framework_context=framework.get("context", "")

    # Identify main SE
    se_name = next((p["name"] for p in participants if p["role"] == "SE"), None)
    if not se_name:
        raise ValueError("No SE found in participants list.")

    results = {}
    metric_scores = {}
    explanations = {}
    
    print("score_transcript debug 2")
    print(scoring_keys)

    for key in scoring_keys:
        print("score_transcript debug 3")
        # Query book content for this habit/framework key
        chunks = collections[framework_name].query(
            query_texts=[f"Best practices for {key}"],
            n_results=config["settings"].get("max_book_chunks", 3),
            where={"framework_key": key}
        )["documents"][0]

        prompt = build_scoring_prompt(
            transcript=transcript,
            metric_list=metrics,
            chunks=chunks,
            framework_key=key,
            se_name=se_name,
            framework_context=framework_context,
            quote_mode=quote_mode,
            scoring_guide=scoring_guide
        )
        
        #print(f"\nPrompt for '{key}':\n{'='*40}\n{prompt}\n")


        score_data = call_gpt(prompt, model=model)
        #print(f"\nRaw GPT Output:\n{'='*40}\n{json.dumps(score_data, indent=2)}\n")

        if not score_data:
            continue

        for metric in metrics:
            m_name = metric["name"]
            if m_name not in score_data:
                continue
            if m_name not in metric_scores:
                metric_scores[m_name] = []
                explanations[m_name] = score_data[m_name]
            metric_scores[m_name].append(score_data[m_name]["score"])

    # Average each metric score
    final_scores = {
        name: round(sum(scores)/len(scores), 2) for name, scores in metric_scores.items()
    }

    # Weighted overall score
    total = 0
    for metric in metrics:
        name = metric["name"]
        if name in final_scores:
            total += final_scores[name] * metric["weight"]
    
    
    summary_prompt = build_summary_feedback_prompt(explanations, total)
    summary_response = call_gpt(summary_prompt, model=model, parse_json=False)
    print("\nSummary GPT output:\n", summary_response)

    summary_feedback = summary_response 

    
    print(final_scores)
    return {
        "overall_score": round(total, 2),
        "metric_scores": final_scores,
        "summary_feedback": summary_feedback,
        "per_metric_explanations": explanations
    }


