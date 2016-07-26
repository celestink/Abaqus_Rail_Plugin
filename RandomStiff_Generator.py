import random
import math
def RandomStiffGen(nt, muE, stE,bounds):
	"""The function generate random stiffness in a track of given number of cross-ties as nt,
	 mean of track modulus,given standard deviation, within given limits as bounds and  the number of realization repetitions.
	 Note: The rail length must be a multiple of 266.7""" 
	#Generating random ties Young's Modulus and poisson ratio for concrete ties
	#The working folder is named the mean after the first letter.
	muPr=0.18
	stPr=0.05
	Pr=0.22
	## This function generate a sample of random numbers 
	# nt from of Gaussian distribution 
	# such that their average and standard deviation are the same as 
	#the pool fixed mean muE and standard deviation stE
	ConcrE1=[]
	ConcrE=[]
	keepsampling=0.0
	while keepsampling<nt:
		ConcrEi=[random.gauss(muE,stE) for i in range(nt)]
		ConcrPr=[random.gauss(muPr,stPr) for i in range(nt)]
		#Force the mean to be the same as requested
		sumstiff=sum(ConcrEi)
		newmean=sumstiff/nt
		Xdev=(nt*muE-sumstiff)/nt
		ConcrEc=[ConcrEi[i]+Xdev for i in range(nt)] 
		
		#Compute the standard deviation of the new sample
		ConcrEsq=[(ConcrEc[i])**2 for i in range(nt)]
		StD=math.sqrt(abs(sum(ConcrEsq)/nt-muE**2))
		
		#Deviation from requested variances
		dStD2=stE**2-StD**2
		
		#Force the standard deviation of the sample to be equal to the standard deviation of the whole population
		#dstD is subtracted from numbers less than the median and and added to numbers greater than the median , that is:
		#Compute the median
		nt1=int(nt/2-1)
		nt2=int(nt/2)
		ListE=ConcrEc
		ListE.sort() #sort numbers in a list from the lowest to greatest
		Xmed=1.0/2.0*(ListE[nt1]+ListE[nt2])
		##Divide the list into two lists separated by the mean
		ListE1=[ListE[i] for i in range(nt2)]
		ListE2=[ListE[i] for i in range(nt2,nt)]
		muE1=(sum(ListE1))/(nt/2.0)
		muE2=(sum(ListE2))/(nt/2.0)
		dmuE=muE2-muE1
		Determ=dmuE**2+4.0*dStD2
		
		if Determ<0.0:
			keepsampling=0.0
		else:
			dStD=0.5*dmuE-0.5*(math.sqrt(dmuE**2+4.0*dStD2))
			#perturb the numbers to have requested standard dev and mean
			ConcrE=[]
			for i in range(nt):
				if ConcrEc[i]<Xmed:
					Ec=ConcrEc[i]+dStD
					ConcrE.append(Ec)
				elif ConcrEc[i]>Xmed:
					Ec=ConcrEc[i]-dStD
					ConcrE.append(Ec)
				else:	
					Ec=ConcrEc[i]
					ConcrE.append(Ec)
			random.shuffle(ConcrE)
			keepsample=[]
			for i in range(nt):
				if ConcrE[i]<=bounds:
					#print (tie modulus error)
					keepsample.append(0)
				else:
					keepsample.append(1)
			keepsampling=sum(keepsample)
		# saving:
	#dataModulus=ConcrE
	#ConcrE=randomstiffness(stE,muE,nt,ConcrE1)
	#print ConcrE
	return ConcrE