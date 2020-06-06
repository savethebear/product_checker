from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import SendMail
import sys
from selenium.webdriver.firefox.options import Options
from datetime import datetime
import requests
from requests.exceptions import HTTPError
import time

# supported stores
STORE_BOOTS = "boots"
STORE_SUPERDRUG = "superdrug"


def boots_crawler(driver, links):
	stocked_links = []
	error_causing_links = []
	for link in links:
		print("checking {}...".format(link))
		driver.get(link)
		text_exists = len(driver.find_elements_by_id("sold_out_text")) > 0
		if text_exists:
			display_value = driver.find_element_by_id("sold_out_text").value_of_css_property("display")
			if display_value == "none":
				stocked_links.append(link)
		else:
			error_causing_links.append(link)
	return stocked_links, error_causing_links
	


def superdrug_crawler(codes):
	stocked_links = []
	error_causing_links = []
	base_http = "https://www.superdrug.com/stores/stocks?productCode={}&storeIds=178"
	base_product_page = "https://www.superdrug.com/p/{}"
	for code in codes:
		request_http = base_http.format(code)
		print("checking {}...".format(request_http))
		try:
			response = requests.get(request_http)

			# If the response was successful, no Exception will be raised
			response.raise_for_status()
		except HTTPError as http_err:
			print(f'HTTP error occurred: {http_err}')  # Python 3.6
			error_causing_links.append(request_http)
		except Exception as err:
			print(f'Other error occurred: {err}')  # Python 3.6
			error_causing_links.append(request_http)
		else:
			response_obj = json.loads(response.content)
			if response_obj["features"][0]["properties"]["stock"]["basketStatus"] == "GREEN":
				stocked_links.append(base_product_page.format(code))


		time.sleep(1)

	return stocked_links, error_causing_links

def send_mail(subject, message, my_address, password):
	SendMail.send_email(subject, message, my_address, password)
	mail_file = open("{}/mail_sent.txt".format(sys.path[0]), 'w')
	mail_file.write("1")
	mail_file.close()

if __name__ == "__main__":
	# take in host email address from commandline args
	if len(sys.argv < 3):
		print("Usage: python3 checker.py HOST_EMAIL EMAIL_PASSWORD")
		return
	
	my_address = sys.argv[1]
	password = sys.argv[2]

	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options=options)
	# driver = webdriver.Firefox()
	
	# check if email has been sent already
	mail_file = open("{}/mail_sent.txt".format(sys.path[0]))
	is_sent = mail_file.readline()
	mail_file.close()
	if is_sent == '1':
		sys.exit()

	log = open("{}/log.txt".format(sys.path[0]), 'a+')
	log.write("checker activated at {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
	log.close()

	file = open("{}/products.json".format(sys.path[0]))
	products_data = json.load(file)

	store_list = products_data["products"]

	stocked_links = []
	error_causing_links = []

	for store in store_list:
		if store["store"] == STORE_BOOTS:
			links, error = boots_crawler(driver, store["items"])
		elif store["store"] == STORE_SUPERDRUG:
			links, error = superdrug_crawler(store["items"])
		else:
			print("{} is not supported yet....".format(store["store"]))
			continue

		stocked_links = stocked_links + links
		error_causing_links = error_causing_links + error


	if error_causing_links:
		message = "There are errors with these products..\n"
		for link in error_causing_links:
			message = message + link + "\n"
		send_mail("Stocked Products Error", message, my_address, password)
	elif stocked_links:
		# create the message
		message = "Some products have been stocked. Check out the links below: \n"
		for link in stocked_links:
			message = message + link + "\n"

		message = message + "\n ps. Remember to kill me \n\nThanks\nCheckerBot"
		send_mail("Stocked Products", message, my_address, password)

	driver.close()
