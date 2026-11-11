# Support message triage

Input: one support message up to 4,000 characters. Output: `category` (billing, bug, feature, other), `urgency` (low, medium, high), `suggested_team` (billing, engineering, product, support), and confidence from 0 to 1. The task is one classification, has a closed output schema, and a person can grade the category/team/urgency. Ambiguous messages map to other/support with low confidence. Do not send private customer material to a provider without appropriate authorization.
