# TODO.md

- [ ] add core tools (pi: read, write, edit, bash)
- [ ] improve base system prompt
- [ ] use rich print? wait for tui overhaul?
---
- [.] add model toggle (hardcode)
  - [ ] add centralized command interface (invoke logic + retries into helper?)
  - [ ] create common state dict that is passed around? god object antipattern
---
- [x] migrate to responses api
- [x] add try/catch for rate limit/conn error
- [x] dynamic tool discovery?
- [x] update tool layout to match skill
- [x] add demo skill (/compact: skills/<name>/SKILL.md + skill.py run() hook)
- [x] migrate skills to commands (/compact: commands/compact.py, module docstring + run() hook)
- [x] flatten tool layout (tools/read/tool.py → tools/read.py)
