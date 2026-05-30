# Qdrant Reward Route Radar Demo Video Script

Target length: no more than 3 minutes.

Rendered local cut: 72 seconds, silent visual walkthrough with captions embedded on screen.

## 0:00 - 0:14

Show the local web demo title and controls.

Narration: "Reward Route Radar is not a chatbot. It is a Qdrant-backed ranking surface that helps an operator choose high-upside reward routes while filtering unsafe work."

## 0:14 - 0:28

Show the synthetic dataset and call out the unsafe fixtures: social-account work, wallet signing, and instruction-disclosure bounties.

Narration: "The dataset includes valid opportunities and adversarial fixtures. Those fixtures are intentionally present so the demo can prove the safety filters are doing real work."

## 0:28 - 0:44

Run the default query in the web demo. Show the ranked result table returning `qdrant-vsd-2026` as the top route.

Narration: "Qdrant stores each route as a vector point with payload fields. The query uses vector similarity for fit, while payload filters enforce reward, risk, and safety constraints."

## 0:44 - 0:58

Show the safety boundary.

Narration: "This is operational triage, not Q&A. Hard blocks remain enforced while KYC, payment, and registration actions stay review-gated."

## 0:58 - 1:12

Show the repeatable evidence package and public repo path.

Narration: "The package includes repeatable tests, a local preflight, and explicit gates for external submission, video hosting, identity, and payment paperwork."
