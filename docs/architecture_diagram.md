flowchart TD
    subgraph "The MCTS Engine"
        Root((Root State)) --> Select{Selection<br/>(UCB1)}
        Select -->|Exploration| Leaf[Leaf Node]
        Leaf --> Expand[Expansion]
    end

    subgraph "Gemini 2.5 Flash"
        Expand -->|Generate k=3| Candidate1[Option A]
        Expand -->|Generate k=3| Candidate2[Option B]
        Expand -->|Generate k=3| Candidate3[Option C]
    end

    subgraph "Secure Sandbox"
        Candidate1 --> CheckSyntax{AST Check}
        CheckSyntax -->|Syntax Error| RewardFail[Reward: -1.0]
        CheckSyntax -->|Valid| RunTests{Run Unit Tests}
        RunTests -->|Pass| RewardWin[Reward: 1.0]
        RunTests -->|Fail| RewardPartial[Reward: 0.1]
    end

    RewardWin --> Backprop[Backpropagation]
    RewardFail --> Backprop
    RewardPartial --> Backprop
    Backprop -->|Update Values| Root
    
    style RewardWin fill:#4caf50,stroke:#333,stroke-width:2px,color:white
    style Root fill:#2196f3,stroke:#333,stroke-width:2px,color:white
    style Expand fill:#ff9800,stroke:#333,stroke-width:2px,color:white