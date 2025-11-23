const MOCK_DATA = {
    user: {
        name: "Founder",
        role: "Independent Entrepreneur",
        level: "Phase 2: Reflection"
    },
    network: {
        velocity: "+12 nodes/week",
        total_nodes: 148,
        recent_connections: [
            { id: "p1", name: "Alex Chen", role: "AI Researcher", tag: "High Value", date: "2024-11-20" },
            { id: "p2", name: "Sarah Jones", role: "Product Lead", tag: "Mentor", date: "2024-11-18" },
            { id: "p3", name: "David Kim", role: "VC Associate", tag: "Funding", date: "2024-11-15" }
        ],
        graph_nodes: [
            { id: 1, label: "YOU", group: "center" },
            { id: 2, label: "AI Learning", group: "goal" },
            { id: 3, label: "Startup Network", group: "goal" },
            { id: 4, label: "Alex Chen", group: "person" },
            { id: 5, label: "Sarah Jones", group: "person" },
            { id: 6, label: "David Kim", group: "person" },
            { id: 7, label: "Transformer Arch", group: "skill" },
            { id: 8, label: "Product Strategy", group: "skill" }
        ],
        graph_edges: [
            { from: 1, to: 2 },
            { from: 1, to: 3 },
            { from: 2, to: 4 },
            { from: 3, to: 5 },
            { from: 3, to: 6 },
            { from: 4, to: 7 },
            { from: 5, to: 8 }
        ]
    },
    communication: {
        weekly_score: 8.5,
        trend: "up",
        insights: [
            { type: "warning", text: "Speaking too fast in technical explanations (180wpm)" },
            { type: "success", text: "Excellent use of Pyramid Principle in VC pitch" },
            { type: "opportunity", text: "Missed follow-up with Sarah regarding 'Product Strategy'" }
        ],
        recent_conversations: [
            { topic: "Deep Seek Arch", partner: "Alex Chen", structure_score: 9.2, empathy_score: 7.5 },
            { topic: "Seed Round", partner: "David Kim", structure_score: 8.8, empathy_score: 6.0 },
            { topic: "Roadmap Review", partner: "Team", structure_score: 7.0, empathy_score: 8.5 }
        ]
    },
    system_building: {
        phase: "Phase 2: Mirror",
        progress: 65,
        next_milestone: "Goal Reasoning Engine",
        recent_commits: [
            { id: "c102", msg: "feat: Add daily reflection loop", time: "2h ago" },
            { id: "c101", msg: "fix: OCR accuracy optimization", time: "5h ago" },
            { id: "c100", msg: "docs: Update Phase 2 Roadmap", time: "1d ago" }
        ],
        metrics: {
            "Recall Accuracy": "94%",
            "Insight Rate": "3.2/day",
            "System Uptime": "99.9%"
        }
    }
};
