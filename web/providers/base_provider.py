"""
Base Provider Class for APEX API Callers
"""

import asyncio
import json
import os
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any


class BaseProvider(ABC):
    """Base class for all service providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.config = {}
        self.connections = {}
    
    @abstractmethod
    async def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get current authentication/connection status"""
        pass
    
    async def execute_command(self, command: str, env: Optional[Dict[str, str]] = None, stream_output: bool = True) -> Dict[str, Any]:
        """Execute a command and return structured result with real-time streaming"""
        try:
            # Set up environment
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Show command being executed
            if stream_output:
                await self.broadcast_message({
                    'type': 'command_output',
                    'data': {
                        'output': f'⚡ {command}',
                        'context': self.name
                    }
                })
            
            # Use async subprocess for real-time streaming
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=exec_env,
                cwd=os.getcwd()
            )
            
            stdout_data = []
            stderr_data = []
            
            # Stream stdout in real-time
            async def stream_stdout():
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode().rstrip()
                    stdout_data.append(line_str)
                    if stream_output and line_str:
                        await self.broadcast_message({
                            'type': 'command_output',
                            'data': {
                                'output': line_str,
                                'context': self.name
                            }
                        })
            
            # Stream stderr in real-time
            async def stream_stderr():
                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break
                    line_str = line.decode().rstrip()
                    stderr_data.append(line_str)
                    if stream_output and line_str:
                        await self.broadcast_message({
                            'type': 'command_output',
                            'data': {
                                'output': line_str,
                                'context': self.name
                            }
                        })
            
            # Run both streams concurrently
            await asyncio.gather(stream_stdout(), stream_stderr())
            
            # Wait for process to complete
            return_code = await process.wait()
            
            return {
                'success': return_code == 0,
                'exit_code': return_code,
                'stdout': '\n'.join(stdout_data),
                'stderr': '\n'.join(stderr_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Send message to all connected clients (to be implemented by main app)"""
        # This will be overridden by the main application
        pass
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get provider-specific environment variables"""
        return {}