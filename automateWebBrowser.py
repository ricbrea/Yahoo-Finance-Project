from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Firefox(executable_path=r'C:\Users\bombe\Downloads\geckodriver-v0.32.0-win64\geckodriver.exe')


url = "https://www.stockmarketgame.org/login.html"

driver.get(url)
loginInfo = ['NY3_19_ZZ2225', 'FFF27069']


driver.find_element(By.XPATH, "/html/body/div/div/section/section/div/form/p[1]/input").send_keys(loginInfo[0])
driver.find_element(By.XPATH, "/html/body/div/div/section/section/div/form/p[2]/input[1]").send_keys(loginInfo[1])
driver.find_element(By.XPATH, "/html/body/div/div/section/section/div/form/p[3]/input").click()
time.sleep(3)
driver.find_element(By.XPATH, "/html/body/div[1]/div/section/section[4]/div/div[3]/input").click()
driver.find_element(By.XPATH, '//*[@id="aStockTrade"]').click()

#check to make sure stock is not on banned list
driver.find_element(By.XPATH, '//*[@id="aBlockedSymbols"]').click()
bannedListHTML = driver.page_source
print(bannedListHTML)