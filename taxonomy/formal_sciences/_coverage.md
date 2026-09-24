# Formal Sciences — coverage map

Breadth pass across the branches of mathematics, statistics, and theoretical
computer science, mapped to established classification systems. (Starts with `_`
/ not `.json`, so the engine ignores it.)

Reference systems used:
- **DDC** — Dewey Decimal: 511 general/combinatorics, 512 algebra, 514 topology,
  515 analysis, 516 geometry, 518 numerical analysis, 519 probability/statistics
- **LCC** — Library of Congress, QA: QA9 logic, QA75-76 computer science,
  QA150+ algebra, QA241 number theory, QA273+ probability/statistics,
  QA299+ analysis, QA440+ geometry, QA611+ topology
- **OECD** — Frascati: pure mathematics, applied mathematics, statistics & probability

| Discipline | Branch | DDC | LCC |
|---|---|---|---|
| Real & Complex Analysis | Pure math | 515 | QA299+ |
| Abstract Algebra | Pure math | 512 | QA150+ |
| Number Theory | Pure math | 512.7 | QA241+ |
| Topology | Pure math | 514 | QA611+ |
| Differential Geometry | Pure math | 516.36 | QA641+ |
| Combinatorics | Pure math | 511.6 | QA164+ |
| Graph Theory *(existing)* | Pure math | 511.5 | QA166+ |
| Category Theory | Pure math | 512.62 | QA169 |
| Probability Theory | Applied math | 519.2 | QA273+ |
| Mathematical Statistics | Applied math | 519.5 | QA276+ |
| Optimization & Operations Research | Applied math | 519.6 | QA402.5 |
| Numerical Analysis | Applied math | 518 | QA297 |
| Differential Equations | Applied math | 515.35 | QA371+ |
| Dynamical Systems & Chaos | Applied math | 515.39 | QA614.8 |
| Information Theory | Applied math | 003.54 | QA268 |
| Cryptography *(existing)* | Applied math | 005.82 | QA268/Z103 |
| Theory of Computation *(existing)* | Theoretical CS | 511.3 | QA267+ |
| Algorithm Design & Analysis | Theoretical CS | 518.1 | QA76.9.A43 |
| Formal Methods & Verification | Theoretical CS | 004.21 | QA76.9.F67 |
| Mathematical Logic *(existing)* | Logic | 511.3 | QA9 |
| Mathematical Physics | Applied math | 530.15 | QA401 |
| Combinatorial & Algorithmic Game Theory | Applied math | 519.3 | QA269 |
| Set Theory | Pure math | 511.322 | QA248 |
| Measure Theory | Pure math | 515.42 | QA312 |
| Functional Analysis | Pure math | 515.7 | QA320 |
| Algebraic Geometry | Pure math | 516.35 | QA564 |
| Algebraic Topology | Pure math | 514.2 | QA612 |
| Stochastic Processes | Applied math | 519.23 | QA274 |
| Coding Theory | Applied math | 003.54 | QA268 |
| Decision Theory | Applied math | 519.542 | QA279.4 |
| Proof Theory & Reverse Mathematics | Logic | 511.36 | QA9.54 |

## Known gaps / candidates for later rounds
_Filled in the scale round: Set Theory, Measure Theory, Functional Analysis,
Stochastic Processes, Coding Theory, Decision Theory; the audit round added
Mathematical Physics and Combinatorial & Algorithmic Game Theory (the political
economy application stays in Social Sciences)._
- _The gap-fill round split Proof Theory & Reverse Mathematics out of
  Mathematical Logic (ordinal analysis, the Big Five subsystems, proof mining;
  cut elimination itself stays in Mathematical Logic)._
- _The latest MSC 2020 and ACM CCS expansion round added 28 highly specific fields:_
  - **Logic/Foundations**: Computability Theory, Model Theory, Non-Classical Logic.
  - **Geometry/Topology**: Discrete Geometry, Convex Geometry.
  - **Analysis**: Harmonic Analysis, Operator Theory, Ergodic Theory, Global/Manifold Analysis (via information geometry), Approximations (via harmonic/operator).
  - **Algebra**: Commutative Algebra, Non-associative Rings and Algebras, Representation Theory, Lie Groups and Lie Algebras, K-Theory, Universal Algebra, Field Theory and Polynomials, Linear Algebra and Matrix Theory, Homological Algebra, Order Theory & Lattices.
  - **Theoretical CS**: Automata Theory & Formal Languages, Computational Complexity Theory, Semantics of Programming Languages, Type Theory, Process Algebra, Computational Geometry, Data Structures, Quantum Computing Theory.
  - **Operations/Statistics**: Queueing Theory, Information Geometry.
- Note: statistics here is the *mathematical* theory; applied/empirical methods
  recur inside domain-specific disciplines elsewhere.
