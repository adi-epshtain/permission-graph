import logging
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, TypeAlias, Optional, Iterator
from edge import Edge, EdgeType, HasRoleEdge, RoleType
from node import Node, NodeNotFoundError

NodeId: TypeAlias = str
SourceNodeId: TypeAlias = str
TargetNodeId: TypeAlias = str


@dataclass(frozen=True)
class PermissionEntry:
    resource_id: str
    resource_type: str
    role: RoleType


class Graph:
    """
    Generic graph implementation for representing permission structures.
    Keeps separate collections for nodes & edges, supports multiple edge types
    O(1) lookup for nodes and their incoming/outgoing edges
    """

    def __init__(self):
        self.nodes: Dict[NodeId, Node] = {}

        # outgoing edges per source node
        self.out_edges: Dict[SourceNodeId, List[Edge]] = defaultdict(list)

        # incoming edges per target node
        self.in_edges: Dict[TargetNodeId, List[Edge]] = defaultdict(list)

    # -------------------- Node Management --------------------

    def add_node(self, node: Node) -> None:
        """Add a node if it does not already exist"""
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[Node]:
        """Return a node by its ID, or None if not found"""
        return self.nodes.get(node_id)

    # -------------------- Edge Management --------------------

    def add_edge(self, edge: Edge) -> None:
        """Add an edge between existing nodes"""
        if edge.source.id not in self.nodes or edge.target.id not in self.nodes:
            raise ValueError("source and target nodes must exist before "
                             "adding an edge")
        self.out_edges[edge.source.id].append(edge)
        self.in_edges[edge.target.id].append(edge)

    def iter_out_edges(self, node_id: str) -> Iterator[Edge]:
        """Yield all outgoing edges from the given node"""
        for edge in self.out_edges.get(node_id, []):
            yield edge

    def iter_in_edges(self, node_id: str) -> Iterator[Edge]:
        """Yield all incoming edges to the given node"""
        for edge in self.in_edges.get(node_id, []):
            yield edge

    # -------------------- Utils Methods --------------------

    def iter_children(self, node_id: str) -> Iterator[Node]:
        """Yield all direct child nodes (PARENT_OF edges only)"""
        for edge in self.out_edges.get(node_id, []):
            if edge.type == EdgeType.PARENT_OF:
                yield edge.target

    def _iter_descendants(self, node_id: str) -> Iterator[Node]:
        """Depth-first traversal yielding all descendant nodes recursively"""
        for child in self.iter_children(node_id):
            yield child
            # recurse lazily – yields grandchildren as well
            yield from self._iter_descendants(child.id)

    def iter_parents(self, node_id: str) -> Iterator[Node]:
        """Yield all parent nodes for a given child node (PARENT_OF edges only)"""
        for edge in self.in_edges.get(node_id, []):
            if edge.type == EdgeType.PARENT_OF:
                yield edge.source

    def __str__(self):
        return "\n".join(
            [f"{src} -> {[str(e) for e in edges]}" for src, edges in self.out_edges.items()]
        )

    def print_resource_tree(self, root_id: NodeId, spaces: int = 0) -> None:
        """Recursively print the resource hierarchy as an indented tree"""
        node: Optional[Node] = self.get_node(root_id)
        if not node:
            raise NodeNotFoundError(root_id)

        print(" " * spaces + f"- {node.id}")
        for child in self.iter_children(root_id):
            self.print_resource_tree(child.id, spaces + 4)

    # Task 2
    def iter_resource_hierarchy(self, resource_id: str) -> Iterator[Node]:
        """
        Yield all ancestor resource IDs for a given resource.
        Supports multiple parents and avoids infinite loops.
        Traverses upwards in the resource graph (BFS style).
        """
        visited = set()
        queue = deque([resource_id])

        while queue:
            current_id = queue.popleft()
            for parent in self.iter_parents(current_id):
                if parent.id in visited:
                    continue
                visited.add(parent.id)
                yield parent
                queue.append(parent.id)

    # Task 3
    def iter_user_permissions(self, node_identity_id: str) -> Iterator[PermissionEntry]:
        """
        Yield permissions (resource_id, resource_type, role) for a given identity
        Includes permissions inherited down the resource hierarchy
        Time complexity: O(V + E) - each node and edge visited once (DFS traversal)
        """
        identity_node: Optional[Node] = self.get_node(node_identity_id)
        if not identity_node:
            raise NodeNotFoundError(node_identity_id)

        # Get all outgoing HAS_ROLE edges for this identity
        for edge in self.iter_out_edges(node_identity_id):
            if edge.type != EdgeType.HAS_ROLE:
                continue

            target_resource: Node = edge.target
            edge: HasRoleEdge  # type hint
            role = edge.role
            logging.debug(
                f"User {identity_node.id} has role {role} on {target_resource.id}")

            # yield direct permission
            yield PermissionEntry(
                resource_id=target_resource.id,
                resource_type=target_resource.inner_type,
                role=role,
            )

            # yield inherited permissions (descendants)
            for descendant_node in self._iter_descendants(
                    target_resource.id):
                yield PermissionEntry(
                    resource_id=descendant_node.id,
                    resource_type=descendant_node.inner_type,
                    role=role,
                )
