from src.graph_store import build_graph, retrieve_graph_evidence

def sample_graph():
    return build_graph([{
        "entities": [
            {"name": "Acme Payments", "type": "Company"},
            {"name": "Orion API Gateway", "type": "System"},
            {"name": "Platform Engineering", "type": "Team"},
            {"name": "Priya Sharma", "type": "Person"},
        ],
        "relationships": [
            {"source": "Acme Payments", "type": "USES", "target": "Orion API Gateway",
             "evidence": "Acme Payments uses Orion API Gateway.", "source_document": "doc1.txt"},
            {"source": "Orion API Gateway", "type": "MAINTAINED_BY", "target": "Platform Engineering",
             "evidence": "The gateway is maintained by Platform Engineering.", "source_document": "doc1.txt"},
            {"source": "Platform Engineering", "type": "LED_BY", "target": "Priya Sharma",
             "evidence": "The team is led by Priya Sharma.", "source_document": "doc1.txt"},
        ],
    }])

def test_graph_contains_expected_edges():
    graph = sample_graph()
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 3

def test_two_hop_question_finds_team_path():
    result = retrieve_graph_evidence(
        "Which team maintains the gateway used by Acme Payments?",
        sample_graph()
    )
    assert result["path"] == [
        "Acme Payments", "Orion API Gateway", "Platform Engineering"
    ]

def test_three_hop_question_finds_leader_path():
    result = retrieve_graph_evidence(
        "Who leads the team that maintains the gateway used by Acme Payments?",
        sample_graph()
    )
    assert result["path"] == [
        "Acme Payments", "Orion API Gateway",
        "Platform Engineering", "Priya Sharma"
    ]
