import json

messages = [
    {"role": "system", "content": "Tu es un assistant spécialisé en stéganographie textuelle."},
    {"role": "assistant", "content": "Le style doit rester naturel, discret et humain."},
    {"role": "user", "content": "Reformule cette phrase : Les pneus roulent sans bruit."},
    {"role": "user", "content": "Reformule cette phrase : La voiture avance très lentement."}
]

print(json.dumps(messages, indent=2, ensure_ascii=False, sort_keys=True))

def f(a: int, b: int) -> int:
    return a + b

d: dict[str, int] = {'a': 1, 'b': 2}
print(f(**d))





