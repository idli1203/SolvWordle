# SolvWordle

A simple wordle Game Solver which uses information theory.

## PLAN OF ACTION

 1. user enter first word.
 2. Then remove the letters from the pool of words which are in gray color.
 3. compute the entropy of the remaining words which follow the feedback pattern.
 4. Then use the words which provide us with the highest amount of entropy.
 5. Later fine tune with n-gram english dataset where we can assign a score to each word based on the frequency of the word in the english language unlike the above where each word is equally likely which is in reality pretty bogus.

## TODO

1. compute the base 3 thing of 0 1 2 to keep track of the feedback.
2. without any prior thing ,compute the probability of each word in the wordlist for that pattern.
3. then sort the words based on probability and return top 10 words kinda.
4. for each of that word entropy should be shown along side.
5. gonna need to repeat this.

## COMPUITNG ENTROPY IS LEFT
