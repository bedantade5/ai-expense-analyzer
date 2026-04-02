import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

CATEGORIES = {
    "Food": {
        "merchants": [
            "Swiggy", "Zomato", "McDonald's", "KFC", "Domino's Pizza",
            "Starbucks", "Cafe Coffee Day", "Subway", "Pizza Hut", "Haldiram's",
            "Barbeque Nation", "Social Restaurant", "Udupi Darshini", "MTR Foods",
            "FreshMenu", "Box8", "EatFit", "Behrouz Biryani", "Faasos", "Rebel Foods"
        ],
        "amount_range": (80, 1200),
        "weight": 0.28,
    },
    "Travel": {
        "merchants": [
            "Ola", "Uber", "Rapido", "RedBus", "IRCTC", "IndiGo Airlines",
            "Air India", "MakeMyTrip", "Goibibo", "Yatra", "Cleartrip",
            "SpiceJet", "Vistara", "Ola Cabs", "Meru Cabs", "FastTag Recharge",
            "BMTC Bus Pass", "Metro Card Recharge", "Zoom Car", "Drivezy"
        ],
        "amount_range": (50, 12000),
        "weight": 0.15,
    },
    "Shopping": {
        "merchants": [
            "Amazon", "Flipkart", "Myntra", "Meesho", "Ajio", "Nykaa",
            "Reliance Digital", "Croma", "Snapdeal", "Tata Cliq", "BigBasket",
            "Blinkit", "Zepto", "DMart", "Spencer's Retail", "More Supermarket",
            "H&M India", "Zara India", "Lifestyle Stores", "Westside"
        ],
        "amount_range": (199, 8000),
        "weight": 0.20,
    },
    "Bills": {
        "merchants": [
            "Airtel Postpaid", "Jio Recharge", "BESCOM Electricity", "BWSSB Water",
            "ACT Fibernet", "Tata Sky DTH", "Amazon Prime", "Netflix",
            "Spotify Premium", "Google One", "Microsoft 365", "Paytm Insurance",
            "LIC Premium", "HDFC Loan EMI", "SBI Credit Card Bill", "ICICI Credit Card",
            "Axis Bank EMI", "Gas Bill GAIL", "Society Maintenance", "Rent Payment"
        ],
        "amount_range": (149, 5000),
        "weight": 0.18,
    },
    "Healthcare": {
        "merchants": [
            "Apollo Pharmacy", "Medplus", "Practo", "1mg", "PharmEasy",
            "Netmeds", "Fortis Hospital", "Manipal Hospital", "Columbia Asia",
            "Narayana Health", "Dr. Lal PathLabs", "SRL Diagnostics", "Max Healthcare",
            "Cult.fit", "HealthifyMe", "Gym Membership", "Yoga Studio", "Ayur Clinic"
        ],
        "amount_range": (100, 4000),
        "weight": 0.08,
    },
    "Entertainment": {
        "merchants": [
            "BookMyShow", "PVR Cinemas", "INOX Movies", "Disney+ Hotstar",
            "SonyLIV", "ZEE5", "ALTBalaji", "MX Player Premium", "YouTube Premium",
            "Steam Games", "PlayStation Store", "Xbox Game Pass", "Lenskart",
            "Fastrack", "Timezone Fun Zone", "Smaaash Entertainment", "VR Park"
        ],
        "amount_range": (99, 3000),
        "weight": 0.06,
    },
    "Education": {
        "merchants": [
            "Udemy", "Coursera", "BYJU'S", "Unacademy", "Vedantu",
            "upGrad", "Simplilearn", "LinkedIn Learning", "Pluralsight",
            "GeeksforGeeks Premium", "LeetCode Premium", "Coding Ninjas",
            "NPTEL Certification", "Skillshare", "MasterClass", "Duolingo Plus"
        ],
        "amount_range": (199, 6000),
        "weight": 0.05,
    },
}

ANOMALY_MERCHANTS = [
    ("Luxury Jewellers", 45000),
    ("International Wire Transfer", 80000),
    ("Forex Exchange Premium", 35000),
    ("Apple Store India", 120000),
    ("Louis Vuitton", 95000),
    ("Foreign Hotel Booking", 55000),
]

def generate_transactions(n=300):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    category_names = list(CATEGORIES.keys())
    weights = [CATEGORIES[c]["weight"] for c in category_names]

    rows = []
    num_anomalies = 8
    anomaly_indices = set(random.sample(range(n), num_anomalies))

    for i in range(n):
        rand_days = random.randint(0, (end_date - start_date).days)
        date = start_date + timedelta(days=rand_days)

        if i in anomaly_indices:
            merchant, amount = random.choice(ANOMALY_MERCHANTS)
            amount = amount + random.randint(-2000, 2000)
        else:
            category = random.choices(category_names, weights=weights, k=1)[0]
            merchant = random.choice(CATEGORIES[category]["merchants"])
            lo, hi = CATEGORIES[category]["amount_range"]
            amount = round(random.uniform(lo, hi), 2)

        rows.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Merchant": merchant,
            "Amount": amount,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def generate_labeled_data(n=300):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    category_names = list(CATEGORIES.keys())
    weights = [CATEGORIES[c]["weight"] for c in category_names]

    rows = []
    for _ in range(n):
        rand_days = random.randint(0, (end_date - start_date).days)
        date = start_date + timedelta(days=rand_days)
        category = random.choices(category_names, weights=weights, k=1)[0]
        merchant = random.choice(CATEGORIES[category]["merchants"])
        lo, hi = CATEGORIES[category]["amount_range"]
        amount = round(random.uniform(lo, hi), 2)
        rows.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Merchant": merchant,
            "Amount": amount,
            "Category": category,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("Date").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df_unlabeled = generate_transactions(300)
    df_unlabeled.to_csv("transactions.csv", index=False)
    print(f"[✓] transactions.csv generated — {len(df_unlabeled)} rows")

    df_labeled = generate_labeled_data(500)
    df_labeled.to_csv("training_data.csv", index=False)
    print(f"[✓] training_data.csv generated — {len(df_labeled)} rows (labeled, for ML training)")
