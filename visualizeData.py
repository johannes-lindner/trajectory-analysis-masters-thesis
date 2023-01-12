import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def list2json(list):
    d = {}
    for index in range(0, len(list) - 1):
        key = index
        d[key] = list[index]
    return json.dumps(d)


def dist2D(posX1, posY1, posX2, posY2):
    return np.sqrt((posX2 - posX1) ** (posX2 - posX1) + (posY2 - posY1) ** (posY2 - posY1))


def strArray2Int(arr):
    new_arr = []
    for element in arr:
        if element != ",":
            new_arr.append(int(element))
    return np.array(new_arr)


# ====================
rootpath = os.path.dirname(__file__)  # Path to this script
with open(os.path.join(rootpath, "data", "misc", "folderstructure.json")) as f:
    config = json.load(f)

scenID = 1
subscenID = 2

folderPath = os.path.join(rootpath, "data", "raw", "Szenarien", config["scenarios"][scenID]["scenName"],
                          config["scenarios"][scenID]["subscen"][subscenID]["subscenName"])
scenariofiles = os.listdir(folderPath)
imagefile = os.path.join(rootpath, "data", "images", config["scenarios"][scenID]["imagepath"])

# ====================
# --- Start Plot ---
fig, ax = plt.subplots(2, 1)
img = plt.imread(imagefile)
imageextent = config["scenarios"][scenID]["imageextent"]
ax[1].imshow(img, extent=imageextent)

# read first file
nrFiles = len(scenariofiles)
dataList = []
lineList = []
avgPosScreenChangeZ = []
avgPosScreenChangeX = []

for i in range(0, nrFiles):
    filename = os.path.join(folderPath, scenariofiles[i])
    with open(filename) as f:
        data = json.load(f)

    scenid = data["scenid"]
    lap = data["lap"]
    simrum = data["simrun"]
    df = pd.read_json(list2json(data["dataframe"]), orient='index')
    df["datetime"] = df["datetime"] - df.loc[0,"datetime"]
    description = data["description"]
    surveyAnswersBike = strArray2Int(data["surveyAnswersBike"])
    surveyAnswersAV = strArray2Int(data["surveyAnswersAV"])
    dataList.append(data)

    screens = df["bike_screens"].to_numpy()
    screenchange = np.where(screens[:-1] != screens[1:])[0]
    print(str(screenchange) + " " + description[0] + description[1])

    # Speed
    #ax[0].plot(df["bike_pos_z"], df["bike_speed"], label=description[0] + description[1], linewidth=1)
    ax[0].plot(df["datetime"], df["bike_speed"], label=description[0] + description[1], linewidth=1)
    ax[0].scatter(df["datetime"][screenchange], df["bike_speed"][screenchange])

    # Distance between vehicles and TTC
    if len(surveyAnswersBike) == 6 and len(surveyAnswersAV) == 6:
        answerEndangerment = np.mean([surveyAnswersAV[5], surveyAnswersBike[5]])
        c = (np.clip(0.5 * answerEndangerment - 0.5, 0, 1), np.clip(-0.5 * answerEndangerment + 2.5, 0, 1), 0,)
    else:
        answerEndangerment = 0
        c = 'grey'

    # print(answerEndangerment)
    df["distanceBetweenVehicles"] = np.sqrt(
        np.power(df["bike_pos_z"] - df["av_pos_z"], 2) + np.power(df["bike_pos_x"] - df["av_pos_x"], 2))
    df["TTC"] = df["distanceBetweenVehicles"] / (df["bike_speed"] + df["av_speed"])
    # ax[0].plot(df["bike_pos_z"], df["TTC"],label=description[0] + description[1] + " - " + str(answerEndangerment), linewidth=1, color=c)

    # Distance to obstacle, too early or too late
    df["distToScenBike"] = -470.2758 - df["bike_pos_z"]
    if len(surveyAnswersBike):
        answerTiming = surveyAnswersBike[1]
        c = (np.clip(0.5 * answerTiming - 0.5, 0, 1), np.clip(-0.5 * answerTiming + 2.5, 0, 1), 0,)
    else:
        answerTiming = 0
        c = 'grey'

    # print(screenchange)
    # ax[0].scatter(df["distToScenBike"][screenchange[0]],answerTiming)
    # ax[0].scatter(df["bike_pos_z"][screenchange[0]],answerTiming,color=c)

    # ax[0].plot(df["bike_pos_z"],df["bike_pos_z"], color='blue')
    # ax[0].plot(df["bike_pos_z"],df["av_pos_z"], color='red')
    if config["scenarios"][scenID]["invertXY"]:
        ax[1].plot(df["bike_pos_x"], df["bike_pos_z"], label=description[0] + description[1], linewidth=1)
        ax[1].scatter(df["bike_pos_x"][screenchange], df["bike_pos_z"][screenchange])
        ax[1].scatter(df["bike_pos_x"][0], df["bike_pos_z"][0], s=100, c="w")
    else:
        ax[1].plot(df["bike_pos_z"], df["bike_pos_x"], label=description[0] + description[1], linewidth=1)
        ax[1].scatter(df["bike_pos_z"][screenchange], df["bike_pos_x"][screenchange])
        ax[1].scatter(df["bike_pos_z"][0], df["bike_pos_x"][0], s=100, c="w")


    # average position of screenchange
    # avgPosScreenChangeZ.append(df["bike_pos_z"][screenchange[1]])
    # avgPosScreenChangeX.append(df["bike_pos_x"][screenchange[1]])

# Truck boundaries
# ax[1].add_patch(Rectangle((-470.2758, 47.96329 - 2.36665), 8.3, 2.36665, fill=False, linewidth=3))
# ----------

# ax[1].scatter(np.mean(avgPosScreenChangeZ),np.mean(avgPosScreenChangeX), color="w", s=100)
ax[1].legend()
ax[1].set_aspect('equal', adjustable='box')

if config["scenarios"][scenID]["invertY"]:
    ax[1].invert_yaxis()
if config["scenarios"][scenID]["invertX"]:
    ax[1].invert_xaxis()

#ax[0].invert_xaxis()
# ax[0].legend()
# ax[0].set_ylim([1,5])
# plt.xlim([-425,-500])


# print(answerEndangerment)
plt.show()
