# S.E.T — Smart Expense Tracker

A streamlined, AI-powered financial dashboard that transforms messy bank statements into categorized insights using GPT-4o.

## The Vision

S.E.T (Smart Expense Tracker) automates the most annoying part of budgeting: data entry(or at least its supposed to). It uses local keyword matching for speed and LLMs for complex categorization, providing a high-fidelity view of where your coin is going.

## Tech Stack

    Frontend: Streamlit

    Intelligence: OpenAI (GPT-4o-mini)

    Data Engine: Pandas

    Visualization: Matplotlib

## Requirements

    Python 3.13 (or 3.8+)

    OpenAI API Key (Stored in .env)

    A CSV bank statement (Supports custom column mapping via AI)

## Setup
### Clone & Navigate

```Bash

git clone https://github.com/alex-marumo/S.E.T.git
cd S.E.T
```

### Environment & Dependencies
```Bash

python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install pandas streamlit matplotlib python-dotenv openai
```

### Configure Secrets

Create a .env file in the root directory:
```Plaintext

OPENAI_API_KEY=your_secret_key_here
```

### Run

The project is a Streamlit web application. Start the server with:
```Bash

streamlit run read.py
```
## Features

    AI Statement Processing: Upload a raw bank CSV; S.E.T identifies columns automatically.
    Hybrid Categorization: Uses a high-speed keyword "Scout" for common vendors and AI for the rest.
    Dynamic Charts: Real-time Bar and Pie chart breakdown of expenses.
    Manual Entry: A simple form to log cash transactions on the fly.

## Contributing

In the spirit of the Abyss, we take all help. Open an issue or a PR. Ensure your code is DRY and your UI components remain modular.

## 📜 License

Do we really need one?
