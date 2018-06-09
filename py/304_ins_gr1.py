#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 17:46:32 2018

@author: kazuki.onodera
"""

import os
import pandas as pd
import gc
from multiprocessing import Pool
from glob import glob
import utils
utils.start(__file__)
#==============================================================================
KEY = 'SK_ID_CURR'
No = '304'
PREF = f'ins_{No}'

col_num = ['NUM_INSTALMENT_VERSION', 'NUM_INSTALMENT_NUMBER', 'DAYS_INSTALMENT', 
           'DAYS_ENTRY_PAYMENT', 'AMT_INSTALMENT', 'AMT_PAYMENT']


col_group = ['SK_ID_PREV', 'NUM_INSTALMENT_VERSION', 'NUM_INSTALMENT_NUMBER']

# =============================================================================
# feature
# =============================================================================
ins = utils.read_pickles('../data/installments_payments')
ins = ins[ins['days_delayed_payment']<0]

ins = utils.get_dummies(ins)
ins.drop('SK_ID_PREV', axis=1, inplace=True)

base = ins[[KEY]].drop_duplicates().set_index(KEY)


def nunique(x):
    return len(set(x))

# =============================================================================
# gr1
# =============================================================================
gr = ins.groupby(KEY)

# stats
base[f'{PREF}_{KEY}_size'] = gr.size()

base = pd.concat([
                base,
                gr.min().add_prefix(f'{PREF}_').add_suffix('_min'),
                gr.max().add_prefix(f'{PREF}_').add_suffix('_max'),
                gr.mean().add_prefix(f'{PREF}_').add_suffix('_mean'),
                gr.std().add_prefix(f'{PREF}_').add_suffix('_std'),
                gr.sum().add_prefix(f'{PREF}_').add_suffix('_sum'),
                gr.quantile(0.25).add_prefix(f'{PREF}_').add_suffix('_q25'),
                gr.quantile(0.50).add_prefix(f'{PREF}_').add_suffix('_q50'),
                gr.quantile(0.75).add_prefix(f'{PREF}_').add_suffix('_q75'),
                ], axis=1)


# =============================================================================
# merge
# =============================================================================
base.reset_index(inplace=True)

train = utils.load_train([KEY])
train = pd.merge(train, base, on=KEY, how='left').drop(KEY, axis=1)
utils.to_pickle_each_cols(train, '../feature/train')
del train; gc.collect()


test = utils.load_test([KEY])
test = pd.merge(test, base, on=KEY, how='left').drop(KEY, axis=1)
utils.to_pickle_each_cols(test,  '../feature/test')






#==============================================================================
utils.end(__file__)


