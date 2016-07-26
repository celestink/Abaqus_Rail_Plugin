# This script prepares the preprocessing of railroad track.
#It will generate repsective inp files as well as text files with that contain crossties moduli values
# Author: Celestin Nkundineza
from abaqus import mdb, session
import abaqus
from abaqusConstants import*
import numpy
import math
import RandomStiff_Generator
import Crosstiesprt
import RailLoaderw2
import railModelsu2
import os
import Paracalc

def TrackModel(Tielength,Tiedepth,lin,dz,nt,minmod,modmean,SDincr,nSDi,nrepeat,railgeom,maxsteps,numsteps,loadtype,meshsize,APBC):
	StatLoad=RailLoaderw2.StaticLoading()
	PLoad=StatLoad[2]['Max Stress']
	a=StatLoad[2]['Major Axis']
	b=StatLoad[2]['Minor Axis']
	if maxsteps == True:
		stepsno=Paracalc.stepsnum(lin,nt,dz) #Number of load steps
	else:
		stepsno=numsteps
	RL=2*lin*(nt-1) #Length of the rail
	Pr=0.22
	l1=114.30 #side tie width
	l2=228.6 #middle tie width
	z1=[2*i*lin-l1 for i in range(1,nt-1)] # translation distances for the middle tie
	z2=2*lin*(nt-1)-l1 #Translation distance for the side tie
	ztr=[0]+z1+[z2] #Translation distances for crossties
	px1=-Tielength/2.0 #half length of the tie
	px2=-px1
	py1=0.0
	py2=-Tiedepth #depth of the tie
	stE0=0.0
	dim=[l1,l2,z1,z2,px1,px2,py1,py2,ztr]
	ConcrE=RandomStiff_Generator.RandomStiffGen(nt,modmean,stE0,minmod)
	density=2.4e-09
	addmat=[ConcrE,Pr,density]
	meshsize=6.0

	#Cross-ties partition parameters
	v=(5.0,-50.0,5.0) # Location of the part (pick one point of the part)
	ch1=-169.80 #First depth of the partition
	ch2=-8.0 # Second depth of the partition
	nSDi=2 #number of moduli standard deviations increments
	nrepeat=1

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#Rail Modelling data
	if railgeom=='Rectangular':
		myModel=railModelsu2.rectRail(nt,dz,stepsno,loadtype,meshsize)
	elif railgeom=='Exact':
		myModel=railModelsu2.realRail(nt,dz,stepsno,loadtype,meshsize)
	## Insert crossties models
	myTies=Crosstiesprt.crosstiesPrep(myModel,nt,dim,addmat, meshsize)
	# Creating tie constraints
					##Apply tie constraints to each tie and the rail
	for i in range(nt):
		myModel.rootAssembly.Surface(name='m_RailSurf', side1Faces=
			myModel.rootAssembly.instances['RailInst'].faces.findAt(((dim[4]/10.0, dim[6], (dim[0]/2.0+dim[8][i])), ), ))
		myModel.rootAssembly.Surface(name='s_TieSurf'+str(i), side1Faces=
			myModel.rootAssembly.instances['Ties'+str(i)].faces.findAt(
			((dim[4]/2.0, dim[6], (dim[0]/2.0+dim[8][i])), ), ))
		myModel.Tie(adjust=ON, master=	myModel.rootAssembly.surfaces['m_RailSurf'], name=
			'Constraint-'+str(i), positionToleranceMethod=COMPUTED, slave=
			mdb.models['SimTrack0'].rootAssembly.surfaces['s_TieSurf'+str(i)], thickness=ON, 
			tieRotations=ON)
	if APBC==True:
		RailLoaderw2.applyperiodicBC(myModel,'Set-1','Set-2','Set-3')
	myViewport = session.Viewport(name='Viewport for Rail track',
		origin=(10, 10), width=150, height=100)

	myViewport.setValues(displayedObject=myModel.rootAssembly)

	myViewport.assemblyDisplay.setValues(renderStyle=SHADED)
	session.viewports['Viewport for Rail track'].makeCurrent()
	session.viewports['Viewport for Rail track'].maximize()
	if railgeom=='Rectangular':
		session.printToFile(
			fileName='C:/Users/celestink/abaqus_plugins/myrailroad/rectarail.png', 
			format=PNG, canvasObjects=(session.viewports['Viewport for Rail track'], ))
	elif railgeom=='Exact':
		session.printToFile(
			fileName='C:/Users/celestink/abaqus_plugins/myrailroad/realrail.png', 
			format=PNG, canvasObjects=(session.viewports['Viewport for Rail track'], ))
	myModel.fieldOutputRequests['F-Output-1'].setValues(variables=(
								'S', 'MISES', 'MISESMAX', 'TRIAX', 'MISESONLY', 'E', 'PE', 'PEEQ', 'PEMAG', 
								'EE', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP'))
	##Create Job output for the first model
	mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
		explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
		memory=90, memoryUnits=PERCENTAGE, model='SimTrack0', modelPrint=OFF, 
		multiprocessingMode=DEFAULT, name='SimTrack0', nodalOutputPrecision=SINGLE, 
		numCpus=1, queue=None, scratch='', type=ANALYSIS, userSubroutine='',waitHours=0, waitMinutes=0)	
	mdb.jobs['SimTrack0'].writeInput(consistencyChecking=OFF)
	
	# Generate other models with standard deviation higher than 0 and repeated nrepeat times
	def multiRandTrack(nSDi,nt,nrepeat,SDincr,Modelname,Materialname):
		for SDi in range(1,nSDi): 
			stE=stE0+SDincr*SDi
			f = open('tieModuli_SD_Incr_'+str(SDi)+'.txt', 'w')
		
			for Nrand in range(nrepeat):
				ln=nrepeat*SDi+Nrand+1
				ConcrE=RandomStiff_Generator.RandomStiffGen(nt,modmean,stE,minmod)
				[f.write(str(ConcrE[i])+'\n') for i in range(nt)]
				mdb.Model(name=Modelname+str(ln), objectToCopy=myModel)
				mdb.models[Modelname+str(ln)].rootAssembly.regenerate()
				for i in range(nt):
					mdb.models[Modelname+str(ln)].materials[Materialname+str(i)].elastic.setValues(
						table=((ConcrE[i], Pr), ))		
					#Set Field output requests
				myModel.fieldOutputRequests['F-Output-1'].setValues(variables=(
								'S', 'MISES', 'MISESMAX', 'TRIAX', 'MISESONLY', 'E', 'PE', 'PEEQ', 'PEMAG', 
								'EE', 'LE', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP'))
			
				mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
					explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
					memory=90, memoryUnits=PERCENTAGE, model=Modelname+str(ln), modelPrint=OFF, 
					multiprocessingMode=DEFAULT, name=Modelname+str(ln), nodalOutputPrecision=SINGLE, 
					numCpus=1, queue=None, scratch='', type=ANALYSIS, userSubroutine='',waitHours=0, waitMinutes=0)	
				mdb.jobs[Modelname+str(ln)].writeInput(consistencyChecking=OFF)
			
			f.close()
	multiRandTrack(nSDi,nt,nrepeat,SDincr,'SimTrack','concrete ties')

	
