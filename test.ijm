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
			IJ.redirectErrorMessages();
			temp = getFileList(""+myDir+list[i]);
			if (endsWith(temp[1],".tif")) {
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
				saveAs("Tiff", output+"HS_"+substring(title1,0,lengthOf(title1))+".tif");   			
				close("*");
				call("java.lang.System.gc");
			}
		}
	}
}

	
