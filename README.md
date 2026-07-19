# LEDGER — AI Expense Tracker

Upload a photo of a receipt, Claude reads the merchant, date, total, and category,
you confirm the details, and it's added to your ledger with a running category breakdown.

## Deploy it yourself (free)

### 1. Get a free Gemini API key
- Go to https://aistudio.google.com/apikey → **Create API key**
- No credit card needed. Copy the key (starts with `AIza...`)
- This app uses `gemini-2.5-flash`, which is on Google's free tier — no cost,
  just a daily request limit that's generous for personal/demo use

### 2. Push this folder to GitHub
```bash
cd ledger-streamlit
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ledger-expense-tracker.git
git push -u origin main
```
(`.gitignore` already excludes secrets.toml and expenses.csv, so you won't
accidentally commit your key or your data.)

### 3. Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub
2. Click **New app** → pick your `ledger-expense-tracker` repo, branch `main`, file `app.py`
3. Before clicking Deploy, open **Advanced settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "AIzaSy-your-real-key-here"
   ```
4. Click **Deploy**. You'll get a URL like `https://your-app-name.streamlit.app`
   you can share with anyone — they don't need their own API key.

### 4. (Optional) Test locally first
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and paste your real key
streamlit run app.py
```

## Notes on this version
- **Free tier, no billing needed.** Anyone visiting your shared link uses
  your Gemini key behind the scenes, but `gemini-2.5-flash` is free — you
  just share a daily request quota across everyone using the app. Fine for
  a demo/portfolio link; if it gets heavy real traffic, Google's paid tier
  is cheap to turn on later.
- **Storage:** expenses are saved to `expenses.csv` on the app's server.
  Streamlit Community Cloud's free tier has ephemeral storage — data can be
  wiped if the app redeploys or sleeps from inactivity and restarts. Fine for
  a demo/portfolio piece; for something you rely on daily, swap in a real
  database (e.g. a free Supabase or Google Sheets backend) — happy to help
  with that if you want it later.
- All UI logic is in `app.py`, single file, easy to read and extend.