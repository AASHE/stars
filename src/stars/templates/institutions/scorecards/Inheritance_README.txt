Two methods of sharing template data: EXTENDING and INHERITING

= scorecards/summary.html =

{% extends 'scorecards/base.html' %}
{% include 'scorecards/summary_include.html %}

= scorecards/base.html =

{% extends 'base.html' %}

= scorecards/summary_include.html =

{% extends 'credits/summary.html' %}

= credits/summary.html =

{% extends 'credits/columned_layout.html' %}

= credits/columned_layout.html =

Designed to be included below the header

@Todo: define title policy Lower | Higher | STARS

== Duplication Notes: ==

It's hard to remove duplication entirely, but this is as close as I could get. Duplication lies in the left column with the STARS Seal and the "Institution Profile" link.