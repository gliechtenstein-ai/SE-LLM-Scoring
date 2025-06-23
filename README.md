# Demo Evaluation Assistant using RAG and the Six Habits Framework

This project is a prototype evaluation engine that analyzes presales demo transcripts using **Retrieval-Augmented Generation (RAG)** and the principles from the book *The Six Habits of Highly Effective Sales Engineers* by Chris White.

It uses OpenAI models to score performance across customizable metrics, extract quotes for coaching, and consolidate feedback — enabling clear, habit-aligned coaching for Sales Engineers.

---

## Architecture

The project is structured following a **three-layer clean architecture**:

```
project/
    app/             # Application Layer (UI)
    services/        # Service Layer (business logic, GPT, orchestration)
    data/            # Data Layer (raw & processed files only)

```

* **Data Layer**: Holds all configs, transcripts, and book content (currently file-based; ready for DB later).
* **Service Layer**: Contains all core logic: config parsing, scoring, quote extraction, and orchestration.
* **Application Layer**: Streamlit interface (or other UI) for uploading, running, and reviewing analysis.

---

## Features

* Load a transcript and customer-specific config
* Evaluate demo transcript against Six Habits-aligned metrics
* Outputs scores, explanations, and coaching quotes per metric
* Configurable weights, evaluation rubric, and prompt behavior
* Clean separation of UI, logic, and data

---

## Technologies

Tools Used and Rationale:
* Python: Primary language for backend development due to its simplicity, ecosystem support, and strong integration with AI libraries.
* Flask (Python Web Framework): Lightweight and flexible framework ideal for building a minimal web UI and RESTful services for the MVP stage.
* HTML & JavaScript: Used to build interactive front-end elements for the user interface (e.g., uploading transcripts, displaying charts, formatting results).
* ChromaDB (Vector Database): Chosen for its speed, simplicity, and native support for local and persistent vector storage — ideal for small-to-medium domain-specific datasets.
* text-embedding-3-small (OpenAI): Embedding model chosen for its performance-to-cost ratio and compatibility with ChromaDB.
* OpenAI API (GPT-4o): Provides reliable and well-documented LLM access; used for Vanilla, RAG, and Advanced RAG variants.


---

##  Example Input Files

* `acme_config.json`: customer-specific evaluation setup
* `anonymized_call_01.txt`: sample transcript
* `six_habits_chunks.json`: knowledge base parsed from the book

---

##  Running the Project

run.py



---

##  Attribution

This project is based on *The Six Habits of Highly Effective Sales Engineers* by Chris White. All credit for the coaching framework and best practices belongs to the original author.

* freeCodeCamp.org, 2024. RAG Fundamentals and Advanced Techniques – Full Course. [Online]. [Accessed 22 June 2025]. Available from: https://www.youtube.com/watch?v=ea2W8IogX80 
* Nello, E. 2024. How to build a Python Flask RAG Chat with documents. [Online]. Medium. [Accessed 22 June 2025]. Available from: https://medium.com/thedeephub/how-to-build-a-python-flask-rag-chat-with-documents-cf5de7b05399
* Pallets. 2025. Templating with Jinja. In: Flask Documentation. [Online]. [Accessed 22 June 2025]. Available from: https://flask.palletsprojects.com/en/stable/templating/
* Grinberg, M. 2020. Handling file uploads with Flask. [Online]. Miguel Grinberg Blog. [Accessed 22 June 2025]. Available from: https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
* Chart.js. 2025. Chart.js. [Online]. [Accessed 22 June 2025]. Available from: https://www.chartjs.org/docs/latest/


