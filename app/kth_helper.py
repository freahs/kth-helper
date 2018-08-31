from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import argparse
from getpass import getpass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class KTHHelper:

    def __get_credits(self, credit_string):
        return float(credit_string.strip().split()[0].replace(',','.'))

    def __get_programme(self, course_group):
        res = course_group.find_element_by_xpath(".//h3[@class='paketering']").text.split(" | ")
        return {
            'name': res[0],
            'credits': self.__get_credits(res[1])
        }
    
    def __get_courses(self, course_group, programme, status, graded=False):
        res = []
        for e in course_group.find_elements_by_xpath(".//div[contains(@class, 'ldk-visa-desktop')]/a"):
            details = e.get_attribute('innerHTML').split(" | ")
            res.append({
                'programme': programme,
                'name': details[0],
                'credits': self.__get_credits(details[1]),
                'code': details[2],
                'status': status
            })
        return res

    def start(self):
        logging.info("starting chromedriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1920, 1080)

    def get_unfinished_courses(self):
        logging.info("processing courses at 'https://www.student.ladok.se/student/#/aktuell'...")
        self.driver.get("https://www.student.ladok.se/student/#/aktuell")
        res = []

        for s, v in {'current':'pagaende', 'upcoming':'kommande', 'unfinished':'oavslutade'}.items():
            groups = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//ladok-{}-kurser-i-struktur".format(v)))
            )
            for g in groups:
                p = self.__get_programme(g)
                res += self.__get_courses(g, p, s)
        return res
    
    def get_finished_courses(self):
        logging.info("processing courses at 'https://www.student.ladok.se/student/#/avslutade'...")
        self.driver.get("https://www.student.ladok.se/student/#/avslutade")
        res = []

        groups = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ladok-avslutade-kurser-i-struktur"))
        )
        for g in groups:
            p = self.__get_programme(g)
            res += self.__get_courses(g, p, 'finished')
        return res
    
    def login_to_ladok(self, username, password):
        # Log in to Ladok
        logging.info("logging in via 'https://www.student.ladok.se'...")
        self.driver.get('https://www.student.ladok.se')
        
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Select higher education to login'))
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@alt[contains(.,'KTH')]]"))
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "proceed"))
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'username'))
        ).send_keys(username)

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'password'))
        ).send_keys(password)

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='submit']"))
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@lang='sv']"))
        ).click()

    def stop(self):
        logging.info('stopping chromedriver...')
        self.driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, help="your kth username (without @kth.se)")
    parser.add_argument('-p', '--password', type=str, help="your kth password")
    args = parser.parse_args()

    u = args.username if args.username else input("your kth username (without @kth.se): ")
    p = args.password if args.password else getpass(prompt='your kth password: ')

    h = KTHHelper()
    h.start()
    h.login_to_ladok(u, p)
    courses = h.get_finished_courses() + h.get_unfinished_courses()
    h.stop()

    courses.sort(key=lambda x: (x['programme']['name'], x['status'], x['name']))
    print("[")
    for i, c in enumerate(courses):
        print("  {},".format(c) if i < len(courses) - 1 else "  {}".format(c))
    print("]")