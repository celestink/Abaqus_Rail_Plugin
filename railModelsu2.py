#This script generate input files for Long track FE models
## Importing modules
import abaqus
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import random
#P=Fd/Area1
import os
import RailLoaderw2
# path1=os.getcwd()
# fd=str(os.path.basename(path1))
# muE0=int(fd[1:4])
#Application of periodic boundary conditions

def rectRail(nt,dz,stepsno,loadtype, meshsize):
	StatLoad=RailLoaderw2.StaticLoading()
	PLoad=StatLoad[2]['Max Stress'] #Maximum wheel load pressure in MPa
	a=StatLoad[2]['Major Axis']
	b=StatLoad[2]['Minor Axis']
	P=PLoad*2.0/3.0 
	#SDi define incremental standard deviation index of tie Young's moduli
	##INFORMATION ON TIES
	##Input dimensional parameters, metric units, mm

	#INFORMATION ON THE RAIL
	lin=266.7 # Half distance on rail between two ties center to center
	tsp=2*lin# rail distance between centrelines of two successive ties; units in mm
	wt=228.6 # Tie width on the rail ( z axis)
	st=tsp-wt # gap distance between two successive ties
	hr=186.0 #height of the rail on y axis
	wr=73.0	#width on x axis
	Lr=(nt-1)*tsp	#length on z axis
	te=20.0
	re=20.0
	#base coordinate of the rail
	R_vx=((wr/2.0,hr/2.0),(-wr/2.0,hr/2.0),(-wr/2.0,-hr/2.0),(wr/2.0,-hr/2.0)) 
	#base coordinate of the tie
	#T_vx=((Lt/2.0,-hr/2.0),(-Lt/2.0,-hr/2.0),(-Lt/2.0,(-hr/2.0-ht)),(Lt/2.0,(-hr/2.0-ht))) 
	#create surfaces for the rail loads
	#Datum plane for partition
	nl=nt-1 #number of load surfaces
	ll=pi*a*b/wr #longitudinal length of load surface in mm
	##Base coordinates
	##Sketching the rail base
	myModel=mdb.Model(name='SimTrack0')
	sketch1=myModel.ConstrainedSketch(name='Rail section', sheetSize=400.0)
	sketch1.Line(point1=R_vx[0],point2=R_vx[1])	
	sketch1.Line(point1=R_vx[1],point2=R_vx[2])
	sketch1.Line(point1=R_vx[2],point2=R_vx[3])	
	sketch1.Line(point1=R_vx[3],point2=R_vx[0])
	##Create Rail part by extrusion
	myrailPart=myModel.Part(name='Rail',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
	myrailPart.BaseSolidExtrude(depth=Lr, sketch=sketch1)
	#
	#CREATE THE STEEL MATERIAL AND THE RAIL SECTION
	myMaterial=myModel.Material(name='Steel')
	myMaterial.Elastic(table=((210000.0, 0.3),))
	myModel.HomogeneousSolidSection(material='Steel', name='RailSteel')
	myrailPart.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
			cells=myrailPart.cells.findAt(((wr/4.0,(hr/4.0),Lr/2.0), 
				), )), sectionName='RailSteel', thicknessAssignment=
			FROM_SECTION)	
	#Creating a rail Instance
	myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
	RailInst=myModel.rootAssembly.Instance(dependent=ON, name='RailInst', 
				part=myrailPart)
	#Translate the rail instance in y direction to match future crossties position!
	myModel.rootAssembly.translate(instanceList=('RailInst', ), 
					vector=(0.0, hr/2.0, 0))
	#Create surfaces for which node sets will be created
	myModel.rootAssembly.Set(faces= RailInst.faces.findAt(((
		0, hr/2.0, 0), ), ), name='Set-1')
	myModel.rootAssembly.Set(faces= RailInst.faces.findAt(((
		0, hr/2.0, Lr), ), ), name='Set-2')
		
	for j in range(stepsno):
					
		#Create step 2 for the load
		myModel.StaticStep(initialInc=0.1, name='Step-2', previous='Initial')
		##APPLYING LOADS ON THE RAIL
		#Start by creating datum planes for partitioning
		dlp11=lin+dz*j-ll/2.0 #starting distance of load surface 
		dlp12=dlp11+ll #ending distance of load surface 
		dlp21=tsp*(j+1.0)-ll/2.0 #starting distance of load surface above the tie
		dlp22=dlp21+ll #ending distance of load surface above the ties
		dlp=(dlp11,dlp12)
		planep1=myrailPart.DatumPlaneByPrincipalPlane(offset=dlp[0], 
			principalPlane=XYPLANE)
		planep2=myrailPart.DatumPlaneByPrincipalPlane(offset=dlp[1], 
			principalPlane=XYPLANE)
		#Do partitions of the rail
		dtm=[3+4*j,4+4*j]
		n1=dtm[0]
		n2=dtm[1]
		partitionp1=myrailPart.PartitionFaceByDatumPlane(datumPlane=
			myrailPart.datums[n1], faces=myrailPart.faces.findAt(((wr/4.0, hr/2.0, (dlp[0])), ), ))
		partitionp2=myrailPart.PartitionFaceByDatumPlane(datumPlane=myrailPart.datums[n2],
			faces=myrailPart.faces.findAt(((wr/4.0, hr/2.0,(dlp[1])), ), ))
	#Apply loads at partitioned surface
	#create a steps and apply loads
	RailLoaderw2.ApplyLoads(myModel,RailInst,nt,'rectgeometry',loadtype,dz,stepsno,a,b,hr)				
	##Mesh the rail part
	
	myrailPart.setElementType(elemTypes=(ElemType(
		elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15, 
			elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), 
		regions=(myrailPart.cells.findAt(((-wr/4.0, 
			hr/4.0, Lr/4.0), ), ), ))
	myrailPart.seedPart(deviationFactor=0.4, minSizeFactor=0.4, size=meshsize)		
	myrailPart.generateMesh()
	##create a dummy element
	sketchd=myModel.ConstrainedSketch(name='dummy section', sheetSize=400.0)
	sketchd.Line(point1=(0,0),point2=(re,0))
	sketchd.Line(point1=(re,0),point2=(re,re))
	sketchd.Line(point1=(re,re),point2=(0,re))	
	sketchd.Line(point1=(0,re),point2=(0,0))
	mydummyPart=myModel.Part(name='dummy',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
	mydummyPart.BaseSolidExtrude(depth=re, sketch=sketchd)
	mydummyPart.SectionAssignment(offset=0.0, 
				offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
				cells=mydummyPart.cells.findAt(((0,0,Lr), 
				), )), sectionName='RailSteel', thicknessAssignment=
					FROM_SECTION)
	#Assigning dammy element material
	mydummyPart.SectionAssignment(offset=0.0, 
		offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
		cells=mydummyPart.cells.findAt(((re/2.0,(re/2.0),re/2.0), 
		), )), sectionName='RailSteel', thicknessAssignment= FROM_SECTION)				
	#Creating a dummy Instance
	myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
	DummyInst=myModel.rootAssembly.Instance(dependent=ON, name='dmyInst', part=mydummyPart)
	#Translate the the dummy instance at a distance Lr
	myModel.rootAssembly.translate(instanceList=('dmyInst', ), 
			vector=(0.0, 0.0, Lr))	
	#Applying Encastred BC
	myModel.EncastreBC(createStepName='Initial', name='BC-dummy',
		region=Region(faces=DummyInst.faces.findAt(((re/2, re/2, Lr+re),),)))
	#Mesh the dummy part
	mydummyPart.setElementType(elemTypes=(ElemType(elemCode=C3D20R, elemLibrary=STANDARD),
		ElemType(elemCode=C3D15, elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), 
		regions=(mydummyPart.cells.findAt(((re/2.0, re/2.0, re/e), ), ), ))
	mydummyPart.seedPart(deviationFactor=0.5, minSizeFactor=0.5, size=re)
	mydummyPart.generateMesh()
	#create dummy node
	myModel.rootAssembly.Set(name='Set-3', vertices=DummyInst.vertices.findAt(((0.0, 0.0, Lr), ), ))

	return myModel
	
def realRail(nt,dz,stepsno,loadtype, Elsize):
	StatLoad=RailLoaderw2.StaticLoading()
	PLoad=StatLoad[2]['Max Stress'] #Maximum wheel load pressure in MPa
	a=StatLoad[2]['Major Axis']
	b=StatLoad[2]['Minor Axis']
	P=PLoad*2.0/3.0
	baL=76.2
	p=1.0/4.0
	p2=1.0/16.0
	rb=1.5875
	R1=355.6
	R2=355.6
	R3=355.6
	rf1=19.05
	rf2=19.05
	rf3=6.35
	rtw=12.7
	Tb1=11.90625
	Tb2=19.05
	h1=Tb1+Tb2
	h2=76.5125
	h3=93.6625
	h4=46.83125
	h5=85.725
	xb1=0.0
	yb1=0.0
	wb=76.2
	H=h1+h3+h4
	baH=Tb1
	wtop=74.6125/2.0
	wm=8.334375
	lin=266.7 #horizontal distance between inclusion center to near end of the rail. Also, center to center distance between two crossties.
	RL=2*lin*(nt-1) #Length of the rail
	#Arc center points
	Xc1=xb1-wm-R1
	Yc1=yb1+h5
	Xc2=xb1-wm-R2
	Yc2=yb1+h5
	Xc3=xb1
	Yc3=yb1+H-R3
	ct1=(Xc1,Yc1)
	ct2=(Xc2,Yc2)
	ct3=(Xc3,Yc3)
	Tt1=wtop*p
	h=h1+h3+Tt1
	htop=(h4-Tt1)*p2
	#force application parameters
	Lf=31.6 #Length of the force application surface
	#wf=76.2 #width of the force application surface
	#Area_f=101.6*76.2
	#Force=263000.0/8*4.4482
	minf=0.10
	devf=0.40

	# Pressure1=Force/Area_f
	Pressure2=-2.0
	L_of1=RL-lin-Lf/2
	L_of2=RL-lin+Lf/2
	dintp=10.32 #vertical distance between inclusion center and the top of the rail center
	din=yb1+H-dintp #vertical distance between inclusion center and the bottom of the rail center
	#Translation of inclusion
	Trin=RL-lin #Horizontal distance between inclusion center to the far end of the rail
	##Inclusion center: 
	yci1=din
	zci1=RL-lin
	xci1=0.0
	rin=1.5 #Inclusion radius
	# #Find the intersection of the rail surface arc and top rail side face
	# def f1(variables1):
		# (x,y)=variables1
		
		# #Equation of the arc
		# ArcEq=(x-xb1)**2+(y-yb1-H+R3)**2-R3**2
		
		# #Equation of the line
		# LineEq1=y*(h4-Tt1)*p2-x*(H-h1-h3-Tt1)-(yb1+h1+h3+Tt1)*(h4-Tt1)*p2-(xb1-wtop)*(H-h1-h3-Tt1)
		# return[ArcEq,LineEq1]
	# intersec1=scipy.optimize.fsolve(f1,(15,170)) 
	# #Find the intersection of the curving and inclined face on the shoulder of the rail
	# def f2(variables2):
		# (x,y)=variables2
		# Arc2Eq=(x-xb1-wm-R2)**2+(y-yb1-h5)**2-R2**2
		# Line2Eq=y*wtop-x*(-Tt1)-(yb1+h1+h3+Tt1)*wtop+(xb1-wtop)*(-Tt1)
		# return[Arc2Eq,Line2Eq]
	# intersec2=scipy.optimize.fsolve(f2,(13,90))
	# #Find the intersection of the curving and inclined face on foot of the rail
	# def f3(variables3):
		# (x,y)=variables3
		# Arc3Eq=(x-xb1-wm-R1)**2+(y-yb1-h5)**2-R1**2
		# Line3Eq=y*wb-x*h1-yb1*wb+(xb1-wtop)*h1
		# return[Arc3Eq, Line3Eq]
	# intersec3=scipy.optimize.fsolve(f3,(13,90))	
	# #Define vertices
	vtces=((xb1,yb1),(xb1,yb1+H),(xb1-wtop,yb1+h1+h3+Tt1),(xb1-wm,yb1+h5),
		(xb1-wb,yb1+Tb1),(xb1-wb,yb1))
	intersec1=(-35.07055819,169.71638149)
	intersec2=(-10.77456866,127.31239217)
	intersec3=(-13.1036804,27.6803299)
	#Start sketching
	myModel=mdb.Model(name='SimTrack0')
	sketch1=myModel.ConstrainedSketch(name='Rail section', sheetSize=400.0)
	sketch1.sketchOptions.setValues(decimalPlaces=6)
	sketch1.sketchOptions.setValues(gridAuto=OFF, gridSpacing=1.0)
	sketch1.sketchOptions.setValues(numMinorGridIntervals=1)
	sketch1.Line(point1=vtces[0],point2=vtces[1])
	sketch1.ArcByCenterEnds(center=ct3, direction=COUNTERCLOCKWISE, 
		point1=vtces[1],point2=intersec1)
	sketch1.Line(point1=intersec1, point2=vtces[2])
	sketch1.Line(point1=vtces[2],point2=intersec2)
	sketch1.ArcByCenterEnds(center=ct2, direction=COUNTERCLOCKWISE, 
		point1=vtces[3],point2=intersec2)
	sketch1.ArcByCenterEnds(center=ct1, direction=CLOCKWISE, 
		point1=vtces[3], point2=intersec3)
	sketch1.Line(point1=intersec3,point2=vtces[4])
	sketch1.Line(point1=vtces[4],point2=vtces[5])
	sketch1.Line(point1=vtces[5],point2=vtces[0])
	#Filleting
	#points to pick when chosing entities
	#Picking the top circular curve, "3rd fillet"
	xfc3=0.98*intersec1[0]
	yfc3=Yc3+(R3**2-(xfc3-Xc3)**2)**0.5
	xfl3=1.02*intersec1[0]
	yfl3=p2*(xfl3-intersec1[0])+intersec1[1]

	#Picking points for the second fillet
	xfc2=0.98*intersec2[0]
	yfc2=Yc2+(R2**2-(xfc2-Xc2)**2)**0.5
	xfl2=1.02*intersec2[0]
	yfl2=-p*(xfl2-intersec2[0])+intersec2[1]
	# #Picking points for 1st smaller fillet:
	xf2=0.99*vtces[2][0]
	yf2=p2*(xf2-intersec1[0])+intersec1[1]
	yf22=-p*(xf2-vtces[2][0])+vtces[2][1]

	#Picking points for the third fillet
	xfc1=0.9*intersec3[0]
	yfc1=Yc1-(R1**2-(xfc1-Xc1)**2)**0.5
	xfl1=1.02*intersec3[0]
	yfl1=p*(xfl1-intersec3[0])+intersec3[1]

	#Picking points for forth fillet
	xf4=0.98*(vtces[4])[0]
	yf4=p*(xf4-(vtces[4])[0])+(vtces[4])[1]
	xfl4=(vtces[4])[0]
	yfl4=0.98*(vtces[4])[1]

	#Picking points for fifth fillet
	xf5=xb1-wb
	yf5=(yb1+1)*0.02
	xfl5=0.98*(vtces[4])[0]
	yfl5=yb1

	#Start Filleting
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[3], curve2=sketch1.geometry[4], nearPoint1=
		(xfc3,yfc3), nearPoint2=(xfl3,yfl3), radius=rf3)
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[4], curve2=
		sketch1.geometry[5], nearPoint1=(
		xf2,yf2), nearPoint2=(xf2,yf22), radius=rb)
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[6], curve2=
		sketch1.geometry[5], nearPoint1=(xfc2,yfc2), nearPoint2=(xfl2,yfl2), radius=rtw)	
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[7], curve2=
		sketch1.geometry[8], nearPoint1=(
		xfc1,yfc1), nearPoint2=(xfl1,yfl1), radius=rf1)	
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[8], curve2=
		sketch1.geometry[9], nearPoint1=(
		xf4,yf4), nearPoint2=(xfl4,yfl4), radius=rb)	
	sketch1.FilletByRadius(curve1=
		sketch1.geometry[9], curve2=
		sketch1.geometry[10], nearPoint1=(
		xf5,yf5), nearPoint2=(xfl5,yfl5), radius=rb)		
	myPart=myModel.Part(name='RailLeft',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
	myPart.BaseSolidExtrude(depth=RL, sketch=sketch1)

	RailPart=myModel.Part(compressFeatureList=ON, mirrorPlane=YZPLANE, name=
		'RailRight0', objectToCopy=myModel.parts['RailLeft'])
	RailPart.Mirror(keepOriginal=ON, mirrorPlane=RailPart.faces.findAt((
		0.0, 57.149999, 711.200033), ))
	del sketch1
	#Make Datum Planes
	x2b=5.92
	Trin=RL-lin #Horizontal distance between inclusion center to the far end of the rail
	RailPart.DatumPlaneByPrincipalPlane(offset=
	   L_of1, principalPlane=XYPLANE) #Datums[3]
	RailPart.DatumPlaneByPrincipalPlane(offset= 
		L_of2, principalPlane=XYPLANE)#Datum[4]
	RailPart.DatumPlaneByPrincipalPlane(offset=
	  x2b, principalPlane=YZPLANE) #Datum[5]	
	RailPart.DatumPlaneByPrincipalPlane(offset=
	  xb1, principalPlane=YZPLANE) #Datum[6]
	RailPart.DatumPlaneByPrincipalPlane(offset=
	  Trin, principalPlane=XYPLANE) #Datum[7] 
	yp=140.0
	RailPart.DatumPlaneByPrincipalPlane(offset=
	  yp, principalPlane=XZPLANE) #Datum[8]
	RailPart.DatumPlaneByPrincipalPlane(offset=0.0,  principalPlane=YZPLANE) # Datum [9] 
	RailPart.DatumPlaneByPrincipalPlane(offset=H,  principalPlane=XZPLANE) # Datum [10] 

	RailPart.PartitionCellByDatumPlane(cells=
		RailPart.cells.findAt(((xb1, H, RL-lin), ), ), datumPlane=
			RailPart.datums[8])

	#Create partition for vertical load application:
	xce=-14.8
	dz=266.7
	z=[zci1-i*dz for i in range(stepsno)]
	for zce in z:
		SkeLo=myModel.ConstrainedSketch(gridSpacing=1.0, name='ellipticLoad', 
			sheetSize=2400.00, transform=RailPart.MakeSketchTransform( sketchPlane=RailPart.datums[10], 
			sketchPlaneSide=SIDE1,sketchUpEdge=RailPart.edges.findAt((-10.0, 0.0, 0.0), ), 
			sketchOrientation=RIGHT, origin=(0.0, 171.45, 0.0)))
		SkeLo.sketchOptions.setValues(decimalPlaces=6)
		SkeLo.sketchOptions.setValues(gridAuto=OFF, gridSpacing=1.0)
		SkeLo.sketchOptions.setValues(numMinorGridIntervals=1)
		RailPart.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=SkeLo)
		SkeLo.EllipseByCenterPerimeter(axisPoint1=(zce, xce+b),axisPoint2=(zce+a,xce),center=(zce,xce))	
		RailPart.PartitionFaceBySketchThruAll(faces=RailPart.faces.findAt(((-3.292674,171.434755, zce), )), sketch=
		SkeLo, sketchPlane= RailPart.datums[10], sketchPlaneSide=  SIDE1, sketchUpEdge= RailPart.edges.findAt((-10.0, 0.0, 
			0.0), ))	

	### Create Materials
	myModel.Material(name='steel rail')
	myModel.materials['steel rail'].Elastic(table=((200000.0, 0.3), 
		))
	myModel.materials['steel rail'].Plastic(table=((440, 0.0),(600, 0.001),(700, 0.004),(800, 0.006)))	
	myModel.materials['steel rail'].Density(table=((7.8e-09, ), ))		
	# myModel.parts['inclusion'].SectionAssignment(offset=0.0, 
		# offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
		# cells=myModel.parts['inclusion'].cells.findAt(((xb1,yci1,0.0), ), )),
			# sectionName='inclusion', thicknessAssignment=FROM_SECTION)	
	myModel.HomogeneousSolidSection(material='steel rail', name=
		'rail', thickness=None)	
	RailPart.SectionAssignment(offset=0.0,
		offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
					cells=RailPart.cells.findAt(((0.0, 169.0, 800.1), ), ((1.0, 20.0, 
	801.0), ), ((-9.143037, 109.693032, 994.833374), ), ((9.516726, 
	114.698953, 249.797251), ), )), sectionName='rail', thicknessAssignment=FROM_SECTION)	
	##create Assembly instances:
	myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
	RailInst=myModel.rootAssembly.Instance(dependent=OFF, name='RailInst', 
			part=RailPart)

	for n in range (stepsno):
		#Create local coordinate systems for the load
		myModel.rootAssembly.DatumCsysByThreePoints(coordSysType=
			CARTESIAN, name='Datum Coord for Load_'+str(n), origin=(xce, H, z[n]), point1=(
			10.0, H, z[n]), point2=(10.0, 180.0, z[n]))
		#Create Steps or individual vertical loads
	hy=171.362215
	RailLoaderw2.ApplyLoads(myModel,RailInst,nt,'realgeometry',loadtype,dz,stepsno,a,b,hy)		
		# Apply the longitudinal load
	myLoadSurface=myModel.rootAssembly.Surface(name='Surf-2', side1Faces=
			myModel.rootAssembly.instances['RailInst'].faces.findAt(
			((xb1,yci1,0.0), ),((xb1,H/2.0,0.0), ),((xb1,yci1,RL), ) ,((xb1,H/2,RL), )))
	myLoad=myModel.Pressure(amplitude=UNSET, createStepName='step_0', 
			distributionType=UNIFORM, field='', magnitude=Pressure2, name='Load-2', region=
			myLoadSurface)			
		#Create Datum planes
		
	##Apply the load
	#Surface area bound:
	#curve equation: (x-xc)^2+(y-yc)^2=Rh^2
	#Rail top curve: y=yc+sqrt(Rh^2-(x-xc)^2)
	# yc=H-R3
	# xc=xb1
	# Rh=R3
	# x1=px1/20.0
	# y1=yc+sqrt(Rh**2-(x1-xc)**2)


	# Create dummy instance
			##create a dummy element
	sketchd=myModel.ConstrainedSketch(name='dummy section', sheetSize=400.0)
	sketchd.Line(point1=(0,0),point2=(rin,0))
	sketchd.Line(point1=(rin,0),point2=(rin,rin))
	sketchd.Line(point1=(rin,rin),point2=(0,rin))	
	sketchd.Line(point1=(0,rin),point2=(0,0))
	mydummyPart=myModel.Part(name='dummy',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
	mydummyPart.BaseSolidExtrude(depth=rin, sketch=sketchd)
	mydummyPart.SectionAssignment(offset=0.0, 
				offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
				cells=mydummyPart.cells.findAt(((0,0,rin), 
				), )), sectionName='rail', thicknessAssignment=
					FROM_SECTION)

	#Creating a dummy Instance
	myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
	DummyInst=myModel.rootAssembly.Instance(dependent=ON, name='dmyInst', part=mydummyPart)
	#Translate the the dummy instance at a distance Lr
	myModel.rootAssembly.translate(instanceList=('dmyInst', ), 
			vector=(0.0, 0.0, RL))	
	#Applying Encastred BC
	myModel.EncastreBC(createStepName='Initial', name='BC-dummy', region=Region(faces=DummyInst.faces.findAt(((rin/2, rin/2, RL+rin),),)))
	#Mesh the dummy part
	mydummyPart.setElementType(elemTypes=(ElemType(elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15, 
		elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), 
		regions=(mydummyPart.cells.findAt(((rin/2, rin/2, rin/2), ), ), ))
	mydummyPart.seedPart(deviationFactor=0.5, minSizeFactor=0.5, size=rin)
	mydummyPart.generateMesh()
	#create dummy node
	myModel.rootAssembly.Set(name='Set-3', vertices=DummyInst.vertices.findAt(((0.0, 0.0, RL), ), ))
	
	
	
		#Start Meshing

	#Mesh the instances 
	myModel.rootAssembly.setElementType(elemTypes=(ElemType(
		elemCode=C3D8R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, 
			kinematicSplit=AVERAGE_STRAIN, hourglassControl=DEFAULT, 
				distortionControl=DEFAULT), ElemType(elemCode=C3D6, elemLibrary=STANDARD), 
					ElemType(elemCode=C3D4, elemLibrary=STANDARD)), regions=(
						RailInst.cells.findAt(((xb1,yb1,lin), ),),))
	myModel.rootAssembly.setMeshControls(elemShape=TET, 
		regions= RailInst.cells.findAt(((xb1,H-1.0,Trin), ), ), technique=FREE)
	myModel.rootAssembly.setElementType(elemTypes=(ElemType(
		elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15, 
			elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)), 
				regions=(RailInst.cells.findAt(((xb1,H-1.0,Trin), ), ), ))
												
	myModel.rootAssembly.seedPartInstance(deviationFactor=devf, 
		minSizeFactor=minf,regions=(RailInst,), size=Elsize)

			#seeds of elements size at load application neighbourhood

	pp=dz-(lin-257.495471)
	pz=[pp+i*dz for i in range(stepsno)]
	for ze in pz:
		myModel.rootAssembly.seedEdgeBySize(constraint=FINER, 
			deviationFactor=0.5, edges=RailInst.edges.findAt(((-14.802219, 171.141788, ze), )),
				minSizeFactor=0.99, size=0.5)						
		myModel.rootAssembly.generateMesh(regions=
			RailInst.cells.findAt(((xci1,H-0.4,ze), ), ))			
	myModel.rootAssembly.generateMesh(regions=
		RailInst.cells.findAt(((xb1,H-1.0,Trin),),((xb1,yb1,lin), ),), seedConstraintOverride=ON)

	return myModel