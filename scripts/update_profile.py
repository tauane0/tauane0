from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "tauane0"
OUTPUT = Path(".github/assets/profile.svg")


# ============================================================
# PROFESSIONAL PROFILE
# ============================================================
#
# These are intentionally MANUAL.
#
# GitHub activity and repository statistics are automatic,
# but your professional positioning remains under your control.
#

TECHNOLOGIES = [
    ("HTML", "#7ee7ff"),
    ("CSS", "#e8c8ff"),
    ("JAVASCRIPT", "#ff88cc"),
    ("PYTHON", "#7ee7ff"),
    ("REACT", "#e8c8ff"),
    ("JAVA", "#ff88cc"),
]


# These are intentionally MANUAL.
#
# A random exercise repository should not automatically become
# part of your portfolio.
#

FEATURED_REPOS = [
    "Projeto-Nails.Studio",
    "resturante-flavolo",
    "java-basico-1",
]


# ============================================================
# GITHUB GRAPHQL QUERY
# ============================================================

QUERY = """
query Profile(
    $login: String!,
    $from: DateTime!,
    $to: DateTime!
) {

    user(login: $login) {

        repositories(
            first: 100
            ownerAffiliations: OWNER
            privacy: PUBLIC
            isFork: false
        ) {

            totalCount

            nodes {

                name
                url
                description
                stargazerCount
                forkCount

                languages(
                    first: 10
                    orderBy: {
                        field: SIZE
                        direction: DESC
                    }
                ) {

                    edges {

                        size

                        node {
                            name
                            color
                        }
                    }
                }
            }
        }

        contributionsCollection(
            from: $from
            to: $to
        ) {

            totalCommitContributions

            contributionCalendar {

                totalContributions

                weeks {

                    contributionDays {

                        date
                        contributionCount
                        color
                    }
                }
            }
        }
    }
}
"""


# ============================================================
# HTML / SVG ESCAPING
# ============================================================

def esc(value):
    """
    Escape text before inserting it into the SVG.
    """
    return escape(
        str(value),
        quote=True
    )


# ============================================================
# GITHUB GRAPHQL REQUEST
# ============================================================

def github_graphql(
    token,
    variables
):
    payload = json.dumps(
        {
            "query": QUERY,
            "variables": variables
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "tauane0-profile-updater",
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        data = json.load(response)

    if data.get("errors"):

        raise RuntimeError(
            json.dumps(
                data["errors"],
                ensure_ascii=False,
                indent=2
            )
        )

    user = data.get("data", {}).get("user")

    if not user:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    return user


# ============================================================
# TECHNOLOGY BADGES
# ============================================================

def build_badges():

    result = []

    x = 114

    widths = {
        "HTML": 48,
        "CSS": 48,
        "JAVASCRIPT": 82,
        "PYTHON": 62,
        "REACT": 60,
        "JAVA": 52,
    }

    for label, color in TECHNOLOGIES:

        width = widths.get(
            label,
            60
        )

        result.append(
            f"""
            <rect
                x="{x}"
                y="314"
                width="{width}"
                height="26"
                rx="13"
                fill="rgba(15,12,28,0.85)"
                stroke="{color}"
                stroke-opacity="0.30"
            />

            <text
                x="{x + width / 2}"
                y="332"
                text-anchor="middle"
                font-family="Inter,sans-serif"
                font-size="10.5"
                font-weight="700"
                fill="{color}"
            >
                {esc(label)}
            </text>
            """
        )

        x += width + 8

    return "".join(result)


# ============================================================
# LANGUAGE ANALYTICS
# ============================================================

def build_language_analytics(
    repositories
):

    totals = {}
    colors = {}

    # --------------------------------------------------------
    # Calculate language usage
    # --------------------------------------------------------

    for repository in repositories:

        language_data = (
            repository
            .get("languages", {})
            .get("edges", [])
        )

        for edge in language_data:

            language = edge["node"]["name"]
            size = edge["size"]

            totals[language] = (
                totals.get(
                    language,
                    0
                )
                + size
            )

            colors[language] = (
                edge["node"].get("color")
                or "#7ee7ff"
            )

    ranked = sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True
    )[:8]

    if not ranked:

        ranked = [
            ("HTML", 1),
            ("CSS", 1),
            ("JavaScript", 1)
        ]

    total = sum(
        value
        for _, value in ranked
    )

    if total <= 0:
        total = 1

    # --------------------------------------------------------
    # Main bar
    # --------------------------------------------------------

    elements = []

    elements.append(
        """
        <rect
            x="40"
            y="544"
            width="720"
            height="8"
            rx="4"
            fill="rgba(255,255,255,0.06)"
        />
        """
    )

    current_x = 40

    for language, value in ranked:

        width = (
            720
            * value
            / total
        )

        color = colors.get(
            language,
            "#7ee7ff"
        )

        elements.append(
            f"""
            <rect
                x="{current_x:.2f}"
                y="544"
                width="{width:.2f}"
                height="8"
                rx="4"
                fill="{color}"
            />
            """
        )

        current_x += width

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    positions = [
        (45, 576),
        (189, 576),
        (333, 576),
        (477, 576),
        (621, 576),
        (45, 606),
        (189, 606),
        (333, 606),
    ]

    for (
        (language, value),
        (cx, cy)
    ) in zip(
        ranked,
        positions
    ):

        percentage = (
            value
            / total
            * 100
        )

        color = colors.get(
            language,
            "#7ee7ff"
        )

        elements.append(
            f"""
            <circle
                cx="{cx}"
                cy="{cy - 4}"
                r="4.5"
                fill="{color}"
            />

            <text
                x="{cx + 10}"
                y="{cy}"
                font-family="Inter,sans-serif"
                font-size="10.5"
                font-weight="700"
                fill="rgba(240,240,255,0.95)"
            >
                {esc(language)}
            </text>

            <text
                x="{cx + 10 + max(45, len(language) * 5.7)}"
                y="{cy}"
                font-family="Inter,sans-serif"
                font-size="9.5"
                fill="rgba(180,180,210,0.6)"
            >
                {percentage:.0f}%
            </text>
            """
        )

    return "".join(elements)


# ============================================================
# CONTRIBUTION CALENDAR
# ============================================================

def build_activity(calendar):

    weeks = calendar.get(
        "weeks",
        []
    )

    # GitHub normally returns enough weeks for the year.
    # Keep the latest 53 weeks.

    weeks = weeks[-53:]

    elements = []

    for week_index, week in enumerate(weeks):

        for day_index, day in enumerate(
            week["contributionDays"]
        ):

            x = (
                55
                + week_index * 12
            )

            y = (
                756
                + day_index * 12
            )

            contribution_count = day.get(
                "contributionCount",
                0
            )

            color = (
                day.get("color")
                or "#151525"
            )

            # Give zero-contribution days a consistent
            # dark background instead of relying only
            # on the API color.

            if contribution_count == 0:
                color = "#151525"

            elements.append(
                f"""
                <rect
                    x="{x}"
                    y="{y}"
                    width="10"
                    height="10"
                    rx="2.5"
                    fill="{color}"
                >
                    <title>
                        {esc(day["date"])}:
                        {contribution_count}
                        contributions
                    </title>
                </rect>
                """
            )

    return "".join(elements)


# ============================================================
# CALCULATE CONTRIBUTIONS FROM DAYS
# ============================================================

def calculate_calendar_contributions(calendar):

    total = 0

    for week in calendar.get(
        "weeks",
        []
    ):

        for day in week.get(
            "contributionDays",
            []
        ):

            total += day.get(
                "contributionCount",
                0
            )

    return total


# ============================================================
# PROJECT CARDS
# ============================================================

def build_project_card(
    repository,
    x,
    accent
):

    name = repository["name"]

    description = (
        repository.get(
            "description"
        )
        or "GitHub project"
    )

    description = " ".join(
        description.split()
    )

    if len(description) > 50:

        description = (
            description[:49]
            + "..."
        )

    words = description.split()

    line1 = ""
    line2 = ""

    for word in words:

        candidate = (
            line1
            + " "
            + word
        ).strip()

        if len(candidate) <= 30:

            line1 = candidate

        else:

            line2 = (
                line2
                + " "
                + word
            ).strip()

    languages = (
        repository
        .get("languages", {})
        .get("edges", [])
    )

    if languages:

        primary_language = (
            languages[0]
            ["node"]
            ["name"]
        )

    else:

        primary_language = "PROJECT"

    return f"""
    <a href="{esc(repository["url"])}">

        <rect
            x="{x}"
            y="920"
            width="230"
            height="180"
            rx="16"
            fill="rgba(10,8,20,0.9)"
            stroke="{accent}"
            stroke-opacity="0.25"
            stroke-width="1.5"
        />

        <text
            x="{x + 18}"
            y="950"
            font-family="Inter,sans-serif"
            font-size="14"
            font-weight="900"
            fill="#ffffff"
        >
            {esc(name[:23])}
        </text>

        <text
            x="{x + 18}"
            y="974"
            font-family="Inter,sans-serif"
            font-size="10"
            fill="rgba(190,190,220,0.8)"
        >
            {esc(line1)}
        </text>

        <text
            x="{x + 18}"
            y="990"
            font-family="Inter,sans-serif"
            font-size="10"
            fill="rgba(190,190,220,0.8)"
        >
            {esc(line2)}
        </text>

        <line
            x1="{x + 18}"
            y1="1044"
            x2="{x + 212}"
            y2="1044"
            stroke="{accent}"
            stroke-opacity="0.12"
        />

        <circle
            cx="{x + 23}"
            cy="1063"
            r="5"
            fill="{accent}"
        />

        <text
            x="{x + 34}"
            y="1067"
            font-family="Inter,sans-serif"
            font-size="10"
            font-weight="700"
            fill="{accent}"
        >
            {esc(primary_language)}
        </text>

        <text
            x="{x + 145}"
            y="1067"
            font-family="Inter,sans-serif"
            font-size="9"
            fill="rgba(200,200,230,0.5)"
        >
            ★ {repository["stargazerCount"]}
            ⑂ {repository["forkCount"]}
        </text>

    </a>
    """


# ============================================================
# BUILD COMPLETE SVG
# ============================================================

def build_svg(user):

    repositories = (
        user["repositories"]["nodes"]
    )

    # --------------------------------------------------------
    # GitHub statistics
    # --------------------------------------------------------

    stars = sum(
        repository["stargazerCount"]
        for repository in repositories
    )

    forks = sum(
        repository["forkCount"]
        for repository in repositories
    )

    repository_count = (
        user["repositories"]
        ["totalCount"]
    )

    contributions_collection = (
        user["contributionsCollection"]
    )

    commits = (
        contributions_collection
        ["totalCommitContributions"]
    )

    calendar = (
        contributions_collection
        ["contributionCalendar"]
    )

    # Calculate directly from contribution days.
    calculated_contributions = (
        calculate_calendar_contributions(
            calendar
        )
    )

    api_contributions = (
        calendar.get(
            "totalContributions",
            0
        )
    )

    # Prefer the calculated value when available.
    # It should normally match GitHub's total.
    total_contributions = (
        calculated_contributions
        if calculated_contributions > 0
        else api_contributions
    )

    print(
        f"GitHub reports "
        f"{api_contributions} total contributions."
    )

    print(
        f"Calculated from days: "
        f"{calculated_contributions}."
    )

    print(
        f"Commit contributions: "
        f"{commits}."
    )

    # --------------------------------------------------------
    # Featured repositories
    # --------------------------------------------------------

    repositories_by_name = {
        repository["name"]:
        repository
        for repository in repositories
    }

    featured = []

    # First use the manually selected
    # portfolio repositories.

    for name in FEATURED_REPOS:

        repository = (
            repositories_by_name
            .get(name)
        )

        if repository:

            featured.append(
                repository
            )

    # If one of them no longer exists,
    # fill the remaining spaces with
    # other public repositories.

    for repository in repositories:

        if repository in featured:
            continue

        featured.append(
            repository
        )

        if len(featured) >= 3:
            break

    featured = featured[:3]

    # --------------------------------------------------------
    # Project cards
    # --------------------------------------------------------

    project_positions = [
        39,
        285,
        531
    ]

    project_colors = [
        "#7ee7ff",
        "#e8c8ff",
        "#ff88cc"
    ]

    project_svg = ""

    for (
        repository,
        x,
        accent
    ) in zip(
        featured,
        project_positions,
        project_colors
    ):

        project_svg += build_project_card(
            repository,
            x,
            accent
        )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics = [

        (
            145,
            stars,
            "STARS",
            "#ffcc33"
        ),

        (
            315,
            forks,
            "FORKS",
            "#e8c8ff"
        ),

        (
            485,
            repository_count,
            "REPOS",
            "#7ee7ff"
        ),

        (
            655,
            commits,
            "COMMITS",
            "#ff88cc"
        )
    ]

    statistics_svg = ""

    for (
        x,
        value,
        label,
        color
    ) in statistics:

        statistics_svg += f"""

        <text
            x="{x}"
            y="423"
            text-anchor="middle"
            font-family="Inter,sans-serif"
            font-size="28"
            font-weight="900"
            fill="#ffffff"
        >
            {value:,}
        </text>

        <text
            x="{x}"
            y="443"
            text-anchor="middle"
            font-family="Inter,sans-serif"
            font-size="9"
            fill="{color}"
            letter-spacing="2.5"
            font-weight="800"
        >
            {label}
        </text>

        """

    for x in (
        230,
        400,
        570
    ):

        statistics_svg += f"""

        <line
            x1="{x}"
            y1="403"
            x2="{x}"
            y2="450"
            stroke="rgba(120,80,220,0.2)"
            stroke-dasharray="3 3"
        />

        """

    # ========================================================
    # COMPLETE SVG
    # ========================================================

    svg = f"""<!--
    Tauane Borges - GitHub Profile

    Automatically generated by:
    scripts/update_profile.py

    GitHub:
    https://github.com/tauane0

    DO NOT EDIT THIS FILE MANUALLY.
-->

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="800"
    height="1184"
    viewBox="0 0 800 1184"
>

<style>

@font-face {{
    font-family: Inter;
    font-style: normal;
    font-weight: 400 900;
    font-display: swap;

    src:
        url(
            https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuGkyMZhrib2Bg-4.woff2
        )
        format("woff2");
}}


@keyframes drift-r {{

    0%,100% {{
        transform: translate(0,0);
        opacity: .6;
    }}

    50% {{
        transform: translate(35px,-18px);
        opacity: 1;
    }}
}}


@keyframes drift-l {{

    0%,100% {{
        transform: translate(0,0);
        opacity: .55;
    }}

    50% {{
        transform: translate(-30px,16px);
        opacity: .95;
    }}
}}


@keyframes drift-u {{

    0%,100% {{
        transform: translate(0,0);
        opacity: .7;
    }}

    50% {{
        transform: translate(25px,-25px);
        opacity: 1;
    }}
}}


@keyframes pulse {{

    0%,100% {{
        transform: scale(1);
        opacity: .6;
    }}

    50% {{
        transform: scale(1.2);
        opacity: .35;
    }}
}}


@keyframes scan {{

    0% {{
        transform: translate(-900px,0);
    }}

    100% {{
        transform: translate(900px,0);
    }}
}}


@keyframes ring-pulse {{

    0%,100% {{
        opacity: .15;
    }}

    50% {{
        opacity: .35;
    }}
}}


.g-dr {{
    animation:
        drift-r
        8s
        ease-in-out
        infinite;
}}


.g-dl {{
    animation:
        drift-l
        9s
        ease-in-out
        infinite
        .3s;
}}


.g-du {{
    animation:
        drift-u
        7s
        ease-in-out
        infinite
        .6s;
}}


.g-p {{
    animation:
        pulse
        6s
        ease-in-out
        infinite;
}}


.g-scan {{
    animation:
        scan
        4.5s
        linear
        infinite;
}}


.g-ring {{
    animation:
        ring-pulse
        4s
        ease-in-out
        infinite;
}}


@media (
    prefers-reduced-motion: reduce
) {{

    *,
    *::before,
    *::after {{
        animation: none !important;
    }}
}}

</style>


<defs>

    <radialGradient id="g1">

        <stop
            offset="0%"
            stop-color="rgba(120,40,255,.6)"
        />

        <stop
            offset="100%"
            stop-color="rgba(120,40,255,0)"
        />

    </radialGradient>


    <radialGradient id="g2">

        <stop
            offset="0%"
            stop-color="rgba(0,200,220,.5)"
        />

        <stop
            offset="100%"
            stop-color="rgba(0,200,220,0)"
        />

    </radialGradient>


    <radialGradient id="g3">

        <stop
            offset="0%"
            stop-color="rgba(220,40,200,.45)"
        />

        <stop
            offset="100%"
            stop-color="rgba(220,40,200,0)"
        />

    </radialGradient>


    <radialGradient id="g4">

        <stop
            offset="0%"
            stop-color="rgba(40,120,255,.4)"
        />

        <stop
            offset="100%"
            stop-color="rgba(40,120,255,0)"
        />

    </radialGradient>


    <radialGradient id="g5">

        <stop
            offset="0%"
            stop-color="rgba(80,50,220,.35)"
        />

        <stop
            offset="100%"
            stop-color="rgba(80,50,220,0)"
        />

    </radialGradient>


    <linearGradient
        id="scan-gradient"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%"
    >

        <stop
            offset="0%"
            stop-color="rgba(120,200,255,0)"
        />

        <stop
            offset="40%"
            stop-color="rgba(120,200,255,.12)"
        />

        <stop
            offset="50%"
            stop-color="rgba(160,120,255,.45)"
        />

        <stop
            offset="60%"
            stop-color="rgba(120,200,255,.12)"
        />

        <stop
            offset="100%"
            stop-color="rgba(120,200,255,0)"
        />

    </linearGradient>


    <pattern
        id="grid"
        width="40"
        height="40"
        patternUnits="userSpaceOnUse"
    >

        <path
            d="M40 0L0 0 0 40"
            fill="none"
            stroke="rgba(110,80,220,.06)"
        />

    </pattern>


    <filter id="glow">

        <feGaussianBlur
            stdDeviation="2"
            result="blur"
        />

        <feMerge>

            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>

        </feMerge>

    </filter>

</defs>


<!-- ====================================================== -->
<!-- BACKGROUND                                             -->
<!-- ====================================================== -->

<rect
    width="800"
    height="1184"
    rx="24"
    fill="#060610"
    stroke="rgba(110,80,220,.2)"
    stroke-width="1.5"
/>


<rect
    width="800"
    height="1184"
    rx="24"
    fill="url(#grid)"
/>


<!-- ====================================================== -->
<!-- HEADER                                                 -->
<!-- ====================================================== -->

<ellipse
    class="g-dr"
    cx="200"
    cy="140"
    rx="180"
    ry="110"
    fill="url(#g1)"
/>


<ellipse
    class="g-dl"
    cx="620"
    cy="160"
    rx="160"
    ry="95"
    fill="url(#g2)"
/>


<ellipse
    class="g-du"
    cx="420"
    cy="110"
    rx="140"
    ry="90"
    fill="url(#g3)"
/>


<ellipse
    class="g-p"
    cx="100"
    cy="180"
    rx="120"
    ry="80"
    fill="url(#g4)"
/>


<rect
    class="g-scan"
    x="-200"
    y="120"
    width="400"
    height="40"
    fill="url(#scan-gradient)"
    opacity=".35"
/>


<circle
    class="g-ring"
    cx="400"
    cy="140"
    r="120"
    fill="none"
    stroke="rgba(120,200,255,.15)"
/>


<circle
    class="g-ring"
    cx="400"
    cy="140"
    r="80"
    fill="none"
    stroke="rgba(200,120,255,.12)"
/>


<path
    d="
        M30 20V10H45
        M770 20V10H755
        M30 260V270H45
        M770 260V270H755
    "
    fill="none"
    stroke="rgba(126,231,255,.7)"
    stroke-width="2.5"
/>


<text
    x="400"
    y="92"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="48"
    font-weight="900"
    fill="#fff"
    letter-spacing="20"
    filter="url(#glow)"
>
    Tauane Borges
</text>


<text
    x="400"
    y="132"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="11"
    fill="rgba(126,231,255,.9)"
    letter-spacing="6"
    font-weight="700"
>
    TECH STUDENT | ASPIRING FRONT-END DEVELOPER
</text>


<line
    x1="260"
    y1="150"
    x2="540"
    y2="150"
    stroke="rgba(126,231,255,.25)"
/>


<text
    x="400"
    y="175"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="10"
    fill="rgba(232,200,255,.8)"
    letter-spacing="3"
    font-weight="600"
>
    FRONT-END DEVELOPMENT | WEB &amp; UI
</text>


<text
    x="400"
    y="200"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="9.5"
    fill="rgba(126,231,255,.6)"
    letter-spacing="2"
>
    HTML | CSS | JAVASCRIPT | PYTHON | REACT | JAVA
</text>


<text
    x="400"
    y="225"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="9"
    fill="rgba(100,100,140,.5)"
    letter-spacing="1.5"
>
    github.com/{USERNAME}
</text>


<!-- ====================================================== -->
<!-- TECHNOLOGIES                                           -->
<!-- ====================================================== -->

<line
    x1="28"
    y1="294"
    x2="772"
    y2="294"
    stroke="rgba(110,80,220,.15)"
/>


{build_badges()}


<!-- ====================================================== -->
<!-- STATISTICS                                             -->
<!-- ====================================================== -->

<line
    x1="28"
    y1="378"
    x2="772"
    y2="378"
    stroke="rgba(110,80,220,.15)"
/>


<ellipse
    class="g-dl"
    cx="400"
    cy="423"
    rx="300"
    ry="55"
    fill="url(#g1)"
    opacity=".7"
/>


{statistics_svg}


<!-- ====================================================== -->
<!-- STACK ANALYTICS                                        -->
<!-- ====================================================== -->

<line
    x1="28"
    y1="502"
    x2="772"
    y2="502"
    stroke="rgba(110,80,220,.15)"
/>


<ellipse
    class="g-dr"
    cx="650"
    cy="602"
    rx="180"
    ry="100"
    fill="url(#g5)"
/>


<text
    x="40"
    y="524"
    font-family="Inter,sans-serif"
    font-size="10"
    fill="rgba(126,231,255,.85)"
    letter-spacing="4"
    font-weight="800"
>
    STACK ANALYTICS
</text>


{build_language_analytics(repositories)}


<!-- ====================================================== -->
<!-- ACTIVITY PULSE                                         -->
<!-- ====================================================== -->

<line
    x1="28"
    y1="716"
    x2="772"
    y2="716"
    stroke="rgba(110,80,220,.15)"
/>


<text
    x="40"
    y="738"
    font-family="Inter,sans-serif"
    font-size="10"
    fill="rgba(126,231,255,.85)"
    letter-spacing="4"
    font-weight="800"
>
    ACTIVITY PULSE
</text>


<text
    x="760"
    y="738"
    text-anchor="end"
    font-family="Inter,sans-serif"
    font-size="10"
    fill="rgba(232,200,255,.65)"
    font-weight="700"
>
    {total_contributions:,} contributions
</text>


{build_activity(calendar)}


<!-- ====================================================== -->
<!-- PRIMARY DEPLOYMENTS                                    -->
<!-- ====================================================== -->

<line
    x1="28"
    y1="890"
    x2="772"
    y2="890"
    stroke="rgba(110,80,220,.15)"
/>


<ellipse
    class="g-du"
    cx="400"
    cy="1000"
    rx="260"
    ry="75"
    fill="url(#g3)"
    opacity=".5"
/>


<text
    x="40"
    y="912"
    font-family="Inter,sans-serif"
    font-size="10"
    fill="rgba(126,231,255,.85)"
    letter-spacing="4"
    font-weight="800"
>
    PRIMARY DEPLOYMENTS
</text>


{project_svg}


<!-- ====================================================== -->
<!-- FOOTER                                                 -->
<!-- ====================================================== -->

<text
    x="400"
    y="1168"
    text-anchor="middle"
    font-family="Inter,sans-serif"
    font-size="8.5"
    fill="rgba(100,100,150,.45)"
    font-weight="600"
    letter-spacing="2"
>
    Tauane Borges - Estudante de Análise e Desenvolvimento de Sistemas
</text>


</svg>
"""

    return svg


# ============================================================
# MAIN
# ============================================================

def main():

    token = os.environ.get(
        "GITHUB_TOKEN"
    )

    if not token:

        raise SystemExit(
            "ERROR: GITHUB_TOKEN is not set."
        )

    now = datetime.now(
        timezone.utc
    )

    start = (
        now
        - timedelta(days=365)
    )

    print(
        "Fetching GitHub data..."
    )

    print(
        f"Username: {USERNAME}"
    )

    print(
        f"Period: {start.isoformat()} "
        f"-> {now.isoformat()}"
    )

    user = github_graphql(
        token,
        {
            "login": USERNAME,
            "from": start.isoformat(),
            "to": now.isoformat()
        }
    )

    if not user:

        raise SystemExit(
            f"GitHub user '{USERNAME}' was not found."
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    svg = build_svg(
        user
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        "Profile updated successfully:"
    )

    print(
        OUTPUT
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()