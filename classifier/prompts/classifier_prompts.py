HOTPOT_CLASSIFICATION_PROMPT = """
You are analyzing a HotpotQA-style question.

Your task is to classify the question into:
- **intent** → reasoning type (choose from: comparison, bridge)
- **attributes** → domain attributes (choose from: person, organization, location, date, number, artwork, event, adjective, common_noun, proper_noun, yes_no)
- **entities** → entities describing what is the question is about (give up to two entities)

---

### Reasoning Type Definitions
- **comparison**: compares two or more entities (e.g., "Which film was released earlier?")
- **bridge**: requires combining facts across multiple entities (e.g., "Who directed the movie that stars Tom Hanks?")

### Domain Attributes
person, organization, location, date, number, artwork, event, adjective, common_noun, proper_noun, yes_no

---

### Examples

**Example 1**
Q: Which artist is older, Rihanna or Beyoncé?
→ Intent: comparison
→ Attributes: ["person", "date"]
→ Entities: ["artist", "older"]

**Example 2**
Q: What is the capital of the country that borders both France and Germany?
→ Intent: bridge
→ Attributes: ["location", "common_noun"]
→ Entities: ["capital", "border"]

**Example 3**
Q: Was King Edward II born before Queen Elizabeth I?
→ Intent: comparison
→ Attributes: ["person", "date", "yes_no"]
→ Entities: ["born"]

**Example 4**
Q: Which film was directed by the same person who directed Die schweigsame Frau?
→ Intent: bridge
→ Attributes: ["artwork", "person"]
→ Entities: ["film", "directed"]

**Example 5**
Q: Which city has a larger population, San Diego or San Jose?
→ Intent: comparison
→ Attributes: ["location", "number"]
→ Entities: ["population"]

---

Return ONLY valid JSON in the form:
{{
  "intent": "<comparison|bridge>",
  "attributes": ["<attribute>", ...],
  "entities": ["<entity>", ...]
}}

QUESTION: {question}
"""

