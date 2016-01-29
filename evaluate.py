import sys

def evaluate(gold, output):
    with open(gold) as g, open(output) as o:
        gold_labels = [line.split()[1].strip() for line in g.readlines()
                       if line.strip()]
        output = [line.strip() for line in o.readlines() if line.strip()]
    total = 0.
    correct = 0.
    assert(len(gold_labels) == len(output))
    for gold, out in zip(gold_labels, output):
        if gold == 'O':
            continue
        else:
            if gold == out:
                correct += 1
                total += 1
            else:
                total += 1
    return correct / total

if __name__ == '__main__':
    print evaluate(sys.argv[1], sys.argv[2])
