import json
import asyncio
from typing import Dict, List
from web3 import Web3

class Orchestrator:
    def __init__(self, config: Dict):
        self.config = config
        self.chains = {}

    async def initialize(self):
        for chain_config in self.config['chains']:
            chain = await self.initialize_chain(chain_config)
            self.chains[chain_config['name']] = chain

    async def initialize_chain(self, config: Dict) -> 'ChainAdapter':
        provider = Web3.HTTPProvider(config['rpc_url'])
        w3 = Web3(provider)
        return ChainAdapter(w3, config)

    async def execute_workflow(self, workflow: Dict):
        tasks = []
        for step in workflow['steps']:
            chain_name = step['chain']
            chain = self.chains[chain_name]
            task = asyncio.create_task(chain.execute_step(step))
            tasks.append(task)
        await asyncio.gather(*tasks)

class ChainAdapter:
    def __init__(self, w3: Web3, config: Dict):
        self.w3 = w3
        self.config = config

    async def execute_step(self, step: Dict):
        contract = self.w3.eth.contract(
            address=step['contract_address'],
            abi=json.load(open(step['abi_path']))
        )
        tx = contract.functions[step['function']](
            *step['args']
        ).build_transaction({
            'from': self.config['wallet_address'],
            'gasPrice': self.w3.toWei('50', 'gwei'),
            'nonce': self.w3.eth.getTransactionCount(self.config['wallet_address'])
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, private_key=self.config['private_key'])
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return tx_receipt
