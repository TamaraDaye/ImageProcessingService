import requests


r = requests.get("https://imgs.xkcd.com/comics/python_environment.png")

print(r.status_code)
print(type(r.content))


with open("comics.jpeg", "wb") as f:
    try:
        f.write(r.content)

    except Exception as e:
        print(e)
