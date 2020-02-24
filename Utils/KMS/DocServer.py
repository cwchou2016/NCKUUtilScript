import getpass
import os

import requests
from bs4 import BeautifulSoup

from Utils.KMS.Document import Document

HOST = "http://kms.hosp.ncku.edu.tw"

CODE = {0: "Success", 404: "Failed"}


class DocServer:
    login_link = HOST + "/KM/login.aspx"
    logout_link = HOST + "/KM/logout.aspx"
    doc_link = HOST + "/KM/readdocument.aspx"

    def __init__(self):
        self.user_data = {}
        self.session = requests.session()
        self.response = self.session.get(DocServer.login_link)

        soup = self.get_soup()
        self.user_data["__VIEWSTATE"] = soup.find('input', {'id': "__VIEWSTATE"}).get("value")
        self.user_data["__VIEWSTATEGENERATOR"] = soup.find('input', {'id': "__VIEWSTATEGENERATOR"}).get("value")
        self.user_data["__EVENTVALIDATION"] = soup.find('input', {'id': "__EVENTVALIDATION"}).get("value")
        self.user_data['LoginButton'] = soup.find('input', {'id': "LoginButton"}).get("value")
        self.user_data["txtOpenIdUser"] = ""

    def get_soup(self):
        return BeautifulSoup(self.response.content, "html.parser")

    def login(self, user, password):
        """
        :return: int CODE
        """
        self.user_data['txtUserName'] = user
        self.user_data['txtPassword'] = password

        self.response = self.session.post(DocServer.login_link, data=self.user_data)
        soup = self.get_soup()

        if soup.find("a", {"href": "/KM/logout.aspx"}) is None:
            return 404

        return 0

    def logout(self):
        self.response = self.session.get(DocServer.logout_link)
        soup = self.get_soup()

        if soup.find("a", {"href": "/KM/logout.aspx"}) is None:
            return 404

        return 0

    def read_doc(self, doc_id):
        """
        Get document information
        :param doc_id:
        :return: Document
        """
        link = DocServer.doc_link + f"?documentId={doc_id}"
        self.response = self.session.get(link)

        soup = self.get_soup()
        if soup.find("div", {"class": "errorMessage"}) is not None:
            return None  # TODO raise Exception here

        doc = Document(doc_id, soup)
        return doc

    def download_view_url(self, url):
        """
        Download pdf from online pdf viewer
        """
        self.response = self.session.get(url)
        soup = self.get_soup()

        links = soup.find_all("a", {"class": "page-data-link"})
        title = (str(soup.title.string).strip())

        print(os.getcwd(), title)
        os.makedirs(f"export/{title}/")

        page_number = 1
        for i in links:
            img_link = HOST + i.get("href")

            content = server.session.get(img_link).content

            with open(f"export/{title}/{page_number:03}.jpg", "wb") as f:
                f.write(content)
                page_number += 1


if __name__ == "__main__":

    user = input("User:")
    password = getpass.getpass()

    server = DocServer()
    result = server.login(user, password)

    if result != 0:
        print("Login not success!")

    # with open("download_urls.txt", "r") as f:
    #     for url in f.readlines():
    #         server.download_view_url(url)