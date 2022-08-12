import cv2
from deepface import DeepFace
import matplotlib.pyplot as plt
import dlib
import face_alignment
from skimage import io
import plotly.express as px

import numpy as np
import pandas as pd

import torch.backends.cudnn as cudnn
cudnn.benchmark = False

# conda install opencv matplotlib dlib matplotlib numpy pandas -y
# pip install deepface
# pip install face-alignment
# pip install jupyter-dash

# TODO: zip and host deepface weights (file unreadable)


capture = cv2.imread('./some_asian_baddie.jpg')
rows, cols, ch = capture.shape

capture_grey = cv2.cvtColor(capture, cv2.COLOR_BGR2GRAY)
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("landmarks")

fig, ax = plt.subplots(1, figsize=(16, 7))
ax.imshow(capture[:, :, ::-1])
plt.show()

obj = DeepFace.analyze(img_path="some_asian_baddie.jpg", actions=('age', 'gender', 'race', 'emotion'))
# objs = DeepFace.analyze(["img1.jpg", "img2.jpg", "img3.jpg"]) #analyzing multiple faces same time
print("{} year old {} {}, {} expression".format(obj["age"], obj["dominant_race"], obj["gender"],
                                                obj["dominant_emotion"]).lower())

print(obj)

LEFT_EYE = None
RIGHT_EYE = None
BRIDGE = None
LANDMARKS = []
landmarks = None
LEFT_EYE, RIGHT_EYE, BRIDGE, LEFT_BROW, RIGHT_BROW, LEFT_JAW, RIGHT_JAW = tuple([None] * 7)


def set_globals():
    global LEFT_EYE, RIGHT_EYE, BRIDGE, LEFT_BROW, RIGHT_BROW, LEFT_JAW, RIGHT_JAW
    LEFT_EYE = (landmarks.part(39).x, landmarks.part(39).y)
    RIGHT_EYE = (landmarks.part(42).x, landmarks.part(42).y)
    BRIDGE = [landmarks.part(27).x, landmarks.part(27).y]
    LEFT_BROW = (landmarks.part(17).x, landmarks.part(17).y)
    RIGHT_BROW = (landmarks.part(26).x, landmarks.part(26).y)
    LEFT_JAW = (landmarks.part(4).x, landmarks.part(4).y)
    RIGHT_JAW = (landmarks.part(12).x, landmarks.part(12).y)


def get_roll_matrix(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    tan = (y2 - y1) / (x2 - x1)
    angle = np.degrees(np.arctan(tan))
    xc = (x1 + x2) // 2
    yc = (y1 + y2) // 2
    M = cv2.getRotationMatrix2D((xc, yc), angle, 1)
    return M


faces = face_detector(capture_grey)
landmarks = landmark_predictor(capture, faces[0])
set_globals()
# Roll correction
M = get_roll_matrix(LEFT_EYE, RIGHT_EYE)
roll_corrected = cv2.warpAffine(capture, M, (rows, cols))
rows, cols, ch = roll_corrected.shape
faces = face_detector(roll_corrected)
landmarks = landmark_predictor(roll_corrected, faces[0])
set_globals()
# Pitch and Yaw
# orig = np.float32([LEFT_BROW, RIGHT_BROW, RIGHT_JAW, LEFT_JAW])
# aspect = rows/cols
# x_buffer = -120
# y_buffer = int(x_buffer * aspect)
# dest = np.float32([[-x_buffer, -y_buffer], [rows-x_buffer, -y_buffer],
#                    [rows-x_buffer, cols-y_buffer], [-x_buffer, cols-y_buffer]])
# M = cv2.getPerspectiveTransform(orig, dest)
# roll_corrected = cv2.warpPerspective(roll_corrected, M, (rows-x_buffer*3, cols-y_buffer*3))
# faces = face_detector(roll_corrected)
# landmarks = landmark_predictor(roll_corrected, faces[0])
# set_globals()

for mark in range(0, 68):
    x = landmarks.part(mark).x
    y = landmarks.part(mark).y
    if mark in [39, 42, 27, 8]:
        cv2.circle(roll_corrected, (x, y), 3, (255, 0, 0), -1)
    else:
        cv2.circle(roll_corrected, (x, y), 3, (0, 255, 0), -1)

    LANDMARKS.append([x, y])

fig, axes = plt.subplots(1, 2, figsize=(12, 7))
axes[0].imshow(roll_corrected)
LANDMARKS = np.array(LANDMARKS)

axes[1].scatter(LANDMARKS[:, 0], LANDMARKS[:, 1], c='green')
axes[1].plot([LEFT_EYE[0], BRIDGE[0]], [LEFT_EYE[1], LEFT_EYE[1]], c='red')
axes[1].plot([BRIDGE[0], RIGHT_EYE[0]], [RIGHT_EYE[1], RIGHT_EYE[1]], c='blue')
plt.tight_layout()
plt.show()

# ---


fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._3D, flip_input=False)

img = io.imread('some_asian_baddie.jpg')
preds = np.array(fa.get_landmarks(img)[0])
df = pd.DataFrame(
    {'x': preds[::, 0], 'y': preds[::, 1], 'z': preds[::, 2], 'id': range(len(preds)), 'colour': [1] * len(preds)})
df.head()
df.dtypes

pupil_y = (abs((df[df['id'] == 41]['y'].values) - (df[df['id'] == 37]['y'].values))[0] / 2) + \
          (df[df['id'] == 37]['y'].values)[0]
print(pupil_y)

# Append other key points to dataframe that need to be calculated
data = []
pupil_x = (abs((df[df['id'] == 39]['x'].values) - (df[df['id'] == 36]['x'].values))[0] / 2) + \
          (df[df['id'] == 36]['x'].values)[0]
pupil_y = (abs((df[df['id'] == 41]['y'].values) - (df[df['id'] == 37]['y'].values))[0] / 2) + \
          (df[df['id'] == 37]['y'].values)[0]
pupil_z = df[df['id'] == 41]['z'].values[0]
pupil = [pupil_x, pupil_y, pupil_z, len(df) + 1, 2]
data.append(pupil)
df = df.append(pd.DataFrame(data=data, columns='x y z id colour'.split()))

fig = px.scatter_3d(df, x='x', y='y', z='z', color='colour')
fig.update_traces(mode='markers', marker_line_width=2, marker_size=3)

# tight layout
fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))


def build_feature_vector(df, label):
    # Extract key distances
    nose_chin = abs((df[df['id'] == 33]['y'].values) - (df[df['id'] == 8]['y'].values))[0]
    nose_lips = abs((df[df['id'] == 33]['y'].values) - (df[df['id'] == 66]['y'].values))[0]
    pupil_nose = abs((df[df['id'] == 69]['y'].values) - (df[df['id'] == 33]['y'].values))[0]
    nose_width = abs((df[df['id'] == 31]['x'].values) - (df[df['id'] == 35]['x'].values))[0]
    eye_span_outside = abs((df[df['id'] == 36]['x'].values) - (df[df['id'] == 45]['x'].values))[0]
    lip_height = abs((df[df['id'] == 57]['y'].values) - (df[df['id'] == 51]['y'].values))[0]
    face_width = abs((df[df['id'] == 0]['x'].values) - (df[df['id'] == 16]['x'].values))[0]
    middle_third = abs((df[df['id'] == 50]['y'].values) - (df[df['id'] == 37]['y'].values))[0]

    # Build feature vector of distance ratios
    # TODO: Hairline estimate?
    return [
        obj["age"],
        1 if obj["gender"] == "Woman" else 0,
        face_width / middle_third,
        nose_chin / nose_lips,
        nose_chin / pupil_nose,
        nose_width / nose_lips,
        lip_height / nose_width,
        1 if label == 'hot' and obj["gender"] == "Woman" else 0
    ]


feature_vector = build_feature_vector(df, label='hot')
print(feature_vector)
