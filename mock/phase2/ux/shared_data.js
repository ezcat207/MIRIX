const SHARED_DATA = {
    user: {
        name: "Player One",
        level: 24,
        class: "System Architect",
        xp: { current: 2450, max: 3000 },
        attributes: {
            intelligence: 85, // Learning
            charisma: 42,     // Communication
            endurance: 60,    // Execution
            creativity: 75    // System Building
        }
    },
    goals: [
        {
            id: "g1",
            title: "Master Structured Communication",
            type: "Learning",
            progress: 65,
            status: "Active",
            rpg_context: {
                quest_name: "The Bard's Tongue",
                reward: "+5 Charisma, +200 XP",
                difficulty: "Hard"
            },
            cockpit_context: {
                module: "COMM_UPLINK",
                signal_strength: "65%",
                drift: "-5% (Warning)"
            }
        },
        {
            id: "g2",
            title: "Build Personal Palantir v2",
            type: "Execution",
            progress: 40,
            status: "On Track",
            rpg_context: {
                quest_name: "Forge of the Oracle",
                reward: "+10 Intelligence, +500 XP",
                difficulty: "Epic"
            },
            cockpit_context: {
                module: "SYS_CORE",
                integrity: "98%",
                uptime: "14d 2h"
            }
        }
    ],
    daily_tasks: [
        {
            id: "t1",
            title: "Analyze 3 VC Pitch Decks",
            goal_id: "g1",
            completed: true,
            rpg_val: "+50 XP",
            cockpit_val: "Input: 3 Records"
        },
        {
            id: "t2",
            title: "Refactor OCR Module",
            goal_id: "g2",
            completed: false,
            rpg_val: "+100 XP",
            cockpit_val: "Pending Commit"
        },
        {
            id: "t3",
            title: "Reach out to 1 Mentor",
            goal_id: "g1",
            completed: false,
            rpg_val: "+30 XP",
            cockpit_val: "Outbound: 0/1"
        }
    ],
    insights: [
        {
            type: "warning",
            msg: "Communication structure degrading in afternoon meetings.",
            rpg_msg: "Debuff Detected: 'Mental Fatigue' (-10 CHA)",
            cockpit_msg: "Alert: Signal Noise Ratio High (14:00-16:00)"
        },
        {
            type: "success",
            msg: "System uptime is perfect this week.",
            rpg_msg: "Buff Active: 'Flow State' (+20% XP Gain)",
            cockpit_msg: "Status: Nominal. Efficiency Index 1.2x"
        }
    ]
};
