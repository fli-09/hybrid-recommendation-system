# Model Details

## ALS Collaborative Filtering

Alternating Least Squares (ALS) represents users and items in a shared 64-dimensional latent space. Recommendations are scored from the relationship between a user's latent vector and item vectors, allowing the service to capture collaborative behavior that is not directly expressed in product metadata.

## TF-IDF Content-Based Filtering

The content model converts product information into TF-IDF vectors using a 50,000-feature vocabulary. Cosine similarity retrieves products with related attributes and supports content-driven recommendations when interaction signals are limited.

## Hybrid Scoring

The hybrid recommender combines ALS and content scores after normalization. Its default weighted fusion is:

```text
final_score = 0.5 × normalized_als_score + 0.5 × normalized_content_score
```

This balances behavioral relevance from ALS with product similarity from TF-IDF. The inference layer uses a popular-item fallback for cold-start users.

## Evaluation Metrics

| Metric | Meaning | Result |
| --- | --- | ---: |
| Precision@10 | Fraction of the top 10 recommendations that are relevant | 0.0100 |
| Recall@10 | Fraction of relevant items retrieved in the top 10 | 0.1000 |
| Hit Rate@10 | Share of evaluated users with at least one relevant top-10 result | 0.1000 |
| Catalog Coverage | Fraction of the catalog surfaced by recommendations | 0.0016 |
