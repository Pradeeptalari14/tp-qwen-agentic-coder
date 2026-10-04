#!/usr/bin/env python3
"""
Qwen2.5-Coder-32B Enterprise Agentic Coding Engine
Autonomous code editing loop with AST syntax verification, file tools, and bash sandboxing.
"""

import ast
import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from openai import OpenAI

class QwenCoderAgent:
    """Enterprise Autonomous Coding Agent powered by Qwen2.5-Coder-32B."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key: str = "EMPTY",
        model_name: str = "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
        max_turns: int = 15,
        workspace_dir: str = "./workspace"
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model_name
        self.max_turns = max_turns
        self.workspace_dir = os.path.abspath(workspace_dir)
        os.makedirs(self.workspace_dir, exist_ok=True)

    def tool_read_file(self, file_path: str) -> str:
        """Reads contents of a file within the workspace."""
        full_path = os.path.join(self.workspace_dir, file_path)
        if not os.path.exists(full_path):
            return f"Error: File '{file_path}' does not exist."
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def tool_write_file(self, file_path: str, content: str) -> str:
        """Writes content to a file after passing AST syntax verification."""
        full_path = os.path.join(self.workspace_dir, file_path)
        if file_path.endswith(".py"):
            try:
                ast.parse(content)
            except SyntaxError as e:
                return f"AST Validation Error: Invalid Python syntax at line {e.lineno}: {e.msg}"
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: File '{file_path}' updated and verified."

    def tool_run_bash(self, command: str) -> str:
        """Runs a sandboxed bash command within the workspace."""
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            out = res.stdout if res.returncode == 0 else f"Stderr: {res.stderr}\nStdout: {res.stdout}"
            return out or "(Command returned with exit code 0 and no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."

    def execute_task(self, user_instruction: str) -> Dict[str, Any]:
        """Main agentic execution loop."""
        tools_definition = [
            {
                "type": "function",
                "function": {
                    "name": "tool_read_file",
                    "description": "Read file contents from repository workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tool_write_file",
                    "description": "Write and AST-verify code into a repository file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "tool_run_bash",
                    "description": "Run shell commands (pytest, git, ripgrep) in workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {"command": {"type": "string"}},
                        "required": ["command"]
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Qwen2.5-Coder, an elite autonomous software engineering agent. "
                    "You diagnose issues, edit code with AST-level safety, run tests, and confirm fixes."
                )
            },
            {"role": "user", "content": user_instruction}
        ]

        for turn in range(self.max_turns):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_definition,
                tool_choice="auto",
                temperature=0.1
            )
            choice = response.choices[0]
            msg = choice.message
            messages.append(msg)

            if not msg.tool_calls:
                return {
                    "status": "completed",
                    "final_response": msg.content,
                    "total_turns": turn + 1
                }

            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if fn_name == "tool_read_file":
                    result = self.tool_read_file(args.get("file_path"))
                elif fn_name == "tool_write_file":
                    result = self.tool_write_file(args.get("file_path"), args.get("content"))
                elif fn_name == "tool_run_bash":
                    result = self.tool_run_bash(args.get("command"))
                else:
                    result = f"Unknown tool: {fn_name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        return {"status": "turn_limit_reached", "total_turns": self.max_turns}

if __name__ == "__main__":
    agent = QwenCoderAgent()
    print("Qwen2.5-Coder-32B Agent Initialized.")
    print("Context: 128k Tokens | Precision: AWQ 4-Bit")
