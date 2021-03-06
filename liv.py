# automated
import numpy, pandas, face_recognition, cv2, os,datetime

thres = 0.45  # Threshold to detect object
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
classNames =[]
classFile ='coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')
    print(classNames)
configPath ='ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath ='frozen_inference_graph.pb'
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

names = []
images = []
path = 'Only one'
for _ in os.listdir(path):
    img = cv2.imread(f'{path}/{_}')
    images.append(img)
    names.append(os.path.splitext(_)[0])
print(names)

def encodings(images):
    encoded_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_e = face_recognition.face_encodings(img)[0]
        encoded_list.append(img_e)
    return encoded_list

known_faces_encoding = encodings(images)
print("Faces encoded")

def mark_attendence(name):
    nameslist=[]
    with open('atten.csv','r+') as f:
        data=f.readlines()
        for _ in data:
            entry=_.split(',')
            nameslist.append(entry[0])
        if name not in nameslist:
            now=datetime.datetime.now()
            dtstr=now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtstr}')

count=0
old=''
def accu(val):
    global count
    global old
    print(old,count,val,sep='\t')
    if old==val:
        count+=1
    else:
        count=0
        old=val
        return False
    if count>=10:
        return True
    else:
        return False

cap = cv2.VideoCapture(0)

while True:
    a, img = cap.read()
    small_img = cv2.resize(img, (0,0), None, 0.25, 0.25)
    small_img=cv2.cvtColor(small_img,cv2.COLOR_BGR2RGB)

    classIds, confs, bbox = net.detect(img, confThreshold=0.6)
    if list(classIds) == [1,1]:
        print("SPOOF")
    else:
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                if (classNames[classId-1]) in ["tv","laptop","cell phone","suitcase","remote","skateboard","book"]:
                    print("SPOOF",box)
                    cv2.rectangle(img, (0,0),(1000,100), color=(0, 255, 0), thickness=2)
                    cv2.rectangle(img, (0,0),(1000,100), (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, "SPOOF",(130,70),cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 3)
                    #cv2.putText(img, str(round(confidence * 100, 2)), (box [0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    all_faces_locations = face_recognition.face_locations(small_img)
    all_faces_encoding = face_recognition.face_encodings(small_img, all_faces_locations)
    # bcoz in camera we may have more than one face
    for face_encode, face_loc in zip(all_faces_encoding, all_faces_locations):
        #print(face_encode)
        result = face_recognition.compare_faces(known_faces_encoding, face_encode)
        face_dis=face_recognition.face_distance(known_faces_encoding,face_encode)
        index=numpy.argmin(face_dis)
        if face_dis[index] and min(face_dis)<=0.5:
            #print(face_dis,names[index].upper())
            x1,y1,x2,y2=all_faces_locations[0][3],all_faces_locations[0][0],all_faces_locations[0][1],all_faces_locations[0][2]
            x1,y1,x2,y2=x1*4,y1*4,x2*4,y2*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,0,255),cv2.FILLED)
            resulttt=accu(names[index])
            if resulttt:
                cv2.putText(img,names[index].upper(),(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                mark_attendence(names[index])
            else:
                cv2.putText(img,'DETECTING...',(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        else:
            x1,y1,x2,y2=all_faces_locations[0][3],all_faces_locations[0][0],all_faces_locations[0][1],all_faces_locations[0][2]
            x1,y1,x2,y2=x1*4,y1*4,x2*4,y2*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,0,255),cv2.FILLED)
            cv2.putText(img, 'UNKNOWN...', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imshow('webcam',img)
    cv2.waitKey(1)
