# The visual

Read this in step 3. Every run that writes screens produces at least one visual. You suggest one type with a one-line reason. The user confirms it, changes it, or adds another type.

## Which type to suggest

| The screens need | Suggest | Where it lives |
| --- | --- | --- |
| Zoom, docking, motion, or a clickable flow between screens | **HTML mock** | `ui/mock/index.html`, plus one file per screen when that is clearer |
| A static layout: regions, lists, forms, panels | **PlantUML Salt** | a fenced `plantuml` block with `@startsalt` under the screen's `#### Layout` in `ui/design.md` |
| Flows between screens, or the states of one screen | **Mermaid** | a fenced `mermaid` block under `#### Flow` in `ui/experience.md` |

The reason is one line that names the need, for example `HTML mock, because the canvas zooms and the side panels dock.` A slice often has a static layout and a state flow: suggest Salt and say Mermaid comes with it for the flow.

**Text art** is allowed only when none of the three can be rendered where the team reads the files. Put it in a `text` fence and say why in the `## Visual` line.

## The card

Card: Which visual should the screens get?
- **The suggested type (Recommended)**: name it and its one-line reason; it is written as the table above says.
- **Another type instead**: name the other type; the same screens are drawn that way, and the suggestion is not written.
- **Add an HTML mock too** (`with-mock`): keep the suggested type and also write the throwaway clickable mock under `ui/mock/`.
- **No mock this run** (`skip-mock`): Salt for the layout and Mermaid for the flow, inside the Markdown only.

Leave out the option that repeats the suggestion, for example `Add an HTML mock too` when the mock is the suggestion. `with-mock` or `skip-mock` in the invocation answers this card without asking.

## The HTML mock

- One self-contained file per page under `ui/mock/`, plain HTML, CSS and a little script, no build step, no package, no network font or image. Use the tokens from `ui/design.md` as CSS variables.
- Throwaway. It is never shipped, never copied into the application, and never named as a plan input or a file likely touched. The plan reads the Markdown, not the mock.
- It may show every state with a switcher. Text on it matches the Markdown. When the user changes the mock in feedback, write the change into the Markdown first; the mock follows the text.
- No image files. A logo or an icon is a CSS shape, an inline SVG, or a text label.

## Salt and Mermaid

- Salt: `@startsalt` and `@endsalt` inside a `plantuml` fence. One block per screen layout. Keep labels short and the same words as the Markdown.
- Mermaid: `stateDiagram-v2` for the states of one screen, `flowchart` for moving between screens. Node names without spaces; labels in the Markdown words.
- These blocks are part of the Markdown, so a change to them is a change to that screen's layout or flow.
