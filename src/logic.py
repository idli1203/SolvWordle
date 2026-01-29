import numpy as np
import files as fs
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

def pattern_to_int(pattern_str : str):
    val = 0
    multipliers = [81, 27, 9, 3, 1]
    for i, char in enumerate(pattern_str):
        val += int(char) * multipliers[i]
    return val

class WordleSolver:
    def __init__(self):

        self.allowed_dict = fs.load_word_list(os.path.join(curr_dir, 'allowed_words.txt'))
        self.answers_dict = fs.load_word_list(os.path.join(curr_dir, 'answer_words.txt'))

        self.guesses = list(self.allowed_dict.keys())
        self.answers = list(self.answers_dict.keys())

        matrix_path = os.path.join(curr_dir, 'matrix.npy')
        if not os.path.exists(matrix_path):
            matrix_path = os.path.join(curr_dir, '../matrix.npy')

        try:
            self.matrix = np.load(matrix_path)
        except FileNotFoundError:
            print("error : matrix not found")
            self.matrix = None

        self.candidate_indices = np.arange(len(self.answers))

        print(f"Solver Ready! {len(self.candidate_indices)} candidates.")

    def update_candidates(self, guess_word, pattern_str):
        if guess_word not in self.guesses:
             print(f"Warning: {guess_word} not in dictionary!")
             return

        guess_idx = self.guesses.index(guess_word)
        pattern_int = pattern_to_int(pattern_str)

        candidate_patterns = self.matrix[guess_idx, self.candidate_indices]

        valid_mask = (candidate_patterns == pattern_int)

        self.candidate_indices = self.candidate_indices[valid_mask]
        print(f"new candidate set: {len(self.candidate_indices)}")

    def get_best_guesses(self, top_k=10):
        if len(self.candidate_indices) == 0:
            return []

        sub_matrix = self.matrix[:, self.candidate_indices]

        entropies = []
        n_candidates = len(self.candidate_indices)


        # We can optimize this with Numba later
        for i, row in enumerate(sub_matrix):
            _, counts = np.unique(row, return_counts=True)

            probs = counts / n_candidates
            entropy = -np.sum(probs * np.log2(probs))

            entropies.append((entropy, self.guesses[i]))

        entropies.sort(key=lambda x: x[0], reverse=True)

        return entropies[:top_k]

