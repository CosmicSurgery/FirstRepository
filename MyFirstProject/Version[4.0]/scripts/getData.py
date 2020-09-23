import pandas as pd
from scripts.parsedData import parsedData as data

df = pd.DataFrame(data, columns=['Date', 'Time', 'Author', 'Message', 'Conversation'])

authors = df['Author'].unique()
conversations = df['Conversation'].unique()

df = df.drop(df[df['Author'].isnull()].index)
df['Word Count'] = df['Message'].apply(lambda s : len(s.split(' ')))

df['Datetime'] = df['Date'] +' '+ df['Time']
df['Datetime'] = pd.to_datetime(df['Datetime'])

df['Sent Messages'] = 1
df['Sent Words'] = df['Word Count']
df['WPM'] = 0
df['Total Messages'] = 1
df['Total Words'] = df['Word Count']

new_df = pd.DataFrame()

for group in conversations:
    subset_group = df[df.Conversation == group].copy()
    authors = list(subset_group.Author.unique())
    
    subset_group['Total Messages'] = subset_group['Total Messages'].cumsum()
    subset_group['Total Words'] = subset_group['Total Words'].cumsum()

    for key in authors:
        subset = subset_group[subset_group.Author == key].copy()
        
        subset['Sent Messages'] = subset['Sent Messages'].cumsum()
        subset['Sent Words'] = subset['Sent Words'].cumsum()
        
        new_df = new_df.append(subset)
        

df = new_df[['Datetime', 'Author', 'Conversation', 'Sent Messages', 'Sent Words', 'WPM', 'Total Messages', 'Total Words']].copy()
df['WPM'] = df['Sent Words'] / df['Sent Messages']
df = df.sort_values(['Datetime'])

