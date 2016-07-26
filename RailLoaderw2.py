import abaqus
from abaqusConstants import*
def StaticLoading():
	#Loading input parameters:
	
	R1=355.6;# Rail radius (mm)
	R2=457.2; # Wheel radius (mm)
	Cb=0.84;# Constants(Seely and Smith, 1952)
	Csgm=0.62;#Constants(Seely and Smith, 1952) 
	k=0.85;# Constants(Seely and Smith, 1952) 
	v1=0.33;# Poisson ratio for the rail 
	v2=0.33;# Poisson ratio for the wheel 
	E1=200000;# Young's modulus for the rail (MPa)
	E2=200000;# Young's modulus for the wheel (MPa)
	Ps=146235 # Static load (N)
	vel=60 # Train Speed (MPH)
	D_w=36;# Wheel diameter (inches)
	
	# Resulting dynamic load, contact area geometry and maximum normal stress:
	theta=0.33*vel/D_w
	Pd=Ps*(1+theta) #Dynamic load for static loading
	Delta=2*R1*R2/(R1+R2)*((1-v1**2)/E1+(1-v2**2)/E2);
	b=Cb*(Pd*Delta)**(1.0/3.0) # Elliptic wheel rail contact area minor semi axis
	a=b/k # Elliptic wheel rail contact area major semi axis
	Sigm=Csgm*b/Delta # Maximum normal stress
	
	# Output data:
	InterMData={'Theta':theta, 'Delta':Delta}
	LoadInData={'RailRadius':R1, 'Wheel Radius':R2,'Cb':Cb,'CStress':Csgm,'k':k,'Rail Poisson Ratio':v1,
	'Wheel Poisson Ratio':v2,'Rail Modulus':E1, 'Wheel Modulus':E2,'Static Load':Ps} 
	LoadOutData={'DynamicLoad':Pd,'Major Axis':a,'Minor Axis':b,'Max Stress':Sigm}
	#LoadData={'LoadInputs':LoadInData,'Data':InterMData,'LoadOutputs':LoadOutData}
	return LoadInData,InterMData,LoadOutData
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
def DynamicLoading():

	# Loading time increment (ms):
	myTime=[0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]+[7.0+i for i in range(5)]
	""" Load magnitude at each time increment(kN) (W. Zai and Z. Zai and Cai, "Dynamic Interaction between 
	and lumped mass vehicle and a discretely supported continuous rail track," Computers and Structures, 
	vol.63, no 3, pp. 987-997,1997):"""
	LoadkN=[146,176,226,206,196,176,166,171,173,175,176,174,172,171]+[171 for i in range (5)] #(KN)
	LoadN=[10**3*load for load in LoadkN]
	LoadData=StaticLoading()
	a=LoadData[2]['Major Axis']
	b=LoadData[2]['Minor Axis']
	Cb=LoadData[0]['CStress']
	Delta=LoadData[1]['Delta']
	Csgm=LoadData[0]['Cb']
	bd=[Cb*(Pdyn*Delta)**(1.0/3.0) for Pdyn in LoadN]
	DSigm=[Csgm*ib/Delta for ib in bd]
	DLoadInData=LoadData[0]
	DynInputs={'time':myTime,'DynamicLoads':LoadN}
	DLoadInData.update(DynInputs)
	DLoadOutData={'Major Axis':a,'Minor Axis':b,'Instant Max Stresses':DSigm}
	#DLoadData={'DynLoadInputs':DLoadInData,'DynLoadOutputs':DLoadOutData}
	return DLoadInData,DLoadOutData
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ApplyLoads(myModel,RailInst,nt,railgeom,loadtype,dz,stepsno,a,b,hy):
	lin=266.7
	zf=[(2*(nt-1)*lin-lin-i*dz) for i in range(stepsno)]
	dtc=[4+n for n in range(stepsno)]
	stepname=['Initial']+['step_'+str(n) for n in range(stepsno)]
	for n in range (stepsno):
		if loadtype == 'Static':
				StatLoad=StaticLoading()
				PLoad=StatLoad[2]['Max Stress']
				myModel.StaticStep(description='load applied'+str(n), initialInc=0.1,maxInc=0.3, 
					name=stepname[n+1], previous=stepname[n],timePeriod=0.5)
						#Create load fields
				if railgeom=='realgeometry':
					myModel.ExpressionField(description='elliptic contact load_'+str(n), expression='sqrt(1.0-Z*Z/pow('+str(a)+',2)-X*X/pow('+str(b)+',2))', 
						localCsys=myModel.rootAssembly.datums[dtc[n]], name='Contact load_'+str(n))
					Pl=PLoad
					myloadsurf=myModel.rootAssembly.Surface(name='loadsurf-'+str(n), side1Faces=RailInst.faces.findAt(((-7.90097, hy, zf[n]), ), ))
					myModel.SurfaceTraction(createStepName=stepname[n+1], 
						directionVector=((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), distributionType=FIELD,
						field='Contact load_'+str(n), localCsys=myModel.rootAssembly.datums[dtc[n]], magnitude=Pl, name='ContactLoad_'+str(n), region=
						myloadsurf, resultant=ON, traction=GENERAL)
				elif railgeom=='rectgeometry':
					#Create the load amplitude in the created step
					Pl=2.0*PLoad/3.0
					myloadsurf=myModel.rootAssembly.Surface(name='loadsurf-'+str(n), side1Faces=RailInst.faces.findAt(((-7.90097, hy, zf[n]), ), ))
					myModel.SurfaceTraction(createStepName=stepname[n+1], 
						directionVector=((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), distributionType=
						UNIFORM, field='', localCsys=None, magnitude=Pl, name='ContactLoad_'+str(n), region=myloadsurf,resultant=ON, traction=GENERAL)
		elif loadtype=='Dynamic':
				DynamicLoad=DynamicLoading()
				Tim=DynamicLoad[0]['time']
				DLoads=DynamicLoad[1]['Instant Max Stresses']
				
				myModel.ImplicitDynamicsStep(description='load applied'+str(n), initialInc=0.001,maxInc=0.01, 
					name=stepname[n+1], previous=stepname[n],timePeriod=0.01)
						#Create load fields
				if railgeom=='realgeometry':
								
					#dt=10+n # datum local coordinate reference number
					myModel.ExpressionField(description='elliptic contact load_'+str(n), expression='sqrt(1.0-Z*Z/pow('+str(a)+',2)-X*X/pow('+str(b)+',2))', 
						localCsys=myModel.rootAssembly.datums[dtc[n]], name='Contact load_'+str(n))
					DL=DLoads
					myModel.TabularAmplitude(data= dloadata, name='Dynamic Loading', smooth=SOLVER_DEFAULT, timeSpan=STEP)	
					myloadsurf=myModel.rootAssembly.Surface(name='loadsurf-'+str(n), side1Faces=RailInst.faces.findAt(((-7.90097, hy, zf[n]), ), ))
					myModel.SurfaceTraction(amplitude='Dynamic Loading',createStepName=stepname[n+1], 
						directionVector=((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), distributionType=FIELD,
						field='Contact load_'+str(n), localCsys=myModel.rootAssembly.datums[dtc[n]], magnitude=1.0, name='ContactLoad_'+str(n), region=
						myloadsurf, resultant=ON, traction=GENERAL)
						#Create the load amplitude in the created step
				elif railgeom=='rectgeometry':
					DL=[2.0/3.0*ld for ld in DLoads]
					
					dloadata=tuple([(Tim[i],DL[i])for i in range(len(Tim))])
					myModel.TabularAmplitude(data= dloadata, name='Dynamic Loading', smooth=SOLVER_DEFAULT, timeSpan=STEP)	
					myloadsurf=myModel.rootAssembly.Surface(name='loadsurf-'+str(n), side1Faces=RailInst.faces.findAt(((-7.90097, hy, zf[n]), ), ))
					myModel.SurfaceTraction(amplitude='Dynamic Loading',createStepName=stepname[n+1], 
						directionVector=((0.0, 0.0, 0.0), (0.0, -1.0, 0.0)), distributionType=FIELD,
						field='Contact load_'+str(n), localCsys=None, magnitude=1.0, name='ContactLoad_'+str(n), region=
						myloadsurf, resultant=ON, traction=GENERAL)
				#Deactivating loads in steps that they are no longer active
		s=0				
		while s<n:
			[myModel.loads['ContactLoad_'+str(s)].deactivate(stepname[i+2]) for i in range(s,n)]
			s=s+1	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~			
def applyperiodicBC(myModel,stx,sty,stz):	
	#Apply Periodic boundary conditions
	set1=myModel.rootAssembly.sets[stx].nodes
	set2=myModel.rootAssembly.sets[sty].nodes
	set3=myModel.rootAssembly.sets[stz].nodes
	# node1=mdb.models['Model-1'].rootAssembly.instances['fullrail-1'].nodes
	#node2=DummyInst.nodes
	set2new=[]
	set1new=[]
	x2s=[]
	y2s=[]
	z2s=[]
	z1s=[]
	#compute the minimum distance in xy plane between one node from 
	#one face and each node from the other face and create a list of matched nodes
	x=[]
	y=[]
	z=[]
	def ArrNodeSet(set2,set2new):
		for n in range(len(set2)):
			x1=set2[n].coordinates[0]
			y1=set2[n].coordinates[1]
			z1=set2[1].coordinates[2]
			labe=set2[n].label
			x2s.append(x)
			y2s.append(y)
			z2s.append(z)
			set2new.append([labe,x1, y1, z1])
		z2cst=max(z2s)
	ArrNodeSet(set2,set2new)
	ArrNodeSet(set1,set1new)
	Tm=1 #Condition to match coordinates in set 2 to coordinates in set 1 else vice versa.
	NodeEqxy=[]
	set2n=[]
	def editingNodes(set1new,set2new,Tm):
		# set2n=[]
		for i in range(len(set1new)):
			d12xyp=[((set2new[n][1]-set1new[i][1])**2+(set2new[n][2]-set1new[i][2])**2)**0.5 for n in range(len(set2new))]
			dnmin=min(d12xyp) 
			mlab=d12xyp.index(dnmin) # Index of matching node in set2 to a node of index i in set1
			if (Tm==1):
				nameOfset=sty
				#lab1 and lab2 are labels of matching nodes.
				lab1=set1new[i][0]
				lab2=set2new[mlab][0]
				no2nx=set1new[i][1]
				no2ny=set1new[i][2]
				no2nz=set1new[1][3]
				set2n.append([no2nx,no2ny,no2nz,i,mlab])
				NodeEqxy.append([set1new[i],lab1,lab2])
				myModel.rootAssembly.editNode(coordinate1=set2n[i][0], 
				coordinate2=set2n[i][1], coordinate3=set2n[i][2],
				nodes=myModel.rootAssembly.sets[nameOfset].nodes[set2n[i][4]])	
			elif (Tm==2):
				nameOfset=stx
				labn=set1new[nj][0]
				no2nx=set2new[i][1]
				no2ny=set2new[i][2]
				no2nz=set2new[1][3]
				set2n.append([no2nx,no2ny,no2nz,mlab,lab2])
				NodeEqxy.append([set1new[i],lab1,lab2])
	#start editing nodes with new coordinates keeping the node number the same
				myModel.rootAssembly.editNode(coordinate1=set2n[i][0], 
				coordinate2=set2n[i][1], coordinate3=set2n[i][2],
				nodes=myModel.rootAssembly.sets[nameOfset].nodes[set2n[i][3]])		
	##find extra nodes on the other face that has more nodes
	#set2new-set2n
	editingNodes(set1new,set2new,Tm)
	if (range(len(set2))>range(len(set1))):
		set2node=[set2new[n][0] for n in range(len(set2new))]
		set2noden=[set2n[n][0] for n in range(len(set2n))]
		hangnode=list(set(set2node)-set(set2noden))
		#Edit these nodes 
		SetToEdit=[]
		def indexOfnodes(hangnode,set2,SetToEdit):
	#This function returns the set of nodes with their coordinates and their index in the nodes set)
			for k in range(len(hangnode)):
				NoToEdit=hangnode[k]
				for l in range(len(set2)):
					Nodenum=set2[l].label
					if (Nodenum==NoToEdit):
						xEdit=set2[l].coordinates[0]
						yEdit=set2[l].coordinates[1]
						zEdit=zcst
						SetToEdit.append([Nodenum,xEdit,yEdit,ZEdit,l])
						break
					elif (Nodenum!=NoToEdit):
						continue
		Tmm=2
		editingNodes(SetToEdit,Set1new,Tmm,sty)
		#Print nodes numbers pairs of the same coordinates
		print 'Equal x y coordinates node pairs are', NodeEqxy
		print 'hanging nodes are', SetToEdit
	#	Start defining boundary conditions
	elif (range(len(set2))==range(len(set1))):
		for i in range(len(set1)):
	#create the names of node sets
			setname1='set1a-'+str(i)
			setname2='set2a-'+str(i)
			setname3='set3'
	##creates the node sets

			st1=set1[set2n[i][3]:set2n[i][3]+1]
			st2=set2[set2n[i][4]:set2n[i][4]+1]

	#Create a dummy node
			st3=set3;
	#Create the node sets
			myModel.rootAssembly.Set(name=setname1, nodes=st1)
			myModel.rootAssembly.Set(name=setname2, nodes=st2)	
			myModel.rootAssembly.Set(name=setname3, nodes=st3)	
	#Apply constraints equations for periodic boundary conditions	
			myModel.Equation(name='ConstraintX1-'+str(i), terms=((1.0, 
				setname1, 1), (-1.0, setname2, 1)))
			myModel.Equation(name='ConstraintY1-'+str(i), terms=((1.0, 
				setname1, 2), (-1.0, setname2, 2)))
			myModel.Equation(name='ConstraintZ1-'+str(i), terms=((1.0, 
				setname1, 3), (-1.0, setname2, 3),(1, setname3, 3)))
