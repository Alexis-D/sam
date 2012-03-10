# -*- coding: utf-8 -*-
"""
file   lm-0_0_2.py
author Ernesto P. Adorio, Ph.D
       UPDEPP at Pampanga,
       UP at Clarkfield
       ernesto.adorio@gmail.com
license For noncommerical educational use
            attribution requested.
desc   least squares class object system
references
        The correlational transform is explained in
        Neter, Wasserman, Kutner, Applied Linear Regression, 2nd ed., p. 289
revisions
      0.0.1 initial release mar 27, 2009
      0.0.2 revised october 12, 2009
             AIC,
             BIC,
             coding,
             withintercept
             polydatamatrix
             DW statistic
"""
from matlib import *
import scipy.stats as stat
from   math import sqrt, log, pi
import numpy
mean     = numpy.var
variance = numpy.var
def colmeans(X):
    # computes the mean of each column of input matrix X.
    k = len(X[0])
    n = len(X)
    cmeans = [0.0] * k
    # is it faster when switching j and i loops?
    for j in range(k):
        for i in range(n):
            cmeans[j] += X[i][j]
    for j in range(k):
        cmeans[j] /= float(n)
    return cmeans
def colvariances(X, cmeans = None):
    # computes the variance of each column of input matrix X.
    if colmeans is None:
       cmeans = colmeans(X)
    k = len(X[0])
    n = len(X)
    cvars = [0.0] * k
    for j in range(k):
        for i in range(n):
            cvars[j] += (X[i][j] - cmeans[j])**2
    for j in range(k):
        cvars[j] /= (n - 1.0)
    return cvars
def lsqcorrmat(X, Y, ztol = 1.0e-5):
    # computes the correlation coefficient matrix of matrix X and vector Y
    # will delete first column if it is a constant vector.
    Z = []
    n1 = sum([1 if x[0]- 1 > ztol else 0 for x in X])
    if n1 == 0:
       # The following needs simplification.
       for (x, y) in zip(X, Y):
          z= x[1:]
          z.append(y)
          Z.append(z)
    return numpy.corrcoef(Z, rowvar = 0)
def DWstat(errvector):
    """
    returns the Durbin watson statistic for error vector.
    Ref: p.491Neter, Wasserman, Kutner.
    """
    N = sum([(e - em1)**2 for (e, em1) in zip(errvector[:-1], errvector[1:])])
    D = sum([e*e for e in errvector])
    return N/D
def AIC(RSS, k, n):
    """
    Computes the Akaike Information Criterion.
       RSS-residual sum of squares of the fitting errors.
       k  - number of fitted parameters.
       n  - number of observations.
    """
    AIC = 2 * k + n * (log(2 * pi * RSS/n) + 1)
    return AIC
def AICc(RSS, k, n):
    """
    Corrected AIC. formula from Wikipedia.
    """
    retval = AIC(RSS, k, n)
    if  n-k-1 != 0:
        retval += 2.0 *k* (k+1)/ (n-k-1)
    return retval
def BIC(RSS, k, n):
    """
    Bayesian information criterion or Schwarz information criterion.
    Formula from wikipedia.
    """
    return n * log(RSS/n) + k * log(n)
class ols:
    def __init__(self, X, Y, makecopy = True, coding=0, withintercept=True, ztol = 1.0e-5):
        """
        Descriotion
             An implementation of basic least squares usin the
             matrix formulation, computing estimates of unknown
             coefficients with attendant statistics.
        Arguments:
          X  - matrix of explanatory or regressor variables.
          Y  - output vector.
          matcopy
              False - do not make a copy. (might change X or Y).
              True  - make a local copy (does not change X or Y.
          coding:
              0 - none.
              1 - centered.  all column values subtracted by column mean.
              2 - standardized. all column values are transformed to (x -xbar) /sd or zscores.
              3 - corellation.  all colummn values are standardized and limited to [-1,1]
          withintercept
              True - prepend a 1 to X.
              False - accept X as is.
          ztol- comparison with zero values.
        """
        n = len(Y)
        self.n = n     # number of observations
        if n != len(X):
            raise Exception("incompatible X and Y lengths")
        if not makecopy:
            self.Y = Y   # a reference to Y, do not erase Y!
            self.X = X   # a reference to X, do not erase X!
        else:
            self.Y = [y for y in Y]
            self.X = matcopy(X)
            self.Y = Y   # a reference to Y, do not erase Y!
        if withintercept:
            #Check whether X has a constant column of 1 and prepend
            #a 1 column if it has none.
            n1 = sum([1 if x[0]- 1 < ztol else 0 for x in X])
            if n1 == 0 and coding == 0:
               for i in range(self.n):
                 self.X[i].insert(0, 1) # prepend a column of all 1s.
        self.k = len(self.X[0]) # number of variables
        if self.n < self.k:
            self = None
            raise Exception("Insufficient number of observations")
        # get the means and variances.
        self.ybar = numpy.mean(Y)
        self.xbars = colmeans(X)
        # and the variances.
        self.yvariance = variance(Y)
        self.xvariances = colvariances(X, cmeans=self.xbars)
        # Coding.
        self.coding = coding
        if coding >= 1: # deviations from mean
           for j in range (self.k):
               for i in range(self.n):
                   self.X[i][j] -= self.means
           for i in range(self.n):
               self.Y[i] -= self.ybar
        elif coding >= 2: # standardized or z-scores
           for j in range (self.k):
               invsd = 1.0 / sqrt(self.xvariances[j])
               for i in range(self.n):
                   self.X[i][j] *= invsd
           invsd = 1.0  / sqrt(self.yvariance)
           for i in range(self.k):
               self.Y[i] *= invsd
        elif coding == 3:  # Correlation transform
           invsqrtnm1 = 1.0/sqrt(self.n-1)
           for j in range (self.k):
               for i in range(self.n):
                   self.X[i][j] *= invsqrtnm1
           for i in range(self.n):
               self.Y[i] *= invsqrtnm1
        # process data matrix.
        self.xtx = mattmat(self.X, self.X)
        # unadjusted variance-covariance matrix.
        self.VC  = matinverse(self.xtx)
        self.xty = mattvec(self.X, self.Y)
        # beta coefficients.
        self.betas = matvec(self.VC, self.xty)
        #residuals and sum of squares
        self.Yhat   = matvec(self.X, self.betas)
        self.resids = vecsub(self.Y, self.Yhat)
        self.DWstat = DWstat(self.resids)
        self.RSS =  dot(self.Y, self.Y) - dot(self.betas, self.xty)
        self.MRSS = self.RSS /(self.n-self.k)
        self.ESS   = dot(self.betas, self.xty) - self.n* self.ybar**2
        self.MRSS  = self.RSS /(self.n-self.k)
        self.MESS  = self.ESS/(self.k-1)
        self.dfESS = self.n-self.k
        self.dfRSS = self.k - 1
        self.TSS  = dot(self.Y,self.Y)- self.n * self.ybar**2
        #adjusted Variance -covariance matrix
        self.varcov = matcopy(self.VC)
        # variance/covariance, correlation matrices.
        self.varcov  = matkmul(self.VC, self.MRSS)
        self.corrmat = lsqcorrmat(X, Y)
        # coefficient of determination, anova table
        self.R2  = self.ESS/self.TSS
        self.adjR2 = 1 - (1 - self.R2) * (self.n-1)/(self.n-self.k)
        self.F = self.MESS/self.MRSS
        self.Fpvalue = 1- stat.f.cdf(self.F,  self.k-1,  self.n - self.k)
        self.anova = []
        self.anova.append(["Source of Variation", "SS", "df", "MSS,F"])
        self.anova.append(["ESS:Due to Xi's", self.ESS, self.k-1, self.MESS])
        self.anova.append(["RSS:Due to residuals", self.RSS, self.n - self.k, self.MRSS])
        self.anova.append(["TSS:Total", self.TSS, str(self.n -1),"F="+str(self.F)])
        # pvalues and computed t.
        self.pvalueF = 1-stat.f.cdf(self.F, self.k-1, self.n-self.k)
        self.sdbetas = [sqrt(self.varcov[i][i]) for i in range(self.k)]
        self.tbetas =  [(self.betas[i] - 0) /self.sdbetas[i] for i in range(self.k)]
        self.tdf = 1
        self.pvalues = [2 * stat.t.cdf(-abs(tbeta), self.tdf) for tbeta in self.tbetas]
        # AIC and BIC criterion
        self.AIC = AIC(self.RSS, self.k, self.n)
        self.BIC = BIC(self.RSS, self.k, self.n)
        self.AICc = AICc(self.RSS, self.k, self.n)
        #Durbin-Watson statistic.
        self.DWstat= DWstat(self.resids)
    def variance_yhat(self, x):
        """
        Variance of individual prediction at x.
        """
        t = matvec(self.VC, x)
        return self.MRSS * dot(x, t)
    def variance_y(self, x):
        """
        To be continued....matcol
        need to be rechecked.
        """
        t = matvec(self.VC, x)
        return self.MRSS * (1 + dot(x, t))
    def estimate(self,x, usecoding = False):
        """
        Given a tuple (x1, x2, ...), returns the least squares estimate.
        Be sure to prepend a 1 if interceprt is used!
        """
        if len(x) < self.k:
           # don't forget prepend a 1 for the constant term
           raise Exception("invalid input x vector")
        if not usecoding:
           return dot(x, self.betas)
        if self.coding >= 1:
           xcoded = [x[i] - self.means[i] for i in range (self.k)]
        elif self.coding >= 2:
           xcoded = [xcoded[i] / self.xvariances[i] for i in range(self.k)]
        elif self.coding ==3:
           xcoded = [xcoded[i]/(sqrt(self.n-1)) for i in range(self.k)]
        return dot(xcoded, self.betas)
def summary_coeffs_stat(fit):
    print "Computed coefficients with standard deviations and p-values."
    tabular(["%10s", "%10s", "%10s", "%10s"],
            ["Betas", "S.E.", "t-values", "pvalues"],
            ["%10.4f", "%10.4f","%10.4f", "%10.5f"],
            zip(fit.betas, fit.sdbetas, fit.tbetas, fit.pvalues))
    print
def summary_anova(fit):
    print "ANOVA for Least Squares"
    for i,row in enumerate(fit.anova):
        if i > 0:
            print "%-20s %15.6f %3s %18s" % (row[0], float(row[1]), row[2], row[3])
        else:
            print "%-20s %15s %3s %18s" % (row[0], row[1], row[2], row[3])
    print
def summary_error_table(fit):
    print "Difference table."
    print "%3s %10s %10s %10s %10s" % ("idx", "Y", "Yhat", "error", "error^2")
    sumu  = 0.0
    sumu2 = 0.0
    for i in range(fit.n):
        error = fit.resids[i]
    out = "%-3d %10.4f %10.4f %10.4f %10.4f" % (i, fit.Y[i], fit.Yhat[i], error, error**2)
    print out
    sumu  += error
    sumu2 += error**2
    print "Totals","%17s" % "", sumu, sumu2
    print "Residual sum of squares:", sum([e**2 for e in fit.resids])
    print
def summary_f_test(fit):
    print "F-test for Testing all Betas = 0.0"
    print "F-value = ", fit.F,  "with df1=",  fit.dfRSS,  "df2=", fit.dfESS
    print "pvalue = ",  fit.pvalueF
    print
def summary_estimate(fit, X):
    print "Example estimation at X :", X
    print "Value of Yhat is ",  fit.estimate(X)
    print "Variance of Yhat is ", fit.variance_yhat(X)
    print
def summary_matrices(fit, sformat="%15.5f"):
    print "X model matrix|Y"
    mataugprint(fit.X, fit.Y, sformat)
    print "XtX|XtY"
    mataugprint(fit.xtx, fit.xty,  sformat)
    print
    print "Inverse XtX|Betas"
    mataugprint(fit.VC, fit.betas,sformat)
    print "Variance-Covariance matrix"
    matprint(fit.varcov)
    print "Correlation Matrix of X and Y"
    matprint( fit.corrmat)
    print
def summary_misc_stat(fit):
    print "Miscellaneous Statistics"
    print "Coef. Determination: R^2=", fit.R2
    print "Adjusted Coef. Determination=", fit.adjR2
    print "AIC, ajdusted AICc=", fit.AIC,",", fit.AICc
    print "BIC=", fit.BIC
    print "DW statistic:", fit.DWstat
    print
def polydatamatrix(X,maxdeg = 1):
    """
    Creates a data matrix for fitting a polynomial by least squares.
      X - input vector.
    Returns a matrix of the powers of X.
    Example from ipython session:
A =[1,2,3,4,5,6,7,8,9,10]
polydatamatrix(A, maxdeg= 2)
[[1, 1, 1],
 [1, 2, 4],
 [1, 3, 9],
 [1, 4, 16],
 [1, 5, 25],
 [1, 6, 36],
 [1, 7, 49],
 [1, 8, 64],
 [1, 9, 81],
 [1, 10, 100]]
    """
    outX = []
    for x in X:
       row = [1, x]
       for j in range(1, maxdeg):
           row.append(row[-1] * x)
       outX.append(row)
    return outX
def Test():
    if 0:
      # Small problem for manual work.
      X = [[1,1,1],[1,2,4],[1,3,6],[1,4,5]]
      Y = [2.939887,4.244599,1.212064,8.882774]
    else:
      # Test example from Gujarati, Basic Econometrics, page 943, 4th ed.
      Y = [1673,1688,1666,1735,1749,1756,1815,1867,1948,2048,2128,2165,
    2257,2316,2324]
      X = [[1, 1839, 1],
    [1, 1844, 2],
    [1, 1831, 3],
    [1, 1881, 4],
    [1, 1883, 5],
    [1, 1910, 6],
    [1, 1969, 7],
    [1, 2016, 8],
    [1, 2126, 9],
    [1, 2239, 10],
    [1, 2336, 11],
    [1, 2404, 12],
    [1, 2487, 13],
    [1, 2535, 14],
    [1, 2595, 15],
    ]
    example = ols(X, Y)
    summary_matrices(example)
    summary_anova(example)
    summary_error_table(example)
    summary_coeffs_stat(example)
    summary_f_test(example)
    Xexample=[1,2610,16]
    summary_estimate(example, Xexample)
    summary_misc_stat(example)
    print
if __name__ =="__main__":
   Test()



