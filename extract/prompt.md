# Extractor prompt

This is the instruction given to the extraction model, verbatim, for every fixture. It is committed
because an eval whose prompt lives only in someone's shell history is not reproducible.

The model receives this text followed by the fixture's spans, each on its own line as
`[span-id] (page N) text…`. It sees **spans only**: not the label, not the bidder profile, not the
hand-authored extraction, and it has no tools. Its whole task is to fill the schema from the text in
front of it.

---

You are extracting structured facts from one solicitation document. You will be given the document
as a list of numbered spans. Do not use any knowledge from outside this document.

Return **only** a JSON object, with no commentary, in exactly this shape:

```
{
  "fixture": "<the fixture filename given to you>",
  "facts": {
    "<name>": {"value": <string>, "citations": [{"span_id": "...", "page": <int>, "quote": "..."}]}
  },
  "requirements": {
    "<name>": {"value": <value>, "kind": "<kind>", "citations": [{"span_id": "...", "page": <int>, "quote": "..."}]}
  }
}
```

## Facts to extract

- `issuer` — the organisation issuing the solicitation.
- `subject` — what is being procured, in a few words.

## Requirements to extract

Every requirement must appear, including the ones that are false or empty. Values:

| name | kind | value |
|---|---|---|
| `requires_recurring_onsite` | `bool` | true if winning requires a standing on-site presence (regular days per week, a staffing quota that is mostly on site, or attendance at meetings in person) |
| `requires_emergency_onsite_response` | `bool` | true if the winner must physically attend site within a stated response time |
| `requires_product_supply` | `bool` | true if the issuer is buying a product, platform or licences, such that the winning bidder must supply or host the thing itself |
| `delivery_model` | `enum` | one of `advisory`, `project`, `continuous_operations`. Use `continuous_operations` when the winner monitors, pages, staffs a desk or runs a service continuously. Use `project` for a defined build or migration. Use `advisory` for a study, strategy or plan. |
| `functional_stacks` | `list` | the vendor stacks the winner must **configure functionally** — deciding how the product is set up for the customer. Exclude stack administration, hosting, migration and integration work: those are not functional configuration. Empty list if none. |

### Two distinctions that are easy to get wrong, with examples

**A travel expectation is not a standing on-site presence.**

> "Respondent staff must be able to travel to the offices located within Indianapolis."

That is business travel on a study engagement. `requires_recurring_onsite` is **false**. Reserve true
for text that commits the winner to being there repeatedly — days per week, a majority of staffing
hours on site, or attendance at meetings in person.

**Migrating onto a platform is not configuring it.**

> "Develop a migration plan and data model for the call center database to move into Dynamics 365,"
> and "implement an intelligent virtual assistant" on it.

That is project work *on* a platform. `functional_stacks` is **empty**. List a stack only when the
winner must make the product's own setup decisions — security roles, entities and fields, business
rules, workflow configuration, licence selection. "Recommend which Dynamics 365 applications and
licences to buy" and "configure security roles, teams and field-level security" are functional
configuration; "migrate the data onto it" is not.

## The citation rules — these are enforced, and a mistake is refused

1. **Every value carries at least one citation**, including a `false` or empty one. For those, cite
   the text that shows what the work actually is.
2. **`span_id` must be one of the ids given to you.** Inventing an id fails the whole extraction.
3. **`quote` must be copied character for character out of that span's text**, and must be a
   contiguous run of whole words from it. Do not retype it from memory, do not fix its spelling, do
   not reformat numbers: `$150,000` must stay `$150,000` and `four (4) hours` must not become
   `4 hours`.
4. **Quote from ONE span.** Spans are sentence-sized units and a sentence in the document may
   straddle two of them. If the words you want run across a span boundary, cite the span that holds
   the part you need and quote only that part. A quote that crosses a boundary is refused.
5. **Prefer short quotes — five to twelve words.** A short run inside one span is what you want; you
   are pointing at evidence, not reproducing the document. There is no credit for a longer quote and
   a longer quote is likelier to cross a boundary or hit a typographic character.
6. **These documents use non-breaking hyphens and typographic apostrophes** — `’` where you would
   type `'`, and `‑` where you would type `-`. `INPRS’s` and `GMV’s` are the common ones. Copy the
   characters from the span; do not reproduce them from habit.

A quote that does not appear in the cited span is rejected, and the extraction is not used.
