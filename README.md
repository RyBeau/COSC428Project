# Golf Swing Analysis Using Pose Estimation
Author: Ryan Beaumont (2021)

This repository contains the code used for golf swing analysis using pose estimation by performing a direct comparison of the joint
angles of a professional golfer to that of an amateur.

## Dependencies
* Python
* OpenCV
* PyTorch (The analysis.sh script may need to be updated if your PyTorch version differs)
* Requires Linux OS

## Running the Demo
To run a demo of the program run the command `bash analysis.sh` in the terminal.
This will run a demo of the program using the two videos; reference_video.mp4 and analysis_video.mp4, contained in the folder.
The output of the demo will be in the root directory of the project.

## Running with Other Videos
The command in within analysis.sh can be adjusted to take other videos as input.

`python3 demo.py --ref-video reference_video.mp4 --analysis-video analysis_video.mp4 
--confidence-threshold 0.99 --output ../../analysis-output.mkv --config-file ../configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml --opts MODEL.WEIGHTS detectron2://COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl
`

#### Key Arguments
* --ref-video: Path to the video to use as the swing reference. If it is not in the same
folder it will need the full path.
  
* --analysis-video: Path to the video to perform the analysis on. If it is not in the same
folder it will need the full path.
  
* --opposite-hands: A flag for if the two golfers in the clips have opposite dominant hands. If this argument is given 
  followed by any value in the command line it will flip the frame of the analysis video to match the reference.
  E.g. `--opposite-hands true` will flip the frame.
  
* --output: The output file name and destination. This path is from the /demo/ directory in the detectron2 repository.

* Details about other arguments can be found in the detectron2 documentation.

## Files
There are four files related to running the program.
* demo.py
* predictor.py
* swing_analysis.py
* analysis.sh

### demo.py
This is a version of the demo.py provided with the detectron2 repository with
slight modifications for processing the two videos at once. It creates the output video
or OpenCV preview window using the analyser in predictor.py.

### predictor.py
This is a version of the demo predictor.py contained with the detectron2 repository.
Some modifications have been made for processing the two videos at once and calling the appropriate
functions from the swing_analysis.py file to perform/display the analysis.

### swing_analysis.py
swing_analysis.py contains the code related to performing the joint angle calculation, comparison
and drawing of coloured markers on the frame.

### analysis.sh
This file is a bash script to make setting up and running the program simpler. Upon
running `bash analysis.sh` the script will pull the needed repositories and move the
demo.py, predictor.py, analysis.sh and video files into the /demo/ directory in the detectron2 repository replacing the files
within. It will then run the analysis program and perform clean up of the detectron2 repository upon completion.

## Things to Note
* Both the videos need to be at the same frame rate. Preferably 60 fps, or it will be unlikely that
many swing events have been captured due to the speed of the swing.
  
* The two videos need to be synchronised. In many cases only the start of the swing needs
to be matched across the two videos. However, it may be that another key event will need to be synced.
  Testing has shown that syncing the start and impact events of the swing results in
  the swings being synchronised throughout the analysis.