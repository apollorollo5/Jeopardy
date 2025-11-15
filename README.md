### Acceptance creiteria for minimum viable product.
```
1.) The intro menu has start and exit button.
2.) The main gameplay will contain 4 potential answers and 1 question.
3.) 2.) repeats
```
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
