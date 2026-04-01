import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import init_db, insert_transactions, fetch_all_transactions, clear_transactions
from ml_engine import predict_batch, train_all
import os

app = FastAPI(title="AI Expense Analyzer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()
    if not os.path.exists("models/classifier.joblib"):
        print("[startup] Models not found — training now...")
        train_all()


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Expense Analyzer API is running."}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), replace: bool = True):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse CSV: {e}")

    df.columns = [c.strip().title() for c in df.columns]

    missing = {"Date", "Merchant", "Amount"} - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV missing required columns: {missing}. Found: {list(df.columns)}",
        )

    df = df.dropna(subset=["Date", "Merchant", "Amount"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount"])
    df["Merchant"] = df["Merchant"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["Date"])

    if df.empty:
        raise HTTPException(status_code=422, detail="No valid rows found in CSV after cleaning.")

    predictions = predict_batch(
        merchants=df["Merchant"].tolist(),
        amounts=df["Amount"].tolist(),
    )

    records = []
    for i, row in df.iterrows():
        pred = predictions[i - df.index[0]]
        records.append({
            "date": row["Date"],
            "merchant": row["Merchant"],
            "amount": float(row["Amount"]),
            "category": pred["category"],
            "is_anomaly": pred["is_anomaly"],
        })

    if replace:
        clear_transactions()

    insert_transactions(records)

    anomaly_count = sum(1 for r in records if r["is_anomaly"])

    return JSONResponse(content={
        "status": "success",
        "rows_processed": len(records),
        "anomalies_detected": anomaly_count,
        "message": f"Processed {len(records)} transactions, {anomaly_count} anomalies flagged.",
    })


@app.get("/data")
def get_data():
    rows = fetch_all_transactions()
    return JSONResponse(content={"status": "ok", "count": len(rows), "transactions": rows})


@app.get("/summary")
def get_summary():
    rows = fetch_all_transactions()
    if not rows:
        return {"total_spend": 0, "anomaly_count": 0, "category_breakdown": {}, "monthly_trend": {}}

    df = pd.DataFrame(rows)
    df["amount"] = df["amount"].astype(float)
    df["date"] = pd.to_datetime(df["date"])

    category_breakdown = (
        df.groupby("category")["amount"].sum().round(2).to_dict()
    )

    df["month"] = df["date"].dt.strftime("%Y-%m")
    monthly_trend = (
        df.groupby("month")["amount"].sum().round(2).to_dict()
    )

    return {
        "total_spend": round(df["amount"].sum(), 2),
        "anomaly_count": int(df["is_anomaly"].sum()),
        "transaction_count": len(df),
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
    }


@app.delete("/data")
def delete_all_data():
    clear_transactions()
    return {"status": "ok", "message": "All transactions cleared."}


@app.post("/retrain")
def retrain_models():
    try:
        train_all()
        return {"status": "ok", "message": "Models retrained successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
