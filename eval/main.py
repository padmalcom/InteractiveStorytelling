import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
 
df0 = pd.read_csv("0coherence.txt", header=0, sep='\t')
df1 = pd.read_csv("1coherence.txt", header=0, sep='\t')
df2 = pd.read_csv("2coherence.txt", header=0, sep='\t')
df3 = pd.read_csv("3coherence.txt", header=0, sep='\t')
df4 = pd.read_csv("4coherence.txt", header=0, sep='\t')

# Data
#df=pd.DataFrame({'x': range(1,11), 'y1': np.random.randn(10), 'y2': np.random.randn(10)+range(1,11), 'y3': np.random.randn(10)+range(11,21) })
 
# multiple line plot
#plt.plot( 'x', 'y1', data=df, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
#plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2)
#plt.plot( 'x', 'y3', data=df, marker='', color='olive', linewidth=2, linestyle='dashed', label="toto")
matplotlib.style.use('seaborn')
ax = plt.gca()
df0.plot(x='id', y='value', ax=ax)
df1.plot(x='id', y='value', ax=ax)
df2.plot(x='id', y='value', ax=ax)
df3.plot(x='id', y='value', ax=ax)
df4.plot(x='id', y='value', ax=ax)
ax.set_ylabel('coherence')
ax.set_xlabel('paragraphs')
plt.legend(['DistilGPT-2','GPT-2 small', 'GPT-2 medium', 'GPT-2 large', 'GPT-2 xl'])
plt.show()