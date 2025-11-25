# **AI-Enhanced Supply Chain Knowledge Graph and Risk Modeling**

## **🎯 Project Goal**

Transform highly fragmented and inconsistent data (from forms, Excel sheets, and PDFs) into a unified Knowledge Graph for network analysis and resilience planning.

The workflow proceeds through three core stages:
- 1. Graph Construction: Entity Resolution (ER) and Relationship Extraction (RE)
  2. Structural Analysis: NetworkX's built in functions to find bottlenecks and paths
  3. Risk Quantification: Risk score calculation and Monte Carlo Simulation to calculate the final probabilistic disruption rate at the supply chain endpoint


## **🗂️ Code Files Description**

The project is structured into a logical, four-stage pipeline orchestrated by main.py.

| **File** | **Purpose** | **Functionality** |
| --- | --- | --- |
| data_simulator.py | **Data Ingestion** | Generates fragmented and inconsistent input data, mimicking real-world sources like human-filled forms (e.g. to provide flow), Excel sheets (e.g. to provide metadata), and PDFs (e.g. to provide context on risks). |
| graph_builder.py | **Graph Construction** | User input mappings for entity resolution (e.g., "Fxncn 3" = "Foxconn Facility No. 3") and infers relationships (Delivers $\rightarrow$ SUPPLIES). It then builds a NetworkX directed graph, aggregating attributes onto unique nodes. |
| graph_analyzer.py | **Graph Analysis** | Performs analysis on the following: **Centrality** (Betweenness to find bottlenecks, In-Degree to find hubs), **Clustering** (community detection to find tightly coupled groups), and **Traceability** (shortest path and upstream supplier audits). |
| risk_modeler.py | **Risk Modeling** | Implements two methods for risk assessment: 1) A **Deterministic Model** using inventory buffers for linear risk damping. 2) A **Monte Carlo Simulation** (1,000 runs) to calculate the probabilistic disruption rate, factoring in both local and cascade failures. |
| main.py | **Orchestration** | Executes the pipeline sequentially and prints the final consolidated report, including structural analysis results and the final simulated endpoint disruption probability. |

## **🌎 Difference from Real-World Deployment**

This project serves as a conceptual model. A production-ready solution would require significant scaling and complexity increases:

| **Feature** | **Current Settingl** | **Real-World Improvements** |
| --- | --- | --- |
| **Data Flow** | Small volume, static Python list | High volume, **streaming data** from connectors (APIs, S3/GCS, Databases). |
| **Dynamic mappings for entity resolution** | Simulated/Hardcoded Mapping | Relies on an external API (like Gemini) to dynamically generate canonical names and relationships. Likely achieved using a structured JSON schema and canonicalization rules to force the model to interpret inconsistent raw text and output validated entities. |
| **Database** | **NetworkX** (In-memory, non-persistent) | **Neo4j** or **Amazon Neptune** (Persistent, horizontally scalable graph databases). |
| **Pathfinding** | Unweighted path (counts hops) | **Weighted Paths** (e.g., weighted by $\text{CO}_2$ emissions, lead time, or shipping cost). |
| **Risk Data** | Single, static risk score | **Time-Series, Multi-Dimensional Risk Data** (e.g., political instability, climate risk, financial health, updated daily). |
| **Risk Model** | Linear damping | **Non-linear, Stochastic Simulations** using complex probability distributions. |
