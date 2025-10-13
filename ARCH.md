# Big-Hammer Architecture

## 1. High-Level Concept

`big-hammer` is designed as a "smart execution wrapper." Its primary role is to monitor a command for failure. If a failure is detected, it orchestrates a process of automated diagnosis and remediation by interfacing with an external Large Language Model (LLM).

The architecture is founded on three core principles:
1.  **Immutability:** The user's original script or files are never modified.
2.  **Delegation:** The complex task of interacting with LLM APIs is delegated to a specialized, external tool. `big-hammer` does not manage API keys or network communication with the LLM provider.
3.  **Automation:** The entire process is non-interactive, making it suitable for use in automated workflows and scripts.

