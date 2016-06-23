import scipy
import ols

__all__ = ['chow']

def chow(X,Y, X1, Y1, X2, Y2, alpha = 0.05):
	"""
	Performs a chow test.
	Split input matrix and output vector into two
	using specified breakpoint.
	  X - independent variables matrix
	  Y - dependent variable vector
	  breakpoint -index to split.
	  alpha is significance level
	"""
	if isinstance(X[0],int) or isinstance(X[0], float):
		k = 1
	else:
		k = len(X[0])
	k = k + 1
	n = len(X)

	# Perform separate three least squares.
	allfit   = ols.ols(Y,X)
	lowerfit = ols.ols(Y1, X1)
	upperfit = ols.ols(Y2, X2)

	rss = allfit.rss
	rss1 = lowerfit.rss
	rss2 = upperfit.rss

	df1 = k
	df2 = n - 2 *k

	rss_u = (rss1 + rss2)
	num = (rss - rss_u) /float(df1)
	den = rss_u / df2


	chow_ratio = num/den    
	Fcrit = scipy.stats.f.ppf(1 -0.05, df1, df2)
	p = scipy.stats.f.pdf(chow_ratio, df1, df2)
	return (chow_ratio, p, Fcrit, df1, df2, rss, rss1, rss2)


if __name__ == "__main__":
	# linear equation to fit is pcer = const +  gnpr
	data = """year    pcer    gnpr
1975    311.848 452.735
1976    327.436 489.471
1977    344.706 517.88
1978    362.676 545.516
1979    380.263 579.576
1980    397.404 605.687
1981    407.958 626.321
1982    422.067 641.51
1983    424.634 652.097
1984    425.767 592.694
1985    420.832 551.428
1986    434.815 571.492
1987    452.386 600.907
1988    480.562 644.229
1989    504.619 684.231
1990    531.772 716.929
1991    543.788 720.218
1992    561.509 731.396
1993    578.589 746.921
1994    600.106 786.136
1995    622.985 825.164
1996    651.79  882.399"""

	W = data.split("\n")[1:] #ignore first line
	X = []
	Y = []
	for (i,w) in enumerate(W):
		w = w.split()
		X.append([1.0, float(w[2])])
		Y.append(float(w[1]))

	# for (x,y) in zip(X,Y):
	#   print x[0], x[1],y

	breakpoint = 9
	Ftest, Fcrit, df1, df2, RSS, RSS1, RSS2 = \
		 chow(X, Y, breakpoint, alpha = 0.05)
	print "Chow Summary statistics:"
	print "Breakpoint index,(zero based)= ", breakpoint
	print "Number of indep. vars(incl. const), k =", len(X[0])
	print "RSS1=", RSS1, "n1=", breakpoint
	print "RSS2=", RSS2,"n2=", len(X) - breakpoint
	print "RSS =", RSS, "n=", len(X)
	print "df1,df2=", df1, df2  
	print "F values:(test, crit)=", Ftest, Fcrit