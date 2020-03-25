from bert import Bert

bert = Bert()
verb, probability = bert.getBestPredicateAndProbability("She", "the ball")
print("'" + verb + "'" + " " + str(probability))

item, probability = bert.combineTo("jar", "water")
print("'" + item + "'" + " " + str(probability))