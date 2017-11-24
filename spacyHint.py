"""
spacyPredictor.py

This file allows generating hints by measuring
the words using spaCy word vector models.
"""

import spacy
import numpy

def similarity(wv1, wv2):
    """ compare similarity between two numpy vectors
    Adapted from wordembeddings lab from class
    """
    if (numpy.linalg.norm(wv1) == 0) or (numpy.linalg.norm(wv2) == 0):
        return 0.0
    return numpy.dot(wv1, wv2) / numpy.linalg.norm(wv1) * numpy.linalg.norm(wv2)

def tenMostSimilar(vector, vectorModel):
    """ Return the 10 most similar words compared to the given vector
    Adapted from wordembeddings lab from class
    """
    similarWords = []
    for w in vectorModel.vocab:
        if (w.has_vector) and (w.orth_.islower()) and (w.lower_ not in words):
            similarWords.append(w)
    similarWords.sort(key=lambda w: similarity(w.vector, vector), reverse=True)
    return similarWords[:10]

def chooseHint(candidates, words):
    """ Pick the first candidate hint that does not overlap the
    current board, represented by words.

    :param candidates:  List of candidate hints, as spaCy lexemes
    :param words:       List of word strings
    """
    if len(candidates) > 0:
        for clue in candidates:
            if not overlap(clue.orth_, words):
                return clue

def overlap(hint, words):
    """ Check if the hint has overlaps or is overlapped
    by any word in words. (e.g. 'clown' in 'clowns')

    :param hint:    The proposed hint string
    :param words:   List of word strings
    """
    overlap = False
    for codename in words:
        overlap = overlap or (hint in codename or codename in hint)
    return overlap

def filterBoard(board, keyCard, vectorModel):
    """ Organize the given codenames on the board,
    categorizing each word according to role,
    then generating a spaCy lexeme of each word.
    """
    blues = []
    reds = []
    assassin = ''
    for i in range(len(keyCard)):
        if keyCard[i] == 3:
            assassin = board[i]
        elif keyCard[i] == 2:
            reds.append(board[i])
        elif keyCard[i] == 1:
            blues.append(board[i])
    blues = [vectorModel.vocab[b] for b in blues if b != 'BLU']
    reds = [vectorModel.vocab[r] for r in reds if r != 'RED']
    return blues, reds, vectorModel.vocab[assassin]

def selectReferences(blues, reds, threshold):
    """ Select the best set of words to create a hint for,
    based on the words' similarity with each other.

    :param blues:       list of operatives on the blue team, as spaCy lexemes
    :param reds:        list of operatives on the red team, as spaCy lexemes
    :param threshold    similarity threshold between two words, from 0-1
    """
    plus = {}
    minus = {}
    score = {}
    for i in range(len(blues)):
        bi = blues[i]
        plus[bi] = []
        minus[bi] = []
        for j in range(len(blues)):
            if i != j:
                bj = blues[j]
                if bi.similarity(bj) > threshold:
                    plus[bi].append(bj)
        for k in range(len(reds)):
            if i != k:
                rk = reds[k]
                if bi.similarity(rk) > threshold:
                    minus[bi].append(rk)
        score[bi] = len(plus[bi]) - len(minus[bi])
    scoreVals = list(score.values())
    bestScoreIndex = scoreVals.index(max(scoreVals))
    bestKey = list(score.keys())[bestScoreIndex]
    return [bestKey] + plus[bestKey]

def averageVector(words):
    """ Find the average of the vectors of each given word.

    :param words: a list of spaCy lexemes
    """
    sum = None
    for w in words:
        if sum is None:
            sum = w.vector
        else:
            sum += w.vector
    return sum / len(words)

def generateHint(board, keyCard):
    """ Generate a hint based on spaCy's word vector model.
    """
    vectorModel = spacy.load('en_vectors_web_lg')
    blues, reds, assassin = filterBoard(board, keyCard, vectorModel)
    refs = selectReferences(blues, reds, 0.4)
    v = averageVector(refs)
    v -= assassin.vector
    similar = tenMostSimilar(v, vectorModel)
    hint = chooseHint(similar, board)
    return (hint.orth_, len(refs))

if __name__ == '__main__':
    words = ['clown', 'sphere', 'money', 'cube', 'box']
    keyCard = [1, 1, 1, 2, 3]
    hint = generateHint(words, keyCard)
    print(hint)
