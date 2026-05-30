# Qdrant Reward Route Radar Demo Video Script

Target length: 2:10 to 2:45.

## 0:00 - 0:20

Show the local web demo title and controls.

Narration: "Reward Route Radar is not a chatbot. It is a Qdrant-backed ranking surface that helps an operator choose high-upside reward routes while filtering unsafe work."

## 0:20 - 0:55

Show the synthetic dataset and call out the unsafe fixtures: social-account work, wallet signing, and instruction-disclosure bounties.

Narration: "The dataset includes valid opportunities and adversarial fixtures. Those fixtures are intentionally present so the demo can prove the safety filters are doing real work."

## 0:55 - 1:35

Run the default query in the web demo. Show the ranked result table returning `qdrant-vsd-2026` as the top route.

Narration: "Qdrant stores each route as a vector point with payload fields. The query uses vector similarity for fit, while payload filters enforce reward, risk, and safety constraints."

## 1:35 - 2:05

Change minimum reward and maximum risk. Toggle human-review routes.

Narration: "This is operational triage, not Q&A. Changing the controls reshapes the action queue while hard blocks remain enforced."

## 2:05 - 2:35

Show `contest_preflight.md` and the public README links.

Narration: "The package includes repeatable tests, a local preflight, and explicit gates for external submission, video hosting, identity, and payment paperwork."

## 2:35 - 2:45

End on the GitHub package path.

Narration: "The result is a reproducible Qdrant demo for vector search beyond chatbots: reward route ranking with safety-aware payload filtering."
