"""Official DİM block distribution for mathematics buraxılış exam.

Every topic name must EXACTLY match the Qdrant `dim_tests` payload `topic` field.
Topics that exist in Qdrant but do NOT belong to any block (İbtidai funksiya,
Törəmə, Qəbul sualları, İsbat, İmtahan sualları) are intentionally excluded —
they are either out-of-scope for buraxılış or meta-categories.
"""

DIM_MATH_BLOCKS = {
    "Ədədlər": {
        "topics": [
            "Natural ədədlər",
            "Adi və onluq kəsrlər",
            "Faiz. Nisbət. Tənasüb",
            "Həqiqi ədədlər",
            "Kvadrat köklər. Həqiqi üstlü qüvvət",
            "Kompleks ədədlər",
        ],
        "target_count": 3,
    },
    "Cəbr_və_Tənliklər": {
        "topics": [
            "Tam cəbri ifadələr",
            "Çoxhədlinin vuruqlara ayrılması",
            "Rasional kəsrlər",
            "Birməchullu tənliklər və məsələlər",
            "Tənliklər sistemi",
            "Bərabərsizliklər və bərabərsizliklər sistemi",
            "Triqonometrik tənliklər",
            "Üstlü, loqarifmik tənliklər və bərabərsizliklər",
            "Situasiya",
            "Situasiya məsələləri",
        ],
        "target_count": 6,
    },
    "Həndəsə": {
        "topics": [
            "Həndəsənin əsas anlayışları",
            "Üçbucaqlar",
            "Çevrə və dairə",
            "Çoxbucaqlılar. Dördbucaqlılar",
            "Fiqurların sahəsi",
            "Hərəkət. Oxşarlıq",
            "Vektorlar. Koordinatlar metodu",
            "Fəzada düz xətlər və müstəvilər",
            "Çoxüzlülər, onların səthi və həcmi",
            "Fırlanma cisimləri",
        ],
        "target_count": 6,
    },
    "Ardıcıllıqlar_və_Limit": {
        "topics": [
            "Ədədi ardıcıllıqlar. Silsilələr",
            "Ədədi ardıcıllığın limiti. Funksiyanın limiti",
        ],
        "target_count": 3,
    },
    "Ehtimal_və_Statistika": {
        "topics": [
            "Çoxluqlar",
            "Birləşmələr nəzəriyyəsi. Ehtimal nəzəriyyəsi və statistika",
        ],
        "target_count": 3,
    },
    "Funksiyalar": {
        "topics": [
            "Funksiyalar və qrafiklər",
            "Triqonometrik funksiyalar",
            "Üstlü və loqarifmik funksiyalar",
        ],
        "target_count": 4,
    },
}

# Topics in Qdrant that are intentionally EXCLUDED from block distribution:
# - "İbtidai funksiya və inteqral" (40 pts) — calculus, out of buraxılış scope
# - "Törəmə və tətbiqləri" (24 pts) — calculus, out of buraxılış scope
# - "İsbat məsələləri" (53 pts) — meta-category, not a real topic
# - "İmtahan sualları (2025)" (48 pts) — meta-category
# - "Qəbul imtahanı sualları" (30 pts) — qəbul, not buraxılış
