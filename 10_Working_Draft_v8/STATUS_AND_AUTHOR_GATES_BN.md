# CBDC paper v8: বর্তমান অবস্থা ও author gates

তারিখ: 29 August 2026

## নিশ্চিত সিদ্ধান্ত

- Canonical six-field intake ব্যবহারকারী `CONFIRM INTAKE` দিয়ে নিশ্চিত করেছেন।
- JFMI এখন একটি **provisional trial target**; এটি final confirmed journal নয়।
- Journal-neutral v8 master অপরিবর্তিত authoritative source হিসেবে থাকবে।
- JFMI branch reversible; অন্য journal বেছে নিলে neutral master থেকে নতুন branch তৈরি করা যাবে।
- বর্তমান author draft-এ systems/cryptography বা privacy/AML independent review-কে submission requirement হিসেবে উল্লেখ করা হয়নি।
- Publishing title নিশ্চিত ও প্রয়োগ করা হয়েছে: `Composable assurance for sovereign digital currency (CBDC): An evidence-gated qualification framework`।
- Author name `Zubaer Mahmood Zubraj`, email `zmzubraj@gmail.com`, canonical ORCID, এবং `Self-funded` statement প্রয়োগ করা হয়েছে।
- Code/repository licence হিসেবে MIT প্রয়োগ করা হয়েছে; manuscript/figure content licence আলাদা gate।
- Submission exclusivity author নিশ্চিত করেছেন।

## প্রস্তুত deliverables

- Journal-neutral author draft: DOCX এবং PDF।
- Provisional JFMI blinded manuscript: DOCX এবং PDF।
- Separate JFMI title-page template।
- Figure/table legends document।
- 16টি editable SVG figure।
- Reproducible prototype, formal model, synthetic experiments, queueing simulation, tests, provenance, citation audit, and checksums।

## Verification snapshot

- Test suite: 14/14 passed।
- Journal-neutral verifier: `PASS`।
- JFMI verifier: `PASS_WITH_AUTHOR_GATES`।
- Abstract: 185 words; keywords: 6; key messages: 4।
- JFMI main-text count: 5,355 words including table text।
- Citations/references: 44/44 author-date/APA-mapped।
- Figures/tables: 16/22; separate editable SVG figures: 16।
- Blinded identity check: `PASS`।
- End-to-end checksum verification: 164/164 files passed।

## আপনার কাছ থেকে যে তথ্যগুলো এখনও দরকার

নিচের তথ্য বা সিদ্ধান্তগুলো নিশ্চিত না হওয়া পর্যন্ত title page এবং declarations ইচ্ছাকৃতভাবে gated থাকবে:

**29 August 2026 author instruction:** affiliation, postal address, corresponding-author designation, conflict statement এবং AI wording আপনি পরে manually যোগ করবেন। Automated workflow এগুলো skip করবে এবং অনুমান করবে না।

1. Affiliation।
2. Full postal address।
3. Corresponding author কে।
4. Conflict-of-interest statement।
5. সত্যনিষ্ঠ AI-use acknowledgement অনুমোদন বা সংশোধন। ব্যবহারকারী বর্তমান wording-এ `No` বলেছেন; actual AI use গোপন করা হবে না।
6. GitHub public owner-authorized research repository: `https://github.com/zmzubraj/composable-assurance-cbdc`; DOI/Zenodo deposit এবং final content licence এখনও author gate।
7. JFMI final target হিসেবে confirm করবেন কি না।

## Evidence boundary

বর্তমান paper formal, synthetic, simulation, public-list benchmark, এবং internal local-prototype evidence সমর্থন করে। এটি certified-HSM, physical multi-region, governed institutional data, independent field replication, বা national deployment evidence দাবি করে না। এই সীমা না বদলালে একটি নতুন production software product বা live CBDC deployment publication-এর পূর্বশর্ত নয়; বর্তমান minimal research prototype-ই paper-এর bounded contribution পরীক্ষা করার জন্য ব্যবহৃত হয়েছে।

## পরবর্তী safe step

উপরের অবশিষ্ট author fields পাওয়া গেলে title page ও declarations পূরণ করে final venue branch পুনর্নির্মাণ করা যাবে। কোনো portal upload বা final submission human approval ছাড়া করা হবে না।
