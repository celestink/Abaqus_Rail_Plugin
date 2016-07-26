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
path1=os.getcwd()
fd=str(os.path.basename(path1))
# muE0=int(fd[1:4])
import RandomStiff_Generator
#Material Properties

#SDi define incremental standard deviation index of tie Young's moduli
##INFORMATION ON TIES
##Input dimensional parameters, metric units, mm

##Information on ties
# f = open('tieModuli_SD_Incr_'+str(SDi)+'.txt', 'w')
#Cross-ties partition parameters

#Partitioning function				
def partitionties(myPart,nj,v,ch1,ch2):

	myPart[nj].DatumPlaneByPrincipalPlane(offset=
		ch1, principalPlane=XZPLANE) #Datum[3] for the part
		
	myPart[nj].DatumPlaneByPrincipalPlane(offset=
		ch2, principalPlane=XZPLANE) #Datum[4] for the part
		
	myPart[nj].PartitionCellByDatumPlane(cells=
		myPart[nj].cells.findAt((v, ), ), datumPlane=
			myPart[nj].datums[3])
			
	myPart[nj].PartitionCellByDatumPlane(cells=
		myPart[nj].cells.findAt((v, ), ), datumPlane=
			myPart[nj].datums[4])
def crosstiesPrep(myModel, nt,dim,addmat, meshsize):	
		#Vertices of the crossties
		lin=266.7
		vtce=((dim[4],dim[6]),(dim[5],dim[6]),(dim[5],dim[7]),(dim[4],dim[7]))
		#Start sketching by joining vertices
		Tiesketches1=myModel.ConstrainedSketch(name='Tiesection1', sheetSize=800.0)
		Tiesketches1.Line(point1=vtce[0],point2=vtce[1])	
		Tiesketches1.Line(point1=vtce[1],point2=vtce[2])
		Tiesketches1.Line(point1=vtce[2],point2=vtce[3])	
		Tiesketches1.Line(point1=vtce[3],point2=vtce[0])
		Tiesketches2=myModel.ConstrainedSketch(name='Tiesection2', sheetSize=800.0)
		Tiesketches2.Line(point1=vtce[0],point2=vtce[1])	
		Tiesketches2.Line(point1=vtce[1],point2=vtce[2])
		Tiesketches2.Line(point1=vtce[2],point2=vtce[3])	
		Tiesketches2.Line(point1=vtce[3],point2=vtce[0])
		
		#Create Tie part by extrusion
		mysidetiePart1=myModel.Part(name='SideTie1',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
		mysidetiePart1.BaseSolidExtrude(depth=dim[0], sketch=Tiesketches1)
		mysidetiePart2=myModel.Part(name='SideTie2',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
		mysidetiePart2.BaseSolidExtrude(depth=dim[0],sketch=Tiesketches2)
		mymiddletiePart1=myModel.Part(name='MiddleTie1_0',dimensionality=THREE_D,
		type=DEFORMABLE_BODY)
		mymiddletiePart1.BaseSolidExtrude(depth=dim[1], sketch=Tiesketches1)
		mytiePart=[myModel.Part(name='MiddleTie1_'+str(i), objectToCopy=mymiddletiePart1) for i in range(1,nt-2)]
		mytiePart.insert(0,mysidetiePart1)
		mytiePart.insert(1,mymiddletiePart1)
		mytiePart.append(mysidetiePart2)
		myTies=[]
		# Materials of the crosstie parts
		for i in range(nt):
			#CREATE THE TIE CONCRETE  MATERIALS 
			myModel.Material(name='concrete ties'+str(i))
			myModel.materials['concrete ties'+str(i)].Elastic(table=((addmat[0][i], addmat[1]),))
			myModel.materials['concrete ties'+str(i)].Density(table=((addmat[2], ), ))	
			#Create section
			myModel.HomogeneousSolidSection(material='Concrete'+str(i), name='ConcreteTie'+str(i))	
			#Assign section
			mytiePart[i].SectionAssignment(offset=0.0, 
				offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
				cells=mytiePart[i].cells.findAt(((dim[4]/4.0, (dim[7]/2.0), dim[0]/2.0), 
				), )), sectionName='ConcreteTie'+str(i), thicknessAssignment=FROM_SECTION)
		
			#Instancing each tie
			myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
			mytieInst=myModel.rootAssembly.Instance(dependent=ON, name='Ties'+str(i), 
				part=mytiePart[i])	
			myTies.append(mytieInst)
			#Translate the tie at a distance Tr along the rail
			myModel.rootAssembly.translate(instanceList=('Ties'+str(i), ), 
				vector=(0.0, 0.0, dim[8][i]))
			##Applying Encastred BC
			myModel.EncastreBC(createStepName='Initial', name='BC-Tie'+str(i), region=Region(
				faces=mytieInst.faces.findAt(((dim[4]/4.0, dim[7], (dim[0]/2+dim[8][i])), ), )))
			
			if i==0 or i==nt-1:
				v=(5.0,-50.0,5.0) # Location of the part (pick one point of the part)
				ch1=-169.80 #First depth of the partition
				ch2=-8.0 # Second depth of the partition
				partitionties(mytiePart,i,v,ch1,ch2)	
				
			##Mesh each tie part
			mytiePart[i].setElementType(elemTypes=(ElemType(elemCode=C3D20R, elemLibrary=STANDARD),
				ElemType(elemCode=C3D15, elemLibrary=STANDARD), ElemType(elemCode=C3D10,
				elemLibrary=STANDARD)), regions=(mytiePart[i].cells.findAt(((dim[4]/4.0, (dim[7]/2.0), dim[0]/2.0), ), ), ))
			mytiePart[i].seedPart(deviationFactor=0.2, minSizeFactor=0.2, size=meshsize)
			mytiePart[i].generateMesh()
			
			#Creates node sets for periodic boundary conditions
			if i==0:
				myModel.rootAssembly.Set(faces= mytieInst.faces.findAt(((
				5.0, -50.0, 0.000), )), name='Set-1')
			elif i==(nt-1):
				myModel.rootAssembly.Set(faces= mytieInst.faces.findAt(((
				5.0, -50.0, 2*(nt-1)*lin), )), name='Set-2') 
		