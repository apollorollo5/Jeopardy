### Acceptance creiteria for minimum viable product.
```
1.) The intro menu has start and exit button.
2.) The main gameplay will contain 4 potential answers and 1 question.
3.) 2.) repeats
```
### How to set up Gemini API key.
How to get a Gemini API key (Developer key)

Go to Google AI Studio:
👉 https://aistudio.google.com/

Sign in with your Google account.

If it’s your first time:

Accept the Gemini / Generative AI Terms of Service.

In the left sidebar, open “API keys”
(or click any big “Get API key” / “Create API key” button you see).

Click “Create API key”:

Choose an existing project or create a new one.

Confirm, and Google will generate a key string (long random characters).

Copy that key — this is your GEMINI_API_KEY, this is in `settings.py`.

How to provide the GEMINI_API_KEY to the app (recommended)

Option A — environment variable (recommended, safe):

PowerShell (temporary for this session):

```powershell
$env:GEMINI_API_KEY = "your-real-gemini-key-here"
python manage.py runserver
```

Or set it permanently in your user/system environment variables via Windows settings.

Option B — .env file (convenient for local development):

1. Copy `.env.example` to `.env` in the project root.
2. Fill in `GEMINI_API_KEY=your-real-gemini-api-key-here`.
3. We include `python-dotenv` in `requirements.txt` so `mysite/settings.py` will try to load `.env` automatically in development.

# Execute the below command to get started:
pip install -r requirements.txt

# To run the project:
python manage.py runserver

# The structure of the project at the moment:
```
mysite/                 ← project root (folder name doesn’t matter)
├── manage.py
├── requirements.txt
├── mysite/             ← Django project config (settings, urls, etc.)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── main/               ← your app
    ├── __init__.py
    ├── views.py
    ├── models.py
    ├── apps.py
    ├── templates/
    │   └── main/
    │       └── index.html
    └── static/
        └── main/
            ├── css/
            │   └── style.css
            ├── img/
            │   └── logo.png
            ├── audio/
            │   └── bgm.mp3
            └── js/
                └── app.js
```
