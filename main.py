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

class TransactionPool:
	transaction_pool = []
	is_empty = True

	def add(self, transaction : str) -> None:
		self.is_empty = False
		self.transaction_pool.append(transaction)
		# print('add: ', self.transaction_pool)

	def pop(self) -> str:
		if(not self.is_empty):
			value = self.transaction_pool.pop(0)
			if(len(self.transaction_pool) == 0):
				self.is_empty = True

			# print('pop: ', self.transaction_pool)
			return value
		else:
			# print('pop: ', self.transaction_pool)
			return ''

class Node(ABC):	
	transactionPool = TransactionPool()

	def __init__(self, id = 0, name = ''):
		self.id = id
		self.name = name
		print(f"{type(self).__name__} node created: {self.name}({self.id})")

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
		Node.transactionPool.add(f"{Operation.RECOVER.value}|{VIN}|{self.id}")
		print(f"{self.name}({self.id}) recovered VIN: {VIN}")

class Auction(Node):
	miner = True

	def performOperation(self, VIN):
		Node.transactionPool.add(f"{Operation.AUCTION.value}|{VIN}|{self.id}")
		print(f"{self.name}({self.id}) auctioned VIN: {VIN}")


class Locksmith(Node):
	miner = False

	def performOperation(self, VIN):		
		Node.transactionPool.add(f"{Operation.CUT_KEYS.value}|{VIN}|{self.id}")
		print(f"{self.name}({self.id}) cut keys for VIN: {VIN}")

class Transport(Node):
	miner = False

	def performOperation(self, VIN, origin, destination):
		Node.transactionPool.add(f"{Operation.TRANSPORT.value}|{VIN}|{self.id}|{origin}|{destination}")
		print(f"{self.name}({self.id}) transported VIN: {VIN} from {Main.companies[int(origin)].name}({origin}) to {Main.companies[int(destination)].name}({destination})")

class Mechanic(Node):
	miner = False

	def performOperation(self, VIN):
		Node.transactionPool.add(f"{Operation.REPAIR.value}|{VIN}|{self.id}")
		print(f"{self.name}({self.id}) repaired VIN: {VIN}")

class Main:
	VIN_length = 11
	companies = dict()
	miners = []
	company_ledger = [[100, 'RecoveryInc', Company.RECOVERY, 2],
	 [200, 'TransportCo', Company.TRANSPORT], [201, 'TransportInc', Company.TRANSPORT],
	  [300, 'MechanicLtd', Company.MECHANIC], [400, 'LocksmithCo', Company.LOCKSMITH],
	   [500, 'AuctionCo', Company.AUCTION, 2], [501, 'AuctionLLC', Company.AUCTION, 3]]

	def run(self):
		self.setupNodes();	
		self.runSimulation();

	def setupNodes(self):
		for company in self.company_ledger:
			if(company[2] == Company.RECOVERY):	
				Main.companies[company[0]] = Recovery(company[0], company[1])
				Main.miners.extend(company[3] * [company[0]])
			elif(company[2] == Company.TRANSPORT):	
				Main.companies[company[0]] = Transport(company[0], company[1])
			elif(company[2] == Company.LOCKSMITH):	
				Main.companies[company[0]] = Locksmith(company[0], company[1])
			elif(company[2] == Company.MECHANIC):	
				Main.companies[company[0]] = Mechanic(company[0], company[1])
			elif(company[2] == Company.AUCTION):	
				Main.companies[company[0]] = Auction(company[0], company[1])
				Main.miners.extend(company[3] * [company[0]])

	def runSimulation(self):
		firstVIN = self.generateVIN()
		#RecoveryCo recovers a car and logs the operation
		Main.companies[100].performOperation(firstVIN)
		#TransportCo takes the car from RecoveryCo and delivers it to MechanicLtd
		Main.companies[200].performOperation(firstVIN, 100, 300)
		#MechanicLtd repairs the car
		Main.companies[300].performOperation(firstVIN)
		#TransportInc takes the car from MechanicLtd and delivers it to AuctionCo
		Main.companies[201].performOperation(firstVIN, 300, 500)
		#AuctionCo auctions the car
		Main.companies[500].performOperation(firstVIN)

		self.runMining()

	def runMining(self):
		random.shuffle(Main.miners)

	def generateVIN(self):
		return ''.join(random.choices(string.ascii_uppercase + string.digits, k = self.VIN_length))    

	def trace(self, VIN):
		# print(Operation(int(Node.transactionPool.pop().split('|')[0])) == Operation.RECOVER)
		pass

if __name__ == "__main__":	
	Main().run()