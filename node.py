from enum import Enum
from dataclasses import dataclass


class NodeNotFoundError(Exception):
    def __init__(self, node_id: str):
        super().__init__(f"Node '{node_id}' not found in graph.")


class NodeType(Enum):
    IDENTITY = "identity"
    RESOURCE = "resource"


class IdentityType(Enum):
    USER = "User"
    GROUP = "Group"
    SERVICE_ACCOUNT = "ServiceAccount"


class ResourceType(Enum):
    ORGANIZATION = "Organization"
    FOLDER = "Folder"
    PROJECT = "Project"


@dataclass(eq=True, frozen=True)
class Node:
    """
    Base class representing a graph node
    Each node has:
      - type: high-level category ('identity' or 'resource')
      - inner_type: sub-type (e.g. 'user', 'Folder', 'Project')
      - id: unique identifier
    """
    type: NodeType
    inner_type: str
    id: str

    def __str__(self):
        return f"{self.type.value}:{self.inner_type}:{self.id}"


class IdentityNode(Node):
    """Represents an identity (user, service account, group)"""

    def __init__(self, identity_id: str, inner_type: IdentityType):
        super().__init__(type=NodeType.IDENTITY,
                         inner_type=inner_type.value,
                         id=identity_id)


class ResourceNode(Node):
    """Represents a resource entity (Folder, Project, Organization)"""

    def __init__(self, resource_id: str, inner_type: ResourceType):
        super().__init__(type=NodeType.RESOURCE,
                         inner_type=inner_type.value,
                         id=resource_id)
