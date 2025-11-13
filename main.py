from edge import ParentOfEdge, HasRoleEdge, RoleType
from graph import Graph
from node import ResourceNode, IdentityNode, ResourceType, IdentityType

USER = "adi@test.com"
ORGANIZATION = "Organization1"


def build_demo_graph() -> Graph:
    """Build a demo resource hierarchy graph with user-role assignments."""
    g = Graph()

    # Define resource hierarchy (parent -> [children])
    hierarchy = {
        ORGANIZATION: ["Folder1", "Folder2", "Folder3", "Folder4"],
        "Folder1": ["Folder5"],
        "Folder5": ["Folder6"],
    }

    # Create all resource nodes
    nodes: dict[str, ResourceNode] = {}
    for parent, children in hierarchy.items():
        if parent not in nodes:
            parent_type = (
                ResourceType.ORGANIZATION
                if "Org" in parent or "Organization" in parent
                else ResourceType.FOLDER
            )
            parent_node = ResourceNode(resource_id=parent, inner_type=parent_type)
            nodes[parent] = parent_node
            g.add_node(parent_node)

        for child in children:
            child_node = ResourceNode(resource_id=child, inner_type=ResourceType.FOLDER)
            nodes[child] = child_node
            g.add_node(child_node)
            g.add_edge(ParentOfEdge(parent=nodes[parent], child=nodes[child]))

    # Create user and assign role
    user = IdentityNode(identity_id=USER, inner_type=IdentityType.USER)
    g.add_node(user)
    g.add_edge(HasRoleEdge(identity=user, resource=nodes["Folder1"], role=RoleType.OWNER))

    return g


if __name__ == "__main__":
    graph = build_demo_graph()

    print("\n--- RESOURCE TREE ---")
    graph.print_resource_tree(ORGANIZATION)

    print("\n--- RESOURCE HIERARCHY (Folder6) ---")
    print("Expected: Folder5 → Folder1 → Organization1")
    for node in graph.iter_resource_hierarchy("Folder6"):
        print(f"-> {node.id}")

    print("\n--- USER PERMISSIONS ---")
    print(f"{'Resource ID':<15} | {'Type':<10} | {'Role':<10}")
    print("-" * 40)
    found = False
    for permission in graph.iter_user_permissions(USER):
        found = True
        print(f"{permission.resource_id:<15} | {permission.resource_type:<10} | {permission.role.value:<10}")
    if not found:
        print("No permissions found.")
