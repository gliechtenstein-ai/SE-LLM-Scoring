import os
from dotenv import load_dotenv
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from app.service.config_loader import load_config
from app.service.vectordb import get_chroma_collections
from app.service.participant_extractor import extract_participants_from_transcript
from app.service.scoring_engine import score_transcript as run_scoring
import json
import uuid


#Load OpenAI Key
load_dotenv()

#Load basic directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "app", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "source", "transcripts")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "myscoresystemkey" 


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Main Page
@app.route("/")
def scoring_summary():
    filename = request.args.get("filename") or session.get("last_filename")
    config = session.get("last_config") or load_config()
    results = None
    results_path = session.get("last_results_file")
    participants = session.get("last_participants")

    
    if results_path and os.path.exists(results_path):
        with open(results_path, "r") as f:
            results = json.load(f)
    
    collections = get_chroma_collections(config)    
    #Debug to check framworks
    print("Frameworks loaded:")
    for name in collections:
        print(f"{name}")

    #return render_template("scoringsummary.html", filename=filename, config=config)
    return render_template(
            "scoringsummary.html",
            filename=filename,
            config=config,
            participants=participants,
            results=results
        )


#File upload routine
@app.route("/upload", methods=["POST"])
def upload_transcript():
    file = request.files.get("transcript")
    if file and file.filename:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        print("Transcript uploaded to:", file_path)

        # Load transcript content
        with open(file_path, "r") as f:
            transcript = f.read()

        # Extract participants + roles via OpenAI
        participants = extract_participants_from_transcript(transcript)

        # Load config + render page with participants
        config = load_config()
        return render_template(
            "scoringsummary.html",
            filename=filename,
            config=config,
            participants=participants
        )

    return "No file selected", 400

#Score routine
@app.route("/score", methods=["POST"])
def score_transcript():
    filename = request.form.get("filename")
    participant_count = int(request.form.get("participant_count", 0))

    participants = []
    for i in range(1, participant_count + 1):
        name = request.form.get(f"name_{i}")
        role = request.form.get(f"role_{i}")
        if name and role:
            participants.append({"name": name, "role": role})

    # Validation: exactly one SE
    se_count = sum(1 for p in participants if p["role"] == "SE")
    if se_count != 1:
        error = "You must assign exactly one participant as the Sales Engineer (SE)."
        config = load_config()
        return render_template(
            "scoringsummary.html",
            filename=filename,
            config=config,
            participants=participants,
            error=error
        )
    else:
        # Load transcript and config
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        with open(file_path, "r") as f:
            transcript = f.read()

        config = load_config()
        collections = get_chroma_collections(config)

        results = run_scoring(
            transcript=transcript,
            config=config,
            collections=collections,
            participants=participants
        )
        
        session["last_filename"] = filename
        session["last_participants"] = participants
        #session["last_results"] = results
        session["last_config"] = config
        
        results_id = str(uuid.uuid4())
        results_path = os.path.join("data", "temp", f"{results_id}.json")
        os.makedirs(os.path.dirname(results_path), exist_ok=True)

        with open(results_path, "w") as f:
            json.dump(results, f)

        session["last_results_file"] = results_path
        
        try:
            print("\n=== DEBUG: Serializing results for session ===")
            print(json.dumps(results, indent=2))  # See if it can be serialized for session
        except Exception as e:
            print("⚠️ Error serializing results:", e)


        return render_template(
            "scoringsummary.html",
            filename=filename,
            config=config,
            participants=participants,
            results=results
        )



#Details Page
@app.route("/details")
def scoring_details():
    
    config = session.get("last_config")
    #results = session.get("last_results") #too big for a cookie
    #print("DEBUG /details: session keys =", list(session.keys()))

    results_path = session.get("last_results_file")
    if not results_path or not os.path.exists(results_path):
        print("Results file not found.")
        return redirect(url_for("scoring_summary", filename=session.get("last_filename")))

    with open(results_path, "r") as f:
        results = json.load(f)



    return render_template("scoringdetails.html", results=results, config=config)


@app.route("/reset")
def reset_session():
    results_path = session.get("last_results_file")
    if results_path and os.path.exists(results_path):
        os.remove(results_path)
    session.clear()
    return redirect(url_for("scoring_summary"))



if __name__ == "__main__":
    app.run(debug=True)