def raillength(lin,nt):
	RL=2*lin*(nt-1)
	return RL
def stepsnum(lin,nt,dz):
	RL=2*lin*(nt-1)
	maxsteps=int((RL-2*lin)/dz+1)
	return maxsteps
	
	