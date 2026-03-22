import os
import sys
import logging
import asyncio
from dao.core.orchestrator import Orchestrator
from dao.governance.protocol import GovernanceProtocol
from dao.agents.registry import AgentRegistry

# Initialize the Orchestrator
orchestrator = Orchestrator()

# Register governance protocol
governance_protocol = GovernanceProtocol()
orchestrator.register_governance_protocol(governance_protocol)

# Register agent types
agent_registry = AgentRegistry()
agent_registry.register_agent_type("scraper", ScraperAgent)
agent_registry.register_agent_type("task_agent", TaskAgent)
agent_registry.register_agent_type("decision_maker", DecisionMakerAgent)

# Start the Orchestrator
orchestrator.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(orchestrator.run())