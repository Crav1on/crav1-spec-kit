# Diagrams

Read this only when you are about to draw. The flow file and `references/common.md` stay the procedure.

Use the words of the chosen approach. Do not invent one official notation for every approach.

- **Formal specification.** UML is an Object Management Group specification. A Mermaid picture in this model is not a claim of UML conformance.
- **Method-author terms.** Grain, fact, and dimension are dimensional-modeling terms. Hub, link, and satellite are Data Vault terms. They name concepts. They do not make a Mermaid shape the method's official drawing.
- **Tool convention.** Mermaid's `erDiagram` uses crow's-foot markers such as `||--o{`. That is Mermaid syntax. It is not a universal formal standard, and it is not a foreign key the database will enforce.
- **Local recommendation.** This kit draws structure as a small ER diagram and movement, layers, or ownership as a labelled flowchart. That is a communication choice. Say which arrows mean movement and which mean responsibility. The flowchart legend is not the ER legend.

Name the view in the caption: business meaning, logical structure, or physical proposal. Do not treat one box as one table unless the physical design says so. Do not treat a layer name as a modeling method. Medallion layers, when the evidence actually calls for them, are a flow. They are not the default and they are not a star schema.

Store one `er` diagram and one `flow` diagram through `diagram`. The exporter draws `erDiagram` and `flowchart` `LR` or `TD` only. Any other diagram fails the export. Show that failure. Do not drop the picture and do not paste the Mermaid source into the PDF instead.

The picture is not one long row scaled down to the page. Nodes wrap into rows, or top-down when the flowchart says TD, and the labels stay at a readable size. A wide diagram gets its own landscape page. If it is still too big, it is split into numbered parts and the page says so. The PDF titles each picture with the diagram id, such as `platform-structure`.

A rendered picture shows that the drawing was produced. It does not show that a method was followed, that a key is enforced, or that the model was tried on real data.

Labels stay short: letters, digits, spaces, and simple punctuation. Put the nuance in the caption and the decision text.
