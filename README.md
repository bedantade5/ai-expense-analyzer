# AI-Powered Expense Analyzer Using Intelligent Agent Framework

An intelligent backend system and machine learning engine that automatically categorizes bank transactions and flags unusual spending patterns.

Built as a mini-project by **Bedanta De** and **Shreya Thakre**, this framework uses Natural Language Processing (NLP) and anomaly detection to act as a smart financial assistant, processing raw financial data into actionable, organized insights.

---

## 🚀 Key Features

- **Smart Categorization:** Uses a TF-IDF Vectorizer and Logistic Regression to read merchant names (e.g., "Swiggy", "BESCOM") and automatically assign them to categories like Food, Bills, or Travel.
- **Anomaly Detection:** Implements an Isolation Forest algorithm to monitor spending amounts and flag highly unusual, out-of-character transactions (e.g., an unexpected ₹95,000 charge).
- **Synthetic Data Generation:** Includes a localized, realistic fake-data factory to train the machine learning models without requiring sensitive personal bank statements.
- **RESTful API:** A fully functional FastAPI backend that bridges the machine learning models with a SQLite database, ready to be consumed by any frontend dashboard.
- **Data Persistence:** Uses SQLAlchemy to neatly file processed transactions and alerts into a local database for long-term storage and trend tracking.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| Machine Learning | `scikit-learn`, `joblib`, `pandas`, `numpy` |
| API Framework | `FastAPI`, `uvicorn` |
| Database | `SQLite`, `SQLAlchemy` |

---

## 📂 Project Structure
```text
ai-expense-analyzer/
├── api.py                  # The Dispatcher: FastAPI server and endpoints
├── ml_engine.py            # The Brain: Trains models and makes predictions
├── generate_dummy_data.py  # The Textbook: Generates training and testing CSVs
├── database.py             # The Filing Cabinet: SQLAlchemy DB setup and queries
├── app.py                  # The Storefront: Frontend UI dashboard
├── requirements.txt        # Python dependencies
└── models/                 # Saved joblib machine learning models
```

---

## 💻 Local Installation & Setup

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/bedantade5/ai-expense-analyzer.git
cd ai-expense-analyzer
```

### 2. Install Dependencies

It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

### 3. Generate Training Data

Before the AI can categorize anything, it needs to study. Run the data generator to create `training_data.csv` (the study guide) and `transactions.csv` (the test data).
```bash
python generate_dummy_data.py
```

### 4. Train the Machine Learning Models

Run the ML engine to process the training data and save the active models into the `/models` directory.
```bash
python ml_engine.py
```

### 5. Start the API Server

Launch the FastAPI backend. It will automatically initialize the SQLite database on startup.
```bash
uvicorn api:app --reload --port 8000
```

### 6. In a NEW terminal, start Streamlit

```bash
streamlit run app.py
```
Then open http://localhost:8501, upload transactions.csv, and click Analyze Transactions.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check. |
| `POST` | `/upload` | Upload a CSV of raw transactions. The API cleans the data, runs it through the ML pipeline for categorization and anomaly detection, and saves results to the database. |
| `GET` | `/data` | Retrieve all processed transactions. |
| `GET` | `/summary` | Get aggregated analytics — total spend, anomaly count, category breakdowns, and monthly trends — for UI charting. |
| `POST` | `/retrain` | Force the ML models to retrain on the latest dataset. |

---

## 🔮 Future Scope

- **Manual Transaction Logging:** Build an endpoint and UI component that allows users to quickly add individual expenses on the fly (e.g., logging a quick coffee purchase), eliminating the need to upload CSV files every time.

- **Comprehensive Budgeting Tools:** Evolve the analyzer into a full budgeting application with features like custom monthly category limits, visual progress tracking, and real-time overspending alerts.

- **User Authentication:** Implement secure login functionality so multiple users can manage their own transactions and budgets independently.

- **Database Migration:** Replace the local SQLite `DATABASE_URL` with a managed PostgreSQL database (e.g., Neon or Supabase) for secure and persistent cloud storage.

- **Cloud Hosting:** Deploy both backend and frontend to platforms like Render, Railway, or Vercel for continuous uptime and global accessibility.

---

## 👥 Authors

| Name | Roll Number | Batch |
|------|-------------|-------|
| Bedanta De | 230968178 | DSE-B Batch-1 |
| Shreya Thakre | 230968039 | DSE-B Batch-1 |
