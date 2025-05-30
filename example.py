#!/usr/bin/env python

import asyncio
import os
import yaml
from roles.researcher import Researcher
from utils.llm import OpenAIClient

async def main():
    # Load configuration
    with open("config2.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize OpenAI client
    llm = OpenAIClient(
        api_key=config["llm"]["api_key"],
        model=config["llm"]["model"]
    )
    
    # Create researcher instance
    researcher = Researcher(language="en-us")
    
    # Set LLM for all actions
    for action in researcher.actions:
        action.llm = llm
    
    # Run research
    topic = "The impact of artificial intelligence on healthcare"
    report = await researcher.run(topic)
    
    print("\nResearch Report:")
    print(report.content)
    
    # Save report to file
    os.makedirs("research_reports", exist_ok=True)
    researcher.write_report(topic, report.content)

if __name__ == "__main__":
    asyncio.run(main()) 