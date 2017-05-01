# -*- coding: utf-8 -*-

from slackclient import SlackClient
from block_io import BlockIo
import time
import requests


def clean(text):
	text = text.split(" ")
	for i in range(text.count(' ')):
		text.remove(' ')
	return text

def address(message,user):
	try:
		data = block_io.get_address_by_label(label=user)
		if "success" in data["status"]:
			return	"Your address is "+data['data']['address']+""
	except:
		return "Looks like you are not registered yet :( Use !register to register."

def balance(message,user):
	try:
		data = block_io.get_address_balance(labels=user)

		if "success" in data["status"]:
			balance = float(data['data']['balances'][0]['available_balance']) 
			pending_balance = float(data['data']['balances'][0]['pending_received_balance'])
			if(pending_balance > 1):
				return "Balance : "+str(balance)+"Ð ("+str(pending_balance)+"Ð Unconfirmed)"
			return "Balance : "+str(balance) + "Ð"
	except:
		return "Looks like you are not registered yet :( Use !register to register."

def tip(message,user):
	try:
		person = (message[1].replace('<@','')).replace('>','')
		amount = float(message[2])
		if(amount < 2):
			return "Oops....Minimum amount is 2 for tipping"
		data = block_io.withdraw_from_labels(amounts=str(amount), from_labels=user, to_labels=person,priority="low")
		if "success" in data["status"]:
			return "Successfully tipped."
	except ValueError:
		return "Invalid amount."
	except:
		return" Insufficient balance or the person is not registered."

def register(message,user):
	try:
		data = block_io.get_new_address(label=user)
		if "success" in data["status"]:
			return "You are now registered :)."
	except:
		return "You are already registered."

def withdraw(message,user):
	try:
		amount = float(message[1])
		if(amount < 2):
			return "Oops....Minimum amount is 2 for withdrawing"
		address = message[2]
		data = block_io.withdraw_from_labels(amounts=str(amount), from_labels=user, to_addresses=address)
		return "Coins sent!"
	except ValueError:
		return "invalid amount."
	except:
		return "Insufficient balance."

def price(message,user):
	links = {"Coinsecure":"https://api.coinsecure.in/v0/noauth/newticker",
            "Unocoin":"https://www.unocoin.com/trade?all",
            "Zebpay":"https://api.zebpay.com/api/v1/ticker?currencyCode=INR",
            "Pocketbits":"http://pocketbits.in/api/ticker"}

	price = "```"
	for i in links:
		data = requests.get(links[i]).json()
		vol = "0"

		try:
			if "bid" in data:
				bid = data["bid"] / 100
				ask = data["ask"] / 100
				vol = data["coinvolume"] * 0.00000001
			else:
				bid = data["buy"]
				ask = data["sell"]
				vol = data["volume"]
		except:
			pass
		price = price + "%-15s\nBuy : ₹%-8s   Sell : ₹%-6s\n" %(i,bid,ask)
	price = price + "```"
	return price

def market(message,user):
	try:

		if(len(message) < 2):
			return "Correct syntax : !market coin_ticker"
		inr_price = float(requests.get("https://api.coinsecure.in/v0/noauth/newticker").json()["ask"]/100)
		data = requests.get("https://poloniex.com/public?command=returnTicker").json()
		if("BTC_"+message[1].upper() in data):
			price_data = data["BTC_"+message[1].upper()]
			price = "```Poloniex "+message[1].upper()+"\nPrice : %-10s\nLow : %-10s  High : %-10s\nVol : %-10.2f  INRvol : %.2f \nChange : %.2f%%\n\n" %(price_data["last"],price_data["low24hr"],price_data["high24hr"],float(price_data["baseVolume"]),float(price_data["baseVolume"])*inr_price,float(price_data["percentChange"]))
		else:
			price = "```Poloniex "+message[1].upper()+"\nNot listed here.\n\n"
		data = requests.get("https://bittrex.com/api/v1.1/public/getmarketsummary",data={"market":"btc-"+message[1]}).json()

		if(data["success"]):
			data = data["result"][0]
			price = price + "Bittrex "+message[1].upper()+"\nPrice : %.8f\nLow : %-10.8f  High : %-10.8f\nVol : %-10.2f  INRvol : %.2f```" %(data["Last"],data["Low"],data["High"],data["BaseVolume"],data["BaseVolume"]*inr_price)
		else:
			price = price + "Bittrex "+message[1].upper()+"\nNot Listed here.```"

		return price
	except:
		return "Something went wrong :("


def calc(message,user):
	try:
		int(message[2])
		if(len(message) < 3):
			return "Correct syntax : !calc coin amount"
		btc_price = float(requests.get("https://poloniex.com/public?command=returnTicker").json()["BTC_"+message[1].upper()]["last"])
		inr_price = float(requests.get("https://api.coinsecure.in/v0/noauth/newticker").json()["ask"]/100)
		amount = int(message[2])
		total = (btc_price*amount) * inr_price
		return "```[%s %s] [%.4f BTC] [%.2f INR]```" %(message[2],message[1].upper(),btc_price*amount,total)
	except ValueError:
		return "Correct syntax : !calc coin amount"
	except:
		pass


def help(message,user):
	m = """```
		!address : Get your tipbot address.i
		!balance : Get your tipbot balance.
		!tip : Tip someone [!tip <username> <amount>] (Min. Amount : 2)
		!register : Register with tipbot.
		!withdraw : Withdraw coins from tipbot. [!withdraw <amount> <address>] (Min. Amount : 2)
		!price : Bitcoin price on Indian exchanges.
		!market : Get altcoin price [!market <coinNAme>]
		!calc : Get how much N amount of X coin is worth in INR and BTC.
		!help : For help.
			
		Donate : 13fRUvzJJSZWSYCaJA9GpsA9Q7x2p6cgA4
		```"""
	return m	

token = "slackToken"
sc = SlackClient(token)
sc.rtm_connect()
block_io = BlockIo("token","pin", 2)

commands = {"!address":address,
			"!balance":balance,
			"!tip":tip,
			"!register":register,
			"!withdraw":withdraw,
			"!price":price,
			"!market":market,
			"!calc":calc,
			"!help":help
			}

while(True):
	try:
		data = sc.rtm_read()
		if(data):
			print(data)
			if("subtype"  in data[0] and "channel_join" in data[0]["subtype"]):
				user = data[0]["channel"]
				sc.rtm_send_message(user,"Welcome")

			if("text" in data[0] and "C2ACQLM7B" not in data[0]["channel"]):
				message = clean(data[0]["text"])
				channel = data[0]["channel"]
				user = data[0]["user"]
				print(message[0])
				if "!" in message[0]:
					sc.rtm_send_message(channel,commands[message[0]](message,user))
			elif("C2ACQLM7B" in data[0]["channel"] and "!" in clean(data[0]["text"])[0]):
				sc.rtm_send_message(data[0]["channel"],"Please use bot in DM or in #bots-area")
	except:
		pass

