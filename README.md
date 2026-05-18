# 🎓 CUD Course Offering Scraper

> An AI-powered web scraper that autonomously navigates the Canadian University Dubai student portal, extracts course offering data for the SEAST division, and presents it through an interactive Streamlit dashboard.

---

## 📌 Overview

This project was built for **BCS 206 – Information Structures** at Canadian University Dubai. It uses AI browser agents to log into the CUD portal, apply filters, and extract structured course data across multiple pages — all without manual interaction. The extracted data is saved to a CSV file and visualized through a local web app.

Two agent modes are supported:
- **Cloud mode** — powered by Google Gemini (`gemini-2.0-flash-lite`) via API
- **Local mode** — powered by Mistral running on Ollama (fully offline)

---

## 🗂️ Project Structure

```
cud-course-scraper/
│
├── local_version.py          # AI agent using local Ollama (Mistral)
├── tutorial_cloud_old.py     # AI agent using Google Gemini API
├── stream_gui.py             # Streamlit UI — credentials, scraping, data viewer
├── course_data.csv           # Auto-generated output file (gitignored)
├── .env                      # Your credentials (gitignored — never commit this)
├── .env.example              # Template for environment variables
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed (for local mode only)
- A Google Gemini API key (for cloud mode only)
- Google Chrome installed (used by `browser-use`)

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/Hassan-Mujtabaa/cud-course-scraper.git
cd cud-course-scraper
```

**2. Install dependencies**
```bash
pip install browser-use langchain-ollama langchain-google-genai pydantic python-dotenv streamlit pandas
```

**3. Set up your `.env` file**

Copy the example file and fill in your details:
```bash
cp .env.example .env
```

Then edit `.env`:
```
PORTAL_USERNAME=your_cud_username
PORTAL_PASSWORD=your_cud_password
SELECTED_TERM=FA 2025-26
GOOGLE_API_KEY=your_google_gemini_api_key
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## 🚀 Running the App

**If using Local Mode (Ollama):** set the Ollama host port before launching:
```bash
# Windows
set OLLAMA_HOST=127.0.0.1:1111

# macOS/Linux
export OLLAMA_HOST=127.0.0.1:1111
```

Then pull the Mistral model if you haven't already:
```bash
ollama pull mistral
```

**Launch the Streamlit app:**
```bash
streamlit run stream_gui.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🖥️ How to Use

1. Enter your **CUD portal username and password** and select the **term** in the app
2. Click **Save to .env file** to store credentials securely
3. Click either:
   - **Update Course Data FROM CLOUD MODEL** — uses Gemini API
   - **Update Course Data FROM LOCAL MODEL** — uses Ollama (offline)
4. Wait for the agent to finish scraping (may take a few minutes)
5. The course table will populate automatically
6. Use the **sidebar filters** to search by course code, name, instructor, room, days, or credits

---

## 🔍 Filters Available

| Filter | Type |
|---|---|
| Course Code | Text search (substring) |
| Course Name | Text search (substring) |
| Instructor | Dropdown |
| Days | Multi-select |
| Room | Text search (substring) |
| Credits | Range slider |

---

## 🧱 Data Structures Used

- **JSON** — intermediate format used by the AI agent to structure scraped output before CSV conversion
- **Linked List (via Pydantic models)** — `Course` objects are stored as a list inside the `Courses` class, representing each course offering as a typed data node
- **CSV (flat file)** — persistent storage for the extracted dataset

---

## 📚 Libraries Used

| Library | Purpose |
|---|---|
| `browser-use` | Enables AI agents to control and extract data from a real browser |
| `langchain-google-genai` | Google Gemini LLM integration via LangChain |
| `langchain-ollama` | Local Ollama LLM integration via LangChain |
| `pydantic` | Structured data models with validation (`Course`, `Courses`) |
| `python-dotenv` | Loads credentials from `.env` file |
| `streamlit` | Interactive web UI for credentials, scraping, and data viewing |
| `pandas` | CSV loading, cleaning, and filtering |

---

## 🔐 .env.example

```
PORTAL_USERNAME=
PORTAL_PASSWORD=
SELECTED_TERM=
GOOGLE_API_KEY=
```

---

## 👥 Team

| Student | ID | Role |
|---|---|---|
| **Anfal Talib** | 20230003487 | Lead Developer — core agent logic, cloud & local scraper implementation |
| **Hassan Mujtaba** | 20220002085 | Developer — Streamlit GUI, integration, environment configuration |
| **Hans Misquitta** | 20230003918 | Contributor — testing and code support |
| **Yijie Huang** | 20220002483 | Team Member |
| **Khashir Mokhammad Rakhim** | 20230003736 | Team Member |

---

## 🏫 Course Information

**BCS 206 – Information Structures**  
School of Engineering, Applied Sciences, and Technology  
Canadian University Dubai — Spring 2024–25

**CLOs Addressed:** CLO3 · CLO4 · CLO5

---

## ⚠️ Notes

- This tool is intended for **personal academic use only**
- The scraper targets the SEAST division filter by default — this can be changed in the agent task prompt
- Cloud scraping requires a valid Gemini API key with sufficient quota
- Local scraping requires Ollama running with the Mistral model loaded
