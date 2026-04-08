export const scenes = [
  {
    id: 1,
    year: "1938",
    label: "SCENE 01",
    title: "The Map Appears",
    policy: "HOLC Residential Security Maps",
    body: "In 1938, federal agents surveyed every Boston neighborhood and assigned it a color: green, blue, yellow, or red. The color determined who could get a loan. Wherever Black families lived, the grade was D: Hazardous.",
    quote:
      'Roxbury was deemed red despite its great public transit and school system because of the "infiltration of Negros." A neighborhood in Cambridge was labeled yellow despite high-class apartments because "a few Negro families moved in... and threaten to spread."',
    source: "Boston Political Review, Redlining in Boston",
    sourceUrl:
      "https://www.bostonpoliticalreview.org/post/redlining-in-boston-how-the-architects-of-the-past-have-shaped-boston-s-future",
    stat: null,
    visual: null, // placeholder: HOLC map hover interaction
  },
  {
    id: 2,
    year: "1934–1950s",
    label: "SCENE 02",
    title: "The Grade Becomes Policy",
    policy: "FHA Underwriting Manual",
    body: "The Federal Housing Administration didn't just observe segregation, it funded it. The FHA refused to insure mortgages in or near Black neighborhoods from day one of its operations. Federally-backed loans flooded green neighborhoods. Red neighborhoods got almost nothing.",
    quote:
      '"If a neighborhood is to retain stability it is necessary that property shall continue to be occupied by the same social and racial classes. A change in racial or social occupancy generally leads to instability and a reduction in value."',
    source: "Federal Underwriting Manual, used into the 1950s,via GBH News",
    sourceUrl:
      "https://www.wgbh.org/news/local/2019-11-12/how-a-long-ago-map-created-racial-boundaries-that-still-define-boston",
    stat: "The FHA excluded Black borrowers from day one, before the HOLC maps were even finished.",
    statSource: "Federal Reserve Bank of Chicago",
    statSourceUrl:
      "https://www.chicagofed.org/research/content-areas/mobility/policy-brief-federal-housing-programs-redlining",
    visual: null, // placeholder: loan distribution bar chart by district grade
  },
  {
    id: 3,
    year: "1944–1960s",
    label: "SCENE 03",
    title: "The Loans Build the Suburbs",
    policy: "GI Bill Servicemen's Readjustment Act of 1944",
    body: "After WWII, the GI Bill promised every veteran a home. White veterans moved to newly built suburbs, accumulating wealth. Black veterans were turned away by the same maps, locked in the redlined core, denied the postwar boom.",
    quote:
      '"The GI Bill helped foster a long-term boom in white wealth but did almost nothing to help build Black wealth."',
    source: "Demos How the GI Bill Left Out African Americans",
    sourceUrl:
      "https://www.demos.org/blog/how-gi-bill-left-out-african-americans",
    stat: "Families of white veterans held on average 32× the wealth of Black veterans' families.",
    statSource: "Brandeis University Institute for Economic and Racial Equity",
    statSourceUrl:
      "https://heller.brandeis.edu/news/items/releases/2023/impact-report-gi-bill.html",
    visual: null, // placeholder: wealth gap / population shift animation
  },
  {
    id: 4,
    year: "1947–1964",
    label: "SCENE 04",
    title: "Transit Follows the Money",
    policy: "MTA / MBTA Formation",
    body: "Transit expansion followed investment. The MTA and then the MBTA, formed in 1964 to serve 78 municipalities, prioritized the suburbs being built for white families. The redlined urban core received aging infrastructure and bus replacements. The Orange Line elevated through Roxbury was already being eyed for removal.",
    quote:
      '"The transportation networks built in that era served primarily the green-lined neighborhoods of the City reserved for the white and the wealthy. Through boxing people of color into specific areas and then not providing adequate transportation to leave those places, Boston ensured deep geographic segregation."',
    source: "Isaac Gewirth Race and the MBTA",
    sourceUrl: "https://www.isaacgewirth.com/work/racembta",
    stat: "The MBTA was voted into law on August 3, 1964, the first combined regional transit system in the U.S., serving 78 municipalities.",
    statSource: "MBTA The History of the T",
    statSourceUrl: "https://www.mbta.com/history",
    visual: null, // placeholder: transit lines toggle 1940 vs 1964
  },
  {
    id: 5,
    year: "1950s–1972",
    label: "SCENE 05",
    title: "Urban Renewal and the Highway That Never Came",
    policy: "Federal Urban Renewal Program + I-95 Southwest Corridor",
    body: "What redlining starved, urban renewal demolished. Roxbury was cleared for a highway that was never built. The Orange Line was eventually rerouted away from Dudley Square, the commercial heart of Black Boston, into a corridor carved out by the cancelled freeway.",
    quote:
      '"Jazz clubs ran up and down Washington Street, under the elevated rail line to downtown Boston. Dudley Station cemented the square\'s status as a major commercial center well into the 1960s. But after decades of redlining and the demolition of acres of housing for two never-built freeways, Roxbury and Dudley Square fell into decline."',
    source:
      "Next City, Fixing a Highway-Shaped Hole in the Heart of Black Boston",
    sourceUrl:
      "https://nextcity.org/features/fixing-urban-renewal-highways-cities-black-boston-neighborhoods",
    stat: "Construction of I-95 into Boston was cancelled in 1972, but the land through Roxbury had already been cleared.",
    statSource: "Orange Line Wikipedia",
    statSourceUrl: "https://en.wikipedia.org/wiki/Orange_Line_(MBTA)",
    visual: null, // placeholder: highway overlay + aerial before/after + Orange Line reroute
  },
];
