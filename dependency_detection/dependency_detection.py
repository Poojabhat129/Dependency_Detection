#!/usr/bin/python

from statsmodels.tsa import stattools
from statsmodels.tsa.stattools import grangercausalitytests

import numpy as np
import scipy

class DependencyDetection(object):
    def __init__(self):
        pass

    @staticmethod
    def is_granger_causal(x1, x2, lag=None, significance_level=0.05):
        '''
        does x2 granger cause x1?
        '''
        if lag is None:
            lag = int((x1.shape[0] - 1) / 3) - 1

        input_data = np.column_stack((x1, x2))
        results = grangercausalitytests(input_data, maxlag=lag, verbose=False)
        pvalues = []
        for r in results:
            pvalues.append(results[r][0]['ssr_ftest'][1])
        pvalues = np.array(pvalues)
        mean_pvalue = np.mean(pvalues)
        std_pvalue = np.std(pvalues)
        pvalues = pvalues[pvalues >= mean_pvalue - std_pvalue]
        pvalues = pvalues[pvalues <= mean_pvalue + std_pvalue]
        causal = False
        if (np.min(pvalues) < significance_level):
            causal = True
        return causal, np.argmin(pvalues), np.min(pvalues)

    @staticmethod
    def get_correlation_coefficient(x1, x2):
        return scipy.stats.pearsonr(x1, x2)[0]
