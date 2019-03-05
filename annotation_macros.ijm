/* How toggle overlay ? */
//run("Hide Overlay");
//run("Show Overlay");

macro "Save ROI List [f1]" {
	dir = getDirectory("image");
	name = getTitle;
	csv_name = replace(name, ".tif", ".csv");
	path = dir + csv_name;
	roiManager("List");
	saveAs("Results", path);
}

 macro "Toggle Overlay [o]" {
	if (Overlay.size>0) {
		if (Overlay.hidden)
		Overlay.show;
		else
		Overlay.hide;
	}
} 

/* These two are kinda buggy. I didn't want to destroy the ROI's when they get
 * sent to the overlay for fear of destroying someone's work, but if you do a
 * From/To overlay cycle it adds an extra set of objects into the ROI
 */ 
macro "ROIs to Overlay [T]" {
	// We're overriding something?
	run("From ROI Manager");
	roiManager("Show None");
}

macro "ROIs from Overlay [F]" {
	// We're overriding Flatten
	run("To ROI Manager");
	roiManager("Show All");
}
