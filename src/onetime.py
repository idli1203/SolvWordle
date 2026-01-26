import numpy as np
import files as fs
# Compute the base 3 thing of 0 1 2 to keep track of the feedback.
def ComputeBase3(feedback: str):

  temp = np.frombuffer(feedback.encode() , dtype=np.uint8) - ord('0')
  mult = np.array([81 , 27 , 9 , 3 , 1])

  feedbackbase3 = np.dot(temp , mult)

  return feedbackbase3

## Compare two word and classify them
# 0 for gray , 1 for yellow and 2 fro green

def CompareWords(word1: str , word2: str):

  feedback = "" # The feedback string calculation
  mp = defaultdict(int)
  for i in range(5):
    mp[word1[i]] += 1
  for i in range(5):
    if word2[i] == word1[i]:
      feedback += "2"
      mp[word2[i]] -= 1
    elif word2[i] in word1:
      feedback += "1"
      mp[word2[i]] -= 1
    else :
      feedback += "0"
  return feedback

def make_matrix():

  rows = fs.load_word_list('allowed_words.txt')
  columns = fs.load_word_list('answer_words.txt')

  matrix = np.zeros((len(rows) , len(columns)) , dtype = np.int16)


## now make matrix for total and possible words and keep a pattern of them
def populate_matrix(possible_words : dict, answer_list : dict , matrix : np.ndarray ):

  possible_keys = list(possible_words.keys())
  answer_keys = list(answer_list.keys())

  for i, pw in enumerate(possible_keys):
    for j, aw in enumerate(answer_keys):
      matrix[i][j] = ComputeBase3(CompareWords(pw, aw))

  np.save("matrix.npy" , matrix)




