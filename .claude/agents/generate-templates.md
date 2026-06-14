# Agent: generate-templates

Generates WhatsApp message templates for Meta approval.

## Input

Read `clients/<client-id>/requirements/flows.md` for tone, escalation language, and legal constraints.

## Meta template rules (always apply)

1. No threatening language ("we will sue you", "legal action will be taken immediately")
2. Must include a clear way to respond or opt out
3. Variables use double curly braces: `{{1}}`, `{{2}}`
4. Body text max 1024 characters
5. Template name: lowercase, underscores only, max 512 chars
6. Language code must match the client's configured language

## Debt collection templates

Generate 4 templates in `clients/<client-id>/debt-templates.yaml`:

**Stage D+3 (friendly reminder)**
- Tone: warm, assumes good faith (forgotten payment, card change)
- Must include: amount, payment link variable, response invitation

**Stage D+10 (follow-up)**
- Tone: direct but not hostile
- Must include: amount, days overdue, payment link, "reply to arrange payment"

**Stage D+20 (formal notice)**
- Tone: formal, factual
- Must include: contract number, total debt, payment link, deadline date variable

**Stage D+30 (final notice)**
- Tone: firm, consequences stated without threats
- Must include: total debt, "access may be restricted", contact for arrangements

## Customer service templates

Generate templates for first-contact scenarios that happen outside the 24h window:
- Post-inquiry follow-up (lead didn't convert)
- Payment confirmation receipt
- Appointment reminder

## Output format

```yaml
templates:
  - name: retras_debt_d3
    language: es
    category: UTILITY
    components:
      - type: BODY
        text: "Hola {{1}}, te recordamos que tienes un pago pendiente de {{2}}€ con Retras. Puedes regularizarlo aquí: {{3}}"
        example:
          body_text: [["María García"], ["89.50"], ["https://pay.retras.es/abc123"]]
```
