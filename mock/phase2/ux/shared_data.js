const SHARED_DATA = {
    user: {
        name: "Power",
        level: 25,
        class: "Strategic Executor",
        xp: { current: 2800, max: 3000 },
        attributes: {
            growth_rate: 85,    // O2 Metric: Capability
            wealth_flow: 42,    // O2 Metric: Income
            influence: 60,      // O2 Metric: Influence
            clarity: 75         // KR0 Metric: Review Quality
        }
    },
    okrs: [
        {
            id: "o2",
            code: "O2",
            title: "Personal Growth (Q4)",
            metric: "Growth Rate",
            progress: 45,
            krs: [
                {
                    id: "kr0",
                    code: "KR0",
                    title: "Active Review (Highest Priority)",
                    status: "At Risk",
                    progress: 30,
                    projects: ["p1", "p3"] // MIRIX, VeryLoving
                },
                {
                    id: "kr1",
                    code: "KR1",
                    title: "Capability Growth",
                    status: "On Track",
                    progress: 60,
                    projects: ["p1"] // MIRIX
                }
            ]
        }
    ],
    projects: [
        {
            id: "p1",
            name: "MIRIX",
            type: "Dev",
            priority: "High",
            status: "Active",
            context: "Building Phase 2 SDK",
            tasks_today: ["t1", "t2"]
        },
        {
            id: "p2",
            name: "Dad & Daughter",
            type: "Life",
            priority: "Medium",
            status: "Active",
            context: "Quality Time",
            tasks_today: ["t3"]
        },
        {
            id: "p3",
            name: "VeryLoving",
            type: "Biz",
            priority: "Low",
            status: "Pending",
            context: "Maintenance",
            tasks_today: []
        }
    ],
    daily_tasks: [
        {
            id: "t1",
            title: "Design Phase 2 Ontology",
            project_id: "p1",
            completed: false,
            rpg_val: "+100 XP (Intelligence)",
            cockpit_val: "Focus: Deep Work"
        },
        {
            id: "t2",
            title: "Fix Chat History Bug",
            project_id: "p1",
            completed: true,
            rpg_val: "+50 XP (Engineering)",
            cockpit_val: "Status: Done"
        },
        {
            id: "t3",
            title: "Read Bedtime Story",
            project_id: "p2",
            completed: false,
            rpg_val: "+30 XP (Love)",
            cockpit_val: "Mode: Disconnect"
        }
    ],
    insights: [
        {
            type: "warning",
            msg: "KR0 (Active Review) is falling behind schedule.",
            rpg_msg: "Oracle Alert: Review ritual missed yesterday.",
            cockpit_msg: "Suggestion: Schedule 15m review at 20:00."
        },
        {
            type: "success",
            msg: "MIRIX development velocity is high.",
            rpg_msg: "Buff: 'Flow State' active (+20% XP).",
            cockpit_msg: "System: Optimal Performance."
        }
    ]
};
