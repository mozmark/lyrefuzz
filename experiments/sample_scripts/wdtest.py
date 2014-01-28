from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

print DesiredCapabilities.FIREFOX

driver = webdriver.Remote(command_executor='http://localhost:5555/wd/hub',desired_capabilities = DesiredCapabilities.FIREFOX)
try:
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.send_keys("selenium")
    elem.send_keys(Keys.RETURN)
    assert "Google" in driver.title
    #elem = driver.find_element_by_name("arse!")
except:
    pass
driver.close()
