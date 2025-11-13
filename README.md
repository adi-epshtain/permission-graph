# Permission Graph

A generic **Python based graph model** for representing identities, resources, and permissions.

---

##  Overview

This project models users, groups, and resources as **nodes**, and their relationships (hierarchical or permission-based) as **directed edges**.  
It provides an extendable structure for analyzing access relationships and permission inheritance across resources.

---

##  Design

- **Graph-Oriented Architecture**  
  The system is based on a `Graph` class that manages all nodes (`IdentityNode`, `ResourceNode`) and edges (`ParentOfEdge`, `HasRoleEdge`).

- **Entity Separation**  
  - `Node` – base class for all entities (identity or resource).  
  - `Edge` – represents a relationship between nodes (e.g., ownership or hierarchy).

- **Extensible Edge Types**  
  The graph supports multiple relationship types via `EdgeType` enum:
  - `PARENT_OF` – defines resource hierarchy.  
  - `HAS_ROLE` – defines a permission relation between an identity and a resource.

---

##  Key Classes

| Class | Responsibility |
|--------|----------------|
| `Graph` | Core data structure managing nodes and edges |
| `Node` | Base entity (Identity or Resource) |
| `IdentityNode` | Represents a user, group, or service account |
| `ResourceNode` | Represents a resource (organization, folder, project) |
| `Edge` | Generic directed connection between nodes |
| `ParentOfEdge` | Hierarchical relationship between resources |
| `HasRoleEdge` | Role assignment between identity and resource |

---
Graph Structure Example (Resources Graph and Permission Graph):

                 ┌────────────────────────┐
                 │   Organization: org_1  │
                 └──────────┬─────────────┘
                            │  (PARENT_OF)
                            ▼
                 ┌────────────────────────┐
                 │     Folder: folder_1   │
                 └──────────┬─────────────┘
                            │  (PARENT_OF)
                            ▼
                 ┌────────────────────────┐
                 │     Project: project_1 │
                 └────────────────────────┘

          Identity: Adi (User)
                   │
                   │ (HAS_ROLE: owner)
                   ▼
         ┌────────────────────────┐
         │     Folder: folder_1   │
         └──────────┬─────────────┘
                    │  (PARENT_OF)
                    ▼
         ┌────────────────────────┐
         │     Project: project_1 │
         └────────────────────────┘
