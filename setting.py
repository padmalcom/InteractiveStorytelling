class Setting:
    name = ""
    introductions = []
    endings = []

    def __init__(self, name, introductions, endings):
        self.name = name
        self.introductions = introductions
        self.endings = endings

settings = {
    "fantasy": Setting("Fantasy", ["He was known as the Kingslayer, a man without honor, an oath breaker; he was also the richest man and undisputedly the best looking in all seven kingdoms. [name] was the greatest sword fighter in the world; his armor had not a scratch, for no man could match his talent - until he met Brienne of Tarth. She was laughed at, constantly ridiculed, and because of her size and talent with a sword, she was often mistaken for a man under her armor. When they laid down their armor and swords, they grew to know each other's true character and fell in love, never letting the other know their feelings.", "Not only [name] and his team are struggling with the reform of the government, but also the new royal family. The fact that there is now someone around who apparently knows how to kill dragons and a cult is rising that regards ghule and dragons as monsters is not only causing many problems but also a big question: Should the dragons and ghule continue to live in this dimension at all?"], ["[name] had the feeling that the story had reached its end.","[name] suddenly felt weak and thought that the situation grew over his head."]
    ),
    "sci-fy": Setting("Sci-Fy", ["In rain and wind, the world had changed. All of a sudden they had been there, the storm was their dark harbinger who had accompanied them for so many light years. Their destination, your world, my world, another world and then, then the storm would continue to accompany them on their long journey through the wide open spaces of the galaxies.  Never they come alone, never without a plan, before them others were already here and after them, what will remain then. [name] went on a journey to explore where they came from.", "[name] already has enough problems in the Concordia base Lachanx, e.g. the lousy canteen food, various mental ailments and the annoying commander Sator. But the latest problem at his side robs him of his last nerve - although it is mainly characterized by silence. Unfortunately, his membership in the Peace Corps is now at stake, which forces [name] to become friends with this new problem."],["This was the end of the word. There were storms and fires. [name] could not get it.","The Concordia base Lachanx lay in bright sunlight."]
    ),
    "harry potter": Setting("Harry Potter", ["Harry was in love with Hermione. They know each other for four years now and finally felt that they belong together. When they were alone in the Griffindor rooms, they hugged each other for a long time and before Harry knew what he was up to he kissed her gently on the lips."], ["They married on a rainy saturday with all their friends and family around them."]
    ),
    "simple": Setting("Simple", ["Winter had recently arrived and Peter sat at the window and watched the thick flakes fall from the sky. The crisis, which had forced them all to stay at home for months, had hardly subsided."], ["The vaccine was suddenly announced in the news. Success was eventually won by a smaller British pharmaceutical company."])
}

coherence_phrases = ["[person] rolled [hisher] eyes.",
    "[person] cleared [hisher] throat.",
    "[person] made a noise.",
    "[person] raised [hisher] hand.",
    "[person] stamped [hisher] feet.",
    "[person]'s face expressed interest.",
    "[person] raised [hisher] eyebrows.",
    "[person] looked bored.",
    "[person] yawned.",
    "[person] rubbed [hisher] closed eyes.",
    "[person] took a deep breath.",
    "[person] laughed."]