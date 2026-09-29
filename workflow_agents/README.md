# Workflow Agents

| Folder | Pattern | Demo |
|---|---|---|
| `sequential_agent/` | Steps run **one after another** | Support ticket triage |
| `parallel_agent/` | Steps run **at the same time**, then combine | Trip planner |
| `loop_agent/` | A step **repeats** until a condition is met, or a round limit | News summarizer (under 500 words) |

## `sequential_agent`: Support Ticket Triage

A small demo of agents running **in sequence**. Type a customer complaint, and three agents handle it one after another:

```text
START → analyze_agent → reply_agent → ticket_agent
                                          🔧 create_ticket (mock)
```

| Step | Does | Saves to state |
|---|---|---|
| `analyze_agent` | Finds the name, product, issue, category and priority | `analysis` |
| `reply_agent` | Writes a short reply to the customer, using `{analysis}` | `reply` |
| `ticket_agent` | Calls `create_ticket`, then shows the ticket and the reply | `ticket` |

Each step saves its output with `output_key`, and the next step reads it with `{key}` in its instruction.

### New way vs old way

`SequentialAgent` is **deprecated** in ADK 2.x in favor of `Workflow`. The code uses `Workflow`, and the old way is kept as a comment:

```python
# NEW WAY (in the code)
root_agent = Workflow(
    name='support_ticket_triage',
    edges=[(START, analyze_agent, reply_agent, ticket_agent)],
)

# OLD WAY (commented out)
# root_agent = SequentialAgent(
#     name='support_ticket_triage',
#     sub_agents=[analyze_agent, reply_agent, ticket_agent],
# )
```

### Run

From the `adk-fundamentals` folder (with `.env` set up like `vertex_agent`):

```bash
adk web      # pick workflow_agents.sequential_agent
```

Try: *"Hi, I'm Priya. My laptop arrived with a cracked screen. I need a replacement urgently."*

Result: ticket `TKT-1001`, category **Returns**, priority **High**, plus a reply to Priya.

---

## `parallel_agent`: Trip Planner

A small demo of agents running **in parallel**. Name a city, and three research agents work on it at the same time. A planner then combines their results:

```text
          ┌─> weather_agent ─────┐
 START ──>├─> attractions_agent ─┼──> join ──> planner_agent
          └─> food_agent ────────┘
```

| Step | Does | Saves to state |
|---|---|---|
| `weather_agent` | Typical weather and what to pack | `weather` |
| `attractions_agent` | Top 3 attractions | `attractions` |
| `food_agent` | 3 local dishes to try | `food` |
| `join` (`JoinNode`) | Waits until all three are done | |
| `planner_agent` | Combines `{weather}`, `{attractions}` and `{food}` into one plan | |

The three research agents don't depend on each other, so they can run in parallel. In a test, all three finished at about 4 seconds, versus about 12 seconds if they had run one after another.

### New way vs old way

```python
# NEW WAY (in the code): a tuple in the edge = run in parallel; JoinNode waits for all
root_agent = Workflow(
    name='trip_planner',
    edges=[(START, (weather_agent, attractions_agent, food_agent), JoinNode(name='join'), planner_agent)],
)

# OLD WAY (commented out, deprecated): ParallelAgent inside a SequentialAgent
# root_agent = SequentialAgent(
#     name='trip_planner',
#     sub_agents=[
#         ParallelAgent(name='research', sub_agents=[weather_agent, attractions_agent, food_agent]),
#         planner_agent,
#     ],
# )
```

### Run

```bash
adk web      # pick workflow_agents.parallel_agent
```

Try: *"Plan a weekend trip to Paris"*, or any other city.

---

## `loop_agent`: News Summarizer

A small demo of a **loop**. Name a news topic. A news agent writes a detailed report with Google Search. A summarizer then shortens it, and the workflow **loops until the summary is under 500 words**:

```text
START -> news_agent -> summarizer_agent -> check_length --ok--> final_agent
                              ^                  |
                              └── too_long ──────┘
```

| Step | Does | Saves to state |
|---|---|---|
| `news_agent` | Uses `google_search` to write a detailed report (about 1,000 words) | `draft`, `word_count` |
| `summarizer_agent` | Shortens `{draft}` to about 75% of its length (never below 300 words) and overwrites `draft` | `draft`, `word_count` |
| `check_length` | A Python function. It routes `too_long` (500 words or more, so loop again) or `ok` (under 500, or `MAX_ROUNDS = 4` reached), and shows a status line | `rounds` |
| `final_agent` | Formats the summary with a title and one heading per story, then "Summary: N words after R round(s)" | |

The loop decision is made in Python, not by the model, so it's exact and predictable.

**Keeping the chat readable:** the news and summarizer agents use an `after_model_callback` (`save_draft`). It saves the full draft to state and shows only a short status line in the chat, so the long drafts don't fill the screen.

What you see in the chat for *"Space exploration news this week"*:

```text
📰 News report ready: 932 words
✂️ Shortened to 757 words
🔁 Round 1: 757 words, still 500 or more. Shortening again.
✂️ Shortened to 539 words
🔁 Round 2: 539 words, still 500 or more. Shortening again.
✂️ Shortened to 411 words
✅ Round 3: 411 words, under 500. Done.

## Space Exploration Weekly
### SpaceX Starship Achieves First-Ever Orbital Flight ...
### NASA's Crew-13 Astronauts Arrive Ahead of October Launch ...
...
Summary: 411 words after 3 round(s).
```

### New way vs old way

```python
# NEW WAY (in the code): a routing map sends 'too_long' back to the summarizer
root_agent = Workflow(
    name='news_summarizer',
    edges=[(START, news_agent, summarizer_agent, check_length,
            {'too_long': summarizer_agent, 'ok': final_agent})],
)

# OLD WAY (commented out, deprecated): LoopAgent with max_iterations. It needs a
# custom checker agent (or a tool that calls exit_loop) to stop when the summary is short enough.
```

### Settings

In `agent.py`: `MAX_WORDS = 500` (the target) and `MAX_ROUNDS = 4` (a safety limit, so it can't loop forever).

### Run

```bash
adk web      # pick workflow_agents.loop_agent
```

Try: *"Latest AI news"*, *"Space exploration news this week"* or *"Electric vehicle industry news"*.

The loop makes several model calls, including search. If Gemini is busy you may see a short delay while it retries.
