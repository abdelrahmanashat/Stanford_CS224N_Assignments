#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CS224N 2022-23: Homework 4
sanity_check.py: Sanity Checks for Assignment 4
Sahil Chopra <schopra8@stanford.edu>
Michael Hahn <>
Vera Lin <veralin@stanford.edu>
Siyan Li <siyanli@stanford.edu>

If you are a student, please don't run overwrite_output_for_sanity_check as it will overwrite the correct output!

Usage:
    sanity_check.py 1d
    sanity_check.py 1e
    sanity_check.py 1f
    sanity_check.py overwrite_output_for_sanity_check
"""
import sys

import numpy as np

from docopt import docopt
from utils import batch_iter
import nltk
from utils import autograder_read_corpus
from vocab import Vocab, VocabEntry

from nmt_model import NMT


import torch
import torch.nn as nn
import torch.nn.utils

#----------
# CONSTANTS
#----------
BATCH_SIZE = 5
EMBED_SIZE = 3
HIDDEN_SIZE = 2
DROPOUT_RATE = 0.0

def reinitialize_layers(model):
    """ Reinitialize the Layer Weights for Sanity Checks.
    """
    def init_weights(m):
        if type(m) == nn.Linear:
            m.weight.data.fill_(0.3)
            if m.bias is not None:
                m.bias.data.fill_(0.1)
        elif type(m) == nn.Embedding:
            m.weight.data.fill_(0.15)
        elif type(m) == nn.Conv1d:
            m.weight.data.fill_(0.15)
        elif type(m) == nn.Dropout:
            nn.Dropout(DROPOUT_RATE)
        elif type(m) == nn.LSTM:
            for param in m.state_dict():
                getattr(m, param).data.fill_(0.1)
        elif type(m) == nn.LSTMCell:
            for param in m.state_dict():
                getattr(m, param).data.fill_(0.1)
    with torch.no_grad():
        model.apply(init_weights)


def generate_outputs(model, source, target, vocab):
    """ Generate outputs.
    """
    print ("-"*80)
    print("Generating Comparison Outputs")
    reinitialize_layers(model)
    model.gen_sanity_check = True
    model.counter = 0

    # Compute sentence lengths
    source_lengths = [len(s) for s in source]

    # Convert list of lists into tensors
    source_padded = model.vocab.src.to_input_tensor(source, device=model.device)
    target_padded = model.vocab.tgt.to_input_tensor(target, device=model.device)

    # Run the model forward
    with torch.no_grad():
        enc_hiddens, dec_init_state = model.encode(source_padded, source_lengths)
        enc_masks = model.generate_sent_masks(enc_hiddens, source_lengths)
        combined_outputs = model.decode(enc_hiddens, enc_masks, dec_init_state, target_padded)

    # Save Tensors to disk
    torch.save(enc_hiddens, './sanity_check_en_es_data/enc_hiddens.pkl')
    torch.save(dec_init_state, './sanity_check_en_es_data/dec_init_state.pkl') 
    torch.save(enc_masks, './sanity_check_en_es_data/enc_masks.pkl')
    torch.save(combined_outputs, './sanity_check_en_es_data/combined_outputs.pkl')
    torch.save(target_padded, './sanity_check_en_es_data/target_padded.pkl')

    # 1f
    # Inputs
    Ybar_t = torch.load('./sanity_check_en_es_data/Ybar_t.pkl', weights_only=True)
    enc_hiddens_proj = torch.load('./sanity_check_en_es_data/enc_hiddens_proj.pkl', weights_only=True)
    reinitialize_layers(model)
    # Run Tests
    with torch.no_grad():
        dec_state_target, o_t_target, e_t_target = model.step(Ybar_t, dec_init_state, enc_hiddens, enc_hiddens_proj,
                                                        enc_masks)
    torch.save(dec_state_target, './sanity_check_en_es_data/dec_state.pkl')
    torch.save(o_t_target, './sanity_check_en_es_data/o_t.pkl')
    torch.save(e_t_target, './sanity_check_en_es_data/e_t.pkl')

    model.gen_sanity_check = False

def question_1d_sanity_check(model, src_sents, tgt_sents, vocab):
    """ Sanity check for question 1d. 
        Compares student output to that of model with dummy data.
    """
    print("Running Sanity Check for Question 1d: Encode")
    print ("-"*80)

    # Configure for Testing
    reinitialize_layers(model)
    source_lengths = [len(s) for s in src_sents]
    source_padded = model.vocab.src.to_input_tensor(src_sents, device=model.device)

    # Load Outputs
    enc_hiddens_target = torch.load('./sanity_check_en_es_data/enc_hiddens.pkl', weights_only=True)
    dec_init_state_target = torch.load('./sanity_check_en_es_data/dec_init_state.pkl', weights_only=True)

    # Test
    with torch.no_grad():
        enc_hiddens_pred, dec_init_state_pred = model.encode(source_padded, source_lengths)
    assert(enc_hiddens_target.shape == enc_hiddens_pred.shape), "enc_hiddens shape is incorrect: it should be:\n {} but is:\n{}".format(enc_hiddens_target.shape, enc_hiddens_pred.shape)
    assert(np.allclose(enc_hiddens_target.numpy(), enc_hiddens_pred.numpy())), "enc_hiddens is incorrect: it should be:\n {} but is:\n{}".format(enc_hiddens_target, enc_hiddens_pred)
    print("enc_hiddens Sanity Checks Passed!")
    assert(dec_init_state_target[0].shape == dec_init_state_pred[0].shape), "dec_init_state[0] shape is incorrect: it should be:\n {} but is:\n{}".format(dec_init_state_target[0].shape, dec_init_state_pred[0].shape)
    assert(np.allclose(dec_init_state_target[0].numpy(), dec_init_state_pred[0].numpy())), "dec_init_state[0] is incorrect: it should be:\n {} but is:\n{}".format(dec_init_state_target[0], dec_init_state_pred[0])
    print("dec_init_state[0] Sanity Checks Passed!")
    assert(dec_init_state_target[1].shape == dec_init_state_pred[1].shape), "dec_init_state[1] shape is incorrect: it should be:\n {} but is:\n{}".format(dec_init_state_target[1].shape, dec_init_state_pred[1].shape) 
    assert(np.allclose(dec_init_state_target[1].numpy(), dec_init_state_pred[1].numpy())), "dec_init_state[1] is incorrect: it should be:\n {} but is:\n{}".format(dec_init_state_target[1], dec_init_state_pred[1])
    print("dec_init_state[1] Sanity Checks Passed!")
    print ("-"*80)
    print("All Sanity Checks Passed for Question 1d: Encode!")
    print ("-"*80)


def question_1e_sanity_check(model, src_sents, tgt_sents, vocab):
    """ Sanity check for question 1e. 
        Compares student output to that of model with dummy data.
    """
    print ("-"*80)
    print("Running Sanity Check for Question 1e: Decode")
    print ("-"*80)

    # Load Inputs
    dec_init_state = torch.load('./sanity_check_en_es_data/dec_init_state.pkl', weights_only=True)
    enc_hiddens = torch.load('./sanity_check_en_es_data/enc_hiddens.pkl', weights_only=True)
    enc_masks = torch.load('./sanity_check_en_es_data/enc_masks.pkl', weights_only=True)
    target_padded = torch.load('./sanity_check_en_es_data/target_padded.pkl', weights_only=True)

    # Load Outputs
    combined_outputs_target = torch.load('./sanity_check_en_es_data/combined_outputs.pkl', weights_only=True)
    print(combined_outputs_target.shape)

    # Configure for Testing
    reinitialize_layers(model)
    COUNTER = [0]
    def stepFunction(Ybar_t, dec_state, enc_hiddens, enc_hiddens_proj, enc_masks):
       dec_state = torch.load('./sanity_check_en_es_data/step_dec_state_{}.pkl'.format(COUNTER[0]), weights_only=True)
       o_t = torch.load('./sanity_check_en_es_data/step_o_t_{}.pkl'.format(COUNTER[0]), weights_only=True)
       COUNTER[0]+=1
       return dec_state, o_t, None
    model.step = stepFunction

    # Run Tests
    with torch.no_grad():
        combined_outputs_pred = model.decode(enc_hiddens, enc_masks, dec_init_state, target_padded)
    assert(combined_outputs_target.shape == combined_outputs_pred.shape), "combined_outputs shape is incorrect: it should be:\n {} but is:\n{}".format(combined_outputs_target.shape, combined_outputs_pred.shape)
    assert(np.allclose(combined_outputs_pred.numpy(), combined_outputs_target.numpy())), "combined_outputs is incorrect: it should be:\n {} but is:\n{}".format(combined_outputs_target, combined_outputs_pred)
    print("combined_outputs Sanity Checks Passed!")
    print ("-"*80)
    print("All Sanity Checks Passed for Question 1e: Decode!")
    print ("-"*80)

def question_1f_sanity_check(model, src_sents, tgt_sents, vocab):
    """ Sanity check for question 1f. 
        Compares student output to that of model with dummy data.
    """
    print ("-"*80)
    print("Running Sanity Check for Question 1f: Step")
    print ("-"*80)
    reinitialize_layers(model)

    # Inputs
    Ybar_t = torch.load('./sanity_check_en_es_data/Ybar_t.pkl', weights_only=True)
    dec_init_state = torch.load('./sanity_check_en_es_data/dec_init_state.pkl', weights_only=True)
    enc_hiddens = torch.load('./sanity_check_en_es_data/enc_hiddens.pkl', weights_only=True)
    enc_masks = torch.load('./sanity_check_en_es_data/enc_masks.pkl', weights_only=True)
    enc_hiddens_proj = torch.load('./sanity_check_en_es_data/enc_hiddens_proj.pkl', weights_only=True)

    # Output
    dec_state_target = torch.load('./sanity_check_en_es_data/dec_state.pkl', weights_only=True)
    o_t_target = torch.load('./sanity_check_en_es_data/o_t.pkl', weights_only=True)
    e_t_target = torch.load('./sanity_check_en_es_data/e_t.pkl', weights_only=True)

    # Run Tests
    with torch.no_grad():
        dec_state_pred, o_t_pred, e_t_pred= model.step(Ybar_t, dec_init_state, enc_hiddens, enc_hiddens_proj, enc_masks)
    assert(dec_state_target[0].shape == dec_state_pred[0].shape), "decoder_state[0] shape is incorrect: it should be:\n {} but is:\n{}".format(dec_state_target[0].shape, dec_state_pred[0].shape)
    assert(np.allclose(dec_state_target[0].numpy(), dec_state_pred[0].numpy())), "decoder_state[0] is incorrect: it should be:\n {} but is:\n{}".format(dec_state_target[0], dec_state_pred[0])
    print("dec_state[0] Sanity Checks Passed!")
    assert(dec_state_target[1].shape == dec_state_pred[1].shape), "decoder_state[1] shape is incorrect: it should be:\n {} but is:\n{}".format(dec_state_target[1].shape, dec_state_pred[1].shape)
    assert(np.allclose(dec_state_target[1].numpy(), dec_state_pred[1].numpy())), "decoder_state[1] is incorrect: it should be:\n {} but is:\n{}".format(dec_state_target[1], dec_state_pred[1])
    print("dec_state[1] Sanity Checks Passed!")
    assert(np.allclose(o_t_target.numpy(), o_t_pred.numpy())), "combined_output is incorrect: it should be:\n {} but is:\n{}".format(o_t_target, o_t_pred)
    print("combined_output  Sanity Checks Passed!")
    assert(np.allclose(e_t_target.numpy(), e_t_pred.numpy())), "e_t is incorrect: it should be:\n {} but is:\n{}".format(e_t_target, e_t_pred)
    print("e_t Sanity Checks Passed!")
    print ("-"*80)    
    print("All Sanity Checks Passed for Question 1f: Step!")
    print ("-"*80)



def main():
    """ Main func.
    """
    args = docopt(__doc__)

    # Check Python & PyTorch Versions
    assert (sys.version_info >= (3, 5)), "Please update your installation of Python to version >= 3.5."
    assert(torch.__version__ >= "1.6.0"), "Please update your installation of PyTorch >= 1.6.0. You have version {}.".format(torch.__version__)

    # Seed the Random Number Generators
    seed = 1234
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed * 13 // 7)

    # Load training data & vocabulary
    train_data_src = autograder_read_corpus('./sanity_check_en_es_data/train_sanity_check.es', 'src')
    train_data_tgt = autograder_read_corpus('./sanity_check_en_es_data/train_sanity_check.en', 'tgt')
    train_data = list(zip(train_data_src, train_data_tgt))

    for src_sents, tgt_sents in batch_iter(train_data, batch_size=BATCH_SIZE, shuffle=True):
        src_sents = src_sents
        tgt_sents = tgt_sents
        break
    vocab = Vocab.load('./sanity_check_en_es_data/vocab_sanity_check.json') 

    # Create NMT Model
    model = NMT(
        embed_size=EMBED_SIZE,
        hidden_size=HIDDEN_SIZE,
        dropout_rate=DROPOUT_RATE,
        vocab=vocab)

    if args['1d']:
        question_1d_sanity_check(model, src_sents, tgt_sents, vocab)
    elif args['1e']:
        question_1e_sanity_check(model, src_sents, tgt_sents, vocab)
    elif args['1f']:
        question_1f_sanity_check(model, src_sents, tgt_sents, vocab)
    elif args['overwrite_output_for_sanity_check']:
        generate_outputs(model, src_sents, tgt_sents, vocab)
    else:
        raise RuntimeError('invalid run mode')


if __name__ == '__main__':
    main()
    
