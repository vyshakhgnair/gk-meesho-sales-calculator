# Deploy Meesho Sales Calculator — Free on Streamlit Cloud

## Files in this folder
```
app.py           ← main application
requirements.txt ← dependencies
DEPLOY.md        ← this guide
```

---

## Step 1 — Install & test locally (optional but recommended)

```bash
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501 in your browser and test with your Excel files.

---

## Step 2 — Push to GitHub

1. Go to https://github.com and create a **new public repository** (e.g. `meesho-sales-calculator`)
2. Upload these 3 files (`app.py`, `requirements.txt`, `DEPLOY.md`) to the repo
   - Click **Add file → Upload files**

---

## Step 3 — Deploy on Streamlit Community Cloud (FREE)

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **New app**
4. Fill in:
   - Repository: `your-username/meesho-sales-calculator`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **Deploy!**

Your app will be live at:
`https://your-username-meesho-sales-calculator-app-xxxxx.streamlit.app`

---

## How to use the app

1. Open the deployed URL
2. Upload `tcs_sales.xlsx` (your sales file)
3. Upload `tcs_sales_return.xlsx` (your returns file)
4. The summary table appears instantly with 3 tabs:
   - **State Summary** — matches the format in your reference image
   - **GST Rate Breakdown** — state + GST slab detail
   - **Raw Data** — preview of uploaded files
5. Click **Download as CSV** to export the net sales summary
