import numpy as np
import files as fs
import time

def get_pattern_matrix(guesses, answers):
    """
    Vectorized calculation of the pattern matrix.
    Returns a (n_guesses, n_answers) uint8 matrix.
    Values: 0=Gray, 1=Yellow, 2=Green (Base 3 encoded: 2*3^i)
    """
    # Convert strings to uint8 np array as ascii values
    # This is like (X , 5) shape
    guess_arr = np.array([list(w.encode()) for w in guesses], dtype=np.uint8)
    answer_arr = np.array([list(w.encode()) for w in answers], dtype=np.uint8)

    n_guesses = len(guesses)
    n_answers = len(answers)

    # Initialize matrix

    matrix = np.zeros((n_guesses, n_answers), dtype=np.uint8)

    # guess_arr: (G, 1, 5)
    # answer_arr: (1, A, 5)
    G = guess_arr[:, None, :]
    A = answer_arr[None, :, :]

    greens = (G == A)

    pass

from numba import jit, prange

@jit(nopython=True, parallel=True)

def populate_matrix_numba(guess_arr, answer_arr):
    n_guesses = guess_arr.shape[0]
    n_answers = answer_arr.shape[0]
    matrix = np.zeros((n_guesses, n_answers), dtype=np.uint8)

    multipliers = np.array([81, 27, 9, 3, 1], dtype=np.uint8)

    for i in prange(n_guesses):
        for j in range(n_answers):
            g = guess_arr[i]
            a = answer_arr[j]

            temp_a = np.empty(5, dtype=np.uint8)
            for k in range(5):
                temp_a[k] = a[k]

            code = 0
            colors = np.zeros(5, dtype=np.uint8)

            # GREEN PASS
            for k in range(5):
                if g[k] == temp_a[k]:
                    colors[k] = 2
                    temp_a[k] = 255 # Mark answer index as used

            # YELLOW PASS
            for k in range(5):
                if colors[k] == 0: # Not green
                    g_char = g[k]
                    for m in range(5):
                        if temp_a[m] == g_char:
                            colors[k] = 1
                            temp_a[m] = 255 # Mark used
                            break
            # Compute Base 3
            val = 0
            for k in range(5):
                val += colors[k] * multipliers[k]

            matrix[i][j] = val

    return matrix

def make_matrix():
    print("Loading word lists...")
    rows_dict = fs.load_word_list('allowed_words.txt')
    cols_dict = fs.load_word_list('answer_words.txt')

    guesses = list(rows_dict.keys())
    answers = list(cols_dict.keys())

    print("Converting to uint8 arrays...")
    guess_arr = np.array([list(w.lower().encode()) for w in guesses], dtype=np.uint8)
    answer_arr = np.array([list(w.lower().encode()) for w in answers], dtype=np.uint8)

    print(f"Computing matrix {guess_arr.shape} x {answer_arr.shape}...")
    start = time.time()

    # Numba compilation happens on first call, so it might take 1 second extra
    matrix = populate_matrix_numba(guess_arr, answer_arr)

    end = time.time()
    print(f"Done in {end - start:.2f} seconds!")

    np.save("matrix.npy", matrix)

if __name__ == "__main__":
    make_matrix()




