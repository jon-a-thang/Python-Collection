"""
Filename:
  excel_zipcode_universal.py

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
  full_file_path = "PATH_TO_EXCEL_FILE"

  df = pd.read_excel(full_file_path, usecols=['COL_NAME_THAT_NEEDS_TO_BE_ALTERED'])
  # print(df.values.tolist())
  new_df_list = []
  # Checking the output of the dataframe from the excel sheet
  for each in df.values.tolist():
    print(each[0])
    print(each[0].split(",")[-2])
    # Appending the data that we are altering or need into its own new list
    new_df_list.append(each[0].split(",")[-1])

  dff = pd.read_excel(full_file_path)
  # inserting the new column
  dff.insert(0, "Zipcode", new_df_list, True)
  print(dff)
  print(dff.to_excel("PATH_OF_NEW_EXCEL_FILE"))


def main():
  """
  Main function to run excel_zipcode

  :return:
    None
  """
  excel_zipcode()


if __name__ == '__main__':
  main()
