# main/views.py
from django.shortcuts import render
from .gemini_client import ask_gemini

def home(request):
    prompt = ""
    answer = ""

    if request.method == "POST":
        prompt = request.POST.get("prompt", "")
        print("Received prompt:", prompt)
        if prompt:
            answer = ask_gemini(prompt)

    return render(
        request,
        "main/index.html",
        {
            "title": "My First Django Page",
            "prompt": prompt,
            "answer": answer,
        },
    )
