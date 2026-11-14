# Gauss Control

Primary website: https://www.gauss-control.net/

GitHub Pages publishes the `main` branch root with HTTPS enforced.
The static files contain English, Chinese and Spanish editions and 22 product videos.

## Staged search indexing

Corporate and directory pages and the five application guides are indexable in
all three site languages. Product details, process details, individual knowledge
articles, news placeholders and design notes stay `noindex, follow` pending
editorial review. The sitemap lists the indexable canonical URLs.
The secondary Sites publication stays noindex and uses the primary domain in canonical tags.

After updating website files, reapply and validate the policy:

    python3 scripts/apply_seo_policy.py . --mode primary

Keep CNAME and relative internal URLs when publishing from GitHub Pages.
The contact form currently prepares an email draft; it is not an online submission service.
