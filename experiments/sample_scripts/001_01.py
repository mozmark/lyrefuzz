import config
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

capabilities = DesiredCapabilities.FIREFOX

driver = webdriver.Remote(command_executor=config.executor, desired_capabilities = capabilities)

try:
    driver.get(config.test_cases+'001.html')
    assert "001" in driver.title
    elem = driver.find_element_by_name("input1")
    elem.send_keys("New title")
    btn = driver.find_element_by_name("btn1")
    btn.click()
    assert "New title" in driver.title
except:
    print 'oh noes!'
    pass
driver.close()
