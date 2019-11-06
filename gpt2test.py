from gpt2 import GPT2

gpt2 = GPT2()
history = """My name is Jonas and I have been hunting dinosaurs my entire life. One day during a tough hunt I met my wife Lilly. She was the love of my life and when I saw her the first time I could not focus on the triceratops who was just attacking me. He"""
text = gpt2.generate_texts(history, 100, 3)

for t in text:
    print(history + t)