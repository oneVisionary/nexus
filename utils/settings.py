from ultralytics import YOLO
landmarks=  ["front_left_paw","front_left_knee"
    ,"front_left_elbow"
    ,"rear_left_paw"
    ,"rear_left_knee"
    ,"rear_left_elbow"
    ,"front_right_paw"
    ,"front_right_knee"
    ,"front_right_elbow"
    ,"rear_right_paw"
    ,"rear_right_knee"
    ,"rear_right_elbow"
    ,"tail_start"
    ,"tail_end"
    ,"left_ear_base"
    ,"right_ear_base"
    ,"nose"
    ,"chin"
    ,"left_ear_tip"
    ,"right_ear_tip"
    ,"left_eye"
    ,"right_eye"
    ,"withers"
    ,"throat"]

device = "cpu"
model = YOLO("best.pt") 

