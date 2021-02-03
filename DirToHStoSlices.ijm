//#@File(label='Source directory', style="directory") myDir
#@String myDir
output=myDir+"/"; 
myDir=myDir+"/";


print("directory : "+ myDir + " - output dir : "+output);

find(myDir) 

function find(myDir) { 
	list = getFileList(myDir); 	
	for (i=0; i<list.length; i++) {  
		//print(""myDir+list[i]);	
		if (endsWith(list[i], ")/")) 			
			find(""+myDir+list[i]);			
		else if (endsWith(list[i], "/")) {
			//print(""+myDir+list[i]);
			open(""+myDir+list[i]);
			getDimensions(w, h, channels, slices, frames);
			title1=getTitle();
			index1=indexOf(title1,"range");
			index2=indexOf(title1,"step");
			range=parseInt(substring(title1,index1+5,index2-1));
			index1=indexOf(title1,"_exposure");
			//title2=substring(title1,index2+4,index1);
			step=parseInt(substring(title1,index2+4,index1));
			TrueSlices=(range/step)+1;				
			run("Stack to Hyperstack...", "order=xyczt(default) channels=1 slices="+toString(TrueSlices)+" frames="+toString(slices/TrueSlices)+" display=Grayscale");						
			getDimensions(w, h, channels, slices, frames);
			for (j=1; j<=slices; j++) {                                 
				Stack.setSlice(j);
				run("Reduce Dimensionality...", "frames keep");                                
				/*
						list2 = getList("image.titles");
					  if (list2.length==0)
						 print("No image windows are open");
					  else {
						 print("Image windows:");
						 for (i=0; i<list2.length; i++)
							print("   "+list2[i]);
					  }
					 print("");
					*/ 
				title2=replace(title1,'power50','power50-1');
				//print(title2);
				selectWindow(title2);
				saveAs("Tiff", output+"Slice"+toString(j)+"_"+substring(title1,0,lengthOf(title1))+".tif");                	
				selectWindow(title1);
				close("Slice*");
				call("java.lang.System.gc");
			}
			
			close("*");
			call("java.lang.System.gc");
		}
	}
}

	
