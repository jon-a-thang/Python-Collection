"""
Filename:
    PDF_Processor.py

Description:
    This script allows the user to easily process PDF documents.
    First, the script will process the PDF file by attempting to convert the PDF file to an HTML. IF the HTML
    file contains strings, then it will continue to promptly extract different data-types from the downloaded files.
    These data-types can include the Carrier, Policy Number, Policy Term, Policy Type, Document Type, and etc.
    If the converted HTML files do not contain any text, those files are images and goes through an OCR Library
    in order to obtain the data-types discussed above.
    Upon completing the processing process, the file is renamed to contain the Document Type and the Policy Number
    and the file is then moved to a directory where the rest of the "Fully Processed Files" are located. If at this
    point, the script was not able to properly extract a proper policy number or get a MISC document type, then
    those "Not Fully Processed" files will be moved to their own directory.

    This script will also create output files and store the information of which files were completely processed
    and which files weren't completely processed.

Author(s):
    Jonathan Jang
"""


import csv
import os
import re
import shutil
from datetime import datetime
from dateparser.search import search_dates
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import enchant
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\location_here\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'


# Master List 1
Category_dict_1 = {
    "key_1" : ["value_1", "value_2", "value_3"],
    "key_2" : ["value_1", "value_2", "value_3"],
    "key_3" : ["value_1", "value_2", "value_3"]
}
# Master List 2
Category_dict_2 = {
    "key_1" : ["value_1", "value_2", "value_3"],
    "key_2" : ["value_1", "value_2", "value_3"],
    "key_3" : ["value_1", "value_2", "value_3"]
}
# Master List 3
Category_dict_3 = {
    "key_1" : ["value_1", "value_2", "value_3"],
    "key_2" : ["value_1", "value_2", "value_3"],
    "key_3" : ["value_1", "value_2", "value_3"]
}


def get_filenames(file_path):
    """
    get_filenames is a function that will get and return a list of filenames of PDFs from the directory that the
    user of this script is working in.

    :param file_path: str
        The file-path of the working directory

    :return: list
        a list of strings that has the name of each PDF file in each index
    """
    list_a = []
    os.chdir(file_path)
    for filename in os.listdir():
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            list_a.append(filename)
    return list_a


def pdf_to_html(filenames_list, file_path):
    """
    pdf_to_html is a function that will use the file pdf2txt.py from the pdfminer Python Library
    in order to convert the PDF files into HTML files.

    :param filenames_list: list
        List of PDF filenames from the working directory
    :param file_path: str
        The file-path of the working directory

    :return:
        None
    """
    tmp_path = 'python C:\\PDF_Processor\\pdf2txt.py -o '
    for files in filenames_list:
        command = tmp_path + files + '.html -t html ' + file_path + files
        os.system(command)


def get_policy_num(soup, html_file, curr_ppe):
    """
    get_policy_num is a helper function of getPolicyInfoHTML()

    :param soup: bs4.BeautifulSoup
        BeautifulSoup contents containing the HTML data
    :param html_file: str
        file_path + ".html" | the string of the file that Soup currently contains
    :param curr_ppe: str
        PPE of the document that is being parsed through at the moment

    :return:
        policy_number : str
            The policy number as a string back to the function that get_policy_num gets called by
        identifiers : str
            The identifier as a string back to the function that get_policy_num gets called by
    """
    if (soup.find(string=re.compile("[(]cid[:][0-9]")) and curr_ppe == "LIBERTY MUTUAL") or \
            (soup.find(string=re.compile("[(]CID[:][0-9]")) and curr_ppe == "LIBERTY MUTUAL"):
        tmp_filepath = html_file.replace(".html", "")
        readfile = open(tmp_filepath, 'rb')
        read_pdf = PyPDF2.PdfFileReader(readfile, strict=False)
        page_text = ""
        for i in range(read_pdf.numPages):
            if i < 16:
                page_text += read_pdf.getPage(i).extractText().replace("\n", " ")
            break
        readfile.close()
        find_items = ["BLS [(][0-9][0-9][)] [0-9][0-9] [0-9][0-9] [0-9][0-9] [0-9][0-9]",
                      "BZS [(][0-9][0-9][)] [0-9][0-9] [0-9][0-9] [0-9][0-9] [0-9][0-9]"]
        for eachFindItem in find_items:
            if re.findall(eachFindItem, page_text) != []:
                return re.findall(eachFindItem, page_text)[0], eachFindItem
    else:
        tmp_list = policyNumDict[curr_ppe]
        for identifiers in tmp_list:
            search_item = soup.find(string=re.compile(identifiers))
            if search_item is not None:
                if len(search_item.strip()) >= 20:
                    eng_word = enchant.Dict('en_US')
                    # Special Case for 680 in Travelers
                    if identifiers == policyNumDict["TRAVELERS"][0] or identifiers == \
                            policyNumDict["THE TRAVELERS INDEMNITY COMPANY"][0]:
                        return re.findall(identifiers, search_item.strip())[0], identifiers
                    # Special Case for Travelers
                    if curr_ppe == "TRAVELERS" or curr_ppe == "THE TRAVELERS INDEMNITY COMPANY":
                        if ":" in search_item:
                            new_search = search_item.strip().split(":")
                            # print(newSearch[1].strip())
                            return new_search[1].strip(), identifiers
                    if curr_ppe == "CNA" and ":" in search_item:
                        new_search = search_item.strip().split(":")
                        # print(newSearch[1].strip())
                        return new_search[1].strip(), identifiers
                    for each in search_item.strip().split():
                        if each == identifiers:
                            break
                        if re.search(identifiers, each):
                            each = re.sub('[:.-]', '', each)
                            each_filter = each.replace("-", "").replace(" ", "")
                            identifiersFilter = identifiers.replace("-", "").replace(" ", "")
                            if each != '' and each_filter != identifiersFilter:
                                if eng_word.check(each) is False:
                                    if re.search('[0-9]/[0-9][0-9][0-9][0-9]', each) is None:
                                        return each, identifiers
                                if each.isdigit():
                                    return each, identifiers
                    if re.search(identifiers, search_item) is not None:
                        x, y = re.search(identifiers, search_item).span()
                        return search_item[x:y], identifiers
                else:
                    policyNumTerms = ["NO"]
                    refNum = re.sub('[:.-]', '', search_item.strip().upper())
                    for each in refNum.split():
                        for terms in policyNumTerms:
                            if each == terms:
                                return refNum.replace(each, '').strip(), identifiers
                return search_item.strip(), identifiers


def policy_num_digit_check(text_extract, policy_num, identifier):
    """
    policy_num_digit_check is a helper function that is used to check policy numbers that only contain numbers.
    This will ensure that the policy number outputted will be the same length as the identifier which will provide
    a more robust system at determining and finding the policy numbers from a PDF file.

    :param text_extract: str
        The extracted text from the PDF file
    :param policy_num: str
        The policy number that needs to be checked
    :param identifier: str
        the string used as an identifier for the re.search() & re.findall() functions

    :return: str
        Either will return the same policy number or an updated number that is more closer to the real policy number
    """
    found_list = re.findall(identifier, text_extract)
    for each in found_list:
        search_item = re.search(each, text_extract)
        possible_nums = text_extract[search_item.span()[0]: search_item.span()[1] + 10]
        if len(possible_nums.split()[0]) == len(found_list[0]):
            return possible_nums.split()[0]
    return policy_num


def get_policy_info_html(html_file, curr_ppe, text_extract):
    """
    get_policy_info_html is a function that will open a BeautifulSoup instance and call upon the helper
    function getPolicyNum() to extract the policy number from the PDF file

    :param html_file: str
        file_path + ".html" | the string of the file that Soup currently contains
    :param curr_ppe: str
        PPE of the document that is being parsed through at the moment
    :param text_extract: str
        The extracted text from the PDF file

    :return: str
        The policy number as a string
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        policy_num, identifier = get_policy_num(soup, html_file, curr_ppe)
        if policy_num.isdigit():
            policy_num = policy_num_digit_check(text_extract, policy_num, identifier)
        return policy_num


def get_policy_num_image(text_extract, curr_ppe):
    """
    get_policy_num_image is a function that will extract the policy number from a PDF file that contains images.

    :param text_extract: str
        The extracted text from the PDF file
    :param curr_ppe: str
        PPE of the document that is being parsed through at the moment

    :return: str
        The policy number as a string
    """
    # Special UTICA FIRST case
    if curr_ppe == "UTICA FIRST" and re.search("SOP [0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]", text_extract):
        tempNum = re.findall("SOP [0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]", text_extract)[0]
        return re.sub("SOP", "BOP", tempNum)
    if curr_ppe == "UTICA FIRST" and re.search("BOP:[0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]", text_extract):
        tempNum = re.findall("BOP:[0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]", text_extract)[0]
        return re.sub("BOP:", "BOP ", tempNum)
    # Special AMTRUST case
    temp_text_extract = re.sub(" +", "", text_extract)
    if curr_ppe == "AMTRUST NORTH AMERICA" and re.search("[$]WC[0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]",
                                                         temp_text_extract):
        tempNum = re.findall("[$]WC[0-9][0-9][0-9][0-9][0-9][0-9][0-9] [0-9][0-9]", temp_text_extract)[0]
        return re.sub("[$]WC", "SWC", tempNum)
    if curr_ppe == "AMTRUST NORTH AMERICA" and re.search("[$]WC[0-9][0-9][0-9][0-9][0-9][0-9][0-9]", temp_text_extract):
        tempNum = re.findall("[$]WC[0-9][0-9][0-9][0-9][0-9][0-9][0-9]", temp_text_extract)[0]
        return re.sub("[$]WC", "SWC", tempNum)
    if (curr_ppe == "TRAVELERS" and
            re.search("BME[0-9] -[0-9][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9][0-9] [0-9]-TIL-[0-9][0-9]", text_extract)):
        tempNum = re.findall("BME[0-9] -[0-9][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9][0-9] [0-9]-TIL-[0-9][0-9]",
                             text_extract)[0]
        tempNum = re.sub(" +", "", tempNum)
        tempNum2 = ""
        for i in range(len(tempNum)):
            if i != 7:
                tempNum2 += tempNum[i]
        return tempNum2
    if (curr_ppe == "THE TRAVELERS INDEMNITY COMPANY" and
            re.search("BME[0-9] -[0-9][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9][0-9] [0-9]-TIL-[0-9][0-9]", text_extract)):
        tempNum = re.findall("BME[0-9] -[0-9][a-zA-Z][a-zA-Z][0-9][0-9][0-9][0-9][0-9] [0-9]-TIL-[0-9][0-9]",
                             text_extract)[0]
        tempNum = re.sub(" +", "", tempNum)
        tempNum2 = ""
        for i in range(len(tempNum)):
            if i != 7:
                tempNum2 += tempNum[i]
        return tempNum2
    if curr_ppe == "ATTUNE" and re.search("INTUAI[0-9][0-9][0-9][0-9][0-9]HIBP[-]", text_extract):
        if re.search("[0-9][0-9][0-9][0-9][0-9][-][0-9][0-9]", text_extract) is not None:
            part1 = re.search("INTUAI[0-9][0-9][0-9][0-9][0-9]HIBP[-]", text_extract)[0]
            part2 = re.search("[0-9][0-9][0-9][0-9][0-9][-][0-9][0-9]", text_extract)[0]
            return part1 + part2
    listToParse = policyNumDict[curr_ppe]
    for eachVal in listToParse:
        if re.search(eachVal, text_extract):
            return re.findall(eachVal, text_extract)[0]


def get_policy_term(text_extract, file, curr_ppe):
    """
    get_policy_term is a function that will extract the policy term's dates from a PDF file

    :param text_extract: str
        The extracted text from the PDF file
    :param file: str
        The PDF file's name without the location/path
    :param curr_ppe: str
        PPE of the document that is being parsed through at the moment

    :return: list
        The policy term as a string list with the EFF date in index 0 and EXP date in index 1
    """
    termDict = {}
    # Special case for Progressive b/c date format is ex. Oct 15, 2021
    if curr_ppe == "PROGRESSIVE":
        dateFormat = "[0-9], [0-9][0-9][0-9][0-9]"
        text_extract = re.sub('[(%$:/@.)<>=;?]', ' ', text_extract.strip())
        for eachLine in text_extract.split("\n"):
            if not re.sub(' +', '', eachLine).isdigit():
                if re.search(dateFormat, eachLine):
                    if search_dates(eachLine) is not None:
                        # For special progressive case
                        patternList = ["[0-9][0-9][0-9][0-9]  -  [a-zA-z][a-zA-z][a-zA-z]",
                                       "[0-9][0-9][0-9][0-9] - [a-zA-z][a-zA-z][a-zA-z]"]
                        for pattern in patternList:
                            # successfully runs when the progressive document contains the patterns above
                            if re.search(pattern, eachLine) is not None:
                                parsedDates = eachLine.split("-")
                                effDate = parsedDates[0].strip().split()[-3:]
                                expDate = parsedDates[1].strip().split()[:3]
                                return [" ".join(effDate), " ".join(expDate)]
                        # For Special Case within Progressive with a line having a phone number along
                        # with the date format
                        eachLine = re.sub("[0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", "", eachLine)
                        for elements in search_dates(eachLine):
                            if re.search(dateFormat, elements[0]) is not None:
                                key = elements[1].strftime('%m/%d/%y')
                                if key in termDict:
                                    termDict[key] = termDict[key] + 1
                                else:
                                    termDict[key] = 1
    else:
        # termDict = {}
        dateFormatList = ["[0-9]/[0-9]/[0-9][0-9]", "[0-9]/[0-9][0-9]/[0-9][0-9]", "[0-9]-[0-9]-[0-9][0-9]",
                          "[0-9]-[0-9][0-9]-[0-9][0-9]"]
        for each in text_extract.split():
            each = re.sub('[a-zA-Z(%$;:@,.)]', '', each)
            if each != "":
                # Special Case for when date is ##/##/####-##/##/####
                if "/" in each and "-" in each:
                    if len(each.split("-")) == 2:
                        for item in each.split("-"):
                            if search_dates(item) is not None:
                                for dateFormat in dateFormatList:
                                    if re.search(dateFormat, item) is not None:
                                        if each in termDict:
                                            termDict[item] = termDict[item] + 1
                                        else:
                                            termDict[item] = 1
                    if len(each.split("/")) == 2:
                        for item in each.split("/"):
                            if search_dates(item) is not None:
                                for dateFormat in dateFormatList:
                                    if re.search(dateFormat, item) is not None:
                                        if each in termDict:
                                            termDict[item] = termDict[item] + 1
                                        else:
                                            termDict[item] = 1
                if search_dates(each) is not None:
                    for dateFormat in dateFormatList:
                        if re.search(dateFormat, each) is not None:
                            if each in termDict:
                                termDict[each] = termDict[each] + 1
                            else:
                                termDict[each] = 1
    if len(termDict) != 0:
        tmpVal = 0
        tmpKey = ""
        for date, count in termDict.items():
            if tmpVal < count:
                tmpVal = count
                tmpKey = date
        termDict.pop(tmpKey)
        if len(re.split('[/-]', tmpKey)) == 3:
            d1, m1, y1 = re.split('[/-]', tmpKey)
            for date in termDict.keys():
                if len(re.split('[/-]', date)) == 3:
                    d2, m2, y2 = re.split('[/-]', date)
                    if d1 == d2 and m1 == m2 and int(y2) - int(y1) == 1:
                        return [tmpKey, date]
                    elif d1 == d2 and m1 == m2 and int(y1) - int(y2) == 1:
                        return [date, tmpKey]
                    else:
                        continue
    for checkDate in termDict.keys():
        if len(re.split('[/-]', checkDate)) == 3:
            d1, m1, y1 = re.split('[/-]', checkDate)
            for valDate in termDict.keys():
                if len(re.split('[/-]', valDate)) == 3:
                    d2, m2, y2 = re.split('[/-]', valDate)
                    if d1 == d2 and m1 == m2 and int(y2) - int(y1) == 1:
                        return [checkDate, valDate]
                    elif d1 == d2 and m1 == m2 and int(y1) - int(y2) == 1:
                        return [valDate, checkDate]
                    else:
                        continue

    # IF CIDs ARE EXISTENT
    if re.search("[(]CID[:][0-9]", text_extract) is not None or re.search("[(]cid[:][0-9]", text_extract) is not None:
        readFile = open(file, 'rb')
        readPDF = PyPDF2.PdfFileReader(readFile, strict=False)
        pageText = ""
        for i in range(readPDF.numPages):
            if i < 16:
                pageText += readPDF.getPage(i).extractText().replace("\n", " ")
            break
        readFile.close()

        tmpDates = {}
        for each in pageText.split():
            each = re.sub('[a-zA-Z(%$:@,.)]', '', each)
            if each != "":
                if search_dates(each) is not None:
                    dateFormatList = ["[0-9]/[0-9]/[0-9][0-9]", "[0-9]/[0-9][0-9]/[0-9][0-9]", "[0-9]-[0-9]-[0-9][0-9]",
                                      "[0-9]-[0-9][0-9]-[0-9][0-9]"]
                    for dateFormat in dateFormatList:
                        if re.search(dateFormat, each) is not None:
                            if each in tmpDates:
                                tmpDates[each] = tmpDates[each] + 1
                            else:
                                tmpDates[each] = 1
        # print(tmpDates)
        for checkDate in tmpDates.keys():
            if len(re.split('[/-]', checkDate)) == 3:
                d1, m1, y1 = re.split('[/-]', checkDate)
                for valDate in tmpDates.keys():
                    if len(re.split('[/-]', valDate)) == 3:
                        d2, m2, y2 = re.split('[/-]', valDate)
                        if d1 == d2 and m1 == m2 and int(y2) - int(y1) == 1:
                            return [checkDate, valDate]
                        elif d1 == d2 and m1 == m2 and int(y1) - int(y2) == 1:
                            return [valDate, checkDate]
                        else:
                            continue

    # IF ONLY LOOKING FOR DATES ISN'T WORKING [SEARCH BY SPECIFIC KEY WORDS AND PATTERNS]
    datePattern = ["[0-9][0-9] TO [0-9]", "EFFECTIVE DATE OF POLICY [0-9]", "EFFECTIVE ON [0-9]", "EXPIRES ON [0-9]"]
    for pattern in datePattern:
        if pattern == "[0-9][0-9] TO [0-9]":
            text_extract = re.sub(":", "", text_extract)
        found = re.search(pattern, text_extract)
        if found is not None:

            parsedDates = text_extract[found.span()[0] - 10: found.span()[1] + 10].split()

            if pattern != datePattern[0] and "EFFECT" in pattern:
                # Special case for when converting from image for Amtrust; ex: RE-SWC1262924.pdf
                if pattern == datePattern[3]:
                    useSTR = ""
                    for i in range(len(text_extract.split("\n"))):
                        if pattern in text_extract.split("\n")[i]:
                            useSTR = text_extract.split("\n")[i + 1]
                            break
                    datesList = search_dates(useSTR)
                    if datesList is not None:
                        for date in datesList:
                            dateFormatList = ["[0-9]/[0-9]/[0-9][0-9]", "[0-9]/[0-9][0-9]/[0-9][0-9]",
                                              "[0-9]-[0-9]-[0-9][0-9]", "[0-9]-[0-9][0-9]-[0-9][0-9]"]
                            for each_format in dateFormatList:
                                if re.search(each_format, date[0]) is not None:
                                    return date[0]
                # Only has an effective date
                id_of_index = 0
                for eachDate in parsedDates:
                    if pattern.split()[-2] == eachDate:
                        id_of_index = parsedDates.index(eachDate)
                return [parsedDates[id_of_index + 1], ""]
            elif pattern != datePattern[0] and "EXPIR" in pattern:
                id_of_index = 0
                for eachDate in parsedDates:
                    if pattern.split()[-2] == eachDate:
                        id_of_index = parsedDates.index(eachDate)
                return ["", parsedDates[id_of_index + 1]]
            else:
                termDates = []
                for eachDate in parsedDates:
                    if re.search("[0-9][/-][0-9][0-9]", eachDate) is not None:
                        termDates.append(eachDate)
                if termDates != []:
                    return termDates[0], termDates[1]

    # Special case for when and if there are date formats with words
    text_extract = re.sub('[(%$:/@.)<>=;?]', ' ', text_extract.strip())
    for eachLine in text_extract.split("\n"):
        if not re.sub(' +', '', eachLine).isdigit():
            if re.search("[0-9], [0-9][0-9][0-9][0-9]", eachLine):
                if search_dates(eachLine) is not None:
                    currLine = re.sub(" +", "", eachLine)
                    patternList = ["[0-9][0-9][0-9][0-9]  -  [a-zA-z][a-zA-z][a-zA-z]",
                                   "[0-9][0-9][0-9][0-9] - [a-zA-z][a-zA-z][a-zA-z]",
                                   "[0-9][0-9][0-9][0-9]  TO  [a-zA-z][a-zA-z][a-zA-z]",
                                   "[0-9][0-9][0-9][0-9] TO [a-zA-z][a-zA-z][a-zA-z]"]
                    for i in range(len(patternList)):
                        # successfully runs when the progressive document contains the patterns above
                        if re.search(patternList[i], currLine) is not None:
                            parsedDates = eachLine.split("-")
                            effDate = parsedDates[0].strip().split()[-3:]
                            expDate = parsedDates[1].strip().split()[:3]
                            return [" ".join(effDate), " ".join(expDate)]

    return []


def get_policy_type_two(text_extract, pol_type_list):
    """
    get_policy_type_two is a helper function of getPolicyType()

    :param text_extract: str
        The extracted text from the PDF file
    :param pol_type_list: list
        Master list of the different types of policy types

    :return: str
        Master list of the different types of policy types
    """
    textExtract = re.sub(r'([^a-zA-Z\s]+?)', '', text_extract)
    newExtract = " ".join(textExtract.split())
    # print(newExtract)
    if "COMMERCIAL FIRE GENERAL LIABILITY" in newExtract:
        # print(f"{file} :: Policy Type: COMMERCIAL FIRE GENERAL LIABILITY")
        return "COMMERCIAL FIRE GENERAL LIABILITY"

    elif "PROFESSIONAL LIABILITY" in newExtract or "GENERAL LIABILITY" in newExtract:
        tmpDict = {}
        liabilityList = ["COMMERCIALGENERALLIABILITY", "PROFESSIONALLIABILITY", "GENERALLIABILITYOCCURRENCE"]
        presentList = ["COMMERCIAL GENERAL LIABILITY", "PROFESSIONAL LIABILITY", "GENERAL LIABILITY OCCURRENCE"]
        for liabilityType in liabilityList:
            liabilitySearch = re.findall(liabilityType, newExtract.replace(" ", ""))
            if liabilitySearch != []:
                tmpDict[liabilitySearch[0]] = len(liabilitySearch)
        # Special case for progressive auto coverage
        if "COMMERCIAL AUTO" in newExtract and "AUTO COVERAGE" in newExtract:
            return "COMMERCIAL AUTO"
        if len(tmpDict) == 1:
            liabilityType, count = list(tmpDict.items())[0]
            for items in liabilityList:
                if items == liabilityType:
                    return presentList[liabilityList.index(items)]
        elif len(tmpDict) == 2:
            tmpCount = 0
            for key_type, count in tmpDict.items():
                if count > tmpCount:
                    tmpCount = count
            result = list(tmpDict.keys())[list(tmpDict.values()).index(tmpCount)]

            for items in liabilityList:
                if items == result:
                    return presentList[liabilityList.index(items)]
            return result
        else:
            for eachID in pol_type_list:
                found = re.search(eachID, newExtract)
                if found is not None:
                    polTypeList = newExtract[found.span()[0]: found.span()[1]]
                    return polTypeList
            return "DNE"
    else:
        for eachID in pol_type_list:
            found = re.search(eachID, newExtract)
            if found is not None:
                polTypeList = newExtract[found.span()[0]: found.span()[1]]
                return polTypeList
        return "DNE"


def get_policy_type(curr_pol_num, text_extract):
    """
    get_policy_type is a function that will extract the policy type from the extracted text and call upon the helper
    function getPolicyTypeTwo() in order to grab the policy type if it can be found within the file.

    :param curr_pol_num: str
        The current policy number that is from the current file that is being worked on
    :param text_extract: str
        The extracted text from the PDF file

    :return: str
        The policy type as a string
    """
    pol_type_list = ["WORKER'S COMPENSATION AND EMPLOYER'S LIABILITY",
                     "BUSINESSOWNER", "BUSINESS OWNERS POLICY", "COMMERCIAL AUTO", "AUTO INSURANCE",
                     "DWELLING FIRE POLICY", "HOMEOWNERS POLICY", "WORKERS COMPENSATION", "COMMERCIAL PACKAGE",
                     "COMMERCIAL LINES INSURANCE POLICY", "EMPLOYMENT PRACTICES LIABILITY", "LANDLORD POLICY",
                     "COMMERCIAL LIABILITY", "UMBRELLA LIABILITY", "DWELLING POLICY", "CNA CONNECT", "FLOOD"]
    if curr_pol_num is not None:
        if "WC" in curr_pol_num or "UB" in curr_pol_num or "WECA" in curr_pol_num:
            return "WORKERS COMPENSATION"
        if "BOP" in curr_pol_num:
            return "BUSINESS OWNERS POLICY"
        if "HOP" in curr_pol_num:
            return "HOME"
        if "BLS" in curr_pol_num:
            return "COMMERCIAL GENERAL LIABILITY"
        if "CPP" in text_extract and "TYPE OF POLICY" in text_extract and "CP" in curr_pol_num:
            return "COMMERCIAL PACKAGE"
        if "UMBRELLA LIABILITY OCCURRENCE" in text_extract \
                and "TYPE OF POLICY" in text_extract \
                and "UM" in curr_pol_num:
            return "UMBRELLA LIABILITY OCCURRENCE"
        if "ULC" in curr_pol_num and "YOUR UMBRELLA" in text_extract:
            return "UMBRELLA"
        if "DP" in curr_pol_num and "DWELLING POLICY" in text_extract:
            return "DWELLING POLICY"
        if "CNA CONNECT" in text_extract and curr_pol_num.isdigit():
            return "CNA CONNECT"
        if "WFL" in text_extract and "FLD  RGLR" in text_extract:
            return "FLOOD"
        if "BOP" in text_extract and "BUSINESS OWNERS" in text_extract:
            return "BUSINESS OWNERS POLICY"
        return get_policy_type_two(text_extract, pol_type_list)
    else:
        return get_policy_type_two(text_extract, pol_type_list)


def get_carrier(text_extract):
    """
    get_carrier is a function that will extract the carrier (ICO) if it is found from the extracted text

    :param text_extract: str
        The extracted text from the PDF file

    :return: str
        The carrier (ICO) as a string
    """
    tmpDict = {}
    for carrierList in PPE_CarrierDict.values():
        for eachCarrier in carrierList:
            if eachCarrier.upper() in text_extract:
                count = text_extract.count(eachCarrier.upper())
                tmpDict[eachCarrier.upper()] = count
    # DUPLICATE KEY CHECK
    if len(tmpDict) > 1:
        tmpKey = ""
        for key, value in tmpDict.items():
            # "UTICA FIRST" is there because of a special case with UTICA FIRST doc having "THE HARTFORD"
            if key in PPE_CarrierDict.keys() and "UTICA FIRST" != key:
                tmpKey = key
        if tmpKey != "":
            tmpDict.pop(tmpKey)

    # VALUES CHECK
    tmpValue = 0
    tmpCarrier = ""

    for key, value in tmpDict.items():
        if value >= tmpValue:
            tmpValue = value
            tmpCarrier = key

    # Special Case for Employers Insurance -- PPE: EMPLOYERS INSURANCE COMPANY OF NEVADA vs CHUBB
    if tmpCarrier == "EMPLOYERS INSURANCE":
        for key, value in tmpDict.items():
            if "EMPLOYERS INSURANCE" in key and len(key) > 19:
                tmpCarrier = key

    # special case because of the employers in two PPEs
    # if employers is in the dict and there are multiple occurrences then take the longer name of the two
    # else do the normal thing as in the for loop above? or just continue along

    if tmpCarrier == '':
        tmpCarrier = "UNKNOWN OR DNE"
    # Special CNA case
    if tmpCarrier == "WWW.CNA.COM" or tmpCarrier == "151 N FRANKLIN" or \
            tmpCarrier == "151 N. FRANKLIN ST." or tmpCarrier == "CHICAGO, IL 60606":
        tmpCarrier = "CNA"
    # Special USLI case
    if tmpCarrier == "WWW.USLI.COM":
        tmpCarrier = "USLI"
    # Special DB case
    if tmpCarrier == "1010 NORTHERN BLVD, SUITE 238":
        tmpCarrier = "DB INSURANCE"
    # Special Amtrust case
    if tmpCarrier == "WWW.AMTRUSTGROUP.COM" \
            or tmpCarrier == "800 SUPERIOR AVENUE EAST, 21ST FLOOR" \
            or tmpCarrier == "CLEVELAND, OH 44114" \
            or tmpCarrier == "AMTTRUST NORTH AMERICA" \
            or tmpCarrier == "AN AMTRUST FINANCIAL COMPANY" \
            or tmpCarrier == "WESCO INSURANCE COMPAHY":
        tmpCarrier = "AMTRUST NORTH AMERICA"
    if tmpCarrier == "P.O. BOX 851, UTICA, N.Y." or tmpCarrier == "BOX 851, UTICA, NY":
        tmpCarrier = "UTICA FIRST"
    if tmpCarrier == "PHLY.COM":
        tmpCarrier = "PHILADELPHIA INSURANCE COMPANIES"
    return tmpCarrier


def get_doc_type(text_extract):
    """
    get_doc_type is a function that will find the document type of the PDF file from the extracted text.
    If the document type cannot be found or if it truly does not have a document type, CNF_DocType will be returned.

    :param text_extract: str
        The extracted text from the PDF file

    :return: str
        The document type as a string
    """
    textExtract = text_extract.strip().replace("\n", " ")
    textExtract = re.sub(' +', ' ', textExtract)
    for key_type, identifiers in docTypeDict.items():
        for each in identifiers:
            if "," in each:
                first, second = each.split(",")
                if first in textExtract and second in textExtract:
                    if key_type == "CANN-CAME" and "NOTICE OF REINSTATEMENT" in textExtract:
                        for activeTmp in docTypeDict["RNST"]:
                            first, second = activeTmp.split(",")
                            if first in textExtract and second in textExtract:
                                # print(activeTmp, "RNST")
                                return "RNST"
                    print(each, key_type)
                    return key_type
            if each in textExtract:
                if key_type == "BILL" and "RESCISSION NOTICE" in textExtract:
                    for activeTmp in docTypeDict["RNST"]:
                        first, second = activeTmp.split(",")
                        if first in textExtract and second in textExtract:
                            # print(activeTmp, "RNST")
                            return "RNST"
                print(each, key_type)
                return key_type


def secondary_get_doc_type(file):
    """
    secondary_get_doc_type is a function that will find the document type of the PDF file by using a different
    Python Library. If the document type cannot be found or if it truly does not have a document type, CNF_DocType will
    be returned.

    :param file: str
        The PDF file's name without the location/path

    :return: str
        The document type as a string
    """
    readFile = open(file, 'rb')
    readPDF = PyPDF2.PdfFileReader(readFile, strict=False)
    extractSTR = ""
    for i in range(readPDF.numPages):
        if i < 21:
            extractSTR += readPDF.getPage(i).extractText().replace("\n", " ")
        break
    readFile.close()
    # print(f"\t\t{extractSTR}")
    for key_type, identifiers in docTypeDict.items():
        for each in identifiers:
            each = re.sub(" ", "", each)
            if "," in each:
                first, second = each.split(",")
                if first in extractSTR and second in extractSTR:
                    if key_type == "CANN-CAME" and "NOTICE OF REINSTATEMENT" in extractSTR:
                        for activeTmp in docTypeDict["RNST"]:
                            first, second = activeTmp.split(",")
                            if first in extractSTR and second in extractSTR:
                                print(activeTmp, "RNST")
                                return "RNST"
                    print(each, key_type)
                    return key_type
            if each in extractSTR:
                if key_type == "BILL" and "RESCISSION NOTICE" in extractSTR:
                    for activeTmp in docTypeDict["RNST"]:
                        first, second = activeTmp.split(",")
                        if first in extractSTR and second in extractSTR:
                            print(activeTmp, "RNST")
                            return "RNST"
                print(each, key_type)
                return key_type


def data_pdf_miner():
    """
    data_pdf_miner is the main function for the script.

    :return:
        None
    """
    file_path = input("Enter folder location of files to be processed:\n"
                      "(ex: C:\\Users\\username\\Desktop\\FolderName)\n\t")
    while not os.path.exists(file_path):
        print("That file path does not exist. Please enter an existing location.\n")
        file_path = input("Enter folder location of files to be processed:\n"
                          "(ex: C:\\Users\\username\\Desktop\\FolderName)\n\t")
    file_path = file_path + "\\"

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # Replaces spaces with underscores
    for file in os.listdir(file_path):
        os.rename(file_path + file, file_path + file.replace(" ", "_"))

    # NotFullyProcessedPath = file_path + "Not_Fully_Processed\\"
    FullyProcessedPath = file_path + "Fully_Processed\\"

    # Gets a full list of files from the directory, do not need to remove the output and other directory file names
    filenames_list = get_filenames(file_path)

    # Converts PDF Files to HTML
    pdf_to_html(filenames_list, file_path)

    if not os.path.exists(FullyProcessedPath):
        os.makedirs(FullyProcessedPath)

    dataSet = {}
    f = open("000111_output.txt", 'a')
    csv_f = open("000111_extracted_CSV.csv", "a", encoding="UTF8", newline="")
    for file in filenames_list:
        print(file)
        minedData = extract_text(file_path + "\\" + file, password='', page_numbers=None,
                                 maxpages=20, caching=True, codec='utf-8', laparams=None)
        cleanMinedData = minedData.replace("\n\n", " ").strip().upper()

        # print(cleanMinedData)

        # Special Cases for when there are CIDs in text
        if "(CID:" in cleanMinedData:
            cleanMinedData = ""

        if cleanMinedData != "":
            carrierName = get_carrier(cleanMinedData)

            PPE = ""
            for PPEKeys, carrierList in PPE_CarrierDict.items():
                for eachCarrier in carrierList:
                    if eachCarrier.upper() == carrierName:
                        PPE = PPEKeys
                        break

            policyNum = get_policy_info_html(file + ".html", PPE, cleanMinedData)

            termList = get_policy_term(cleanMinedData, file, PPE)
            policyType = get_policy_type(policyNum, cleanMinedData)

            docType = get_doc_type(cleanMinedData)
            # Special case for when the extraction of text above does not extract all pages
            if docType == "CNF_DocType":
                docType = secondary_get_doc_type(file)

            print(f"{file} :: \n\tCarrier: {carrierName}\n\tPolicyNum: {policyNum}\n\tTermList: "
                  f"{termList}\n\tPolicyType: {policyType}\n\tDocType: {docType}")

            if policyNum is None or len(policyNum) > 30 or len(re.sub(" +", "", policyNum)) < 3:
                """
                Special Case for when PDF to HTML gets converted incorrectly. For the two cases seen, the html had
                each letter from the PDF be on a new line.
                
                Ex converted output of both HTML & PDFMINER:
                p
                O
                L
                I
                C
                Y
                N
                U
                M
                
                In both of the two cases, each were CNA docs. From testing files, reference:
                    - EPOL-4034682840.pdf
                    - RPOL-4018380091.pdf
                
                By checking --> if docType = "CNF_DocType" & PPE = "CNA" for when pdf
                """
                # if docType == "CNF_DocType" and PPE == "CNA":
                if PPE == "CNA":
                    carrierName, policyNum, termList, policyType, docType = image_processor(file)

                    print(f"{file} :: \n\tCarrier: {carrierName}\n\tPolicyNum: {policyNum}\n\tTermList: "
                          f"{termList}\n\tPolicyType: {policyType}\n\tDocType: {docType}")

                    # if docType != "CNF_DocType" and PPE == "CNA":
                    if PPE == "CNA":
                        new_filename = post_processing(f, file, carrierName, PPE, policyNum, termList, policyType,
                                                       docType, FullyProcessedPath, file_path)

                        # Formulating Dataset for output/export
                        if len(termList) == 2:
                            dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], termList[1],
                                             policyType, docType]
                        elif len(termList) == 1:
                            dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], "", policyType,
                                             docType]
                        elif len(termList) == 0:
                            dataSet[file] = [new_filename, carrierName, PPE, policyNum, "", "", policyType, docType]
                        else:
                            print("ERROR")
            # Else write to out file and keep going!
            else:
                new_filename = post_processing(f, file, carrierName, PPE, policyNum, termList, policyType,
                                               docType, FullyProcessedPath, file_path)

                # Formulating Dataset for output/export
                if len(termList) == 2:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], termList[1],
                                     policyType, docType]
                elif len(termList) == 1:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], "", policyType, docType]
                elif len(termList) == 0:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, "", "", policyType, docType]
                else:
                    print("ERROR")
        else:
            # If PDF is an image or contains no text that the converter cannot detect

            # PDF to JPG
            carrierName, policyNum, termList, policyType, docType = image_processor(file)

            # Grabbing the PPE
            PPE = ""
            for PPEKeys, carrierList in PPE_CarrierDict.items():
                for eachCarrier in carrierList:
                    if eachCarrier.upper() == carrierName:
                        PPE = PPEKeys
                        break

            print(f"{file} :: \n\tCarrier: {carrierName}\n\tPolicyNum: {policyNum}\n\tTermList: "
                  f"{termList}\n\tPolicyType: {policyType}\n\tDocType: {docType}")

            # If found any errors or doc is not fully processed
            if policyNum is None or len(policyNum) > 30 or len(re.sub(" +", "", policyNum)) < 3:
                f.write(f"{file} :: \n\tCarrier: {carrierName}\n\tPolicyNum: {policyNum}\n\tTermList: "
                         f"{termList}\n\tPolicyType: {policyType}\n\tDocType: {docType}\n")
                shutil.move(file_path + file, FullyProcessedPath)
            # Else write to out file and keep going!
            else:
                new_filename = post_processing(f, file, carrierName, PPE, policyNum, termList, policyType,
                                               docType, FullyProcessedPath, file_path)

                # Formulating Dataset for output/export
                if len(termList) == 2:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], termList[1],
                                     policyType, docType]
                elif len(termList) == 1:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, termList[0], "", policyType, docType]
                elif len(termList) == 0:
                    dataSet[file] = [new_filename, carrierName, PPE, policyNum, "", "", policyType, docType]
                else:
                    print("ERROR")

    print("\n----------------------------------------------------------------------------------\n")
    for i in dataSet:
        print(i)
        print(f"\t{dataSet[i]}")

    # WRITING TO CSV
    header = ["Original Filename", "New Filename", "Carrier", "PPE", "Policy Num", "Effective Date", "Expiration Date",
              "Policy Type", "DocType"]

    writer = csv.writer(csv_f)
    writer.writerow(header)
    for key, value in dataSet.items():
        value.insert(0, key)
        writer.writerow(value)

    # closing all of the files that were opened and used
    f.close()
    csv_f.close()
    print("Completed!")


def image_processor(file):
    """
    image_processor is a function that will convert the PDF to a JPG image file and then use an OCR library to
    convert the images to text.

    :param file: str
        The PDF file's name without the location/path

    :return:
        carrierName : str
            The extracted carrier from the PDF
        policyNum : str
            The extracted policy number from the PDF
        termList : list
            The extracted effective and expiration dates from the PDF
        policyType : str
            The extracted policy type from the PDF
        docType : str
            The extracted document type from the PDF
    """
    # PDF to JPG
    pagesList = convert_from_path(file)

    # Loop through save as jpg then extract text and keep going by adding output to a string
    rawFromImage = ""
    counter = 1
    for i in range(len(pagesList)):
        if counter <= 20:
            #  "_page" + str(i) +
            pagesList[i].save(file + '.jpg', 'JPEG')

            # Image to text using PIL Image & Tesseract
            im = Image.open(file + '.jpg')
            rawFromImage += pytesseract.image_to_string(im)

            counter += 1
        else:
            break

    cleanMinedData = rawFromImage.replace("\n\n", " ").strip().upper()

    # Marks the beginning of the start of processing after IMAGE -> TEXT
    carrierName = get_carrier(cleanMinedData)

    PPE = ""
    for PPEKeys, carrierList in PPE_CarrierDict.items():
        for eachCarrier in carrierList:
            if eachCarrier.upper() == carrierName:
                PPE = PPEKeys
                break
    
    # Separate processing method for extracting the policy number w/o html
    policyNum = get_policy_num_image(cleanMinedData, PPE)

    termList = get_policy_term(cleanMinedData, file, PPE)
    policyType = get_policy_type(policyNum, cleanMinedData)

    docType = get_doc_type(cleanMinedData)
    # Special case for when the extraction of text above does not extract all pages
    if docType == "CNF_DocType":
        docType = secondary_get_doc_type(file)

    return carrierName, policyNum, termList, policyType, docType


def post_processing(f, file, carrier_name, ppe, policy_num, term_list, policy_type, doc_type,
                    fully_processed_path, file_path):
    """
    post_processing is a function that will handle the post processing of the information extracted from
    the original PDFs. Including writing to a file, changing the file's name, moving the file to a new
    file location.

    :param f: io.TextIOWrapper
        The file object
    :param file: str
        The PDF file's name without the location/path
    :param carrier_name: str
        The extracted carrier name from the PDF
    :param ppe: str
        The extracted ppe from the PDF
    :param policy_num: str
        The extracted policy num from the PDF
    :param term_list: list
        The extracted effective and expiration dates from the PDF
    :param policy_type: str
        The extracted policy type from the PDF
    :param doc_type: str
        The extracted document type from the PDF
    :param fully_processed_path: str
        The location of the fully processed folder to output all the PDF files to
    :param file_path: str
        The PDF file's name with the location/path

    :return: str
        The new filename of the PDF that contains the document type and the policy number
    """
    f.write(f"{file} :: \n\tCarrier: {carrier_name}\n\tPolicyNum: {policy_num}\n\tTermList: "
            f"{term_list}\n\tPolicyType: {policy_type}\n\tDocType: {doc_type}\n")
    policyNum = re.sub(" ", "", policy_num)

    # Check to see if the doc_type directory exists
    if not os.path.exists(fully_processed_path + doc_type + "\\"):
        os.makedirs(fully_processed_path + doc_type + "\\")

    src = file_path + file
    dst = file_path + doc_type + "_" + policyNum + ".pdf"

    # Already parsing through only PDF files, so do not need a condition
    os.rename(src, dst)
    new_filename = doc_type + "_" + policyNum + ".pdf"
    # In case there are duplicates of files
    try:
        # shutil.move(dst, fully_processed_path + fnamePPE + "\\")
        shutil.move(dst, fully_processed_path + doc_type + "\\")
    except:
        c = 1
        # newDst = fully_processed_path + fnamePPE + "\\" + doc_type + "_" + policyNum + ".pdf"
        newDst = fully_processed_path + doc_type + "\\" + doc_type + "_" + policyNum + ".pdf"
        while os.path.exists(newDst):
            # newDst = fully_processed_path + fnamePPE + "\\" + doc_type + "_" + policyNum + "_" + str(c) + ".pdf"
            newDst = fully_processed_path + doc_type + "\\" + doc_type + "_" + policyNum + "_" + str(c) + ".pdf"
            new_filename = doc_type + "_" + policyNum + "_" + str(c) + ".pdf"
            c += 1
        os.rename(dst, newDst)
        try:
            # shutil.move(newDst, fully_processed_path + fnamePPE + "\\")
            shutil.move(newDst, fully_processed_path + doc_type + "\\")
        except:
            pass

    return new_filename


if __name__ == '__main__':
    data_pdf_miner()
