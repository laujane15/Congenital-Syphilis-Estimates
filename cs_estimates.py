import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
import xlwings as xw
import itertools
import pprint
import ci_class_12032024
from ci_class_12032024 import CI
class CS:
    def __init__(self, anc1_attendance,
                 anc1_coverage, prevalence,
                  test, treat, *kwargs):
        '''

        :param anc1_attendance: total number of anc1 attendees
        :param anc1_coverage: percentage of pregnant women that are missed with anc1 attendees
        :param prevalence:
        :param test: testing coverage (needs to be as a decimal less than <1)
        :param treat: treatment coverage (needs to be as a decimal less than <1, percent out of 100%)
        :param kwargs: if known, livebirths
        '''
        self.anc1_coverage = anc1_coverage
        self.anc1_attendance = anc1_attendance
        self.births = kwargs
        self.prevalence = prevalence
        self.test = test
        self.treat = treat

    def get_diganostic_correction(self):
        '''
      Active syphilis is defined as testing positive concurrently
      positive on a treponemal test and on a non-treponemal test.
      This is the definition used by the
      WHO and the *Institute of Health Metrics
      and Evaluation* in their regional and
      global syphilis estimates.

        Prevalence studies that provide data for
        just a treponemal test or a non-treponemal
        test are adjusted using standard parameter
        values.
        :return:
        '''
        diagnostic_dict = {
            'RPR(any titer) & TPHA': 1,
            'TPHA in ANC or FP population': 0.53,
            'TPHA in non - ANC non - FP population': 0.53,
            'RPR|VDRL': 0.53,
            'Rapid syphilis test(TPHA - based)': 0.7,
            'Test unknown': 0.75,
            'RPR >= 1: 8': 2.5}
        return diagnostic_dict
    def get_active_prev(self, diag_type):
        '''
        Calls in diagnostic_correction dictionary and adjusts for prevalence
        :param diag_type: diagnostic type from diagnostic dictionary
        :return:
        '''
        diag_dict = self.get_diganostic_correction()
        for key, value in diag_dict.items():
            if key == diag_type:
                prev = value * self.prevalence
                return prev
    def total_pregnant(self):
        '''
        Returns total pregnant +
        including anc1_attendance +
        :return:
        '''
        percent_missing = (1 - self.anc1_coverage) + 1
        total_preg = percent_missing * self.anc1_attendance
        print(f'total pregnant= {total_preg}')
        return total_preg
    def get_pas(self):
        '''
        get the total number of presumed active syphilis (PAS)
         infections.
        :return:
        '''
        pas_prevalence = self.get_active_prev(diag_type="Test unknown")
        total_pregnant = self.total_pregnant()
        total_pas = total_pregnant * pas_prevalence
        return total_pas
    def abos_untreated(self):
        '''

        :return:
        '''
        abos_untreated = {
            'cs_liveborn':0.16,
            'cs_stillbirth':0.21,
            'cs_neonatal_death':0.09,
            'cs_premature_lbw':0.06
        }
        return abos_untreated
    def abos_treated_ab(self):
        '''
        :return: Dictionary of ABOs risks
        in treated cases
        depending on trimester of treatment (this is
        (A&B) 1-2nd trimester)
        '''
        abos_treated_trimester_a_b = {
            'cs_liveborn':0.97,
            'cs_stillbirth':0.82,
            'cs_neonatal_death':0.8,
            'cs_premature_lbw':0.64
        }
        return abos_treated_trimester_a_b
    def abos_treated_c(self):
        '''
        Dictionary of ABOs risks in treated cases
        depending on trimester of treatment (this is
        (C) 3rd trimester)
        :return:
        '''
        abos_treated_trimester_c = {
            'cs_liveborn':0.485,
            'cs_stillbirth':0.41,
            'cs_neonatal_death':0.4,
            'cs_premature_lbw':0.32
        }
        return abos_treated_trimester_c
    def abos_treated_total(self):
        '''
    Total number of liveborns with “clinical” CS in treated women  = CS risk liveborn (currently 0.16)
    X[(proportion of treatment in trimester A X  (1- effectiveness of treatment on CS risk liveborn in trimester A) +
      (proportion of treatment in trimester B X  (1- effectiveness of treatment on CS risk liveborn in trimester B +
      (proportion of treatment in trimester C X  (1- effectiveness of treatment on CS risk liveborn in trimester C)] X
    Number treated syphilis infected pregnancies

        :return:
        '''
        total_treated_during_pregnancy = self.pas_cascade()[0]
        trimester_a_treatment =.4
        trimester_b_treatment =.5
        trimester_c_treatment =.1
        untreated = self.abos_untreated()
        treatedAB = self.abos_treated_ab()
        treatedC = self.abos_treated_c()
        liveborns = (untreated['cs_liveborn']*
                     ((trimester_a_treatment*(1-treatedAB['cs_liveborn']))
                    + (trimester_b_treatment*(1-treatedAB['cs_liveborn']))
                    + (trimester_c_treatment*(1-treatedC['cs_liveborn'])))
                     * total_treated_during_pregnancy)

        stillbirth = (untreated['cs_stillbirth'] * (
            (trimester_a_treatment * (1 - treatedAB['cs_stillbirth']))
            + (trimester_b_treatment * (1 - treatedAB['cs_stillbirth']))
            + (trimester_c_treatment * (1 - treatedC['cs_stillbirth'])))
                      * total_treated_during_pregnancy)
        neonatal = (untreated['cs_neonatal_death'] * (
            (trimester_a_treatment * (1 - treatedAB['cs_neonatal_death']))
            + (trimester_b_treatment * (1 - treatedAB['cs_neonatal_death']))
            + (trimester_c_treatment * (1 - treatedC['cs_neonatal_death'])))
                    * total_treated_during_pregnancy)
        pre_lbw = (untreated['cs_premature_lbw'] * (
            (trimester_a_treatment * (1 - treatedAB['cs_premature_lbw']))
            + (trimester_b_treatment * (1 - treatedAB['cs_premature_lbw']))
            + (trimester_c_treatment * (1 - treatedC['cs_premature_lbw'])))
                   * total_treated_during_pregnancy)
        total = liveborns + stillbirth + neonatal + pre_lbw
        print(f'ABOs treated:{total}\nliveborns={liveborns}\nstillbirth={stillbirth}\n'
              f'neonatal={neonatal}\npremature/low birthweight={pre_lbw}')
        return total
    def abos_untreated_total(self):
        '''
        :return: total abos from untreated syphilis cases in pregnancy
        '''
        total_untreated = self.pas_cascade()[1]
        print(f'\ntotal untreated PAS={total_untreated}')
        untreated = self.abos_untreated()
        liveborns = untreated['cs_liveborn'] * total_untreated
        stillbirth = untreated['cs_stillbirth'] * total_untreated
        neonatal = untreated['cs_neonatal_death'] * total_untreated
        pre_lbw = untreated['cs_premature_lbw'] * total_untreated
        total = liveborns + stillbirth + neonatal + pre_lbw
        print(f'\nABOs untreated:{total}\n\nliveborns={liveborns}\nstillbirth={stillbirth}\n'
              f'neonatal={neonatal}\n'
              f'premature/low birthweight={pre_lbw}')

        return total
    def pas_cascade(self):
        '''
        Women who don't attend anc or who attend anc but aren't screened are not treated
        :return:
        '''
        pas = self.get_pas()
        notinanc = pas * (1-self.anc1_coverage)
        inanc = pas - notinanc
        pas_notest = inanc * (1 - self.test)
        pas_test = inanc * self.test
        pas_test_treat = pas_test * self.treat
        pas_test_notreat = pas_test * (1 - self.treat)
        total_untreated = pas_notest + pas_test_notreat + notinanc
        print(f"\n\n###Probable active syphilis cases (PAS)###\n"
              f"Attended ANC1 = {inanc}"
              f"\nTested = {pas_test}"
              f"\nNot tested = {pas_notest}"
              f"\nTested and not treated = \n"
              f"{pas_test_notreat}\n"
              f"Tested and treated = {pas_test_treat}\n"
              f"###################################\n\n")
        return pas_test_treat, total_untreated
    def get_total_abos(self):
        '''
        total abo cases from treated and untreated women
        :return:
        '''
        total_dict = {}
        total = self.abos_untreated_total() + self.abos_treated_total()
        total_pregnant = self.total_pregnant()
        print(f'total ABOs due to syphilis\n'
              f'{total}')
        rate = round((total/total_pregnant) * 100000, 2)
        print(f'rate={rate} per 100,000')
        total_dict['total'] = round(total, 2)
        total_dict['rate_per100000']=rate
        return total_dict
    def get_total_cs_cases(self):
        '''
        per WHO definition any birth to sero-positive mother
        :return:
        '''
        total_dict = {}
        total = round(self.pas_cascade()[1], 2)
        total_pregnant = self.total_pregnant()
        print(f'total CS cases = {total}')
        rate = round((total/total_pregnant) * 100000, 2)
        print(f'rate={rate} per 100,000')
        ci_hi, ci_lo = CI(total, total_pregnant, 0.05)
        total_dict['total'] = round(total, 2)
        total_dict['rate_100000']=rate
        total_dict['cihi']=round((ci_hi) * 100000, 2)
        total_dict['cilo']=round((ci_lo) * 100000, 2)

        return total_dict
anc1_coverage = .951
def get_total():
    abos = CS(815, anc1_coverage,
                   .111,.7,
               .6,.5).get_total_abos()
    cs = CS(815, anc1_coverage,
                   .111,.7,
               .6,).get_total_cs_cases()
    return abos, cs
