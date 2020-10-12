# Module 2 - Create a Cryptocurrency
# To be installed: 
# Flask : pip install Flask
# Postman HTTP client: www.getpostman.com
# requests: pip install requests

# Importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self):
       self.chain = []
       self.transactions = []
       self.create_block(proof = 1, previous_hash = '0') # genesis block, sha256 output is a string
       self.nodes = set()
       
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        
        # txns must be cleared once added in the block to avoid duplicate
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1] # -1 refers to the last index in the list
    
    # This is the target threshold set by the network for the miners to solve
    def proof_of_work(self, previous_proof):
        new_proof = 1;
        check_proof = False
        # Trial and error generation of hash 
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
            
    # This will return the SHA256 hash value of the block/data
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    # Validation of the chain
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            '''
            Checkif the current block's previous hash 
                is not equal to the hash value of previous block
            '''
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                    return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block();
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    # This function will primarily be used as part of the consensuss
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # the length of this node is longer, then update
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            # Check if longest_chain is not None anymore (hence, replaced)
            if longest_chain: 
                self.chain = longest_chain    
                return True
            return False # Else, not yet replaced

# Part 2- Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain() # this is the same as Instantiation

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Kirill', amount = 100)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Check if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    # check if not all the keys in txn_keys list are not in json
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201 # HTTP Status code Created

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes or simply connecting to the blockchain network
# You need to provide the ip address of the nodes that are in the network
# Note: nodes must be pulled somewhere (in the network) instead of sending a json file... 
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Jcoin Blockchain now contains the following nodes',
                'total_nodes': list(blockchain.nodes)}
    return response, 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes have different chains. Blockchain has been replaced with the longest chain.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The Blockchain is the largest chain.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200
    
# Running the app using Flask
app.run(host = '0.0.0.0', port = '5002')
