from coherence import Coherence


coherence = Coherence()
#history = """My name is Jonas and I have been hunting dinosaurs my entire life. One day during a tough hunt I met my wife Lilly. She was the love of my life and when I saw her the first time I could not focus on the triceratops who was just attacking me. He"""
#text = gpt2.generate_text(history, 100)
#print(history + text)

paragraphs = ["the book is on the desk.","I want to read the book.", "It was raining so reading a book would be great."]

c = coherence.calculateCoherence(paragraphs)

print("Coherence: " + str(c))