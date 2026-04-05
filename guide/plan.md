# :plan

The `:plan` subcommand is an 8-step interactive wizard that produces a fully configured `conference.md` file. It does not run a conference — it only produces the configuration.

---

## What It Does

Walking through `:plan` ensures your `conference.md` is complete and correct before you spend compute on a conference. Each step probes your intent, validates feasibility, and encodes your decisions into the file.

The wizard is specifically designed to catch two common failure modes:
1. **Vague goals** — a conference started with "improve my model" produces unfocused results
2. **Broken evaluators** — a conference whose metric script fails at iteration 1 wastes all subsequent compute

---

## When to Use `:plan` vs Manual Creation

Use `:plan` when:
- You are setting up your first conference on a new problem
- You are unsure how to partition the search space across researchers
- You want the dry-run gate to verify your evaluator before committing to a full run
- You want guided prompts to help sharpen your goal and success criteria

Create `conference.md` manually when:
- You are copying a template you have used before
- You are running one of the provided templates unchanged (`templates/code-performance.md`, `templates/prompt-optimization.md`, etc.)
- You already have a working `conference.md` from a previous run and just want to adjust parameters

---

## The 8-Step Wizard

### Step 1: Goal Clarification

The wizard asks: "What do you want to achieve?"

It pushes back on vague answers. "I want to improve my model" is rejected. It prompts you to be specific:

> "Improve model accuracy on the CIFAR-10 test set from 85% to above 90%"

The goal must be specific enough that a researcher agent could know what to work on without further clarification. The wizard will not advance to Step 2 until the goal passes this bar.

### Step 2: Mode Selection

Choose `metric` or `qualitative`:

- **Metric** — a number reliably produced each iteration (accuracy, latency, F1, BLEU, LLM judge score)
- **Qualitative** — success requires human or LLM judgment (literature synthesis, hypothesis generation, writing quality)

Decision rule: "Can you measure success with a number that is produced automatically each iteration?" If yes → metric. If assessing quality requires reading the output → qualitative.

### Step 3: Metric + Evaluator Design

**For metric mode:** The wizard asks for metric name, target, direction (maximize/minimize), baseline value, and the evaluator command.

**The dry-run gate:** Before proceeding, the wizard runs your evaluator on the baseline to verify it produces the expected output. This step is non-negotiable.

```
[Running evaluator dry-run: python evaluate.py --input baseline.txt]
Result: 0.847
Expected range: 0–1 (maximize toward 1.0) ✓
```

If the evaluator fails, produces unexpected output, or produces a baseline that surprises you, the wizard stops and helps you fix it. A conference with an unverified evaluator will fail at iteration 1.

**For qualitative mode:** The wizard asks you to describe what "good" looks like. It prompts for specificity:
- What makes a result clearly better than the baseline?
- What are the top 2–3 criteria the Reviewer should weight most heavily?
- Are there disqualifying failure modes?

### Step 4: Researcher Count + Role Assignment

Choose 2, 3 (recommended), or 4–5 researchers. Then decide whether to enable a Devil's Advocate researcher — one who deliberately challenges mainstream assumptions and explores contrarian strategies.

If you have 3 researchers and add a Devil's Advocate, one of the 3 fills that role. No additional agent is spawned.

### Step 5: Search Space Partitioning

Choose `assigned` (recommended) or `free`. For `assigned`, describe each researcher's specific focus area.

Examples:
- ML training: Researcher A → architecture, Researcher B → data augmentation, Researcher C → optimization hyperparameters
- Writing quality: Researcher A → structure and flow, Researcher B → evidence and citations, Researcher C → tone and clarity

Also specify `Allowed Changes` and `Forbidden Changes` — what researchers can and cannot modify.

### Step 6: Devil's Advocate Configuration

Only runs if you enabled the Devil's Advocate in Step 4. Configures:
- Which assumptions the Devil's Advocate should challenge
- What "anti-strategies" to pursue
- Whether they can propose changes that break the current evaluation metric (to stress-test the metric itself)

### Step 7: Execution Preference

Configure how the conference runs:

**Overnight / unattended:**
- Sets `pause_every: never`
- Recommends the `autoconference-loop.sh` script
- Asks for time budget, max rounds, max total iterations, researcher timeout

**Interactive:**
- Asks how often to pause for review (after every round, every N rounds, on PIVOT events only, or never)
- Same budget questions

### Step 8: conference.md Generation

The wizard writes the fully populated `conference.md` file with no placeholders. Every `{...}` in the template is replaced with a real value from Steps 1–7.

Output:

```
conference.md written to: ./my-conference/conference.md

Next steps:
1. Review the file: cat ./my-conference/conference.md
2. Run the conference: /autoconference
   OR for overnight: bash scripts/autoconference-loop.sh ./my-conference/
3. Monitor progress: bash scripts/check_conference.sh ./my-conference/
   OR tail -f ./my-conference/conference_events.jsonl

Skill chain: plan → autoconference → ship
```

---

## Example Walkthrough

**User:** "I want to run a conference to improve my sorting algorithm."

**Wizard (Step 1):** "What would success look like? What metric, what target?"

**User:** "I want it to run faster. Currently takes about 2.4 seconds on my benchmark."

**Wizard:** "Let's be specific. Target: wall-clock time in milliseconds, minimize, target < 500ms. Is that right?"

**User:** "Yes, < 500ms."

**Wizard (Step 2):** "You have a numeric target — this is metric mode."

**Wizard (Step 3):** "What command produces the wall-clock time? I'll run it now to verify the baseline."

**User:** `python benchmark.py --sort bubble`

**Wizard:** "[Running: python benchmark.py --sort bubble] Result: 2391ms. Baseline confirmed. Proceeding."

**Wizard (Step 4):** "3 researchers recommended for this search space. Add a Devil's Advocate?"

**User:** "Yes."

**Wizard (Step 5):** "Assigned strategy: Researcher A → algorithmic approach (sort algorithm choice), Researcher B → data structure optimizations (memory layout, cache), Researcher C (Devil's Advocate) → challenge all assumptions."

**... Steps 6–8 complete ...**

**Result:** `./sorting-conference/conference.md` — fully populated, evaluator verified, ready to run.

---

## Wizard Invariants

- Never writes `conference.md` before all 8 steps are complete
- Never skips the dry-run gate in Step 3 for metric mode
- Never proceeds past Step 1 without a specific, measurable goal
- Produces exactly one output file: `conference.md`
- Does not start a conference, spawn researchers, or run any research
