"""AIOS Agent Registry - Factory and role management.

This module provides the agent registry system that manages agent
creation, discovery, and lifecycle.
"""

from typing import Any, Optional

import structlog

from aios.agents.base import AgentStatus, BaseAgent

logger = structlog.get_logger(__name__)


class AgentRegistry:
    """Registry for managing agent types and instances.

    The registry maintains a mapping of agent roles to their classes,
    and tracks all active agent instances.
    """

    _instance: Optional["AgentRegistry"] = None
    _agent_classes: dict[str, type[BaseAgent]] = {}
    _active_agents: dict[str, BaseAgent] = {}

    def __new__(cls) -> "AgentRegistry":
        """Singleton pattern to ensure one global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, agent_class: type[BaseAgent]) -> type[BaseAgent]:
        """Decorator to register an agent class.

        Args:
            agent_class: The agent class to register.

        Returns:
            The registered class (for use as decorator).
        """
        role = agent_class.ROLE
        cls._agent_classes[role] = agent_class
        logger.info("Agent registered", role=role, class_name=agent_class.__name__)
        return agent_class

    @classmethod
    def get_agent_class(cls, role: str) -> type[BaseAgent] | None:
        """Get the agent class for a given role.

        Args:
            role: The agent role to look up.

        Returns:
            The agent class, or None if not found.
        """
        return cls._agent_classes.get(role)

    @classmethod
    def list_roles(cls) -> list[str]:
        """List all registered agent roles.

        Returns:
            List of role names.
        """
        return list(cls._agent_classes.keys())

    @classmethod
    def list_agents(cls) -> list[dict[str, Any]]:
        """List all registered agent classes with metadata.

        Returns:
            List of agent metadata dictionaries.
        """
        return [
            {
                "role": role,
                "class_name": agent_class.__name__,
                "description": agent_class.DESCRIPTION,
                "capabilities": agent_class.CAPABILITIES,
            }
            for role, agent_class in cls._agent_classes.items()
        ]

    @classmethod
    def create_agent(
        cls,
        role: str,
        name: str | None = None,
        provider: str = "ollama",
        model: str = "llama3",
        config: dict[str, Any] | None = None,
    ) -> BaseAgent:
        """Create an agent instance for the given role.

        Args:
            role: The agent role to create.
            name: Optional custom name.
            provider: AI provider to use.
            model: Model to use.
            config: Additional configuration.

        Returns:
            An instance of the requested agent.

        Raises:
            ValueError: If the role is not registered.
        """
        agent_class = cls.get_agent_class(role)
        if agent_class is None:
            available = ", ".join(cls.list_roles())
            raise ValueError(
                f"Unknown agent role: '{role}'. Available roles: {available}"
            )

        agent = agent_class(
            name=name,
            provider=provider,
            model=model,
            config=config,
        )

        cls._active_agents[agent.agent_id] = agent
        logger.info(
            "Agent created",
            role=role,
            agent_id=agent.agent_id,
            name=agent.name,
        )

        return agent

    @classmethod
    def get_agent(cls, agent_id: str) -> BaseAgent | None:
        """Get an active agent by ID.

        Args:
            agent_id: The agent's unique ID.

        Returns:
            The agent instance, or None if not found.
        """
        return cls._active_agents.get(agent_id)

    @classmethod
    def remove_agent(cls, agent_id: str) -> bool:
        """Remove an agent from the active list.

        Args:
            agent_id: The agent's unique ID.

        Returns:
            True if removed, False if not found.
        """
        if agent_id in cls._active_agents:
            del cls._active_agents[agent_id]
            logger.info("Agent removed", agent_id=agent_id)
            return True
        return False

    @classmethod
    def get_active_agents(cls) -> list[dict[str, Any]]:
        """Get all active agents with their status.

        Returns:
            List of agent state dictionaries.
        """
        return [agent.to_dict() for agent in cls._active_agents.values()]

    @classmethod
    def get_agents_by_status(cls, status: AgentStatus) -> list[BaseAgent]:
        """Get all agents with a specific status.

        Args:
            status: The status to filter by.

        Returns:
            List of matching agents.
        """
        return [
            agent for agent in cls._active_agents.values()
            if agent.status == status
        ]

    @classmethod
    def clear_inactive(cls) -> int:
        """Remove all non-running agents from the active list.

        Returns:
            Number of agents removed.
        """
        to_remove = [
            agent_id for agent_id, agent in cls._active_agents.items()
            if agent.status not in (AgentStatus.RUNNING, AgentStatus.WAITING)
        ]
        for agent_id in to_remove:
            del cls._active_agents[agent_id]

        if to_remove:
            logger.info("Cleared inactive agents", count=len(to_remove))
        return len(to_remove)


class AgentFactory:
    """Factory for creating and configured agents.

    Provides a fluent interface for agent creation with method chaining.
    """

    def __init__(self):
        self._registry = AgentRegistry()
        self._role: str | None = None
        self._name: str | None = None
        self._provider: str = "ollama"
        self._model: str = "llama3"
        self._config: dict[str, Any] = {}

    def with_role(self, role: str) -> "AgentFactory":
        """Set the agent role."""
        self._role = role
        return self

    def with_name(self, name: str) -> "AgentFactory":
        """Set the agent name."""
        self._name = name
        return self

    def with_provider(self, provider: str) -> "AgentFactory":
        """Set the AI provider."""
        self._provider = provider
        return self

    def with_model(self, model: str) -> "AgentFactory":
        """Set the model."""
        self._model = model
        return self

    def with_config(self, **kwargs: Any) -> "AgentFactory":
        """Set additional configuration."""
        self._config.update(kwargs)
        return self

    def build(self) -> BaseAgent:
        """Build and return the agent instance.

        Returns:
            Configured agent instance.

        Raises:
            ValueError: If role is not set.
        """
        if self._role is None:
            raise ValueError("Agent role must be set before building")

        return self._registry.create_agent(
            role=self._role,
            name=self._name,
            provider=self._provider,
            model=self._model,
            config=self._config,
        )
