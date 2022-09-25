import json
import os
import sys
from datetime import date as dt

import requests


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
        fileName (str): filename of the receipt (jpg, .png ,...)
        outputName (str): name of the desired json file
    """
    url = "https://ocr.asprise.com/api/v1/receipt"

    # Make a request to the ASPRISE OCR API
    # Note, there are limited number of requests for the test user per day.
    res = requests.post(
        url,
        data={"api_key": "TEST", "recognizer": "auto", "ref_no": "oct_python_123"},
        files={"file": open(fileName, "rb")},
    )
    # Error checking for API call daily quota (free test version in use here)
    if "Daily quota exceeded" not in res.text:
        # Dump the resulting data into a json file
        with open(outputName, "w") as f:
            json.dump(json.loads(res.text), f)
        return 1
    else:
        print("Error in OCR: ", res.text)
        return 0


def rw_to_file(output_, output_path_full):
    """Reads the json data, and outputs the item names and prices into a tab delimited file for further use.

    Args:
        output_ (str): name of the json file (output of the previous ocr function)
        output_path_full (str): full datapath for the tab delimited file
    """

    # Read the json file associated with the filename
    with open(output_, "r") as f:
        data = json.load(f)

    # Take the items and costs
    date = data["receipts"][0]["date"]
    items = data["receipts"][0]["items"]
    item_list = [item["description"] for item in items]
    amounts = [item["amount"] for item in items]

    # In Europe/Finland, we have the pant system for beverages.
    # This combines the beverage price and pant into one element
    pantti = [i for i, s in enumerate(item_list) if "pantti" in s.lower()]

    for i in pantti:
        amounts[i - 1] = amounts[i - 1] + amounts[i]
        del item_list[i]
    for i in pantti:
        del amounts[i]

    # Write the output into a separate text file
    with open(output_path_full, "w") as f:
        for i, item in enumerate(item_list):
            f.write(
                "\t".join((str(date), str(item), str(amounts[i]).replace(".", ",")))
                + "\n"
            )

    # Add the file into a "full" text file, with all the other files in the input directory
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
    """Main driver function for the whole code

    Args:
        inputDir (str): name of the input folder containing the photos of the receipts
        outputDir (str): name of the desired output folder. If no folder with this name exists, creates a new folder.
    """
    inputFileNames = get_files(inputDir)

    # Create new folder if output folder not found
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # Loop over the filenames
    for file in inputFileNames:
        # Use same filename as the original, without the .png/.jpg/.pdf extension
        fileName_wout_ext = os.path.splitext(file)[0]

        json_out = outputDir + fileName_wout_ext + ".json"
        tab_out = outputDir + fileName_wout_ext + ".txt"

        # OCR API call and save to json file
        OK = ocr(inputDir + file, json_out)

        # OCR API quota exceeded, break
        if not OK:
            print("Stopping code run. Daily quota exceed for OCR API calls.")
            break

        # Write to text files
        rw_to_file(json_out, tab_out)


if __name__ == "__main__":

    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    main_(inputDir, outputDir)
