#!/usr/bin/python

from statsmodels.tsa import stattools
from statsmodels.tsa.stattools import grangercausalitytests

import numpy as np

class GrangerCausality(object):
    def __init__(self, significance_level):
        self.significance_level = significance_level

    def is_granger_causal(self, x1, x2, lag=None):
        '''
        does x2 granger cause x1?
        '''
        if lag is None:
            lag = self.find_optimal_lag(x1, x2)

        input_data = np.column_stack((x1, x2))
        results = grangercausalitytests(input_data, maxlag=lag, verbose=False)
        pvalues = []
        for r in results:
            pvalues.append(results[r][0]['ssr_ftest'][1])
        pvalues = np.array(pvalues)
        causal = False
        if (np.min(pvalues) < self.significance_level):
            causal = True
        return causal, np.argmin(pvalues), np.min(pvalues)

    def find_optimal_lag(self, x1, x2):
        '''
        TODO: calculate this based on length of data?
        '''
        return 30
