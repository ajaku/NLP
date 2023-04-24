from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import string
import math
import os


def tokenize(fileContent):
    tokenized = word_tokenize(fileContent)

    lower = [x.lower() for x in tokenized]

    stopWords = set(stopwords.words('english'))
    ls = WordNetLemmatizer()
    filteredTokens = []
    for word in lower:
        if word in stopWords:
            word = word.replace(word, "")
        if word in string.punctuation:
            word = word.replace(word, "")
        if len(word) <= 2:
            word = word.replace(word, "")
        if any(char.isdigit() for char in word):
            word = word.replace(word, "")
        if word.strip():
            # word = ls.lemmatize(word)
            filteredTokens.append(word)
    return filteredTokens


def createVec(inp):
    file = open(inp)
    lines = file.readlines()
    vec = []
    for line in lines:
        temp = line.strip()
        vec.append(temp)
    return vec


def createTuple(inp):
    file = open(inp)
    lines = file.readlines()
    vec = []
    for line in lines:
        temp = line.strip()
        vec.append(tuple(temp.split(' ')))
    return vec

def trainTF(tup, tf):
    temp = {}
    for x, y in tup:
        file = open(x).read()
        tokens = tokenize(file)
        for word in tokens:
            try:
                tf[y][word] += 1
            except KeyError:
                tf[y][word] = 1
    for x, y in tup:
        file = open(x).read()
        tokens = tokenize(file)

        uniqueTokens = []
        for t in tokens:
            if t not in uniqueTokens:
                uniqueTokens.append(t)
        for i in tf.keys():
            temp[i] = {}
            for j in tf[i].keys():
                temp[i][j] = math.log10(tf[i][j] + 1)
    return temp

def testTF(vec):
    tf = {}
    temp = {}
    for x in vec:
        file = open(x).read()
        tokens = tokenize(file)
        tf[x] = {}
        temp[x] = {}
        for word in tokens:
            try:
                tf[x][word] += 1
            except KeyError:
                tf[x][word] = 1
        uniqueTokens = []
        for t in tokens:
            if t not in uniqueTokens:
                uniqueTokens.append(t)
        for i in tf.keys():
            temp[i] = {}
            for j in tf[i].keys():
                temp[i][j] = math.log10(tf[i][j] + 1)

    return temp

# Normalize TF Category Vector
# Create a unit vector:
#   Sqrt of the sum of all values squared
# take each component and divide by unit vector
# NEED TO MULTIPLY BY IDF
def normalizeCat(tf):
    sumVec = {} 
    normVec = {}   
    for cat in tf:
        sumVec[cat] = 0
        normVec[cat] = 0
        for word in tf[cat].keys():
            sumVec[cat] += tf[cat][word]**2
        
        for i in sumVec.items():
            normVec[cat] = math.sqrt(sumVec[cat])

    temp = {}
    for cat in tf:
        temp[cat] = {}
        for word in tf[cat].keys():
            temp[cat][word] = tf[cat][word]/normVec[cat]
    
    return temp


def cIDF(tup):
    idf = {}
    docs = 0
    for x, _ in tup:
        docs += 1
        file = open(x).read()
        tokens = tokenize(file)
        uniqueTokens = []
        for i in tokens:
            if i not in uniqueTokens:
                uniqueTokens.append(i)
        for token in uniqueTokens:
            try:
                idf[token] += 1
            except KeyError:
                idf[token] = 1

    for keys in idf:
        idf[keys] = math.log10(docs/idf[keys])

    return idf


def computeProbs(vec, tf, tfDoc, idf, tup):
    outVals = []
    for i in vec:
        file = open(i).read()
        tokens = tokenize(file)
        dic = {}

        # Replacement
        for keys in tf:
            upVal = {keys: 0}
            dic.update(upVal)
            for token in tokens:
                try:
                    dic[keys] += tf[keys][token] * tfDoc[i][token] * idf[token]*idf[token]
                except KeyError:
                    dic[keys] += 0
        maxKey = max(zip(dic.values(), dic.keys()))[1]
        outVals.append((i, maxKey))
    return outVals


def createOutput(out, outVals):
    try:
        os.remove(out)
    except FileNotFoundError:
        out = out
    for x, y in outVals:
        with open(out, "a") as f:
            f.write(x)
            f.write(" ")
            f.write(y)
            f.write("\n")
            f.close()


def getFileCats(tup):
    catType = ""
    for _, y in tup:
        if y == ("Str" or "Pol" or "Dis" or "Cri" or "Oth"):
            catType = "cat1"
        if y == ("O" or "I"):
            catType = "cat2"
        if y == ("Wor" or "USN" or "Sci" or "Fin" or "Spo" or "Ent"):
            catType = "cat3"

    return catType


if __name__ == "__main__":
    inp = input('Enter input training file: ')
    inpTup = createTuple(inp)

    cat = getFileCats(inpTup)
    if cat == "cat1":
        tf = {
            'Str': {},
            'Pol': {},
            'Dis': {},
            'Cri': {},
            'Oth': {}
            }
    if cat == "cat2":
        tf = {
            'O': {},
            'I': {},
            }
    if cat == "cat3":
        tf = {
            'Wor': {},
            'USN': {},
            'Sci': {},
            'Fin': {},
            'Spo': {},
            'Ent': {}
            }

    testInp = input('Enter testing file: ')
    testVec = createVec(testInp)

    fileOut = input('Enter output file: ')
    outVec = createVec(testInp)

    tfTrain = trainTF(inpTup, tf)
    tfNorm = normalizeCat(tfTrain)
    tfTest = testTF(testVec)
    idfTrain = cIDF(inpTup)

    prob = computeProbs(testVec, tfNorm, tfTest, idfTrain, inpTup)
    createOutput(fileOut, prob)