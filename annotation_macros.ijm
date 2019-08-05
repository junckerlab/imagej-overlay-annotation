macro "Reload these macros [f9]" {
	// hard coded. Professional.
	run("Install...", "install=/home/nikoli/Clone/McGill/DJGroup/CTC/ctc-scripts/git/imagej-overlay-annotation/annotation_macros.ijm");
}

// TODO
// roiManager("Rename", "bg");
// roiManager("Rename", "ctc");
// roiManager("Rename", "wbc");
// next im please (save overlay, list to tab, clean roi manager, etc)

macro "Toggle Overlay [o]" {
	if (Overlay.size>0) {
		if (Overlay.hidden) {
			Overlay.show;
			run("Labels...", "color=white font=12 show use draw");
		} 
		else {Overlay.hide;}
	}
} 

macro "Add, Name, and Outline in Overlay [a]" {
	// probably shouldn't run the use names as labels each time but yolo
	roiManager("UseNames", "true");
	setKeyDown("alt");
	roiManager("add");
	run("Add Selection...");
	run("Labels...", "color=white font=12 show use draw");
}

/* These two are kinda buggy. I didn't want to destroy the ROI's when they get
 * sent to the overlay for fear of destroying someone's work, but if you do a
 * From/To overlay cycle it adds an extra set of objects into the ROI
 */ 
macro "ROIs to Overlay [T]" {
	// Overrides any previous overlay :( 
	run("From ROI Manager");
	roiManager("Show None");
	// Show the labels 
	run("Labels...", "color=white font=12 show use draw");
}

macro "ROIs from Overlay [F]" {
	// AKA Overlay to ROIs
	// roi manager must be open in order to open roi manager, I feel like this
	// ellipsis is taunting me
	roiManager("Show All");
	// This just adds to the overlay, doesn't override. Potentially makes weird
	// names
	run("To ROI Manager");
	roiManager("Show All");
}

macro "Save ROI List [f1]" {
	// This should probably integrate ROIs to Overlay + save and (maybe) clear
	// ROI manager. Or have a macro for "next im please"
	dir = getDirectory("image");
	name = getTitle;
	csv_name = replace(name, ".tif", ".csv");
	path = dir + csv_name;
	roiManager("List");
	saveAs("Results", path);
	roiManager("reset");
}
