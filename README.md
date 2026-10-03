# Glorp-Cat

> A local, multi-model AI agent with a browser-based interface, built to keep capable AI workflows on your own hardware.

<p align="center">
  <img src="media/glorpCat.png" alt="Glorp Cat" width="400">
</p>

<p align="center"><em>My king, my GOAT.</em></p>

## What is Glorp-Cat?

Glorp-Cat is a Python-based local AI assistant that brings together local language models, tool calling, and retrieval-augmented generation (RAG) in one system. Its goal is to provide a practical agent that can run on personal hardware while still having a clean browser UI for everyday use.

The project is designed around a simple idea: keep routine work local, use tools when the model needs information or actions, and reserve external AI assistance for tasks that genuinely exceed the local system's capabilities.

## Current capabilities

- Streamed chat responses in both the command-line interface and browser UI
- Local-model support with thinking and tool-calling workflows
- A FastAPI-powered web interface
- Model response statistics, including token usage, generation speed, tool use, and timing
- MCP-based tool integration for extensible agent capabilities
- An in-development RAG pipeline for injecting and searching project documents

## Architecture

Glorp-Cat keeps each responsibility separate so the project can grow without turning into one giant script:

| Component | Role |
| --- | --- |
| Local model backend | Runs the language model and produces chat/tool-call responses. |
| Agent layer | Coordinates messages, reasoning output, tool calls, and final responses. |
| MCP tools | Adds capabilities such as search and other external actions through a standard interface. |
| RAG pipeline | Parses, chunks, embeds, and retrieves information from local documents. |
| FastAPI browser UI | Provides a more convenient interface than the terminal while using the same backend. |

## Requirements

Glorp-Cat is intended for a local model that supports both **thinking** and **tool calling**. A capable GPU and sufficient VRAM/RAM are strongly recommended, especially for larger models or longer context windows.

The project is being developed and tested primarily on Linux with Python.

## Getting started

The browser UI is served through FastAPI. From the project directory, start the application's FastAPI server, then open the local address shown in the terminal in your browser.

The command-line version remains available for directly interacting with the agent from a terminal.

> Exact setup commands and configuration details will be documented here as the project structure stabilizes.

## Project direction

Current development is focused on finishing the document-ingestion pipeline and improving the browser UI. Longer-term work includes:

- Better document parsing, chunking, and image-aware retrieval
- ChromaDB-backed retrieval alongside Neo4j knowledge-graph/GraphRAG support
- A graphical document-ingestion workflow
- Additional quality-of-life improvements for the UI
- An optional agent-loop mode for executing user-defined workflows with minimal human intervention

## Status

Glorp-Cat is actively under development. Functionality and reliability take priority over visual polish while the core agent, tools, and RAG system are being built out.

## Why local?

Running locally gives you more control over your data, your models, and your workflow. Glorp-Cat is not trying to replace every cloud model; it is built to make local AI useful enough to handle the work that should stay on your machine.
