import requests
import json
import logging
from time import sleep
from datetime import datetime
import re
from DataValidator import DataValidator
import pandas as pd


class Config:
    def __init__(self):

        self.headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "ru,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json; charset=UTF-8",
            "origin": "https://www.sior.com",
            "priority": "u=1, i",
            "referer": "https://www.sior.com/find-an-sior/find-an-sior-member/?search=FD8E401F-F7B6-34DD-FDD7-29FD2C1B64F2",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }


class SiorScrapper(Config):
    def __init__(
        self,
        id="FD8E401F-F7B6-34DD-FDD7-29FD2C1B64F2",
        locationsIds: list = [],
        specialityIds: list = [],
        areaOfPracticeIds: list = [],
        count=5_000,
    ):
        super().__init__()
        self.guid = id
        skip = 0
        self.count = count
        self.location_ids = locationsIds
        radius = ""
        member_name = ""
        company = ""
        self.specialty_ids = specialityIds
        self.area_of_practice_ids = areaOfPracticeIds
        sort_by = "LastNameAscending"
        self.url = "https://www.sior.com/WebServices/FindAMember.asmx/Search"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)

        self.data = f'{{ guid: "{self.guid}", skip: {skip}, count: {count}, locationIds: {self.location_ids}, radius: "{radius}", memberName: "{member_name}", company: "{company}", specialtyIds: {self.specialty_ids}, areaOfPracticeIds: {self.area_of_practice_ids}, sortBy: "{sort_by}" }}'

    def start_request(self):

        r = requests.post(self.url, data=self.data, headers=self.headers)
        if r.status_code != 200:
            while r.status_code != 200:
                self.logger.warning(
                    f"Error in processing request\nStatus code: {r.status_code}\nRetrying..."
                )
                r = requests.post(self.url, data=self.data, headers=self.headers)
        return self.scrape_lead_info(r.json()["d"])

    def __get_date(self, date_str):
        match = re.search(r"\d+", date_str)
        return datetime.utcfromtimestamp(int(match.group()) / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def scrape_lead_info(self, items: list):
        self.res = []
        for item in items:

            person = {
                "ID": item["PersonId"],
                "First Name": item["FirstName"],
                "Last Name": item["LastName"],
                "Full Name": item["FullName"],
                "Designations": item["Designations"],
                "Company Name": item["CompanyName"],
                "Member Type": item["MemberType"],
                "Directory City": item["DirectoryCity"],
                "Additional Directory City": item["AdditionalDirectoryCity"],
                "Directory State": item["DirectoryState"],
                "Directory Country": item["DirectoryCountry"],
                "Join Date": (
                    self.__get_date(item["JoinDate"]) if item.get("JoinDate") else None
                ),
                "Email": item["Email"],
                "Phone": item["Phone"],
                "Address": item["Address"],
                "City": item["City"],
                "State": item["State"],
                "Postal Code": item["PostalCode"],
                "Country": item["Country"],
                "Website": item["Website"],
                "Market": item["Market"],
                "Join Year": item["JoinYear"],
                "Location": item["Location"],
                "Licenses": ", ".join(item["Licenses"]),
                "Latitude": item["Latitude"],
                "Longitude": item["Longitude"],
                "Full Address": item["FullAddress"],
                "Naylor Ad Code Name": item["NaylorAdCodeName"],
            }

            validator = DataValidator()
            is_valid = validator.validate_email(person)
            if not is_valid:
                self.logger.critical(f'Error email validation, got: {person["Email"]}')
            is_valid = validator.validate_phone(person)
            if not is_valid:
                self.logger.critical(f'Error phone validation, got: {person["Phone"]}')
            self.res.append(person)
        self.__save_to_csv("sior.csv")

    def __save_to_csv(self, filename):
        df = pd.DataFrame(self.res)
        df.to_csv(filename, index=False, mode="w", header=True)
        self.logger.info(f"Data saved to {filename}")


if __name__ == "__main__":
    SiorScrapper().start_request()
