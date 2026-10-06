---
name: content-mapper
description: Builds a content map for a personal brand through question rounds: mission (Point A to Point B), broad topics, subtopics, and post ideas. Use when the user wants to plan what to post, map their content, find their niche, or says they have too many interests to pick one.
---

# Content mapper

Walk the user through the content map in [references/step.md](references/step.md). Read it before the first round. It is the source for every rule, example, and idea angle below.

The user owns the map. Every entry on it is an answer the user gave or accepted. You ask, recommend, and record.

## Done

`content-map.md` exists in the working directory (or where the user says) and holds:

- Point A, Point B, and the mission sentence
- 2-3 broad topics (1 is fine if the user says so)
- 3-5 subtopics under each broad topic
- 3-5 post ideas under each subtopic, each tagged with its angle

`content-map.html` sits next to it with the visual map.

Every line traces to a user answer.

## Question format

Ask in rounds. Number questions across the whole session (Q1, Q2, ... never restart), so the user can reply `Q4: ...`. Use this exact format for each question:

```
[?] **Q1** - **<question title>**: <question body. Can be several paragraphs. Give lettered choices when the answer has natural options.>
[>] <your recommended answer>
```

Rules for `[>]`:

- Make it a concrete answer the user can accept as is, written in their voice. Build it from earlier answers and anything you know about the user (conversation, `.agents/product-marketing.md` if it exists).
- When you know too little to recommend, recommend the choice that gets them unstuck fastest, and say what fact would sharpen it.

End each round with one line: reply per question, or `ok` to accept all recommendations. Wait for the reply. A blank or `ok` for a question accepts its `[>]`. Ask a follow-up in the next round when an answer breaks a rule from the reference (too narrow, not one sentence, off-mission).

After each round, show the map so far as an indented tree before the next round's questions.

## Rounds

### Round 1 - Mission

Ask:

1. What they read, watch, and listen to, and what they care about. This feeds every later recommendation.
2. **Point A**: one sentence. The life their reader wants to escape. The enemy.
3. **Point B**: one sentence. The life they help the reader reach.

Then state the mission: help as many people as possible go from Point A to Point B. Confirm it in the next round's first question.

Done when Point A and Point B are each one sentence the user accepted.

### Round 2 - Territories

Ask for 2-3 broad topics. Broader than the user expects. Use the broadening examples from the reference (lead generation becomes "online business"). Each topic must help a reader move from Point A to Point B. Show the user how their scattered interests fit the mission.

Done when each broad topic is one or two words and sits between Point A and Point B.

### Round 3 - Cities

One question per broad topic. Ask for 3-5 subtopics. The subtopics are where the user's angle shows, so recommend ones that match their Round 1 interests, not a generic list.

Done when every broad topic has 3-5 accepted subtopics.

### Round 4 - Ideas

One round per broad topic, one question per subtopic. Ask for 3-5 post ideas. List the six angles in the body: pain point, how-to, lesson learned, why it matters, harsh truth, opinion on a popular idea. Ask the user to write their own first. The `[>]` holds 3-5 specific ideas, each tagged with its angle, using at least three different angles.

If the user says "who am I to write about this", answer with the reframe from the reference: they only need a different way of thinking about the idea.

Done when every subtopic has 3-5 accepted ideas. Ideas are not judged yet.

## Write the map

Write `content-map.md`:

```markdown
# Content map

**Point A:** <sentence>
**Point B:** <sentence>
**Mission:** Help as many people as possible go from <A> to <B>.

## <Broad topic>

### <Subtopic>

- [<angle>] <idea>
```

Each idea's angle is one of: `Pain point`, `How-to`, `Lesson learned`, `Why it matters`, `Harsh truth`, `Opinion`.

## Render the visual map

From this skill directory:

```bash
python3 scripts/render_map.py /path/to/content-map.md
```

It writes `content-map.html` next to the Markdown file. The page shows Point A to Point B, a radial map (mission in the centre, broad topics on the inner ring, subtopics outside), and every idea under its subtopic, colored by angle. The script uses only the Python standard library. It stops with an error when the Markdown breaks the format above. Fix the Markdown and run it again.

Give the user the HTML page. If the user cannot open local files (a remote box), publish it as an Artifact or send the file.

Done when `content-map.html` exists and its header counts match the map (topics, subtopics, ideas).

Then tell the user to copy the map by hand onto one sheet of paper and keep it next to where they work, as the reference says. The map is meant to change. Offer to rerun any round later, then render again.
