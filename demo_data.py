"""
Demo data for ScholAR Pulse - Pre-determined research papers for specific topics.
When demo topics are entered, mock papers are returned instead of API calls.
"""

DEMO_TOPICS = {
    "ai in healthcare": {
        "sub_questions": [
            "How effective are AI diagnostic tools in clinical settings?",
            "What are the ethical concerns in AI healthcare applications?",
            "What methodological limitations exist in current AI health studies?"
        ],
        "papers": [
            {
                "title": "Deep Learning for Early Cancer Detection: A Multi-Site Study",
                "abstract": "This study evaluates convolutional neural networks for detecting early-stage lung cancer across 5 major hospitals. Using a dataset of 15,000 CT scans, our model achieved 94.2% accuracy with 87% sensitivity. Key findings include improved detection rates for nodules under 5mm and reduced false positives by 23% compared to radiologist-only diagnosis.",
                "year": 2024,
                "venue": "Nature Medicine",
                "authors": ["Dr. Sarah Chen", "Prof. Michael Ross"],
                "url": "https://example.com/paper1",
                "critique": {
                    "sample_size": "15,000 CT scans",
                    "dataset_type": "real",
                    "reproducibility_score": 8,
                    "credibility_score": 8,
                    "boldness_vs_evidence": "appropriate",
                    "red_flags": [],
                    "main_claims": ["94.2% accuracy in lung cancer detection", "23% reduction in false positives"],
                    "methodology_summary": "Multi-site validation with large dataset supports strong clinical applicability"
                }
            },
            {
                "title": "AI Bias in Dermatology: Systematic Review of 47 Studies",
                "abstract": "We analyzed 47 published studies on AI skin cancer detection and found significant performance disparities across skin tones. Models trained primarily on lighter skin types (Fitzpatrick I-III) showed 12-18% lower accuracy on darker skin tones (Fitzpatrick IV-VI). Only 8% of datasets included adequate representation of darker skin populations.",
                "year": 2023,
                "venue": "JAMA Dermatology",
                "authors": ["Dr. Amara Okafor", "Dr. James Liu"],
                "url": "https://example.com/paper2",
                "critique": {
                    "sample_size": "47 studies",
                    "dataset_type": "mixed",
                    "reproducibility_score": 7,
                    "credibility_score": 9,
                    "boldness_vs_evidence": "conservative",
                    "red_flags": [],
                    "main_claims": ["12-18% accuracy gap across skin tones", "Only 8% datasets represent dark skin"],
                    "methodology_summary": "Systematic review of 47 studies identifies critical equity gap in dermatology AI"
                }
            },
            {
                "title": "Explainable AI for Clinical Decision Support: Randomized Trial",
                "abstract": "Randomized controlled trial with 300 physicians testing AI-driven diagnosis support. Physicians using explainable AI systems made 15% fewer diagnostic errors and reported 40% higher trust scores. However, 35% showed over-reliance on AI recommendations in edge cases. Study highlights need for balanced human-AI collaboration frameworks.",
                "year": 2024,
                "venue": "NEJM AI",
                "authors": ["Prof. Elena Vasquez", "Dr. Robert Kim"],
                "url": "https://example.com/paper3",
                "critique": {
                    "sample_size": "300 physicians",
                    "dataset_type": "real",
                    "reproducibility_score": 9,
                    "credibility_score": 8,
                    "boldness_vs_evidence": "appropriate",
                    "red_flags": [],
                    "main_claims": ["15% fewer errors with explainable AI", "35% over-reliance on AI in edge cases"],
                    "methodology_summary": "Well-designed RCT with 300 physicians showing benefits and risks of AI augmentation"
                }
            },
            {
                "title": "Federated Learning for Privacy-Preserving Medical AI",
                "abstract": "Proposes federated learning architecture enabling AI training across 12 hospitals without centralizing patient data. Demonstrates 96% of centralized model performance while maintaining differential privacy (ε=1.2). Addresses regulatory compliance for HIPAA and GDPR in multi-institutional research.",
                "year": 2023,
                "venue": "Science Translational Medicine",
                "authors": ["Dr. Priya Sharma", "Prof. Thomas Weber"],
                "url": "https://example.com/paper4",
                "critique": {
                    "sample_size": "12 hospitals",
                    "dataset_type": "real",
                    "reproducibility_score": 7,
                    "credibility_score": 7,
                    "boldness_vs_evidence": "appropriate",
                    "red_flags": ["prototype system"],
                    "main_claims": ["96% performance of centralized model", "Differential privacy ε=1.2"],
                    "methodology_summary": "Novel privacy-preserving approach with promising but early-stage validation"
                }
            },
            {
                "title": "Retrospective Analysis: AI Overdiagnosis in Radiology",
                "abstract": "Analysis of 50,000 AI-assisted radiology reports reveals 18% increase in incidental findings leading to unnecessary biopsies. Cost analysis shows $2,400 average per false-positive workup. Study questions current validation metrics that prioritize sensitivity over specificity in clinical workflows.",
                "year": 2022,
                "venue": "Radiology",
                "authors": ["Dr. David Park", "Dr. Lisa Johnson"],
                "url": "https://example.com/paper5",
                "critique": {
                    "sample_size": "50,000 reports",
                    "dataset_type": "real",
                    "reproducibility_score": 8,
                    "credibility_score": 8,
                    "boldness_vs_evidence": "appropriate",
                    "red_flags": [],
                    "main_claims": ["18% increase in incidental findings", "$2,400 cost per false positive"],
                    "methodology_summary": "Large retrospective analysis highlighting real-world costs of AI sensitivity bias"
                }
            },
            {
                "title": "Natural Language Processing for Electronic Health Records",
                "abstract": "BERT-based model trained on 2.3 million EHR notes for automated ICD-10 coding. Achieves 91.4% F1 score on 50 common conditions. Reduces coding time by 60% but struggles with rare diseases (prevalence <0.1%) and complex comorbidities requiring clinical reasoning.",
                "year": 2024,
                "venue": "JAMIA",
                "authors": ["Dr. Jennifer Walsh", "Prof. Ahmed Hassan"],
                "url": "https://example.com/paper6",
                "critique": {
                    "sample_size": "2.3 million EHR notes",
                    "dataset_type": "real",
                    "reproducibility_score": 6,
                    "credibility_score": 7,
                    "boldness_vs_evidence": "overclaimed",
                    "red_flags": ["fails on rare diseases", "limited to common conditions"],
                    "main_claims": ["91.4% F1 score", "60% reduction in coding time"],
                    "methodology_summary": "Large-scale study with strong common-case performance but significant edge-case limitations"
                }
            }
        ],
        "contradictions": [
            {
                "contradiction_detected": True,
                "severity": "high",
                "type": "empirical_conflict",
                "claim_a": "AI reduces diagnostic errors by 15% when physicians use explainable AI systems",
                "claim_b": "35% of physicians show over-reliance on AI recommendations in edge cases, leading to new error types",
                "explanation": "Same study shows both benefits and risks - effectiveness depends on use case and physician training",
                "resolution_path": "Need for graduated AI assistance with explicit uncertainty indicators",
                "paper_a_title": "Explainable AI for Clinical Decision Support: Randomized Trial",
                "paper_b_title": "Explainable AI for Clinical Decision Support: Randomized Trial"
            },
            {
                "contradiction_detected": True,
                "severity": "medium",
                "type": "methodological",
                "claim_a": "AI diagnostic tools achieve high accuracy (94.2%) in controlled multi-site studies",
                "claim_b": "Retrospective analysis shows AI overdiagnosis leads to 18% more unnecessary procedures",
                "explanation": "Research metrics prioritize sensitivity while real-world metrics show specificity trade-offs",
                "resolution_path": "Balance validation metrics to include real-world cost-effectiveness",
                "paper_a_title": "Deep Learning for Early Cancer Detection: A Multi-Site Study",
                "paper_b_title": "Retrospective Analysis: AI Overdiagnosis in Radiology"
            }
        ],
        "deep_report": {
            "executive_summary": "The field of AI in healthcare is rapidly maturing from proof-of-concept models to clinical validation. While multi-site studies demonstrate exceptional accuracy (up to 94.2%) in diagnostics such as early cancer detection, a significant methodology gap remains regarding generalizability across diverse demographics. Notably, models trained heavily on specific cohorts struggle significantly with edge cases and diverse skin tones, dropping accuracy by up to 18%. Federated learning architectures show immense promise in addressing data privacy but remain in early prototyping phases.",
            "field_snapshot": {
                "trend": "Pivoting from high-sensitivity validation to real-world specificity and fairness.",
                "dominant_methods": ["Deep Convolutional Neural Networks", "Federated Learning", "Transformer-based NLP (BERT)"]
            },
            "contradictions_summary": [
                {"severity": "high", "paper_a": "Explainable AI (Vasquez et al.)", "paper_b": "Explainable AI Edge Cases", "conflict": "15% error reduction overall vs. 35% over-reliance on incorrect edge-case advice."},
                {"severity": "medium", "paper_a": "Deep Learning Cancer Detection", "paper_b": "Retrospective Overdiagnosis", "conflict": "High raw accuracy does not translate linearly to clinical utility without raising false positive workups."}
            ],
            "gaps": [
                {"area": "Demographic Equity in Datasets", "opportunity_score": 9, "description": "Significant lack of curated datasets featuring Fitzpatrick IV-VI skin types and marginalized demographics.", "why_missing": "Historical healthcare data aggregation biases towards centralized, affluent hospital networks."},
                {"area": "Clinical Workflow Integration", "opportunity_score": 8, "description": "Models often optimize for academic metrics (AUC/F1) rather than workflow efficiency and cost reduction metrics.", "why_missing": "Disconnect between ML researchers and clinical operational staff."}
            ],
            "frontier_directions": [
                {"direction": "Federated Generative Synthesis", "impact_score": 9, "rationale": "Allows hospitals to generate synthetic inclusive data without moving actual PII data.", "addresses_gap": "Demographic Equity in Datasets", "difficulty": "high"},
                {"direction": "Dynamic Cost-Sensitive Thresholding", "impact_score": 8, "rationale": "Adapts AI sensitivity on-the-fly based on current hospital load and downstream biopsy costs.", "addresses_gap": "Clinical Workflow Integration", "difficulty": "medium"}
            ]
        }
    },
    
    "quantum computing": {
        "sub_questions": [
            "What are the current hardware limitations in quantum processors?",
            "Which quantum algorithms show practical speedup over classical computing?",
            "What error correction methods are being developed?"
        ],
        "papers": [
            {
                "title": "Quantum Supremacy using a Programmable Superconducting Processor",
                "abstract": "Google demonstrates quantum supremacy with 53-qubit Sycamore processor completing random circuit sampling in 200 seconds, estimated to take 10,000 years on classical supercomputers. Achieves 99.4% two-qubit gate fidelity. Critics argue practical applications remain distant and benchmark is artificial.",
                "year": 2019,
                "venue": "Nature",
                "authors": ["Dr. John Martinis", "Prof. Sergio Boixo"],
                "url": "https://example.com/qc1"
            },
            {
                "title": "Logical Qubits with Neutral Atoms: Error Rates Below Threshold",
                "abstract": "Harvard team achieves 0.1% error rate for logical qubits using neutral atom arrays with 280 physical qubits. Demonstrates surface code error correction with 99.9% syndrome detection accuracy. Breakthrough suggests fault-tolerant quantum computing may be achievable within 5 years.",
                "year": 2024,
                "venue": "Physical Review Letters",
                "authors": ["Prof. Mikhail Lukin", "Dr. Dolev Bluvstein"],
                "url": "https://example.com/qc2"
            },
            {
                "title": "Quantum Advantage in Drug Discovery: Hype vs Reality",
                "abstract": "Critical analysis of 23 quantum chemistry studies claims. Only 3 show genuine quantum advantage; others use classical approximations or small molecules solvable on laptops. Current NISQ devices lack coherence time for pharmaceutical-relevant molecular simulations (100+ atoms).",
                "year": 2023,
                "venue": "Nature Reviews Chemistry",
                "authors": ["Dr. Alán Aspuru-Guzik", "Dr. Garnet Chan"],
                "url": "https://example.com/qc3"
            },
            {
                "title": "Photonic Quantum Computing at Room Temperature",
                "abstract": "Xanadu's Borealis demonstrates Gaussian boson sampling with 216 squeezed modes, no cryogenics required. Achieves quantum advantage in specific graph optimization problems. Energy consumption 1/1000th of superconducting equivalents but limited to photonic-native algorithms.",
                "year": 2022,
                "venue": "Science",
                "authors": ["Dr. Christian Weedbrook", "Dr. Jonathan Lavoie"],
                "url": "https://example.com/qc4"
            },
            {
                "title": "Quantum Error Correction Scaling: Exponential Overhead Analysis",
                "abstract": "Rigorous analysis shows current surface code approaches require 1000+ physical qubits per logical qubit at 0.1% error rates. For 1000-logical-qubit computer, need 1 million physical qubits. Proposes concatenated codes reducing overhead by 60% but requiring higher native gate fidelity (99.99%).",
                "year": 2024,
                "venue": "Quantum",
                "authors": ["Prof. Barbara Terhal", "Dr. Earl Campbell"],
                "url": "https://example.com/qc5"
            },
            {
                "title": "Post-Quantum Cryptography: NIST Standards Implementation",
                "abstract": "First large-scale deployment study of CRYSTALS-Kyber and CRYSTALS-Dilithium algorithms. Performance overhead 15-40% compared to RSA/ECC. Side-channel vulnerabilities identified in 3 of 12 implementations. Recommends hybrid classical-quantum approach during transition period.",
                "year": 2024,
                "venue": "IEEE Security & Privacy",
                "authors": ["Dr. Lily Chen", "Prof. Daniel Bernstein"],
                "url": "https://example.com/qc6"
            }
        ],
        "deep_report": {
            "executive_summary": "Quantum computing is experiencing a critical inflection point, shifting from theoretical superiority to early-stage fault-tolerant milestones. While Google's Sycamore proved quantum supremacy mathematically, practical applications remain heavily bottlenecked by noise. The recent breakthrough in neutral atom logical qubits achieving <0.1% error rates is a game-changer, potentially compressing the timeline to fault tolerance. However, aggressive claims regarding quantum advantage in drug discovery have been largely debunked as hype, with classical methods still dominating molecular simulations for the foreseeable future.",
            "field_snapshot": {
                "trend": "Accelerated push towards logical qubits and quantum error correction (QEC).",
                "dominant_methods": ["Superconducting Qubits", "Neutral Atom Arrays", "Photonic Computing"]
            },
            "contradictions_summary": [
                {"severity": "medium", "paper_a": "Quantum Supremacy", "paper_b": "Quantum Advantage Hype", "conflict": "Mathematical supremacy is proven, but practical advantage in simulating useful molecular configurations remains unachievable with current coherence limits."}
            ],
            "gaps": [
                {"area": "Middleware and Compilers", "opportunity_score": 8, "description": "Lack of efficient compilers to optimally map algorithms onto specific, noisy physical layouts.", "why_missing": "Hardware evolves faster than the software stack can standardize."},
                {"area": "Scalable Cryogenics", "opportunity_score": 9, "description": "Superconducting processors are fundamentally constrained by the cooling power of dilution refrigerators at the 10,000+ qubit scale.", "why_missing": "Extremely difficult thermodynamic engineering challenge."}
            ],
            "frontier_directions": [
                {"direction": "Room-Temperature Photonics", "impact_score": 8, "rationale": "Bypasses cryogenic bottlenecks entirely, albeit restricted to specific computation classes.", "addresses_gap": "Scalable Cryogenics", "difficulty": "high"},
                {"direction": "Hybrid QPU-CPU Workflows", "impact_score": 9, "rationale": "Delegating only classically intractable subroutines to the quantum processor while the CPU manages state.", "addresses_gap": "Middleware and Compilers", "difficulty": "medium"}
            ]
        }
    },
    
    "renewable energy": {
        "sub_questions": [
            "What are the efficiency limits of current solar cell technologies?",
            "How does grid-scale energy storage impact renewable adoption?",
            "What are the environmental trade-offs in battery production?"
        ],
        "papers": [
            {
                "title": "Perovskite-Silicon Tandem Solar Cells: 33.7% Efficiency Record",
                "abstract": "Oxford PV demonstrates certified 33.7% conversion efficiency in monolithic 2-terminal tandem cells. Perovskite top cell (1.68 eV) harvests high-energy photons while silicon bottom cell captures infrared. Stability testing shows 95% retention after 1000 hours at 85°C/85% humidity.",
                "year": 2024,
                "venue": "Nature Energy",
                "authors": ["Prof. Henry Snaith", "Dr. Laura Miranda"],
                "url": "https://example.com/re1"
            },
            {
                "title": "Grid-Scale Lithium-Ion vs Vanadium Flow: 10-Year TCO Analysis",
                "abstract": "Comparative study of 100MWh installations shows vanadium flow batteries have 40% lower total cost of ownership despite 2x capital cost. Li-ion requires replacement at year 8-10; flow batteries last 25+ years. Flow batteries preferable for 4+ hour discharge duration applications.",
                "year": 2023,
                "venue": "Joule",
                "authors": ["Dr. Maria Skyllas-Kazacos", "Prof. Michael Aziz"],
                "url": "https://example.com/re2"
            },
            {
                "title": "Life Cycle Assessment: EV Batteries vs Internal Combustion",
                "abstract": "Cradle-to-grave analysis shows EVs produce 70% fewer emissions over 200,000 km in Europe/US grids. However, manufacturing phase produces 2-3x more emissions. Battery recycling currently at 5% globally; hydrometallurgical methods can recover 95% lithium but cost $2000/tonne.",
                "year": 2024,
                "venue": "Environmental Science & Technology",
                "authors": ["Dr. Linda Gaines", "Prof. Qiang Zhang"],
                "url": "https://example.com/re3"
            },
            {
                "title": "Offshore Wind: Floating Platform Economics and Grid Integration",
                "abstract": "Analysis of 15GW floating offshore wind projects. Levelized cost $65-85/MWh vs $45-60 for fixed-bottom. Major cost drivers: dynamic cables (18%), mooring systems (22%). Grid integration challenges: 800km+ transmission requiring HVDC, 12-18% transmission losses.",
                "year": 2023,
                "venue": "Energy Policy",
                "authors": ["Dr. Stephanie Thomas", "Prof. John Kaldellis"],
                "url": "https://example.com/re4"
            },
            {
                "title": "Agrivoltaics: Crop Yield and Energy Production Trade-offs",
                "abstract": "3-year study across 8 crops shows partial shade solar panels increase tomato yields 12% while generating 3.2 MWh/acre annually. Lettuce and spinach unaffected; corn yields decrease 18%. Optimal configuration: 50% panel density with elevated tracking systems.",
                "year": 2024,
                "venue": "Scientific Reports",
                "authors": ["Dr. Majdi Abou Najm", "Prof. Greg Barron-Gafford"],
                "url": "https://example.com/re5"
            },
            {
                "title": "Green Hydrogen: Electrolyzer Efficiency and Economic Viability",
                "abstract": "PEM electrolyzers achieve 70% system efficiency (LHV basis) at $400/kW capital cost. Green hydrogen competitive at $2-3/kg with $30/MWh electricity and 90% capacity factor. Current average: $5-7/kg. Alkaline electrolyzers 10% cheaper but slower response time limits renewable coupling.",
                "year": 2024,
                "venue": "Nature Communications",
                "authors": ["Dr. Iva Ridjan", "Prof. Brian Vad Mathiesen"],
                "url": "https://example.com/re6"
            }
        ],
        "deep_report": {
            "executive_summary": "The renewable energy transition is encountering a paradigm shift from pure generation optimization towards integration and storage efficiency. Photovoltaic advancements, particularly Perovskite-Silicon tandem cells, are shattering traditional efficiency ceilings (reaching 33.7%). However, grid-scale storage remains a major friction point. Vanadium flow batteries have emerged as a financially superior alternative to Lithium-Ion for long-duration storage due to their 25+ year lifecycle. Simultaneously, environmental life cycle assessments expose severe upstream manufacturing emissions and lagging recycling ecosystems for current battery infrastructures, demanding a shift in focus from 'green usage' to 'green manufacturing'.",
            "field_snapshot": {
                "trend": "Holistic grid integration and full-lifecycle sustainability metrics rather than isolated generation capacity.",
                "dominant_methods": ["Tandem Photovoltaics", "Flow Battery Storage", "Agrivoltaics", "PEM Electrolysis"]
            },
            "contradictions_summary": [
                {"severity": "low", "paper_a": "Lithium-Ion Dominance", "paper_b": "Vanadium Flow TCO", "conflict": "Li-ion has lower upfront capex, but Flow batteries offer 40% lower Total Cost of Ownership over 10 years, challenging short-term procurement strategies."}
            ],
            "gaps": [
                {"area": "Closed-Loop Battery Recycling", "opportunity_score": 9, "description": "Currently, only 5% of EV batteries are recycled globally, leading to severe resource depletion risk.", "why_missing": "Hydrometallurgical recycling methods remain vastly more expensive ($2000/tonne) than raw mining."},
                {"area": "Grid Topology for Offshore Wind", "opportunity_score": 8, "description": "Existing transmission infrastructures are ill-equipped for massive High-Voltage Direct Current (HVDC) influxes from long-distance offshore platforms.", "why_missing": "Regulatory hurdles and massive subsea cable capital requirements."}
            ],
            "frontier_directions": [
                {"direction": "Direct-to-Hydrogen Offshore Harvesting", "impact_score": 9, "rationale": "Converting wind power directly to green hydrogen on the platform eliminates the need for expensive subsea transmission cables.", "addresses_gap": "Grid Topology for Offshore Wind", "difficulty": "high"},
                {"direction": "Bio-leaching for Battery Recycling", "impact_score": 8, "rationale": "Using extremophile bacteria to recover critical metals from spent cells without harsh industrial chemicals or high heat.", "addresses_gap": "Closed-Loop Battery Recycling", "difficulty": "high"}
            ]
        }
    }
}


def get_demo_topic(query: str) -> str | None:
    """Check if query matches a demo topic (case-insensitive, partial match)."""
    query_lower = query.lower().strip()
    for topic_key in DEMO_TOPICS:
        if topic_key in query_lower or query_lower in topic_key:
            return topic_key
    return None


def get_demo_data(topic: str):
    """Get pre-determined data for a demo topic."""
    return DEMO_TOPICS.get(topic)
