import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

paragraph_characters = [['Jim', 'John'], ['Jim', 'Brian', 'Olli'], ['Jim', 'Brian', 'Olli'], ['Jim', 'Olli', 'John'] ]

# https://stackoverflow.com/questions/50821484/python-plotting-missing-data
distinct_characters = []
for chars in paragraph_characters:
    for char in chars:
        if not char in distinct_characters:
            distinct_characters.append(char)
print("Distinct chars: " + str(distinct_characters))

paragraph_list = range(len(paragraph_characters))
character_presences = []
for idx1, char in enumerate(distinct_characters):
        cp = []
        for idx, pc in enumerate(paragraph_characters):
            if char in pc:
                cp.append(idx1)
            else:
                cp.append(np.nan)
        character_presences.append(cp)
print("Character presences: " + str(character_presences))

character_dict = dict()
for idx, cp in enumerate(character_presences):
    character_dict[distinct_characters[idx]] = cp
df = pd.DataFrame(character_dict, index = paragraph_list)
df.index.name = 'paragraphs'
print("DF: " + str(df))

fig, ax = plt.subplots()

for key in character_dict:
    print("Plotting " + str(key))
    line, = ax.plot(df[key].fillna(method='ffill'), ls = ' ', lw = 1, label='_nolegend_')
    ax.plot(df[key], color=line.get_color(), lw=1.5, marker = 'o')

#ax.set_xlim([0,len(paragraph_characters)])
#ax.set_ylim([0,len(distinct_characters)])
#plt.xlim(0,len(paragraph_characters)-1)
#plt.ylim(0,len(distinct_characters)-1)
plt.xticks(range(len(paragraph_characters)))
plt.yticks(range(len(distinct_characters)))

plt.xlabel('paragraph')
plt.ylabel('character')

# replace labels
labels=ax.get_yticks().tolist()
print("Labels are: " + str(labels))
for idx, char in enumerate(distinct_characters):
    labels[idx] = char
print("Labels are now: " + str(labels))
ax.set_yticklabels(labels)

#fig.savefig(self.out_path + r"/char_" + str(twineid) + ".png")
plt.show()
plt.close(fig)