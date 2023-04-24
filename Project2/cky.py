import string
from collections import defaultdict

def getRules(rules, cnf):
    file = open(cnf)
    lines = file.readlines()
    for line in lines:
        line.strip()
        splitLines = line.split()
        # Condition for a A --> B rule
        if len(splitLines) == 3:
          try:
            rules[splitLines[0]].append(splitLines[2])
          except KeyError:
            rules[splitLines[0]] = splitLines[2]
        # Condition for a A --> B C rule
        else:
          try:
            rules[splitLines[0]].append((splitLines[2], splitLines[3]))
          except KeyError:
            rules[splitLines[0]] = (splitLines[2], splitLines[3])

def applyCky(rules, words):
      # Example: i book the flight through houston
      # Word length is 6, want table ranging from 0-6 => len(words) + 1
      table = [[[] for _ in range(len(words) + 1)] for _ in range(len(words) + 1)]

      # Increment through coloumns from 1->6 => 1 -> len(words) + 1
      # [i][0] column is left empty in this algorithm
      for j in range(1, len(words) + 1):
        # This loop goes through diagonals, thus check terminal rules
        for A, B in rules.items():
          for specificName in B:
            if words[j-1] == specificName:
              table[j-1][j].append((A, words[j-1]))

        # Check the locations that needed for current value (left side and right side)
        for i in reversed(range(j-1)):
           for k in range(i+1, j):
            leftHandRules = table[i][k]
            rightHandRules = table[k][j]

            # Check conditionals on each side to see if they give the desired rule
            for lhr in leftHandRules:
              for rhr in rightHandRules:
                for A, BC in rules.items():
                  for tup in BC:
                    if len(tup) == 1:
                      continue
                    else:
                      if (lhr[0] == tup[0]) & (rhr[0] == tup[1]):
                        table[i][j].append((A, (lhr, rhr)))
                        # Breaking to prevent appending duplicate values
                        break
      # Return the topright value of the table
      return table[0][len(words)]

def getWords(sentence):
  translating = str.maketrans('', '', string.punctuation)
  noPunct = sentence.translate(translating)
  words = noPunct.lower().split()
  return words

def globalParse(parses, treeStatus):
  if treeStatus == "quit":
    print("Goodbye!")
    return 0
  else:
    if len(parses) == 0:
      print("\nNO VALID PARSES")
    else:
      numParses = 0
      for p in parses:
        numParses += 1
        tree = parseTreeTuple(p, 0)
        parse = parseTuple(p)
        print("\nValid parse #", numParses)
        print(parse.lstrip())
        if(treeStatus == "y"):
          print("\n")
          print(tree)
      print("\nNumber of valid parses: ", numParses)
      return 1

def parseTreeTuple(tup, offset):
  output = ""
  A = tup[0]
  B = tup[1]
  if not isinstance(B, tuple):
    output = "[" + A + " " + B + "]"
    for i in range(offset):
      output = "\t" + output
    return output

  for i in range(offset):
    output += "\t"
  output += "[" + A
  B = parseTreeTuple(tup[1][0], offset + 1)
  output += "\n" + B
  C = parseTreeTuple(tup[1][1], offset + 1)
  output += "\n" + C + "\n"
  for i in range(offset):
    output = output + "\t"
  output = output + "]\n"
  return output

def parseTuple(tup):
  output = ""
  A = tup[0]
  B = tup[1]
  if not isinstance(B, tuple):
    output = " [" + A + " " + B + "]"
    return output

  output = " [" + A
  B = parseTuple(tup[1][0])
  output +=  B
  C = parseTuple(tup[1][1])
  output +=  C
  output += "]"
  return output

if __name__ == "__main__":
    cnf = input('Enter the CNF grammar file: ')
    sentence = ""
    treeStatus = input("Do you want textual parse trees to be dispalyed (y/n)?: ")
    status = 1
    while status:
      sentence = input('Enter a sentence: ')
      if(sentence == "quit"):
        treeStatus = "quit"
      rules = defaultdict(list)
      terminals = defaultdict(list)
      words = getWords(sentence)
      getRules(rules, cnf)
      parses = applyCky(rules, words)
      status = globalParse(parses, treeStatus)