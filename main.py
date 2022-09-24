import json
import requests
import os
from datetime import date as dt


def get_files(imgDirectory):
    """Gets all the files in your desired folder. These files should be the photos/files of the receipts.

    Args:
        imgDirectory (str):

    Returns:
        list: list of filenames
    """
    # list file and directories
    res = os.listdir(imgDirectory)
    print("Files: ", res)
    return res


def ocr(fileName, outputName):
    """Reads a receipt file and saves the data into a json file

    Args:
        fileName (str): filename of the receipt (,jpg, .png ,...)
        outputName (str): name of the desired json file
    """
    url = "https://ocr.asprise.com/api/v1/receipt"

    res = requests.post(
        url,
        data={"api_key": "TEST", "recognizer": "auto", "ref_no": "oct_python_123"},
        files={"file": open(fileName, "rb")},
    )

    with open(outputName, "w") as f:
        json.dump(json.loads(res.text), f)


def rw_to_file(output_, output_path_full):
    """Reads the json data, and outputs the item names and prices into a tab delimited file for further use.

    Args:
        output_ (str): name of the json file (output of the previous ocr function)
        output_path_full (str): full datapath for the tab delimited file
    """
    with open(output_, "r") as f:
        data = json.load(f)

    date = data["receipts"][0]["date"]
    items = data["receipts"][0]["items"]

    item_list = [item["description"] for item in items]
    amounts = [item["amount"] for item in items]

    pantti = [i for i, s in enumerate(item_list) if "pantti" in s.lower()]

    for i in pantti:
        amounts[i - 1] = amounts[i - 1] + amounts[i]
        del item_list[i]
    for i in pantti:
        del amounts[i]

    with open(output_path_full, "w") as f:
        for i, item in enumerate(item_list):
            f.write(
                "\t".join((str(date), str(item), str(amounts[i]).replace(".", ",")))
                + "\n"
            )

    today_str = dt.today().strftime("%y-%m-%d")
    with open(
        output_path_full.split("/")[0] + "/" + today_str + " receipt_full.txt", "a"
    ) as f_full:
        for i, item in enumerate(item_list):
            f_full.write(
                "\t".join((str(date), str(item), str(amounts[i]).replace(".", ",")))
                + "\n"
            )


def main_(inputDir, outputDir):
    inputFileNames = get_files(path_to_data)

    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    for file in inputFileNames:
        fileName_wout_ext = os.path.splitext(file)[0]
        json_out = outputFolder + fileName_wout_ext + ".json"
        tab_out = outputFolder + fileName_wout_ext + ".txt"
        ocr(path_to_data + file, json_out)
        rw_to_file(json_out, tab_out)


if __name__ == "__main__":

    path_to_data = "data/"
    outputFolder = "output/"

    main_(path_to_data, outputFolder)
