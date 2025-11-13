import pytest
from graph import Graph
from edge import ParentOfEdge, HasRoleEdge, EdgeType, RoleType
from node import NodeNotFoundError, ResourceNode, IdentityNode, \
    ResourceType, IdentityType


@pytest.fixture
def graph():
    """Create a reusable test graph fixture"""
    g = Graph()

    # Create resources
    org = ResourceNode("org_1", ResourceType.ORGANIZATION)
    folder = ResourceNode("folder_1", ResourceType.FOLDER)
    project = ResourceNode("project_1", ResourceType.PROJECT)

    # Create user
    user = IdentityNode("adi@test.com", IdentityType.USER)

    # Add nodes
    for node in [org, folder, project, user]:
        g.add_node(node)

    # Connect edges
    g.add_edge(ParentOfEdge(org, folder))
    g.add_edge(ParentOfEdge(folder, project))
    g.add_edge(HasRoleEdge(user, folder, RoleType.OWNER))

    return g, org, folder, project, user


# -------------------- Node Management --------------------

def test_add_node(graph):
    g, _, folder, _, _ = graph
    assert folder.id in g.nodes
    assert isinstance(g.get_node("folder_1"), ResourceNode)
    assert g.get_node("nonexistent") is None


def test_add_edge_validation(graph):
    g, _, _, _, _ = graph
    # Create a node not in graph
    fake_folder = ResourceNode("fake_folder", ResourceType.FOLDER)
    org = g.get_node("org_1")
    with pytest.raises(ValueError):
        g.add_edge(ParentOfEdge(org, fake_folder))


# -------------------- Edge Iterators --------------------

def test_iter_out_edges(graph):
    g, _, folder, project, _ = graph
    out_edges = list(g.iter_out_edges(folder.id))
    assert any(e.target.id == project.id for e in out_edges)
    assert all(hasattr(e, "source") and hasattr(e, "target") for e in out_edges)


def test_iter_in_edges(graph):
    g, _, folder, project, _ = graph
    in_edges = list(g.iter_in_edges(project.id))
    assert any(e.source.id == folder.id for e in in_edges)
    assert all(e.type == EdgeType.PARENT_OF for e in in_edges)


# -------------------- Hierarchy traversal --------------------

def test_iter_children(graph):
    g, org, folder, _, _ = graph
    children = list(g.iter_children(org.id))
    assert len(children) == 1 and children[0].id == folder.id


def test_iter_parents(graph):
    g, org, folder, _, _ = graph
    parents = list(g.iter_parents(folder.id))
    assert len(parents) == 1 and parents[0].id == org.id


def test_iter_descendants(graph):
    g, org, folder, project, _ = graph
    descendants = list(g._iter_descendants(org.id))
    ids = [n.id for n in descendants]
    assert "folder_1" in ids and "project_1" in ids


def test_iter_resource_hierarchy(graph):
    g, org, folder, project, _ = graph
    hierarchy = [n.id for n in g.iter_resource_hierarchy(project.id)]
    assert hierarchy == ["folder_1", "org_1"]


def test_iter_resource_hierarchy_no_parents(graph):
    g, org, _, _, _ = graph
    assert list(g.iter_resource_hierarchy(org.id)) == []


# -------------------- Permissions --------------------

def test_iter_user_permissions_direct(graph):
    g, _, folder, _, user = graph
    perms = list(g.iter_user_permissions(user.id))
    assert any(p.resource_id == folder.id and p.role == RoleType.OWNER for p in perms)


def test_iter_user_permissions_inherited(graph):
    g, _, folder, project, user = graph
    perms = list(g.iter_user_permissions(user.id))
    ids = [p.resource_id for p in perms]
    assert "folder_1" in ids and "project_1" in ids  # inherited


def test_iter_user_permissions_invalid_user(graph):
    g, *_ = graph
    with pytest.raises(NodeNotFoundError):
        list(g.iter_user_permissions("ghost@test.com"))


# -------------------- Printing & String --------------------

def test_graph_str(graph):
    g, *_ = graph
    result = str(g)
    assert "parent_of" in result
    assert "has_role" in result


def test_print_resource_tree(capsys, graph):
    g, org, *_ = graph
    g.print_resource_tree(org.id)
    output = capsys.readouterr().out
    assert "org_1" in output
    assert "folder_1" in output
