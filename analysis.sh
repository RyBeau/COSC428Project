#!/bin/bash

rm analysis-output.mkv

# Install detectron2
if [ -z "$(pip3 list | grep detectron2)" ]
then
    # Depending on the version of CUDA/PyTorch, you may need to change this command.
    # There is a table in the Git repo outlining which version to use: https://github.com/facebookresearch/detectron2/blob/master/INSTALL.md
    python3 -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu111/torch1.8/index.html
fi

if [ ! -d detectron2 ]
then
    # Download the repo to access all of the predeveloped config files/scripts/etc.
    git clone https://github.com/facebookresearch/detectron2.git
    cd detectron2 && git checkout f3ada7de1fa30f03c330bb701c5100d88f43b429
    # Copy over the juggling example, and modified predictor.py script.

else
    cd detectron2
fi

yes | cp -rf ../*.py ./demo/
yes | cp -rf ../*.mp4 ./demo/
cd demo

# Run the model on the webcam.
python3 demo.py --ref-video reference_video.mp4 --analysis-video analysis_video.mp4 --confidence-threshold 0.99 --output ../../analysis-output.mkv --config-file ../configs/COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml --opts MODEL.WEIGHTS detectron2://COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x/137849621/model_final_a6e10b.pkl

rm *.*
git reset --hard HEAD