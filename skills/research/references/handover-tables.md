# Handover tables

## Fact notes

```
id    Fact                                  Doc    Kind        Why held
F1    Onboarding completion 14% in Q1       D3     fact
F2    Pricing drove the churn               D5     judgment
F3    Renewal terms hold through FY27       D2     assumption  D2 signed, no
                                                               notice clause
```

Carry why an assumption is held. Do not carry what follows if it is wrong.

## Source records

Eleven columns.

```
id | title | originator | date | locator | class
   | originator reliability | document credibility
   | derives from | licence | stored at
```

- `locator` must let someone else reopen the document. A filename alone does
  not.
- `derives from` names the document this one took its facts from, or `none`
  when it reports its own observation.

## Consulted log

```
D7  regulator's 2025 inspection report  the two findings on staffing
D8  agency press office, by phone       no answer in two attempts, dropped
D9  vendor status page                  current state only, no history, useless
```
