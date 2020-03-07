from coherence import Coherence


coherence = Coherence()
#history = """My name is Jonas and I have been hunting dinosaurs my entire life. One day during a tough hunt I met my wife Lilly. She was the love of my life and when I saw her the first time I could not focus on the triceratops who was just attacking me. He"""
#text = gpt2.generate_text(history, 100)
#print(history + text)

paragraphs1 = ["the book is on the desk.","I want to read the book.", "It was raining so reading a book would be great."]
c1 = coherence.calculateCoherence(paragraphs1)
print("Coherence1: " + str(c1))

paragraphs2 = ["Peter went to the pet store.","The pirate ship did not make it through the story sea.",
"Meat is absolutely no alternative to salad."]
c2 = coherence.calculateCoherence(paragraphs2)
print("Coherence2: " + str(c2))


paragraphs3 = ["Jamie works at a library.","There are plenty of books in the library.",
"Jamies favorite book is the one about dogs."]
c3 = coherence.calculateCoherence(paragraphs3)
print("Coherence3: " + str(c3))