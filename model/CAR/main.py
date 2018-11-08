import sys
import cv2
from moviepy.editor import VideoFileClip
from svm_pipeline import *
from yolo_pipeline import *
from lane import *


def pipeline_yolo(img):

    img_undist, img_lane_augmented, lane_info = lane_process(img)
    output = vehicle_detection_yolo(img_undist, img_lane_augmented, lane_info)

    return output

def pipeline_svm(img):

    img_undist, img_lane_augmented, lane_info = lane_process(img)
    output = vehicle_detection_svm(img_undist, img_lane_augmented, lane_info)

    return output


if __name__ == "__main__":

    demo = 1  # 1:image (YOLO and SVM), 2: video (YOLO Pipeline), 3: video (SVM pipeline)

    if demo == 1:
        filename = sys.argv[1]
        opt = sys.argv[2]

        image = mpimg.imread(filename)

        if opt == "yolo":
            #(1) Yolo pipeline
            yolo_result = pipeline_yolo(image)
            mpimg.imsave("result.jpg", yolo_result)

        elif opt == "svm":
            #(2) SVM pipeline
            svm_result = pipeline_svm(image)
            mpimg.imsave("result.jpg", svm_result)

    elif demo == 2:
        # YOLO Pipeline
        video_output = 'examples/project_YOLO.mp4'
        clip1 = VideoFileClip("examples/project_video.mp4").subclip(30,32)
        clip = clip1.fl_image(pipeline_yolo)
        clip.write_videofile(video_output, audio=False)

    else:
        # SVM pipeline
        video_output = 'examples/project_svm.mp4'
        clip1 = VideoFileClip("examples/project_video.mp4").subclip(30,32)
        clip = clip1.fl_image(pipeline_svm)
        clip.write_videofile(video_output, audio=False)


