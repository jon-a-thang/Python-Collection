"""
Filename:
  excel_zipcode.py

Description:
  Opening and altering an excel file then writing the newly altered excel file to a new copy of the file

Author(s):
  Jonathan Jang
"""
import pandas as pd


def excel_zipcode():
  """
  excel_zipcode will open an excel file and get the data from a particular col and 
  then grab the information that it needs to find and 
  then add a new column and write the new column and the currently existing dataframe into a new excel file.
  :return:
    None
  """
  full_file_path = "C:\\Users\\JJ\\tmp_location\\no_zipcode.xlsx"

  df = pd.read_excel(full_file_path, usecols=['ADDRESS'])
  # print(df.values.tolist())
  ZIPCODE = []
  for each in df.values.tolist():
    print(each[0])
    print(each[0].split(",")[-2])
    ZIPCODE.append(each[0].split(",")[-1])

  dff = pd.read_excel(full_file_path)
  dff.insert(0, "Zipcode", ZIPCODE, True)
  print(dff)
  print(dff.to_excel("C:\\Users\\JJ\\tmp_location\\with_zipcode.xlsx"))


def main():
  """
  Main function to run excel_zipcode
  :return:
    None
  """
  excel_zipcode()


if __name__ == '__main__':
  main()
