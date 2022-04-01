"""
Filename:
    Box_Upload.py

Description:
    Using box.com and their built-in APU to upload files and folders to Box.com along with the use of selenium

Author(s):
    Jonathan Jang
"""
import os
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
# Import two classes from the boxsdk module - Client and OAuth2
from boxsdk import Client, OAuth2


def upload_to_box_api():
    # Going to box and generating a developer token

    # create instance of Chrome webdriver
    browser = webdriver.Chrome()

    # Open box.com to correct account in the developers console
    browser.get("https://_YOUR_BOX_ACCOUNT_LINK_.box.com/developers/console")
    time.sleep(3)

    # Enter Username & Password Info
    browser.find_element_by_id("login-email").send_keys("_ENTER_USERNAME_HERE_")
    time.sleep(1)
    browser.find_element_by_id("login-submit").click()
    time.sleep(2)
    browser.find_element_by_id("password-login").send_keys("_ENTER_PASSWORD_HERE_")
    time.sleep(1)
    browser.find_element_by_id("login-submit-password").click()

    app_name = "appbogusname-temp-name"
    # Will sleep until the page loads by looking to see if the element to change the date filter exists
    while True:
        try:
            app_name = browser.find_element_by_xpath("/html/body/div[1]/div/main/div[2]/div/div[2]/a[2]/div").text
            break
        except NoSuchElementException:
            time.sleep(1)

    print("Successfully logged into the Box account")

    if "_ENTER_NAME_OF_YOUR_APP_NAME_" in app_name:
        # Clicking the App Name to get to the settings of that app
        browser.find_element_by_xpath("/html/body/div[1]/div/main/div[2]/div/div[2]/a[2]/div").click()
        time.sleep(1)

        # Clicking the "Configuration" Tab
        browser.find_element_by_xpath("/html/body/div[1]/div/main/section/div/div/div[1]/a[2]/div[1]/span").click()
        time.sleep(1)

        # Clicking "Generate Developer Token"
        browser.find_element_by_xpath("/html/body/div[1]/div/main/section/div[2]/main/div[2]/section[2]/div[2]/"
                                      "div/label/button/span/span").click()
        time.sleep(1)

        # Getting the developer token
        dev_token = browser.find_element_by_name("devToken").get_attribute("value")
        time.sleep(1)
        # print(dev_token)

        print("Starting to upload the files and folders to Box")

        # Establishing the connection and then uploading to box
        oauth = OAuth2(
            client_id='_YOUR_CLIENT_ID_',
            client_secret='_YOUR_SECRET_ID_',
            access_token=dev_token,
        )
        client = Client(oauth)
        root_folder = client.folder(folder_id='_ENTER_FOLDER_ID_')
        current_parent_folder = root_folder.create_subfolder(datetime.now().strftime("%Y-%m-%d"))

        parent_folderpath = 'C:\\_PATH_OF_YOUR_FOLDER_TO_UPLOAD_ ' + '\\'
        
        # Uploading sub-folders that are contained in the parent folder that you are uploading
        for sub_folder_name in [os.path.join(fold_name) for fold_name in os.listdir(parent_folderpath)
                          if os.path.isdir(os.path.join(parent_folderpath, fold_name))]:
            shared_folder = current_parent_folder.create_subfolder(sub_folder_name)
            for fname in os.listdir(parent_folderpath + sub_folder_name):
                print(fname)
                uploaded_file = shared_folder.upload(parent_folderpath + sub_folder_name + "\\" + fname)
                shared_link = shared_folder.get_shared_link()
                print(uploaded_file)
                print(shared_link)

        # Uploading the all of the files that are in the parent folder
        for only_files in [os.path.join(fold_name) for fold_name in os.listdir(parent_folderpath)
                           if os.path.isfile(os.path.join(parent_folderpath, fold_name))]:
            print(only_files)
            uploaded_file = current_parent_folder.upload(parent_folderpath + only_files)
            shared_link = current_parent_folder.get_shared_link()
            print(uploaded_file)
            print(shared_link)

        shared_link = current_parent_folder.get_shared_link()
        print(shared_link)

        print("---Completed uploading all of the files and folders to Box---")

        # Revoking the Developer Token so that no one else can use it after the upload stage is completed
        browser.find_element_by_xpath("/html/body/div[1]/div/main/section/div[2]/main/div[2]/section[2]/"
                                      "div[2]/div/div[1]/div[2]/button/span/span").click()
        time.sleep(3)

        browser.close()
        browser.quit()

        return shared_link

    else:
        print("Error. Could not find the app name to click on")


def main():
    """
    Main function to run Box_Upload.py

    :return:
        None
    """
    upload_to_box_api()


if __name__ == '__main__':
    main()
