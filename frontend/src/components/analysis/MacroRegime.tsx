type Evidence = {
    regime: string;
    weight: number;
    indicator: string;
    reason: string;
    supporting_indicators?: string[];
};

type MacroRegimeData = {
    regime: string;
    confidence: string;
    score: number;
    scores: {
        expansion: number;
        contraction: number;
    };
    score_share: number;
    evidence: Evidence[];
    evidence_count: number;
    conflicting_evidence: Evidence[];
    conflicting_evidence_count: number;
    indicator_count: number;
    indicators_supporting: string[];
    indicators_used: string[];
    multi_indicator: boolean;
};

type Props = {
    data: MacroRegimeData;
};

function formatRegime(value: string) {
    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatReason(value: string) {
    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function MacroRegime({ data }: Props) {
    const expansionScore = data.scores?.expansion ?? 0;
    const contractionScore = data.scores?.contraction ?? 0;

    const totalScore = expansionScore + contractionScore;

    const expansionShare =
        totalScore > 0
            ? (expansionScore / totalScore) * 100
            : 0;

    return (
        <section
            style={{
                background: "#fff",
                border: "1px solid #e2e8f0",
                borderRadius: 12,
                padding: 24,
                marginBottom: 24,
            }}
        >
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 20,
                    marginBottom: 24,
                }}
            >
                <div>
                    <div
                        style={{
                            fontSize: 12,
                            color: "#94a3b8",
                            fontWeight: 600,
                            textTransform: "uppercase",
                            letterSpacing: "0.06em",
                            marginBottom: 6,
                        }}
                    >
                        Macro Regime
                    </div>

                    <div
                        style={{
                            fontSize: 28,
                            fontWeight: 700,
                            color: "#0f172a",
                            letterSpacing: "-0.03em",
                        }}
                    >
                        {formatRegime(data.regime)}
                    </div>
                </div>

                <div
                    style={{
                        padding: "6px 12px",
                        borderRadius: 20,
                        background:
                            data.confidence.toLowerCase() === "high"
                                ? "#f0fdf4"
                                : "#f8fafc",
                        color:
                            data.confidence.toLowerCase() === "high"
                                ? "#16a34a"
                                : "#64748b",
                        fontSize: 11,
                        fontWeight: 700,
                        textTransform: "uppercase",
                    }}
                >
                    {data.confidence} confidence
                </div>
            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                    gap: 12,
                    marginBottom: 24,
                }}
            >
                <div
                    style={{
                        background: "#f8fafc",
                        borderRadius: 8,
                        padding: 16,
                    }}
                >
                    <div
                        style={{
                            fontSize: 11,
                            color: "#94a3b8",
                            marginBottom: 6,
                        }}
                    >
                        Score
                    </div>

                    <div
                        style={{
                            fontSize: 22,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >
                        {data.score.toFixed(1)}
                    </div>
                </div>

                <div
                    style={{
                        background: "#f8fafc",
                        borderRadius: 8,
                        padding: 16,
                    }}
                >
                    <div
                        style={{
                            fontSize: 11,
                            color: "#94a3b8",
                            marginBottom: 6,
                        }}
                    >
                        Score share
                    </div>

                    <div
                        style={{
                            fontSize: 22,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >
                        {(data.score_share * 100).toFixed(1)}%
                    </div>
                </div>

                <div
                    style={{
                        background: "#f8fafc",
                        borderRadius: 8,
                        padding: 16,
                    }}
                >
                    <div
                        style={{
                            fontSize: 11,
                            color: "#94a3b8",
                            marginBottom: 6,
                        }}
                    >
                        Indicators
                    </div>

                    <div
                        style={{
                            fontSize: 22,
                            fontWeight: 700,
                            color: "#0f172a",
                        }}
                    >
                        {data.indicator_count}
                    </div>
                </div>
            </div>

            <div style={{ marginBottom: 24 }}>
                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: 12,
                        marginBottom: 8,
                    }}
                >
                    <span
                        style={{
                            color: "#16a34a",
                            fontWeight: 600,
                        }}
                    >
                        Expansion
                    </span>

                    <span style={{ color: "#64748b" }}>
                        {expansionScore.toFixed(1)}
                    </span>
                </div>

                <div
                    style={{
                        height: 8,
                        background: "#f1f5f9",
                        borderRadius: 99,
                        overflow: "hidden",
                    }}
                >
                    <div
                        style={{
                            width: `${Math.min(expansionShare, 100)}%`,
                            height: "100%",
                            background: "#16a34a",
                            borderRadius: 99,
                        }}
                    />
                </div>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: 12,
                        marginTop: 10,
                        marginBottom: 8,
                    }}
                >
                    <span
                        style={{
                            color: "#dc2626",
                            fontWeight: 600,
                        }}
                    >
                        Contraction
                    </span>

                    <span style={{ color: "#64748b" }}>
                        {contractionScore.toFixed(1)}
                    </span>
                </div>
            </div>

            <div>
                <div
                    style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: "#0f172a",
                        marginBottom: 12,
                    }}
                >
                    Supporting indicators
                </div>

                <div
                    style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 8,
                        marginBottom: 20,
                    }}
                >
                    {data.indicators_supporting.map((indicator) => (
                        <span
                            key={indicator}
                            style={{
                                padding: "5px 10px",
                                background: "#eff6ff",
                                color: "#2563eb",
                                borderRadius: 6,
                                fontSize: 11,
                                fontWeight: 600,
                            }}
                        >
                            {indicator}
                        </span>
                    ))}
                </div>

                <div
                    style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: "#0f172a",
                        marginBottom: 10,
                    }}
                >
                    Evidence
                </div>

                <div
                    style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 8,
                        marginBottom:
                            data.conflicting_evidence.length > 0
                                ? 24
                                : 0,
                    }}
                >
                    {data.evidence.map((item, index) => (
                        <div
                            key={`${item.indicator}-${index}`}
                            style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                gap: 16,
                                padding: "10px 12px",
                                background: "#f8fafc",
                                borderRadius: 7,
                            }}
                        >
                            <div>
                                <span
                                    style={{
                                        fontWeight: 600,
                                        color: "#334155",
                                        fontSize: 12,
                                    }}
                                >
                                    {item.indicator}
                                </span>

                                <span
                                    style={{
                                        color: "#64748b",
                                        fontSize: 12,
                                        marginLeft: 8,
                                    }}
                                >
                                    {formatReason(item.reason)}
                                </span>
                            </div>

                            <span
                                style={{
                                    fontSize: 11,
                                    fontWeight: 700,
                                    color: "#64748b",
                                    whiteSpace: "nowrap",
                                }}
                            >
                                +{item.weight}
                            </span>
                        </div>
                    ))}
                </div>

                {data.conflicting_evidence.length > 0 && (
                    <>
                        <div
                            style={{
                                fontSize: 13,
                                fontWeight: 600,
                                color: "#0f172a",
                                marginBottom: 10,
                            }}
                        >
                            Conflicting evidence
                        </div>

                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 8,
                            }}
                        >
                            {data.conflicting_evidence.map(
                                (item, index) => (
                                    <div
                                        key={`${item.indicator}-${index}`}
                                        style={{
                                            display: "flex",
                                            justifyContent:
                                                "space-between",
                                            alignItems: "center",
                                            gap: 16,
                                            padding: "10px 12px",
                                            background: "#fef2f2",
                                            borderRadius: 7,
                                            border: "1px solid #fee2e2",
                                        }}
                                    >
                                        <div>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: 8,
                                                    marginBottom: 4,
                                                }}
                                            >
                                                <span
                                                    style={{
                                                        fontWeight: 600,
                                                        color: "#991b1b",
                                                        fontSize: 12,
                                                    }}
                                                >
                                                    {item.indicator}
                                                </span>

                                                {item.supporting_indicators &&
                                                    item
                                                        .supporting_indicators
                                                        .length > 0 && (
                                                        <span
                                                            style={{
                                                                color: "#b91c1c",
                                                                fontSize: 11,
                                                            }}
                                                        >
                                                            {item.supporting_indicators.join(
                                                                " · "
                                                            )}
                                                        </span>
                                                    )}
                                            </div>

                                            <span
                                                style={{
                                                    color: "#7f1d1d",
                                                    fontSize: 12,
                                                }}
                                            >
                                                {formatReason(item.reason)}
                                            </span>
                                        </div>

                                        <span
                                            style={{
                                                fontSize: 11,
                                                fontWeight: 700,
                                                color: "#b91c1c",
                                                whiteSpace: "nowrap",
                                            }}
                                        >
                                            -{item.weight}
                                        </span>
                                    </div>
                                )
                            )}
                        </div>
                    </>
                )}
            </div>
        </section>
    );
}