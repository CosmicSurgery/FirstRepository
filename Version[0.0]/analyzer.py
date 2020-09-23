import re
import pandas as pd
import matplotlib.pyplot as plt
   #For the time graph
import matplotlib.dates as mdates
import datetime as dt
from numpy import cumsum
from qbstyles import mpl_style
mpl_style(dark=True)

def startsWithDateTime(s):
   pattern = '^(\d+/\d+/\d+, \d+:\d+\d+ [A-Z]*) -'
   result = re.match(pattern, s)
   if result:
      return True
   return False
    
    
    
def startsWithAuthor(s):
   patterns = [
      'Louisa \(HSK\):',
      'Kira Arlt \(HSK\):',
      'Mr. S:',
      'G-dizzle:',
      'Good Ol\' Kyle:',
      '([\w]+):',                        # First Name
      '([\w]+[\s]+[\w]+):',              # First Name + Last Name
      '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
      '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
      '([+]\d{2} \d{3} \d{3} \d{4}):',   # Mobile Number (US)
      '([+]\d{2} \d{4} \d{7})'           # Mobile Number (Europe)
   ] 
   pattern = '^' + '|'.join(patterns)
   result = re.match(pattern, s)
   if result:
      return True
   return False
   
   
   
conversationPath = '/home/miles/Desktop/socialLogs/Bird Up.txt' 
   
   
def getDataPoint(line):
   # line = 18/06/17, 22:47 - Loki: Why do you have 2 numbers, Banner?
    
   splitLine = line.split(' - ') # splitLine = ['18/06/17, 22:47', 'Loki: Why do you have 2 numbers, Banner?']
    
   dateTime = splitLine[0] # dateTime = '18/06/17, 22:47'
    
   date, time = dateTime.split(', ') # date = '18/06/17'; time = '22:47'
    
   message = ' '.join(splitLine[1:]) # message = 'Loki: Why do you have 2 numbers, Banner?'
    
   if startsWithAuthor(message): # True
      splitMessage = message.split(': ') # splitMessage = ['Loki', 'Why do you have 2 numbers, Banner?']
      author = splitMessage[0] # author = 'Loki'
      message = ' '.join(splitMessage[1:]) # message = 'Why do you have 2 numbers, Banner?'
   else:
      author = None
   return date, time, author, message
    
parsedData = [] # List to keep track of data so it can be used by a Pandas dataframe


with open(conversationPath, encoding="utf-8") as fp:
   fp.readline() # Skipping first line of the file (usually contains information about end-to-end encryption)
        
   messageBuffer = [] # Buffer to capture intermediate output for multi-line messages
   date, time, author = None, None, None # Intermediate variables to keep track of the current message being processed
   while True:
      line = fp.readline() 
      if not line: # Stop reading further if end of file has been reached
         break    
      line = line.strip() # Guarding against erroneous leading and trailing whitespaces
      if startsWithDateTime(line): # If a line starts with a Date Time pattern, then this indicates the beginning of a new message
         if len(messageBuffer) > 0: # Check if the message buffer contains characters from previous iterations
            parsedData.append([date, time, author, ' '.join(messageBuffer)]) # Save the tokens from the previous message in parsedData
         messageBuffer.clear() # Clear the message buffer so that it can be used for the next message
         date, time, author, message = getDataPoint(line) # Identify and extract tokens from the line
         messageBuffer.append(message) # Append message to buffer
      else:
         messageBuffer.append(line) # If a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer
         

df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
print(df.to_string())   
#Data CleanUp to get rid of Media and null authors
media_messages_df = df[df['Message'] == '<Media omitted>']
null_authors_df = df[df['Author'].isnull()]

messages_df = df.drop(null_authors_df.index) # Drops all rows of the data frame containing messages from null authors
messages_df = messages_df.drop(media_messages_df.index) # Drops all rows of the data frame containing media messages
#End of data clean up#

#Adding more data to the dataframe
messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))


###~~~~~~~~~~~~~~~~~~~~~~~~~~###
###         
# First of all I need some sort of parsable list of names that have indices that I 
# cant use in a for loop. In order to reference an element in a df list, 
# use 'iloc[]' to call a numerical index (not the literal value of the left column)

###~~~~~~~~~~~~UNUSED CODE~~~~~~~~~###

temp_df = messages_df['Date'].drop_duplicates()
date_list = [dt.datetime.strptime(d, '%m/%d/%y').date() for d in temp_df]
tot_message_counts = cumsum(messages_df['Date'].value_counts().sort_index())

author_list = messages_df['Author'].drop_duplicates().values
df_list = {}


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
###~~~~~~ BUILDING THE CALENDAR ~~~###
date_range = pd.date_range(messages_df['Date'].iloc[0], messages_df['Date'].iloc[len(messages_df['Date'])-1])

date_range = date_range.strftime('%m/%d/%y')

date_range = pd.DataFrame(date_range, columns = ['Date'])
date_range['Author'] = pd.Series(['Null' for x in range(len(date_range))])

###~~~                           ~~###
###~~~~~~~ Create df w one author ~###
for i in range(len(author_list)):
   user = author_list[i]
   single_auth = messages_df[['Date', 'Author']]
   single_auth = single_auth[single_auth.Author == user]
   single_auth.reset_index(inplace=True, drop=True)
   comb = pd.concat([single_auth, date_range])
   comb['Date'] =pd.to_datetime(comb.Date)
   comb.sort_values(by=['Date'], inplace=True)
   comb.reset_index(inplace=True)
   comb.rename(columns={'index':'counts'},inplace=True)
   
###~~~ CREATE NEW STRUCTURE ~~~~~~###

   message_per_date = pd.pivot_table(data=comb, values = ['counts'], index=['Date'], aggfunc='size').reset_index()
   message_per_date.rename(columns={0:'counts'},inplace=True)
   message_per_date['counts'] = message_per_date['counts'] -1
   message_per_date['counts'] = message_per_date['counts'].cumsum()
   df_list[user]= message_per_date
   plt.plot(df_list[user]['Date'], df_list[user]['counts'], label=user)
      
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###

plt.legend()
plt.show()

#Further Steps:
#  Increase the "sampling rate", in other words make the x-axis also measure to the nearest hour, in order to curve out the lines a little bit better
#  Create an option to measure by word_count or by messages. 
#  Create an AI who replicates my own speech this one will take a while
#  Make the program interactive so I can choose who's chat to analyze simply by running the program























