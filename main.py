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


DIFFICULTY_HASH = 0x00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

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

class Block():
	def __init__(self, data, timestamp, previous_hash):
		self.data = data 
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.nonce = 0
		self.miner = None 
		self.hash_block()

	def hash_block(self):
		sha = hasher.sha256()
		sha.update(str(self.data).encode('utf-8') + str(self.timestamp).encode('utf-8') + 
					str(self.previous_hash).encode('utf-8') + str(self.nonce).encode('utf-8'))
		self.hash = sha.hexdigest()
		return self.hash

class Blockchain(dict):
	currentBlock = None

	def __init__(self):
		dict.__init__(self)
		self['0'] = self.create_genesis_block()
		self.currentBlock = '0'

	# Generate genesis block
	def create_genesis_block(self):
		# Manually construct a block with index zero and arbitrary previous hash
		genesis = Block("", date.datetime.now(), "")
		genesis.hash = '0'
		return genesis

	def tip(self):
		if(self.currentBlock != None):
			return self[self.currentBlock]
		else:
			return None
	
	def add(self, newBlock):
		self[newBlock.hash] = newBlock	
		self.currentBlock = newBlock.hash

	def writeToFile(self):
		file = open("blockchain.txt", 'w')
		block = self.tip()
		while block.hash != '0':
			file.write("Block Data: " + str(block.data) + "\n")
			file.write("Hash: " + str(block.hash) + "\n")
			file.write("Miner Who Discovered Block: " + str(block.miner) + "\n")
			file.write("----------------------------------\n")
			block = self[block.previous_hash]

		file.write("Genesis Block \n")
		file.write("Hash: 0 \n")
		file.write("Miner Who Discovered Block: NA \n")
		file.write("----------------------------------\n")

		file.close()

class Main:
	VIN_length = 11
	companies = dict()
	miners = []
	blockchain = Blockchain()
	company_ledger = [[100, 'RecoveryInc', Company.RECOVERY, 2],
	 [200, 'TransportCo', Company.TRANSPORT], [201, 'TransportInc', Company.TRANSPORT],
	  [300, 'MechanicLtd', Company.MECHANIC], [400, 'LocksmithCo', Company.LOCKSMITH],
	   [500, 'AuctionCo', Company.AUCTION, 2], [501, 'AuctionLLC', Company.AUCTION, 3]]

	def run(self):
		self.setupNodes()

		print("---------------------")

		self.runSimulation()

	def setupNodes(self):
		for company in self.company_ledger:
			if(company[2] == Company.RECOVERY):	
				Main.companies[company[0]] = Recovery(company[0], company[1])
				self.miners.extend(company[3] * [company[0]])
			elif(company[2] == Company.TRANSPORT):	
				Main.companies[company[0]] = Transport(company[0], company[1])
			elif(company[2] == Company.LOCKSMITH):	
				Main.companies[company[0]] = Locksmith(company[0], company[1])
			elif(company[2] == Company.MECHANIC):	
				Main.companies[company[0]] = Mechanic(company[0], company[1])
			elif(company[2] == Company.AUCTION):	
				Main.companies[company[0]] = Auction(company[0], company[1])
				self.miners.extend(company[3] * [company[0]])

	def runSimulation(self):
		firstVIN = self.generateVIN()
		#RecoveryInc recovers a car
		Main.companies[100].performOperation(firstVIN)
		#TransportCo takes the car from RecoveryInc and delivers it to MechanicLtd
		Main.companies[200].performOperation(firstVIN, 100, 300)

		#Run mining simulation
		self.runMining()

		#MechanicLtd repairs the car
		Main.companies[300].performOperation(firstVIN)
		#TransportInc takes the car from MechanicLtd and delivers it to AuctionCo
		Main.companies[201].performOperation(firstVIN, 300, 500)
		#AuctionCo auctions the car
		Main.companies[500].performOperation(firstVIN)


		#Run mining simulation
		self.runMining()

		print("---------------------")

		secondVIN = self.generateVIN()

		#RecoveryInc recovers a car and logs the operation
		Main.companies[100].performOperation(secondVIN)
		#TransportInc takes the car from RecoveryCO and delivers it to LocksmithCo
		Main.companies[201].performOperation(secondVIN, 100, 400)

		#Run mining simulation
		self.runMining()

		#LocksmithCo cuts keys for the car
		Main.companies[400].performOperation(secondVIN)	
		#TransportCo takes the car from LocksmithCo and delivers it to AuctionLLC
		Main.companies[200].performOperation(secondVIN, 400, 501)
		#AuctionLLC auctions the car
		Main.companies[501].performOperation(secondVIN)

		#Run mining simulation
		self.runMining()

		print("---------------------")

		self.trace(firstVIN)

		print("---------------------")

		self.trace(secondVIN)

		self.blockchain.writeToFile()

	def runMining(self):
		random.shuffle(self.miners)
		while(not Node.transactionPool.is_empty):
			newBlock = Block(Node.transactionPool.pop(), date.datetime.now(), self.blockchain.tip().hash)
			miner = None

			# While the hash is bigger than or equal to the difficulty continue to iterate the nonce
			while int(newBlock.hash_block(), 16) >= DIFFICULTY_HASH:
				newBlock.nonce += 1
				miner = self.miners[newBlock.nonce % len(self.miners)]
				newBlock.miner = miner

			#add found block to the chain
			self.blockchain.add(newBlock)


	def generateVIN(self):
		return ''.join(random.choices(string.ascii_uppercase + string.digits, k = self.VIN_length))    

	def trace(self, VIN):
		currentBlock = self.blockchain.tip()
		transactionHistory = []
		while(currentBlock.hash != '0'):
			if(currentBlock.data.split('|')[1] == VIN):
				data = currentBlock.data.split('|')
				operation = Operation(int(data[0]))	
				company = self.companies[int(data[2])]
				if(operation == Operation.RECOVER):
					transactionHistory.insert(0, f"{company.name}({company.id}) recovered VIN: {VIN}")
				elif(operation == Operation.TRANSPORT):
					transactionHistory.insert(0, f"{company.name}({company.id}) transported VIN: {VIN} from {self.companies[int(data[3])].name}({self.companies[int(data[3])].id}) to {self.companies[int(data[4])].name}({self.companies[int(data[4])].id})")	
				elif(operation == Operation.REPAIR):
					transactionHistory.insert(0, f"{company.name}({company.id}) repaired VIN: {VIN}")
				elif(operation == Operation.CUT_KEYS):
					transactionHistory.insert(0, f"{company.name}({company.id}) cut keys for VIN: {VIN}")
				elif(operation == Operation.AUCTION):
					transactionHistory.insert(0, f"{company.name}({company.id}) auctioned VIN: {VIN}")	
				else:
					transactionHistory.insert(0, "Operation not recognized")
			currentBlock = self.blockchain[currentBlock.previous_hash]

		for log in transactionHistory:
			print(log)

if __name__ == "__main__":	
	Main().run()