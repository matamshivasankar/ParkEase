src = open('backend/app.py', encoding='utf-8').read()
i = src.index('def create_app')
print(src[i-400:i+700])
