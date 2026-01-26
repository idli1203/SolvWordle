import numpy as np

# Read the txt file and map words to indices
def load_word_list(file_path : str):
  with open(file_path , "r") as f:
    words = [ line.strip() for line in f]
  
  mapped_words = {}
  for i in range(len(words)):
    mapped_words.append({words[i] : i})

  return mapped_words

# save the dictionary to repository for a one time expensive compute
def save_mapped_as_json(mapped_words : list , file_path : str):
  with open(file_path , "w") as f:
    json.dump(mapped_words , f)

# load this json everytime we need to do something
def load_mapped_as_json(file_path : str):
  with open(file_path , "r") as f:
    mapped_words = json.load(f)
  return mapped_words

# save the entire populated matrix as .npy file to access later




