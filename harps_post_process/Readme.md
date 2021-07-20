# HARPS Post-Process

Post-Processes subject data from HARPS study.

## Installation

Clone repository. Requires Matlab.

## Directory Format
```
/(containing directory)
	post_process_main.m
	postProcessROSbag.m
	callSoftMax.m
	softMaxSketchCall.py
	softmaxModels.py
	sketchGen.py
	gaussianMixtures.py
	/Subject(#)_(Type (Push, Pull, Both))
		_slash_(Topic Name).csv
	/Subject(#)_(Type)
	...
```

## Usage
Run post_process_main.m with Matlab and proper directory format.

## Output
Directory (/post-process-output-(Date)) of processed subject data .mat files. If subject data .mat file already exists in the directory a new version is saved with a random number ending. 

## Known Issues
Trials of type 'Both2' or with a push sketch type 'you' are not properly handled and will cause an error. Currently working on best practices for softmax evaluation of this sketch type. 
