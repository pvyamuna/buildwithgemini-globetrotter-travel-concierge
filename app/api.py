"""Public Python API Library for Globetrotter Travel Concierge.

Allows developers and external downstream applications to programmatically import,
interact with, and execute tool-augmented queries against the Globetrotter ADK Agent.
"""

import asyncio
from typing import Any, Dict, List, Optional

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import app as default_app, root_agent


class GlobetrotterClient:
    """High-level Python API client for the Globetrotter Travel Concierge Agent."""

    def __init__(self, app_instance=None, user_id: str = "api-user", session_service=None):
        """Initialize the Globetrotter Agent API client.

        Args:
            app_instance: ADK App instance. Defaults to root app in app.agent.
            user_id: Unique identifier for tracking conversation session state.
            session_service: Optional ADK SessionService instance. Defaults to InMemorySessionService.
        """
        self.app = app_instance or default_app
        self.user_id = user_id
        self.session_service = session_service or InMemorySessionService()
        self.runner = Runner(
            app=self.app,
            session_service=self.session_service,
            auto_create_session=True,
        )

    def list_available_tools(self) -> List[str]:
        """Returns names of all registered tools on the root agent."""
        return [getattr(t, "__name__", str(t)) for t in root_agent.tools]

    async def async_query(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Asynchronously executes a user query against the agent.

        Args:
            message: User query string (e.g. 'Search travel packages for Tokyo').
            session_id: Optional session ID string.

        Returns:
            Dict containing 'text' response, 'parts', and 'status'.
        """
        sid = session_id or f"session_{self.user_id}"
        
        # Verify or create session
        session = await self.session_service.get_session(app_name=self.app.name, user_id=self.user_id, session_id=sid)
        if session is None:
            session = await self.session_service.create_session(app_name=self.app.name, user_id=self.user_id, session_id=sid)

        response_parts = []
        user_content = types.Content(
            parts=[types.Part.from_text(text=message)],
            role="user",
        )

        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.session_id,
            new_message=user_content,
        ):
            if hasattr(event, "content") and event.content:
                for p in getattr(event.content, "parts", []):
                    if hasattr(p, "text") and p.text:
                        response_parts.append(p.text)

        full_text = "\n".join(response_parts) if response_parts else "(No text returned)"
        return {
            "status": "success",
            "message": message,
            "session_id": session.session_id,
            "text": full_text,
            "parts": response_parts,
        }

    def query(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Synchronously executes a user query against the agent.

        Args:
            message: User query string.
            session_id: Optional session ID string.

        Returns:
            Dict containing response payload.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.async_query(message=message, session_id=session_id))
        else:
            return loop.run_until_complete(self.async_query(message=message, session_id=session_id))


def run_agent_query(message: str, user_id: str = "default-user") -> Dict[str, Any]:
    """Convenience functional API to run a single query against Globetrotter Agent.

    Example:
        >>> from app import run_agent_query
        >>> result = run_agent_query("Calculate 7-day Tokyo travel budget")
        >>> print(result["text"])
    """
    client = GlobetrotterClient(user_id=user_id)
    return client.query(message=message)
