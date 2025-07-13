# Calculate the accuracy of a baseline that simply predicts "London" for every
#   example in the dev set.
# Hint: Make use of existing code.
# Your solution here should only be a few lines.
from tqdm import tqdm
import utils
import argparse

argp = argparse.ArgumentParser()
argp.add_argument('--eval_corpus_path', default="birth_dev.tsv")
args = argp.parse_args()

correct = 0
total = 0
predictions = []
for line in tqdm(open(args.eval_corpus_path, encoding='utf-8')):
    predictions.append("London")
total, correct = utils.evaluate_places(args.eval_corpus_path, predictions)
print('Correct: {} out of {}: {}%'.format(correct, total, correct/total*100))

