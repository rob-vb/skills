# skills

Personal Cursor agent skills. Clone this repo and link each skill directory into `~/.cursor/skills/`.

```bash
git clone https://github.com/rob-vb/skills.git ~/src/skills
mkdir -p ~/.cursor/skills
ln -s ~/src/skills/skills/submit-ios-app-store ~/.cursor/skills/submit-ios-app-store
```

Cursor loads a skill when `SKILL.md` sits in that folder. After linking, start a new agent chat so it sees the skill.

## Skills

| Skill | Use when |
| --- | --- |
| `content-mapper` | Planning what to post on social media: mission, broad topics, subtopics, and post ideas, built through question rounds and rendered as an HTML map. |
| `submit-ios-app-store` | Shipping a native iOS app to App Store Connect, or when the user says App Store, TestFlight, archive, or submit. |

## License

MIT
