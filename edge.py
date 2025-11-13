from dataclasses import dataclass
from enum import Enum
from node import Node


class RoleType(Enum):
    OWNER = "owner"
    VIEWER = "viewer"
    EDITOR = "editor"


class EdgeType(Enum):
    """Defines supported relationship types between nodes"""
    PARENT_OF = "parent_of"
    HAS_ROLE = "has_role"


@dataclass(eq=True)
class Edge:
    """
    Represents a directed relationship between two nodes in the graph
    """
    source: Node
    target: Node
    type: EdgeType

    def __str__(self):
        return f"{self.source.id} -[{self.type.value}]-> {self.target.id}"


class ParentOfEdge(Edge):
    """Represents parent-child relationship between resources"""

    def __init__(self, parent: Node, child: Node):
        super().__init__(source=parent, target=child, type=EdgeType.PARENT_OF)


class HasRoleEdge(Edge):
    """Represents role assignment of an identity on a resource"""
    role: RoleType

    def __init__(self, identity: Node, resource: Node, role: RoleType):
        super().__init__(source=identity, target=resource,
                         type=EdgeType.HAS_ROLE)
        self.role = role

    def __str__(self):
        return f"{self.source.id} -[{self.type.value}:{self.role}]-> " \
               f"{self.target.id}"
