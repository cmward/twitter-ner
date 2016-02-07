import sys

def evaluate(gold, output):
    with open(gold) as g, open(output) as o:
        gold_labels = [line.split()[2].strip() for line in g.readlines()
                       if line.strip()]
        output = [line.strip() for line in o.readlines() if line.strip()]
    total = 0.
    correct = 0.
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

def precision(gold, output, label='B'):
    with open(gold) as g, open(output) as o:
        gold_labels = [line.split()[2].strip() for line in g.readlines()
                       if line.strip()]
        output = [line.strip() for line in o.readlines() if line.strip()]
        tp = 0.
        fp = 0.
        for gold, out in zip(gold_labels, output):
            if out == label:
                if gold == label:
                    tp += 1
                else:
                    fp += 1
        return tp / (tp + fp)

def recall(gold, output, label='B'):
    with open(gold) as g, open(output) as o:
        gold_labels = [line.split()[2].strip() for line in g.readlines()
                       if line.strip()]
        output = [line.strip() for line in o.readlines() if line.strip()]
        tp = 0.
        fn = 0.
        for gold, out in zip(gold_labels, output):
            if gold == label:
                if out == label:
                    tp += 1
                else:
                    fn += 1
        return tp / (tp + fn)


if __name__ == '__main__':
    gold = sys.argv[1]
    out = sys.argv[2]
    acc = evaluate(gold, out)
    p_b = precision(gold, out, label='B')
    p_i = precision(gold, out, label='I')
    r_b = recall(gold, out, label='B')
    r_i = recall(gold, out, label='I')
    f1_b = 2 * (p_b*r_b)/(p_b+r_b)
    f1_i = 2 * (p_i*r_i)/(p_i+r_i)
    print "Accuracy on B/I tags: {}".format(acc)
    print "Precision (B): {}".format(p_b)
    print "Recall (B): {}".format(r_b)
    print "F1 (B): {}".format(f1_b)
    print "Precision (I): {}".format(p_i)
    print "Recall (I): {}".format(r_i)
    print "F1 (I): {}".format(f1_i)

