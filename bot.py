# GEMINI API CALL (Gemini 3.6 Flash we Ätiýaçlyk Modeller)
def call_gemini_api(contents):
    # gemini-3.6-flash ilkinji saýlaw hökmünde goşuldy
    models = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    last_error = "Nämälim ýalňyşlyk"

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            data = response.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            if "error" in data:
                last_error = data["error"].get("message", str(data["error"]))
        except Exception as error:
            last_error = str(error)

    return f"Gemini API ýalňyşlygy: {last_error}"
