# LEDGER — AI Expense Tracker
An expense tracker that reads your bills for you. Instead of typing every purchase by hand, you upload a photo of a receipt and the AI fills in the details.

# How it works
1. Upload a photo of a bill or receipt (JPG/PNG).
2. The AI scans it and picks out the merchant name, date, amount, and category (Food, Groceries, Transport, Shopping, Bills, Entertainment, Health, Travel, or Other).
3. You review the details in a quick form and confirm.
4. It gets added to your ledger, with a running monthly total and a category-wise chart.

# Download from GitHub to your computer
   git clone https://github.com/4nmol0824/Ledger-expense-tracker.git      
   cd Ledger-expense-tracker

# Run it locally (VS Code)
pip install -r requirements.txt      
streamlit run app.py

# (Add your own free Gemini key in .streamlit/secrets.toml:)
GEMINI_API_KEY = "your-key-here"       
(Get a free key at https://aistudio.google.com/apikey — no card needed.)

# Or just use it online using Streamlit 
No setup needed — open the live link and start uploading receipts.      
Live: https://ledger-expense-tracker-4xnufgxtgtz232rztcvdvm.streamlit.app/

# ## Sample Receipts
I'm providing a few sample bill/receipt photos below — feel free to download and use them to test the app.   
Download sample bills to test the app: https://drive.google.com/drive/folders/1a8ZWIFx9YugMF-IbApSTW5Y_Sfl8ozF-?usp=sharing
