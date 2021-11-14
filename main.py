"""
Created on Sat Nov 13 3:23:30 2021

@author: masonharlan
"""

import hashlib as hasher
import datetime as date
import string    
import random
from enum import Enum
from abc import ABC, abstractmethod

class Operation(Enum):
	RECOVER = 1
	TRANSPORT = 2
	REPAIR = 3
	CUT_KEYS = 4
	AUCTION = 5

class Company(Enum):
	RECOVERY = 1
	TRANSPORT = 2
	MECHANIC = 3
	LOCKSMITH = 4
	AUCTION = 5

class MiningPool:
	transaction_pool = []
	is_empty = True

	def addToMiningPool(self, transaction : str) -> None:
		is_empty = False
		self.transaction_pool.append(transaction)

	def popTransactionFromMiningPool(self) -> str:
		if(not self.is_empty):
			value = self.transaction_pool.pop(0)
			if(len(self.transaction_pool) == 0):
				self.is_empty = True
			return value
		else:
			return ''

class Node(ABC):	
	id = 0
	name = ''
	def __init__(self, id, name):
		self.id = id
		self.name = name

	@property
	@abstractmethod
	def miner(self):
		pass


	@abstractmethod
	def performOperation(self):
		pass

class Recovery(Node):
	miner = True

	def performOperation(self, VIN):
		print("VIN: " + VIN)

class Auction(Node):
	miner = True

	def performOperation(self, VIN):
		pass


class Locksmith(Node):
	miner = False

	def performOperation(self, VIN):
		pass

class Transport(Node):
	miner = False

	def performOperation(self, VIN, origin, destination):
		pass

class Mechanic(Node):
	miner = False

	def performOperation(self, VIN):
		pass

class Main:
	VIN_length = 11
	companies = dict()
	company_ledger = [[100, 'RecoveryInc', Company.RECOVERY],
	 [200, 'TransportCo', Company.TRANSPORT], [201, 'TransportInc', Company.TRANSPORT],
	  [300, 'MechanicLtd', Company.MECHANIC], [400, 'LocksmithCo', Company.LOCKSMITH],
	   [500, 'AuctionCo', Company.AUCTION], [501, 'AuctionLLC', Company.AUCTION]]

	def run(self):
		self.setupNodes();	
		self.runSimulation();

	def setupNodes(self):
		for company in self.company_ledger:
			if(company[2] == Company.RECOVERY):	
				self.companies[company[0]] = Recovery(company[0], company[1])
			elif(company[2] == Company.TRANSPORT):	
				self.companies[company[0]] = Transport(company[0], company[1])
			elif(company[2] == Company.LOCKSMITH):	
				self.companies[company[0]] = Locksmith(company[0], company[1])
			elif(company[2] == Company.MECHANIC):	
				self.companies[company[0]] = Mechanic(company[0], company[1])
			elif(company[2] == Company.AUCTION):	
				self.companies[company[0]] = Auction(company[0], company[1])

	def runSimulation(self):
		#RecoveryCo recovers a car and logs the operation
		self.companies[100].performOperation(self.generateVIN())

	def generateVIN(self):
		return ''.join(random.choices(string.ascii_uppercase + string.digits, k = self.VIN_length))    

if __name__ == "__main__":	
	Main().run()