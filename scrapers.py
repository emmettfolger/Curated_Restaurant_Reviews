import sys
import os
sys.path.append('C:/Users/Emmett Folger/Desktop/NotYelp/NotYelp')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'NotYelp.settings'
print(os.environ['DJANGO_SETTINGS_MODULE'])
import django
django.setup()

from restaurants.models import Restaurant
from restaurants.models import YellowPages as YP
import string
import urllib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
from random import randint
import numpy as np
from random import shuffle
from django.core.files import File

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"
import time

#List of yelp urls to scrape
url=['https://www.yelp.com/biz/the-halal-guys-new-york-2']
i=0

def get_links_on_page(html):
	links = []
	soup = BeautifulSoup(html, "lxml")
	all_biz_spans = soup.find_all('span', {'class': 'indexed-biz-name'})
	for biz in all_biz_spans:
		span_text = str(biz).strip()
		href_start = span_text.find('href') + 6
		# print(href_start)
		href_end = href_start + span_text[href_start:].find('"')
		full_url = 'https://www.yelp.com' + span_text[href_start:href_end]
		links.append(str(full_url))
	return links

def scrape_restaurants_by_city(city, state_two_letters):
	base_url = 'https://www.yelp.com/search?cflt=restaurants&find_loc='
	city = city.replace(' ', '+')

	first_page_url = base_url + city + '%2C+' + state_two_letters
	html = urllib.request.urlopen(first_page_url).read()

	first_page_links =get_links_on_page(html)
	url_list = []

	for link in first_page_links:
		url_list.append(str(link))

	num=30
	while num <=960 :#960
		#960
		next_page_url = 'https://www.yelp.com/search?find_loc=' + city + '+' + state_two_letters + '&start=' + \
		                str(num) + '&cflt=restaurants'
		print(next_page_url)
		time.sleep(randint(3,12))
		html2 = urllib.request.urlopen(str(next_page_url)).read()

		page_links = get_links_on_page(html2)
		for link in page_links:
			url_list.append(str(link))
		num+=30

	#replace colons for urllib
	cleaned_urls = []
	for url in url_list:
		url = urlparse(str(url)).geturl()
		# clean_url = url.replace(':', '%3A')
		cleaned_urls.append(url)

	return cleaned_urls

def scrape_restaurant_page(url):
	r = urllib.request.Request(str(url), headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    })
	html = urllib.request.urlopen(r).read()
	soup = BeautifulSoup(html, "lxml")
	name = soup.find('h1', {'class': 'biz-page-title'}).text.strip()
	try:
		address_div = soup.find('address')
		street_address = address_div.find('span', {'itemprop': 'streetAddress'}).text.strip()
		address_region = address_div.find('span', {'itemprop': 'addressRegion'}).text.strip()
		postal_code = address_div.find('span', {'itemprop': 'postalCode'}).text.strip()
		address_locality = address_div.find('span', {'itemprop': 'addressLocality'}).text.strip()
	except:
		print('Problem with address')

	neighborhood_span = soup.find('span', {'class': 'neighborhood-str-list'})
	neighborhood = None
	if neighborhood_span is not None:
		neighborhood = neighborhood_span.text.strip()

	phone_span =  soup.find('span',{'class': 'biz-phone'})
	phone = None
	if phone_span is not None:
		phone = phone_span.text.strip()
		phone = "+{0}".format(phone.replace('(', '').replace(' ', '').replace(')', '').replace('-', ''))
		print(phone)

	website_div = soup.find('span', {'class': 'biz-website'})
	website = None
	if website_div is not None:
		website = website_div.find('a').text.strip()
	# if website.find('…') is not None:
	# 	slash_loc = website.find('/')
	# 	website = website[0:slash_loc+1]

	# showcase_photo_link = soup.find('a', {'class', 'see-more'})['href']
	# print(showcase_photo_link)
	# photo_request = urllib.request.Request('https://www.yelp.com'+str(showcase_photo_link), headers={
     #    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
	# })
	# photos_html =  urllib.request.urlopen(photo_request).read()
	# photo_soup = BeautifulSoup(photos_html, "lxml")
	# first_photo_src = photo_soup.find('div', {'class', 'photo-box'}).find('img')['src']

	try:
		restaurant_obj = Restaurant.objects.create(
			name=name,
			street_address=street_address,
			address_region=address_region,
			postal_code = postal_code,
			address_locality=address_locality,
			neighborhood=neighborhood,
			local_phone=phone,
			website=website,
			yelp_url=url,

			)
		restaurant_obj.save()
		# photo_temp = urllib.request.urlopen(first_photo_src).read()
		# restaurant_obj.photo.save("image_%s" % restaurant_obj.pk, File(photo_temp))
		# restaurant_obj.save()
		# if created == True:
		# 	print('Added: ', restaurant_obj.name)
		# 	return restaurant_obj
		# else:
		# 	print(restaurant_obj)
	except:
		raise

class YellowPages:
	def get_category_pages_by_city(self):
		r = urllib.request.Request(str('https://www.yellowpages.com/restaurants/new-york-ny'), headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) '
			              'Chrome/35.0.1916.47 Safari/537.36'
			})
		html = urllib.request.urlopen(r).read()
		soup = BeautifulSoup(html, "lxml")
		cols = soup.find('section', {'class': 'category-search'}).find_all('ul')

		category_hrefs = []
		for col in cols:
			rows = col.find_all('li')
			for r in rows:
				category_hrefs.append(r.a['href'])
		return category_hrefs

	#https://www.yellowpages.com/new-york-ny/american-restaurants
	def get_restaurant_links_by_category(self, url):#switch to pass in url
		full_url = 'https://www.yellowpages.com'+url
		r = urllib.request.Request(str(full_url), headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        })
		#LIST TO RETURN
		restaurant_links = []

		# FIRST PAGE
		html = urllib.request.urlopen(r).read()
		soup = BeautifulSoup(html, "lxml")
		restaurant_divs = soup.find_all('a', {'class': 'business-name'})

		for r in restaurant_divs:
			full_href = 'https://www.yellowpages.com'+r['href']
			restaurant_links.append(full_href)

		# 2+ PAGES
		page_num = 2
		prev_page_links = []
		while page_num <= 101:
			time.sleep(randint(1,3))
			r2 = urllib.request.Request(str(full_url+'?page='+str(page_num)), headers={
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
				})
			try:
				html = urllib.request.urlopen(r2).read()
			except:
				print("Error reading category page")
				continue

			soup = BeautifulSoup(html, "lxml")
			restaurant_divs = soup.find_all('a', {'class': 'business-name'})
			print(page_num, len(restaurant_divs))

			page_links = []
			for r in restaurant_divs:
				full_href2 = 'https://www.yellowpages.com' + r['href']
				page_links.append(full_href2)

			if page_links != prev_page_links:
				for p in page_links:
					restaurant_links.append(p)

			prev_page_links = page_links
			page_num+=1

		return restaurant_links

	def store_restaurants(self, restaurant_links):
		#a list is passed in for creating YellowPages restaurant objects
		num_stored = 0
		for link in restaurant_links:
			r3 = None

			#make sure the link isn't two links combined
			if link[6:].find('https://')== -1:
				r3 = urllib.request.Request(link, headers={
					'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) '
					              'Chrome/35.0.1916.47 Safari/537.36'
					})

			try:
				html = urllib.request.urlopen(r3).read()
			except:
				print(link, r3, 'ERROR IN HTTP REQUEST')
				continue
			soup = BeautifulSoup(html, "lxml")
			try:
				yellowpages_obj = YP.objects.create(yp_url=link, error=False)
			except:
				print('DUPLICATE YELLOWPAGES URL')
				continue
			try:
				website = soup.find('a', {'class': 'secondary-btn website-link'})
				if website is not None:
					yellowpages_obj.website = website['href']
				name = soup.find('div', {'class': 'sales-info'})
				if name is not None:
					yellowpages_obj.name = name.text
				street_address = soup.find('p', {'class': 'address'})
				if street_address is not None:
					yellowpages_obj.street_address = street_address.text
				local_phone = soup.find('p', {'class': 'phone'})
				if local_phone is not None:
					yellowpages_obj.local_phone = local_phone.text
				price_range_tag = soup.find('dt', text=r'Price Range')
				if price_range_tag is not None:
					price_range = price_range_tag.find_next_sibling('dd')
					yellowpages_obj.price_range = price_range.text
				payment_method = soup.find('dd', {'class': 'payment'})
				if payment_method is not None:
					yellowpages_obj.payment_method = payment_method.text

				yellowpages_obj.save()
				print("Saved: ", yellowpages_obj.name)
				num_stored+=1
			except:
				yellowpages_obj.error = True
				yellowpages_obj.save()
				num_stored += 1
		print("Objects stored: ", num_stored)

y = YellowPages()
categories = y.get_category_pages_by_city()
num_links = 0
for c in categories[3:]:
	restaurant_links = y.get_restaurant_links_by_category(c)
	print(c, len(restaurant_links))
	num_links+= len(restaurant_links)
	y.store_restaurants(restaurant_links)

print(num_links)



restaurants = scrape_restaurants_by_city('New York', 'NY')
#shuffle the list of restaurant links. Harder for sites to track

shuffle(restaurants)
print(restaurants[0:10])
for restaurant in restaurants:
	try:
		r = scrape_restaurant_page(restaurant)
	except urllib.error.HTTPError as err:
		if err.code == 503 or err.code == 500:
			time.sleep(30)
			try:
				r = scrape_restaurant_page(restaurant)
			except:
				continue
		else:
			raise