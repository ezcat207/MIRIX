const MECH_DATA = {
    pilot: {
        name: "Power",
        rank: "Commander",
        metrics: {
            growth: { label: "Capability", value: 85, trend: "+2.1%" },
            wealth: { label: "Income", value: 42, trend: "+0.5%" },
            influence: { label: "Influence", value: 60, trend: "+1.2%" }
        },
        kr0: {
            label: "Active Review (KR0)",
            progress: 30, // %
            status: "At Risk",
            streak: 2 // days
        }
    },
    mechs: [
        {
            id: "m1",
            name: "MIRIX-01",
            type: "Strategic",
            status: "Ready",
            project_ref: "Project 1: MIRIX",
            description: "Building the Phase 2 SDK & Ontology.",
            why: "To build an external prefrontal cortex that guarantees goal achievement.",
            what: "A gamified OS (Mech Pilot) unifying Strategy, Execution, and Review.",
            loadout: ["VS Code", "Claude", "Obsidian"],
            tasks: [
                {
                    id: "t1",
                    title: "Design Phase 2 Ontology",
                    duration: "45m",
                    xp: "+100 Cap",
                    how: "Define the JSON schema for Objectives, KRs, Projects, and Tasks.",
                    prompt: "💡 提示：从最小可行单元开始。先定义一个 Task 的结构，再往上推导 Project 和 OKR。不要一开始就追求完美。",
                    progress: "Drafting Schema (30%)"
                },
                {
                    id: "t2",
                    title: "Fix Chat History Bug",
                    duration: "30m",
                    xp: "+50 Cap",
                    how: "Investigate why messages aren't persisting in SQLite.",
                    prompt: "🔍 调试策略：先用 print 语句确认函数是否被调用，再检查数据库文件是否真的写入了。不要猜测，用日志说话。",
                    progress: "Pending"
                }
            ]
        },
        {
            id: "m2",
            name: "GUARDIAN-02",
            type: "Support",
            status: "Standby",
            project_ref: "Project 2: Dad & Daughter",
            description: "Quality time and education.",
            why: "To build a deep emotional bond and foster curiosity.",
            what: "Daily bedtime stories and weekend park visits.",
            loadout: ["Storybook", "Park", "Lego"],
            tasks: [
                {
                    id: "t3",
                    title: "Read Bedtime Story",
                    duration: "20m",
                    xp: "+30 Inf",
                    how: "Read 'The Little Prince' Ch. 3. Discuss the Baobabs.",
                    prompt: "📖 慢下来。不要急着讲完，观察女儿的表情。如果她走神了，停下来问她：\"你觉得小王子为什么要拔掉猴面包树？\"",
                    progress: "Ready"
                }
            ]
        },
        {
            id: "m3",
            name: "LOVING-03",
            type: "Economic",
            status: "Maintenance",
            project_ref: "Project 3: VeryLoving",
            description: "Business operations and growth.",
            loadout: ["Shopify", "Excel"],
            tasks: []
        }
    ],
    mission_log: [] // To be populated during session
};
